# grain: one row per order_date (UTC) per region_code
# contract: docs/10-contract/fct_daily_order_revenue.contract.md (pinned 1.0 in impl spec §0)
# implements: BR-01, BR-02, BR-03, BR-04, BR-05, BR-06, BR-07
"""fct_daily_order_revenue: built from docs/20-impl-spec/fct_daily_order_revenue.impl.md."""

import argparse
from datetime import date, timedelta

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

KEY = ["order_date", "region_code"]  # contract §5
RECOMPUTE_DAYS = 3  # impl spec §4: late orders arrive within 3 days

# BR-07: explicit column lists. A new source column never reaches the output unreviewed.
ORDER_COLUMNS = ["order_id", "customer_id", "order_placed_at", "status", "is_test_account", "amount_cents", "tax_cents"]
CUSTOMER_COLUMNS = ["customer_id", "region_code"]

# DQ-02 (disposition: quarantine, BR-06)
QUARANTINE_RULES = {"DQ-02": "order_id IS NOT NULL AND amount_cents IS NOT NULL"}


def split_valid(orders: DataFrame) -> tuple[DataFrame, DataFrame]:
    """Valid orders, and failing orders tagged with dq_rule_id. The two always add up to the input."""
    valid_expr = " AND ".join(f"({c})" for c in QUARANTINE_RULES.values())
    first_failed = F.coalesce(*[F.when(~F.expr(c), F.lit(rid)) for rid, c in QUARANTINE_RULES.items()])
    flagged = orders.withColumn("dq_rule_id", first_failed)
    return flagged.where(F.expr(valid_expr)).drop("dq_rule_id"), flagged.where(~F.expr(valid_expr))


def transform(orders: DataFrame, customers: DataFrame) -> DataFrame:
    """Pure transformation. Session timezone must be UTC (BR-04)."""
    completed = orders.select(*ORDER_COLUMNS).where(
        (F.col("status") == "completed")             # M-03, M-04 · BR-01
        & ~F.coalesce(F.col("is_test_account"), F.lit(False))  # BR-02 (cancelled/refunded excluded by BR-01 filter)
    )
    # J-01 · N:1 per dim_customer contract 1.0 §5 (one row per customer_id). Asserted by T-03.
    joined = completed.join(customers.select(*CUSTOMER_COLUMNS), "customer_id", "left")
    return (
        joined
        .withColumn("order_date", F.to_date("order_placed_at"))                    # M-01 · BR-04
        .withColumn("region_code", F.coalesce("region_code", F.lit("UNKNOWN")))     # M-02 · BR-05
        .groupBy(*KEY)
        .agg(
            F.countDistinct("order_id").cast("bigint").alias("completed_order_count"),        # M-03 · BR-01, BR-02
            F.sum(F.col("amount_cents") - F.col("tax_cents")).cast("bigint").alias("revenue_cents"),  # M-04 · BR-03
        )
    )


def assert_unique(df: DataFrame, key: list[str]) -> None:
    """DQ-01: fail the run on a grain breach."""
    dupes = df.groupBy(*key).count().where("count > 1").count()
    if dupes:
        raise ValueError(f"DQ-01 grain breach: {dupes} duplicated {key}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", required=True)
    p.add_argument("--schema", required=True)
    p.add_argument("--start-date", default="")
    p.add_argument("--end-date", default="")
    a = p.parse_args()

    spark = SparkSession.builder.getOrCreate()
    spark.conf.set("spark.sql.session.timeZone", "UTC")  # BR-04
    end = date.fromisoformat(a.end_date) if a.end_date else date.today() - timedelta(days=1)
    start = date.fromisoformat(a.start_date) if a.start_date else end - timedelta(days=RECOMPUTE_DAYS - 1)
    target = f"{a.catalog}.{a.schema}.fct_daily_order_revenue"

    orders = (spark.read.table(f"{a.catalog}.sales_silver.int_orders")
              .where(F.to_date("order_placed_at").between(start.isoformat(), end.isoformat())))
    customers = spark.read.table(f"{a.catalog}.crm_silver.dim_customer")

    valid, quarantined = split_valid(orders)
    run_id = spark.conf.get("spark.databricks.job.runId", "interactive")
    (quarantined.withColumn("quarantined_at", F.current_timestamp())
        .withColumn("source_run_id", F.lit(run_id))
        .withColumn("reason", F.col("dq_rule_id"))
        .withColumn("is_reprocessed", F.lit(False))
        .withColumn("reprocessed_at", F.lit(None).cast("timestamp"))
        .write.mode("append").saveAsTable(f"{target}_quarantine"))

    out = transform(valid, customers)
    assert_unique(out, KEY)  # DQ-01

    # SP-01: idempotent. Replace exactly the recomputed window.
    (out.write.mode("overwrite")
        .option("replaceWhere", f"order_date BETWEEN '{start}' AND '{end}'")
        .saveAsTable(target))


if __name__ == "__main__":
    main()
