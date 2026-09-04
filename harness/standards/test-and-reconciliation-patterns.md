# Test and Reconciliation Patterns

*v0: drafted ahead of Session 6. Re-align after delivery.*

*Harness standard · S6 · owner: see `OWNERS.md` · reviewed by `dq-reviewer`*

Three different questions, three kinds of evidence. Don't let one stand in for another.

| Question | Evidence | Finds | Can't find |
|---|---|---|---|
| Does the code do what the spec says? | **Transformation tests** on small, hand-built data | logic errors, wrong joins, wrong grain | problems in real data |
| Is the data what the contract promises? | **DQ rules** running on every load | bad rows, drift, freshness | logic that is consistently wrong |
| Did target reproduce source / an independent truth? | **Reconciliation** | lost rows, double counting, restatement | a row that both systems dropped |

---

## Traceability convention (enforced by `trace_check.py` check 9)

Every test carries its `T-` ID and what it traces to, on the line above or in its name:

```python
# T-03 · asserts J-01 cardinality N:1 · traces to BR-02, AE-02
def test_t03_invoice_to_account_is_many_to_one(spark): ...
```

A test that traces to nothing is testing the framework.

---

## Transformation tests

Pure functions, small DataFrames built inline, local Spark (`tests/conftest.py` in the project template). One behaviour per test.

| Pattern | Asserts | Template |
|---|---|---|
| **Grain** | output unique on the contract key | `assert df.groupBy(*key).count().filter("count > 1").count() == 0` |
| **Join cardinality** | the `J-` cardinality holds; no fan-out | row count before join == row count after for N:1 |
| **Rule** | one `BR-` on a minimal input, both sides: a row that should be included, one that shouldn't | build 2–4 rows, assert exact output |
| **Exclusion** | the excluded case really is gone *and* nothing else went with it | assert excluded id absent **and** total count = expected |
| **Edge** | nulls, zero, negative, boundary dates, month-end, timezone midnight, duplicates | one test per contract `edge case` rule |
| **Negative / mutation** | the test fails when the rule is removed | temporarily invert the rule; the test must go red. Do this once per `BR-` when the test is written |
| **Golden** | output equals a reviewed expected result for the golden set inputs | compare to `tests/golden/<object>/expected.*` |

**Mutation check rule:** a rule test that still passes when the rule is deleted doesn't test the rule. Check it once when you write the test.

---

## Reconciliation

| Pattern | Use | Pass condition |
|---|---|---|
| **Row count by partition** | every migration and every load from an external source | counts equal per period, or the difference is explained by a contract rule |
| **Control totals** | money and quantities | `SUM` per period/key equal to the cent; difference = 0 unless a `BR-` explains it |
| **Key set difference** | migration parity | `source EXCEPT target` and `target EXCEPT source` both empty, or every row explained |
| **Full-row hash** | parity contracts with `MUST_MATCH` | `md5(concat_ws('|', cols…))` per key; mismatches listed, not just counted |
| **Independent truth** | Tier 3 financial | target total vs a system of record (GL, billing) per period, with tolerance stated in contract §11 |

```sql
-- Control total by period: one row per period that disagrees
WITH s AS (SELECT period, SUM(amount_cents) AS total_cents, COUNT(*) AS n FROM source GROUP BY period),
     t AS (SELECT period, SUM(amount_cents) AS total_cents, COUNT(*) AS n FROM target GROUP BY period)
SELECT COALESCE(s.period, t.period) AS period,
       s.n AS source_rows, t.n AS target_rows,
       s.total_cents AS source_cents, t.total_cents AS target_cents,
       COALESCE(t.total_cents, 0) - COALESCE(s.total_cents, 0) AS diff_cents
FROM s FULL OUTER JOIN t ON s.period = t.period
WHERE s.n IS DISTINCT FROM t.n OR s.total_cents IS DISTINCT FROM t.total_cents;
```

**Report every difference with a disposition:** explained by `BR-nn`, `INTENTIONAL_CHANGE` (parity contract), or **unexplained → blocks**. "Within tolerance" is only allowed if contract §11 states the tolerance.

**Reconciliation can't see what both sides dropped.** For migrations, pair it with characterization against captured source inputs (`modernization-playbook.md`).

---

## Quarantine pattern (Lakeflow)

```python
from pyspark import pipelines as dp   # older code: import dlt as dp
from pyspark.sql import functions as F

RULES = {"DQ-02 account_id not null": "account_id IS NOT NULL",
         "DQ-03 amount non-negative": "amount_cents >= 0"}
VALID = " AND ".join(f"({r})" for r in RULES.values())

@dp.table(name="fct_example")
@dp.expect_all(RULES)                       # metrics, keep scanning
def fct_example():
    return spark.read.table("int_example").where(VALID)

@dp.table(name="fct_example_quarantine")
def fct_example_quarantine():
    return (spark.read.table("int_example").where(f"NOT ({VALID})")
            .withColumn("quarantined_at", F.current_timestamp()))
```

The same split works in a job: one `filter(valid)` writes the target, one `filter(~valid)` appends to quarantine, **in the same transaction or run**, so the two counts always add up to the input.

---

## What evidence goes with the gate

| Tier | Minimum |
|---|---|
| 1 | transformation tests for each `BR-` |
| 2 | + grain + join cardinality + every `DQ-` executable + golden set |
| 3 | + mutation-checked rule tests + reconciliation against an independent source, with the result attached to contract §11 |

Test output (JUnit XML, `pytest --junitxml=reports/junit.xml`) is the artefact the gate cites, not a statement that "tests pass".
