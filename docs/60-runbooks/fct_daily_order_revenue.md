# Runbook: fct_daily_order_revenue

*Harness template · runbook · filled for the S7 demo.*

| | |
|---|---|
| **Bundle resource** | `resources/fct_daily_order_revenue.job.yml` → `fct_daily_order_revenue` |
| **Produces** | `prod.sales_gold.fct_daily_order_revenue` (Tier 2) · `docs/10-contract/fct_daily_order_revenue.contract.md` |
| **Schedule** | 03:00 UTC daily |
| **Expected duration** | p50 4 min · p95 9 min |
| **Freshness SLA** | previous UTC day by 06:00 UTC (contract §7) |
| **Runs as** | prod: `sp-sales-data-prod` |
| **Owner (team / channel)** | sales-data-eng · #sales-data-alerts |
| **Steward (business questions)** | R. Okafor, Sales data steward |

## Dependencies
| Upstream | If late or missing |
|---|---|
| `prod.sales_silver.int_orders` (02:00 UTC) | fail; the 03:00 run retries twice |
| `prod.crm_silver.dim_customer` | fail |

## Normal operation
~12 rows per day (one per region). Quarantine usually 0–3 rows a day. `DQ-04` (±30% band) fires a handful of times a year around promotions.

## Alerts and what to do

| Alert / symptom | Likely cause | First action | Escalate to |
|---|---|---|---|
| Run failed | upstream late; DQ-01 grain breach | check run output; `databricks jobs get-run <id>` | on call |
| DQ-01 grain breach | duplicated region codes upstream | don't override; open an incident (`/incident`) | steward |
| Quarantine rate rising | upstream data quality | inspect `…_quarantine`, route to sales-platform | steward |
| Late beyond SLA | `int_orders` late | dashboard keeps last complete day (accepted, contract §14 #1) | on call |
| Consumer reports wrong numbers | — | `/incident fct_daily_order_revenue "<symptom>"` | steward + platform |

## Re-run and backfill
- Re-run a failed run: safe (idempotent per automation standard SP-01).
- Backfill: `databricks bundle run -t prod fct_daily_order_revenue --params start_date=YYYY-MM-DD,end_date=YYYY-MM-DD` **via CI or by a human**. Announce to Finance BI and Sales Ops first (contract §10).

## Rollback
Previous good code: redeploy the previous tagged bundle version via CI. Previous good data: `DESCRIBE HISTORY prod.sales_gold.fct_daily_order_revenue`, then `RESTORE TABLE … TO VERSION AS OF <n>` (a human runs this; vacuum retention is 7 days). When to roll back: `harness/standards/incident-and-rollback.md`.

## Known quirks
Month-end promotions trip DQ-04 legitimately. Check with Sales Ops before treating it as an incident.

## Change log
| Date | Change | By |
|---|---|---|
| 2026-09-04 | Initial | data engineer |
| 2026-09-27 | Escalation contact added | data engineer |
