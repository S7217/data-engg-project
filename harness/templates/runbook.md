# Runbook: <job or pipeline name>

*v0: drafted ahead of Session 8. Re-align after delivery.*

*Harness template · S8 · copy to `docs/60-runbooks/<job>.md` · required before first prod deploy of a Tier 2–3 job*

If the on-call engineer can't operate this job from this page alone, the job isn't ready to run unattended.

| | |
|---|---|
| **Bundle resource** | `resources/<file>.yml` → `<resource key>` |
| **Produces** | `catalog.schema.object` (tier) · contract path |
| **Schedule** | cron / trigger · timezone |
| **Expected duration** | p50 · p95 |
| **Freshness SLA** | contract §7 |
| **Runs as** | service principal per target |
| **Owner (team / channel)** | |
| **Steward (business questions)** | |

## Dependencies
| Upstream | If late or missing |
|---|---|
| | wait · fail · proceed stale (per impl spec §7) |

## Normal operation
What a healthy run looks like: row counts, duration, DQ metrics to glance at, and where to see them.

## Alerts and what to do

| Alert / symptom | Likely cause | First action | Escalate to |
|---|---|---|---|
| Run failed | | check run output in the job UI; `databricks jobs get-run <id>` | |
| DQ `ERROR` rule triggered | | inspect quarantine table; don't override the rule | steward |
| Quarantine rate rising | | | |
| Late beyond SLA | | | |
| Schema drift (rescued data present) | | don't widen the schema; route to steward per tolerance rule | steward |

## Re-run and backfill
- Re-run a failed run: safe (idempotent per automation standard SP-01). Command:
- Backfill a date range: `databricks bundle run -t prod <job> --params start_date=…,end_date=…` **via CI or by a human**. Announce Tier 2–3 backfills to contract §10 consumers first.

## Rollback
Previous good version, how to redeploy it, and the `RESTORE` procedure for the table. See `standards/incident-and-rollback.md` for when to roll back.

## Known quirks
Things that look like incidents but aren't.

## Change log
| Date | Change | By |
|---|---|---|
