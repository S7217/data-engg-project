# Acceptance Contract

### What must be true before this publishes

*Harness template · acceptance contract · **v1.1** · filled for the S7 demo. People named are fictional.*

---

## 0 · Header

| | |
|---|---|
| **Artefact** | `prod.sales_gold.fct_daily_order_revenue` |
| **Requirement source** | `docs/00-brd/fct_daily_order_revenue.brd.md` · SALES-2291 |
| **Risk tier** | 2 |
| **Author** | data engineer, sales-data-eng (agent-assisted, `/design-spec`) |
| **Steward** | R. Okafor, Sales data steward |
| **Date** | 2026-09-02 |
| **Version** | `1.0` |
| **Implementation Spec** | `docs/20-impl-spec/fct_daily_order_revenue.impl.md` · written after this passes |

---

## 1 · Purpose

| | |
|---|---|
| Value | Daily completed-order revenue by customer region, for the Finance daily trading dashboard and the regional sales review |
| Status · Source | PRESENT · BRD §1 |

---

## 2 · Inputs

| # | Object | Authoritative? | Upstream contract | Status | Source |
|---|---|---|---|---|---|
| I-01 | `prod.sales_silver.int_orders` | yes: system of record for orders | sales-platform/docs/10-contract/int_orders.contract.md · 1.0 | PRESENT | BRD §2 |
| I-02 | `prod.crm_silver.dim_customer` | yes: customer region | crm-platform/docs/10-contract/dim_customer.contract.md · 1.0 | PRESENT | BRD §2; dim_customer contract §5 (one row per customer_id) |

---

## 3 · Outputs

| | |
|---|---|
| Object | `prod.sales_gold.fct_daily_order_revenue` |
| Columns | order date · region · count of completed orders · revenue |
| Storage / format | managed Delta table |
| Status · Source | PRESENT · BRD §3 |

---

## 4 · Grain

| | |
|---|---|
| One row = | one calendar day (UTC) per customer region |
| Status · Source | PRESENT · BRD §3 "a line per day per region" |

---

## 5 · Keys

| | |
|---|---|
| Unique on | order date + region |
| Natural / business key | order date + region code |
| Status · Source | PRESENT · follows from §4 grain; BRD §3 |

---

## 6 · Business rules

| ID | Type | Statement | Status | Source | Glossary |
|---|---|---|---|---|---|
| BR-01 | inclusion | Only completed orders contribute to counts and revenue | PRESENT | BRD §4 | GL-0001 |
| BR-02 | exclusion | Cancelled and refunded orders, and orders from test accounts, are excluded | PRESENT | BRD §4; steward email 2026-09-01 (test accounts) | GL-0001 |
| BR-03 | derivation | Revenue is the order amount before tax, in cents | PRESENT | BRD §4; GL-0002 | GL-0002 |
| BR-04 | derivation | An order belongs to the UTC calendar day on which it was placed | PRESENT | steward email 2026-09-01 | |
| BR-05 | edge case | Orders whose customer has no region are reported under region `UNKNOWN`, not dropped | PRESENT | steward email 2026-09-01 | |
| BR-06 | tolerance | Order rows failing DQ-02 are not silently dropped; they are retained and reviewable | PRESENT | steward email 2026-09-01 | |
| BR-07 | tolerance | A new column in a source must not reach the published table without steward review | PRESENT | steward email 2026-09-01 | |

---

## 7 · Freshness

| | |
|---|---|
| Expected latency | previous UTC day complete by 06:00 UTC |
| Schedule | daily 03:00 UTC |
| Behaviour when late | dashboard keeps showing the last complete day |
| Status · Source | INFERRED · BRD §5 states 06:00; late behaviour not stated |

---

## 8 · DQ expectations

| ID | Expectation | Threshold | Severity | On failure | Alert owner | Status |
|---|---|---|---|---|---|---|
| DQ-01 | One row per day per region | 0% | ERROR | fail | Sales data engineer on call · #sales-data-alerts | PRESENT |
| DQ-02 | Every order has an id and an amount | 0% | ERROR | quarantine | Sales data steward · #sales-data-alerts | PRESENT |
| DQ-03 | Previous day loaded by 06:00 UTC | 1 hour | WARNING | warn | Sales data engineer on call · #sales-data-alerts | PRESENT |
| DQ-04 | Daily revenue per region within ±30% of its trailing 28-day median | ±30% | WARNING | warn | Sales data steward · #sales-data-alerts | PRESENT |

