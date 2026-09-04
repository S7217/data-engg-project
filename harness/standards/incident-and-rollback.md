# Incident, RCA and Rollback

*v0: drafted ahead of Session 7. Re-align after delivery.*

*Harness standard · S7 · owner: see `OWNERS.md` · reviewed by Platform*

Why did it break, with evidence rather than a plausible story? And when do we roll back?

**Run it:** `/incident <job, pipeline or table> <symptom>` → `rca-investigator` subagent (read-only) → `docs/50-incidents/<date>-<slug>.md` from `templates/post-incident.md`.

---

## Roles

| Concern | Owner |
|---|---|
| Technical root cause; rollback execution | Engineer (on call) |
| Business impact, criticality, communication to consumers | Steward / domain owner |
| Restatement decision (do we correct published history?) | Publication authority for the object |

## Evidence before explanation

An RCA statement is only as strong as the evidence behind it. Use the same five statuses as modernization (`OBSERVED` · `DOCUMENTED` · `INFERRED` · `UNKNOWN` · `DECISION_REQUIRED`).

| Source | Answers |
|---|---|
| `system.lakeflow.job_run_timeline`, `job_task_run_timeline` | What ran, when, with what result |
| Pipeline event log (`event_log(<pipeline>)`) | Expectation metrics, flow progress, errors per update |
| `system.query.history` | What SQL ran against the object, by whom, when |
| `system.access.audit` | Who changed what: permissions, objects, jobs |
| `system.access.table_lineage` / `column_lineage` | What feeds the broken object and what it feeds |
| `DESCRIBE HISTORY <table>` | Which operation and version changed the data, and when |
| Git history of the bundle | What code or config changed and when it was deployed |

**Rules for the investigation**

1. **Timeline first.** Last known good → first known bad, with timestamps, from platform evidence. Explanations come after.
2. **Every causal claim cites evidence.** "The schema changed upstream" is `INFERRED` until a table version or audit event shows it.
3. **List rival hypotheses** and what evidence would eliminate each one. Stop when one is `OBSERVED` and the others are eliminated, not when one sounds right.
4. **The most recent change is a suspect, not a conclusion.**
5. **Empty results are `UNKNOWN`,** not exoneration (retention windows, capture gaps, systems outside Unity Catalog).

## Rollback criteria

Roll back **without waiting for full RCA** when any of these hold:

| # | Condition |
|---|---|
| R1 | A published Tier 2–3 object is **wrong** (a grain breach, wrong totals, missing rows) and consumers are reading it now |
| R2 | An `ERROR` DQ rule failed and was bypassed or didn't halt publication |
| R3 | Sensitive data is visible to someone it shouldn't be (masking, tag or grant regression). This is also a security incident |
| R4 | The defect was introduced by an identifiable deployment, and the previous version is known good |

**Don't** roll back (fix forward instead) when:
- the previous version is *also* wrong, or its data can't be reproduced,
- rollback would re-publish data already corrected downstream (that's a restatement decision for the publication authority),
- the cause is upstream data, not our code. Quarantine, halt and notify instead.

### Rollback mechanisms

| Layer | Mechanism |
|---|---|
| Code / config | redeploy the previous bundle version from Git via CI to the affected target |
| Delta data | `RESTORE TABLE <t> TO VERSION AS OF <v>` (check `DESCRIBE HISTORY` first; mind `VACUUM` retention). Executed by a human or CI, never by the agent |
| Pipeline | stop the pipeline; full refresh only if the contract allows it and sources are retained |
| Consumers | notify through the contract §10 consumer list *before* restoring, if the restore changes numbers they've already used |

Every rollback is recorded in the post-incident document with: what was restored, to which version, by whom, and verification that it worked.

## After the incident

- Post-incident review within 5 working days, using `templates/post-incident.md`. Blameless and evidence-led.
- Every incident produces at least one **regression asset**: a test, a DQ rule, a golden case, a guard hook rule or a CLAUDE.md line, recorded in `registers/failure-library.md`.
- If the agent's output contributed, record what it was given, what it produced, and **why that output looked plausible**.
