"""Tests for fct_daily_order_revenue. One test per §10 row in docs/20-impl-spec/fct_daily_order_revenue.impl.md."""

import csv
from datetime import datetime
from pathlib import Path

from conftest import assert_no_fanout, assert_rows, assert_unique
from pipelines.gold.fct_daily_order_revenue import KEY, split_valid, transform

ORDER_SCHEMA = ("order_id string, customer_id string, order_placed_at timestamp, status string, "
                "is_test_account boolean, amount_cents bigint, tax_cents bigint")
GOLDEN = Path(__file__).resolve().parents[1] / "golden" / "fct_daily_order_revenue"


def ts(s):
    return datetime.fromisoformat(s)


def orders(spark, rows):
    return spark.createDataFrame(rows, ORDER_SCHEMA)


def customers(spark, rows):
    return spark.createDataFrame(rows, "customer_id string, region_code string")


# T-01 · asserts BR-01, BR-02 · traces to M-03, M-04, AE-01
def test_t01_completed_only_and_test_accounts_excluded(spark):
    o = orders(spark, [
        ("o1", "c1", ts("2026-09-01 10:00:00"), "completed", False, 1000, 100),
        ("o2", "c1", ts("2026-09-01 11:00:00"), "cancelled", False, 5000, 0),
        ("o3", "c1", ts("2026-09-01 12:00:00"), "refunded", False, 7000, 0),
        ("o4", "c1", ts("2026-09-01 13:00:00"), "completed", True, 9000, 0),
    ])
    out = transform(o, customers(spark, [("c1", "EMEA")]))
    assert_rows(out, [{"order_date": ts("2026-09-01").date(), "region_code": "EMEA",
                       "completed_order_count": 1, "revenue_cents": 900}], KEY)


# T-02 · asserts BR-04 · traces to M-01, AE-01
def test_t02_utc_day_boundary(spark):
    o = orders(spark, [
        ("o1", "c1", ts("2026-09-01 23:59:00"), "completed", False, 100, 0),
        ("o2", "c1", ts("2026-09-02 00:01:00"), "completed", False, 200, 0),
    ])
    out = transform(o, customers(spark, [("c1", "EMEA")]))
    assert sorted((r.order_date.isoformat(), r.revenue_cents) for r in out.collect()) == [
        ("2026-09-01", 100), ("2026-09-02", 200)]


# T-03 · asserts J-01 cardinality N:1 · traces to AE-01
def test_t03_join_to_dim_customer_does_not_fan_out(spark):
    o = orders(spark, [("o1", "c1", ts("2026-09-01 10:00:00"), "completed", False, 100, 0),
                       ("o2", "c2", ts("2026-09-01 10:00:00"), "completed", False, 100, 0)])
    c = customers(spark, [("c1", "EMEA"), ("c2", "APAC")])
    assert_no_fanout(o, o.join(c, "customer_id", "left"))


# T-04 · asserts BR-05 · traces to M-02, AE-01
def test_t04_missing_region_is_unknown(spark):
    o = orders(spark, [("o1", "c9", ts("2026-09-01 10:00:00"), "completed", False, 100, 0)])
    out = transform(o, customers(spark, [("c1", "EMEA")]))
    assert [r.region_code for r in out.collect()] == ["UNKNOWN"]


# T-05 · asserts DQ-02, BR-06 · traces to AE-01
def test_t05_bad_rows_quarantined_not_dropped(spark):
    o = orders(spark, [("o1", "c1", ts("2026-09-01 10:00:00"), "completed", False, 100, 0),
                       ("o2", "c1", ts("2026-09-01 10:00:00"), "completed", False, None, 0)])
    valid, quarantined = split_valid(o)
    assert valid.count() + quarantined.count() == o.count()
    assert [r.dq_rule_id for r in quarantined.collect()] == ["DQ-02"]


# T-06 · golden data GD-01..GD-03 · traces to AE-02
def test_t06_golden(spark):
    def load(name, schema):
        with open(GOLDEN / name) as f:
            rows = list(csv.DictReader(f))
        return rows, schema
    orows, _ = load("input_orders.csv", ORDER_SCHEMA)
    crows, _ = load("input_customers.csv", None)
    o = orders(spark, [(r["order_id"], r["customer_id"], ts(r["order_placed_at"]), r["status"],
                        r["is_test_account"] == "true", int(r["amount_cents"]), int(r["tax_cents"])) for r in orows])
    c = customers(spark, [(r["customer_id"], r["region_code"] or None) for r in crows])
    erows, _ = load("expected.csv", None)
    expected = [{"order_date": ts(r["order_date"]).date(), "region_code": r["region_code"],
                 "completed_order_count": int(r["completed_order_count"]), "revenue_cents": int(r["revenue_cents"])}
                for r in erows]
    assert_rows(transform(o, c), expected, KEY)


# T-07 · asserts DQ-01 · traces to AE-01
def test_t07_output_unique_on_grain(spark):
    o = orders(spark, [(f"o{i}", "c1", ts("2026-09-01 10:00:00"), "completed", False, 100, 0) for i in range(5)])
    assert_unique(transform(o, customers(spark, [("c1", "EMEA")])), KEY)


# T-08 · reconciliation: control total · traces to M-04, BR-03, AE-03
def test_t08_revenue_reconciles_to_source(spark):
    o = orders(spark, [
        ("o1", "c1", ts("2026-09-01 10:00:00"), "completed", False, 1000, 100),
        ("o2", "c2", ts("2026-09-01 11:00:00"), "completed", False, 2000, 200),
        ("o3", "c3", ts("2026-09-02 11:00:00"), "completed", False, 500, 0),
        ("o4", "c1", ts("2026-09-02 12:00:00"), "refunded", False, 800, 0),
    ])
    c = customers(spark, [("c1", "EMEA"), ("c2", "APAC")])
    out_total = sum(r.revenue_cents for r in transform(o, c).collect())
    source_total = sum(r.amount_cents - r.tax_cents for r in o.collect() if r.status == "completed")
    assert out_total == source_total
