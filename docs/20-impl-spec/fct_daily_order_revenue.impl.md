# Implementation Spec

### How it is built

*Harness template · implementation spec · **v1.1** · filled for the S7 demo. People named are fictional.*

---

## 0 · Header

| | |
|---|---|
| **Artefact** | `prod.sales_gold.fct_daily_order_revenue` |
| **Contract** | `docs/10-contract/fct_daily_order_revenue.contract.md` · **version pinned:** `1.0` |
| **Contract gate decision** | `PASS` · 2026-09-03 · R. Okafor |
| **Open items accepted?** | item 1 (§7 late behaviour), R. Okafor, 2026-09-03 |
| **Author** | data engineer, sales-data-eng (agent-assisted) |
| **Reviewer** | J. Mehta, Platform owner |
| **Date** | 2026-09-04 |
| **Version** | `1.0` |

---

## 1 · Source-to-target mapping

| # | Target column | Type | Null? | Default | Source object | Source column | Transformation | Implements | Class. |
|---|---|---|---|---|---|---|---|---|---|
| M-01 | order_date | DATE | no | | int_orders | order_placed_at | `to_date(order_placed_at)` with session timezone UTC | `BR-04` | |
| M-02 | region_code | STRING | no | `UNKNOWN` | dim_customer | region_code | `coalesce(c.region_code, 'UNKNOWN')` over `int_orders o LEFT JOIN dim_customer c USING (customer_id)` | `BR-05` | |
| M-03 | completed_order_count | BIGINT | no | 0 | int_orders | order_id | `count(DISTINCT order_id)` where `status = 'completed' AND NOT is_test_account` | `BR-01`, `BR-02` | |
| M-04 | revenue_cents | BIGINT | no | 0 | int_orders | amount_cents, tax_cents | `sum(amount_cents - tax_cents)` where `status = 'completed' AND NOT is_test_account` | `BR-01`, `BR-02`, `BR-03` | |

---

## 2 · Join specification

| # | Left | Right | Type | On | Expected cardinality | Fan-out risk | Assertion |
|---|---|---|---|---|---|---|---|
| J-01 | int_orders | dim_customer | left | customer_id | N:1 | low: dim_customer contract 1.0 §5 guarantees one row per customer_id | T-03 |

---

## 3 · Deduplication & survivorship

| | |
|---|---|
| Duplicates possible? | no: `int_orders` contract 1.0 §5 guarantees one row per order_id |
| Match key | n/a |
| Tie-break order | n/a |
| Survivorship rule | n/a |
| Discarded records | n/a |
| Implements | n/a, cited from the upstream contract |
| **Signed by** | R. Okafor, 2026-09-04 |

---

## 4 · Historisation

| | |
|---|---|
| Pattern | snapshot, recomputed per day |
| Business key | order_date + region_code (contract §5) |
| Change detection | none: the last 3 days are recomputed every run |
| Effective-dating columns | none |
| Late-arriving data | orders up to 3 days late are picked up by the rolling recompute |
| Restatement policy | older days are restated only by a backfill run, announced to contract §10 consumers |
| Implements | `BR-04` |

---

## 5 · Bad-row handling & quarantine

| | |
|---|---|
| Behaviour | DQ-02 failures quarantined (contract §8) |
| **Quarantine target** | `prod.sales_gold.fct_daily_order_revenue_quarantine` |
| Retention | 90 days |
| Who reviews quarantined rows | Sales data steward, weekly |
| Reprocessing path | fixed rows re-enter via `int_orders`; the next run picks them up within the 3-day window, or by backfill |
| Implements | `BR-06` |

---

## 6 · Physical design

| | |
|---|---|
| Table type | managed |
| Format | Delta |
| Partitioning / clustering | liquid clustering on `order_date`: every consumer filters by date |
| Expected volume · growth | ~12 regions × 365 days per year: tiny |
| Retention / vacuum | default 7-day vacuum retention: enough for `RESTORE` within a week |
| Compute profile | serverless job |

---

## 7 · Dependencies & run order

| # | Depends on | Type | Upstream contract | If unavailable |
|---|---|---|---|---|
| 1 | `prod.sales_silver.int_orders` | upstream table | sales-platform/docs/10-contract/int_orders.contract.md 1.0 | fail |
| 2 | `prod.crm_silver.dim_customer` | upstream table | crm-platform/docs/10-contract/dim_customer.contract.md 1.0 | fail |

| | |
|---|---|
| Runs after | `int_orders` nightly load (02:00 UTC) |
| Triggers | none |
| Idempotent? | yes: `replaceWhere` on the 3-day window (SP-01) |

---

## 8 · Design decisions

| Decision | Choice | Why | Implements | Decided by |
|---|---|---|---|---|
| Batch or streaming | batch, daily | consumers read once a day | | Engineer |
| Full refresh, incremental or CDC | incremental: rolling 3-day recompute | late orders arrive within 3 days | `BR-04` | Engineer |
| Schema evolution behaviour | reject: explicit column list, no `mergeSchema` | new columns need steward review | `BR-07` | **Steward, via the contract** |
| Bad-row default | quarantine | rows are retained and reviewable | `BR-06` | **Steward, via the contract** |