---

## 9 · Classification

| | |
|---|---|
| `sensitivity` | `confidential` |
| Other governed tags | none (taxonomy v0 has one tag) |
| Column-level exceptions | none |
| Rationale | Commercial trading figures by region; upstream `int_orders` is `confidential` |
| Status · Source | PRESENT · applied by R. Okafor 2026-09-03 (proposed by agent in draft 0.9) |

---

## 10 · Ownership

| | |
|---|---|
| Object owner | `sales-data-eng` (group) |
| Publication authority | R. Okafor, Sales data steward |
| Consumers to notify on change | Finance daily trading dashboard (finance-bi) · Regional sales review (sales-ops) |
| Status · Source | PRESENT · BRD §6 |

---

## 11 · Acceptance evidence

| ID | Evidence | What it proves | Where it lives | Status |
|---|---|---|---|---|
| AE-01 | Tests | each business rule holds on minimal inputs | `tests/unit/test_fct_daily_order_revenue.py` | PRESENT |
| AE-02 | Golden set | expected output on reviewed golden data | `tests/golden/fct_daily_order_revenue/` | PRESENT |
| AE-03 | Reconciliation | daily revenue equals completed, non-test order revenue in `int_orders` | `tests/unit/test_fct_daily_order_revenue.py` (control totals) | PRESENT |
| AE-04 | Sign-off | steward accepts publication | §15 | PRESENT |

---

## 12 · Glossary references

| Term as used here | Glossary ID | Used in | Status |
|---|---|---|---|
| completed order | `GL-0001` | BR-01, BR-02 | PRESENT |
| order revenue | `GL-0002` | BR-03 | PRESENT |

---

## 13 · Delivery envelope

| Decision | Answer |
|---|---|
| Placement — catalog and schema | `prod.sales_gold` (dev: `dev.<user>_order_revenue`) |
| Ownership — role or group | `sales-data-eng` |
| Classification — governed attributes | `sensitivity = confidential` |
| Human access — who may read or change | read: `finance-bi`, `sales-ops`; change: `sales-data-eng` via CI |
| Agent data access — data / metadata only / neither | dev data; prod metadata only |
| Agent mutation — code / data / metadata | code; dev data only |
| Tag authority — may the agent assign governed tags | propose only |
| Environment — identity in dev vs prod | dev: engineer's identity · prod: `sp-sales-data-prod` (bundle `run_as`) |
| Publication — what approval permits promotion | contract PASS with named decider + `make ready` green in CI |

---

## 14 · Open items

| # | Section | Status | Question for | Blocking? | Resolved |
|---|---|---|---|---|---|
| 1 | 7 | INFERRED | steward: is "dashboard keeps last complete day" acceptable when late? | no | accepted R. Okafor 2026-09-03 |

---

## 15 · Gate submission

| | |
|---|---|
| **Decision** | `PASS` |
| Failed criteria | none |
| Evidence cited | BRD §1–§6; steward email 2026-09-01; dim_customer contract 1.0 §5; int_orders contract 1.0 §4 |
| Explanation | Every rule is cited and the one inference is accepted by the steward; grain, exclusions and tolerance rules are explicit. |
| Confidence | high · J-01 cardinality rests on the dim_customer contract 1.0 grain |
| Verification level used | context-separated |
| Decider | R. Okafor, Sales data steward |
| Date | 2026-09-03 |

| | |
|---|---|
| Open items accepted by | R. Okafor · 2026-09-03 · item 1 |

---

## Change log

| Version | Date | Change | Re-gated? | By |
|---|---|---|---|---|
| 0.9 | 2026-09-02 | Draft from `/design-spec` | — | data engineer |
| 1.0 | 2026-09-03 | Classification applied by steward; §7 inference accepted | yes, PASS | R. Okafor |
