"""Shared test fixtures and assertions. Patterns: harness/standards/test-and-reconciliation-patterns.md

Every test carries its T- ID and what it traces to (trace_check.py check 9):

    # T-03 · asserts J-01 cardinality N:1 · traces to BR-02, AE-02
    def test_t03_invoice_to_account_is_many_to_one(spark): ...
"""

import os
import time

import pytest

# Deterministic time: PySpark converts naive Python datetimes using the *process* timezone,
# so a test written in UTC would shift by the laptop's offset. Pin the test process to UTC.
os.environ["TZ"] = "UTC"
time.tzset()


@pytest.fixture(scope="session")
def spark():
    from pyspark.sql import SparkSession

    s = (
        SparkSession.builder.master("local[1]")
        .appName("tests")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield s
    s.stop()


def assert_unique(df, key):
    """Grain: no two rows share the contract key."""
    dupes = df.groupBy(*key).count().where("count > 1")
    n = dupes.count()
    assert n == 0, f"grain breach on {key}: {n} duplicated key(s), e.g. {dupes.limit(5).collect()}"


def assert_no_fanout(left, joined):
    """N:1 / 1:1 join: row count is unchanged by the join."""
    assert joined.count() == left.count(), f"join fan-out: {left.count()} → {joined.count()} rows"


def assert_rows(df, expected, key):
    """Exact output: same rows as `expected` (list of dicts), compared by key, order-insensitive."""
    actual = sorted((r.asDict() for r in df.collect()), key=lambda r: tuple(r[k] for k in key))
    expected = sorted(expected, key=lambda r: tuple(r[k] for k in key))
    assert actual == expected, f"\nexpected: {expected}\nactual:   {actual}"