---

## 9 · DQ implementation

| Contract ref | Expectation | Executable check | Where it runs | On failure |
|---|---|---|---|---|
| `DQ-01` | one row per day per region | `assert_unique(out, KEY)` before write; raises | job + test T-07 | fail |
| `DQ-02` | order id and amount present | `split_valid()` routes failures to quarantine | job + test T-05 | quarantine |
| `DQ-03` | loaded by 06:00 UTC | job health rule `RUN_DURATION_SECONDS` + freshness monitor | job | warn |
| `DQ-04` | revenue within ±30% of 28-day median | volume-band monitor on the output | monitor | warn |

---

## 10 · Test inventory

| Test ID | Type | Asserts | Traces to |
|---|---|---|---|
| T-01 | unit | completed only; cancelled, refunded and test accounts excluded | `M-03` · `M-04` · `BR-01` · `BR-02` · `AE-01` |
| T-02 | unit | an order at 23:59 UTC and one at 00:01 UTC land on different days | `M-01` · `BR-04` · `AE-01` |
| T-03 | grain | join to dim_customer doesn't change the order count | `J-01` · `AE-01` |
| T-04 | unit | customer with no region → `UNKNOWN` | `M-02` · `BR-05` · `AE-01` |
| T-05 | negative | null-amount rows quarantined; valid + quarantined = input | `DQ-02` · `BR-06` · `AE-01` |
| T-06 | golden | output equals golden data GD-01..GD-03 | `AE-02` |
| T-07 | grain | output unique on order_date + region_code | `DQ-01` · `AE-01` |
| T-08 | reconciliation | output revenue total = completed, non-test revenue in int_orders | `M-04` · `BR-03` · `AE-03` |

---

## 11 · Deployment

| | |
|---|---|
| Project / bundle | `order_revenue` (`databricks.yml`) |
| Resources defined | job `fct_daily_order_revenue` (`resources/fct_daily_order_revenue.job.yml`) |
| Targets | dev · test · prod |
| Identity per target | dev: engineer · test: `sp-sales-data-test` · prod: `sp-sales-data-prod` |
| Permissions in the definition | `sales-data-eng` CAN_MANAGE_RUN; table grants via the UC operating model |
| Promotion gate | CI: `make check`, `make test`, `make ready OBJ=fct_daily_order_revenue`, bundle validate all targets |
| Rollback | redeploy the previous bundle version via CI; `RESTORE TABLE … VERSION AS OF` by a human (runbook) |

---

## 12 · Traceability check

| # | Check | Result |
|---|---|---|
| 1 | Every `BR-` in the contract is cited by at least one row in §1, §3, §4, §5 or §8 | ☑ |
| 2 | Every row in §1 cites a `BR-`, or is `PASSTHROUGH` / `SURROGATE` | ☑ |
| 3 | Every join in §2 states a cardinality **and** names a test in §10 | ☑ |
| 4 | Every `DQ-` in the contract appears in §9 | ☑ |
| 5 | Every `AE-` in the contract §11 is realised by a test in §10 | ☑ (AE-04 by sign-off) |
| 6 | Every glossary term in the contract still resolves | ☑ |
| 7 | Contract version in §0 matches the current contract | ☑ |
| 8 | Every input in contract §2 with an upstream contract is pinned in §7 | ☑ |

---

## 13 · Ready to generate

- [x] Contract cleared its gate; version pinned in §0; open items accepted if `HUMAN_REVIEW`
- [x] Every target column has a mapping row with an ID, type and nullability
- [x] Every transformation is an expression, not a sentence
- [x] Every join states expected cardinality and names its assertion
- [x] Load pattern, historisation and deduplication all answered
- [x] Schema evolution and bad-row default each cite a `tolerance` rule
- [x] Quarantine target named, with a named reviewer
- [x] Every `DQ-` has an executable check; every `AE-` has a test
- [x] Deployment targets and identities stated
- [x] §12 run in both directions; every failure has a §14 row

---

## 14 · Deviations & open items

| # | Item | Type | From check | Reason | Action | Blocking? |
|---|---|---|---|---|---|---|
| — | none | | | | | |

---

## 15 · Implementation review

| | |
|---|---|
| **Decision** | `PASS` |
| §12 clean? | yes (`trace_check` PASS, 2026-09-04) |
| Failed criteria | none |
| Evidence cited | `make ready` output 2026-09-04; `reports/junit.xml` |
| Confidence | high |
| Reviewer | J. Mehta, Platform owner |
| Steward sign-off | R. Okafor, 2026-09-04 (§3) |
| Date | 2026-09-04 |

---

## Change log

| Version | Date | Change | Contract version | §12 re-run? | By |
|---|---|---|---|---|---|
| 1.0 | 2026-09-04 | Initial | `1.0` | yes | data engineer |
