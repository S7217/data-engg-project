# Evidence pack: "daily revenue up since the 26th"

**Simulated platform evidence for the S7 demo.** The training workspace has no system-table access, so these files stand in for what `rca-investigator` would query. Values are illustrative but internally consistent. Treat each file as the output of the query named in its header.

| File | Stands in for |
|---|---|
| `01-alert.md` | the report that started it |
| `02-job-runs.csv` | `system.lakeflow.job_run_timeline` for job `fct_daily_order_revenue` |
| `03-fct-history.txt` | `DESCRIBE HISTORY prod.sales_gold.fct_daily_order_revenue` |
| `04-dim-customer-history.txt` | `DESCRIBE HISTORY prod.crm_silver.dim_customer` |
| `05-audit-events.csv` | `system.access.audit`, filtered to the two tables |
| `06-git-log.txt` | `git log` of this repo, plus bundle deploy times |
| `07-query-history.csv` | `system.query.history` against the fact table |
| `08-table-lineage.csv` | `system.access.table_lineage` for the fact table |
| `09-dq-metrics.csv` | DQ results per run (DQ-01, DQ-02 quarantine count, DQ-04 band) |
| `10-probe-results.md` | results of the probe queries an investigator would run next |
| `11-crm-release-note.md` | a message posted in the CRM team's channel |
