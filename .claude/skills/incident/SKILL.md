---
name: incident
description: Investigate a data incident (failed job, wrong or missing data, late pipeline, exposure) with evidence, decide rollback vs fix-forward against the harness criteria, and produce the post-incident record. Use when something in Databricks broke or produced wrong output.
argument-hint: <job | pipeline | catalog.schema.table> <symptom>
---

*v0: drafted ahead of Session 7. Re-align after delivery.*

# incident

Read `harness/standards/incident-and-rollback.md`. Run under the **delivery** layer so the record can be saved to `docs/50-incidents/`. The investigation itself is read-only: `rca-investigator` executes nothing that changes state, and the guard hook blocks rollback commands (RESTORE, prod deploys) from agent sessions.

1. **Open the record now.** Copy `harness/templates/post-incident.md` → `docs/50-incidents/<yyyy-mm-dd>-<slug>.md`. Fill in the header with what's known, and status `investigating`.
2. **Check the rollback criteria straight away (R1–R4).** If R1 or R3 clearly holds, tell the human **first**, before the investigation: rollback doesn't wait for full RCA. Give the exact commands for a human or CI to run. Never run them yourself. The guard hook blocks `RESTORE`, `VACUUM` and prod deploys from agent sessions.
3. **Delegate the investigation** to the `rca-investigator` subagent with: the object, the symptom, detection time, and paths to the object's contract, impl spec and runbook (`docs/60-runbooks/`).
4. **Fill in the record** from its output: timeline, hypotheses with statuses, root cause (and its status), rollback assessment, consumers exposed. Leave §1 *Impact* for the business owner. Draft it from the consumer evidence and mark it `draft: business owner to confirm`.
5. **Propose regression assets** (§6). At least one is mandatory. Prefer something executable: a test, a DQ rule, a golden case, a guard hook rule. A CLAUDE.md line is the weakest option.
6. **Report:** the root cause and its status, the recommendation (rollback / fix forward / halt and quarantine), commands for the human, who needs telling, and the open unknowns.

Don't call the root cause established while it's `INFERRED`. Say what evidence would confirm it.
