# Automation and Stability Standard

*v0: drafted ahead of Session 8. Re-align after delivery.*

*Harness standard · S8 · owner: Platform · see `OWNERS.md`*

How jobs and pipelines run unattended, at volume, without us. The project template's `resources/` already follows this. Pattern IDs are `SP-nn` (stability pattern), not session numbers.

---

## Deployment

| Rule | How |
|---|---|
| Everything deployable is in a bundle | `databricks.yml` + `resources/*.yml`. No UI-created jobs in test or prod |
| Three targets | `dev` (development mode, the engineer's identity) · `test` · `prod` (production mode, `run_as` service principal) |
| Prod is deployed only by CI | the guard hook blocks prod from agent sessions; the CI identity is the only one with deploy rights on prod |
| Validate before merge | `databricks bundle validate -t <each target>` in CI |
| Promotion gate | contract `PASS` (or `HUMAN_REVIEW` with accepted items) + green `make check` + green tests |

## Stability patterns

Every job or pipeline states how it handles each of these, in impl spec §7 and §11.

| # | Pattern | Rule |
|---|---|---|
| SP-01 | **Idempotency** | Re-running the same run with the same inputs produces the same result. Use `MERGE` on the contract key or `INSERT OVERWRITE` / `replaceWhere` on a partition, never a blind `append` to a published table |
| SP-02 | **Retries** | Tasks retry transient failures (`max_retries: 2`, `min_retry_interval_millis: 300000`). Retries are only safe because of SP-01 |
| SP-03 | **Timeouts** | Every task has `timeout_seconds`. A job with no timeout fails silently by never finishing |
| SP-04 | **No overlap** | `max_concurrent_runs: 1` unless the impl spec justifies otherwise |
| SP-05 | **Checkpointing** | Streaming and Auto Loader keep checkpoints in a governed volume per target, never shared between environments |
| SP-06 | **Incremental by watermark** | Incremental loads read from a stored high-water mark, not "yesterday". Late data is handled per impl spec §4 |
| SP-07 | **Schema drift** | Behaviour comes from the contract `tolerance` rule: `rescue` (Auto Loader `_rescued_data`) or `fail`. A new column never reaches a published table without steward review |
| SP-08 | **Backfill / replay** | A parameterised path (`start_date`, `end_date`) that reuses the normal code, idempotent per SP-01. Backfills of Tier 2–3 objects are announced to the contract §10 consumers |
| SP-09 | **Failure notification** | `on_failure` notifications to the owning team's channel, and health rules for duration (`RUN_DURATION_SECONDS`) |
| SP-10 | **Freshness SLA** | contract §7 latency becomes a monitored rule (DQ `WARNING`), not a hope |
| SP-11 | **Compute** | serverless by default; classic clusters only with a reason in impl spec §6 |
| SP-12 | **Tags** | every job is tagged `domain`, `owner`, `tier`, `contract` (path) |

## Service identities

- One service principal per environment, named in the target's `run_as`.
- The service principal owns nothing; groups own objects (`uc-operating-model.md`).
- Credentials live in secret scopes; jobs reference them and code never contains them.

## Operations

Every Tier 2–3 job has a runbook in `docs/60-runbooks/<job>.md` from `templates/runbook.md`, written before first prod deploy. If the on-call engineer can't operate the job from the runbook alone, it isn't ready to run unattended.

Patterns that prove themselves (or fail) in production are recorded in `registers/pattern-catalogue.md`.
