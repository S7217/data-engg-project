# Data Quality Standard and Bad-Data Disposition Policy

*v0: drafted ahead of Session 6. Re-align after delivery.*

*Harness standard · S6 · owner: Steward · see `OWNERS.md` · reviewed by `dq-reviewer`*

Two halves. **Rules** say what "good" means and who answers for it. **Disposition** says what happens to the rows that fail.

---

## Part 1: DQ rules

Every `DQ-` rule has **six fields**. A rule missing any of them isn't a control, it's just something somebody once noticed.

| Field | Meaning | Example |
|---|---|---|
| Expectation | One testable sentence | `subscription_id` is never null |
| Threshold | Failure rate (or bound) that triggers the rule | `0%` · `≤ 0.1%` · `row count within ±10% of 28-day median` |
| Severity | `ERROR` halts publication · `WARNING` publishes and notifies · `INFO` is logged only | `ERROR` |
| Disposition | What happens to failing rows (Part 2) | `quarantine` |
| Routing | Who is notified, and where | on-call data engineer, `#data-alerts` |
| Owner | **A named role** accountable for fixing it | Finance data steward |

"Data team" isn't an owner. If nobody is woken up when a rule fails, the rule is a monitoring cost, not a control.

### How the six fields map onto the contract (v1.1, unchanged)

| Contract §8 column | Carries |
|---|---|
| Expectation · Threshold · Severity | the same three fields |
| On failure | **disposition** (warn / drop / fail / quarantine) |
| Alert owner | **owner** and **routing**: a role, plus where they're notified (e.g. "Finance steward · #fin-data-alerts") |

### Where rules live

| Stage | Location |
|---|---|
| Business expectation | contract §8 (business language, with threshold, severity and owner) |
| Executable check | impl spec §9 → Lakeflow pipeline expectation, a test, or a monitor |
| Test evidence | `tests/`, with the `DQ-` ID in the test's comment or name |

### Default rule set: every gold table

| Rule | Threshold | Severity | Disposition |
|---|---|---|---|
| Grain uniqueness on the contract §5 key | 0% | ERROR | fail |
| Key columns not null | 0% | ERROR | quarantine |
| Referential integrity to conformed dimensions | 0% | ERROR | quarantine |
| Freshness within contract §7 | per contract | WARNING | — |
| Row volume within expected band | ±(set from history) | WARNING | — |
| Contract-specific business rules | per contract | per contract | per contract |

A gold table missing one of the first three needs a §14 deviation with the steward's acceptance.

### Lakeflow expectation mapping

| Disposition | Lakeflow Declarative Pipelines (`from pyspark import pipelines as dp`; older code: `import dlt`, same decorator names) |
|---|---|
| `warn` | `@dp.expect` / `EXPECT (...)`: rows kept, metric recorded |
| `drop` | `@dp.expect_or_drop` / `ON VIOLATION DROP ROW` |
| `fail` | `@dp.expect_or_fail` / `ON VIOLATION FAIL UPDATE` |
| `quarantine` | no single keyword. Route failing rows to `<object>_quarantine` with an inverted expectation (see `test-and-reconciliation-patterns.md`) |

Expectation metrics land in the pipeline event log. Monitoring reads them from there, not from logs.

---

## Part 2: Bad-data disposition policy

### The default

> **Rows are never silently dropped.** Unless a contract `tolerance` rule (§6) says otherwise, a failing row is **quarantined**: kept, reviewable and reprocessable.

`drop` is allowed only where the contract states, in business language, that the business accepts losing those rows without being told. *"Test accounts may be discarded"* is a valid tolerance rule. *"Bad rows are dropped"* isn't. It's an engineer making a business decision.

### Choosing a disposition

| Disposition | Use when | Required with it |
|---|---|---|
| `fail` | A violation means the whole batch is untrustworthy: grain breach, schema break, empty load | alert to owner; publication blocked |
| `quarantine` | Individual rows are bad and the rest is fine | quarantine table, named reviewer, retention, reprocessing path |
| `warn` | Data is usable but suspicious | notification route; a threshold at which it escalates to `fail` |
| `drop` | The contract has an explicit tolerance rule allowing it | the `BR-` tolerance rule ID; a count of dropped rows logged on every run |

### Quarantine table contract

Every quarantine table carries the failing row as-is plus: `dq_rule_id`, `quarantined_at`, `source_run_id`, `reason`, `is_reprocessed`, `reprocessed_at`.

| Concern | Rule |
|---|---|
| Reviewer | a named role, recorded in impl spec §5. If nobody reviews it, the table just grows forever |
| Review cadence | at least weekly; daily for Tier 3 |
| Retention | 90 days by default, or the source's retention if that's longer |
| Reprocessing | idempotent: a fixed row re-enters through the normal pipeline and is marked `is_reprocessed` |
| Escalation | quarantine rate above the rule threshold for 3 consecutive runs becomes an incident (`incident-and-rollback.md`) |
| Sensitivity | the same as the source object, never lower |

### Precedence

Contract §8 per-rule disposition **wins** over the contract §6 `tolerance` default, which wins over anything chosen in the implementation spec. If the impl spec disagrees with the contract, the contract is right and the spec is wrong.

### Sign-off

The steward signs the disposition of every Tier 2–3 rule, through the contract gate. Disposition changes after publication re-gate the contract.
