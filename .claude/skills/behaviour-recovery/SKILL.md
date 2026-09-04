---
name: behaviour-recovery
description: Reverse-engineer what a legacy component (stored procedure, SSIS package, legacy SQL, old notebook) actually does before modernizing it - characterize behaviour from captured evidence, classify every claim, register unknowns, and draft a parity contract. Use for migrations to Databricks, rewrites, or when asked "what does this proc/package do".
argument-hint: <path to legacy source> [path to captured inputs/outputs]
---

# behaviour-recovery

> **Never let modernization silently turn an observation into an assumption, or an assumption into a requirement.**

Read `harness/standards/modernization-playbook.md` first. This skill produces documents, not converted code. Run it under the **delivery** layer so the records can be saved to `docs/40-modernization/`. Reading the legacy system stays read-only, and impact work goes to the `lineage-impact-reviewer` subagent, which has no write tools.

## Step 1: Gather evidence, not just code

- Legacy source: the procedure, package (`.dtsx`), SQL scripts, job definitions.
- **Captured I/O:** input tables/files, parameters and the **actual output** of real runs. Look in `docs/40-modernization/<object>/captured/`.
- If there's no captured output, **say so before going further**. Without it you can only describe the code's apparent *intent*. Every behaviour will be at best `DOCUMENTED`/`INFERRED`, never `OBSERVED`. Tell the human which captures would change that (input + output for the cases listed in Step 2).

## Step 2: Characterize (facts only)

Copy `harness/templates/behaviour-recovery-record.md` → `docs/40-modernization/<object>/behaviour-recovery.md`.

Read the source line by line and list each observable behaviour as a **fact** with its file:line. Work through the checklist in the template: implicit filters, inner joins dropping rows, NULL handling, integer division/rounding/truncation, implicit casts, date boundaries and timezones, dedup/"latest wins", error handling, hard-coded values, order dependence.

Where captured I/O exists, **trace specific rows**: pick input rows, compute by hand what the code does, and compare to the captured output. Explain every row that's missing or changed. If expected and captured disagree, that disagreement *is* a finding.

## Step 3: Classify every claim

One status each: `OBSERVED` · `DOCUMENTED` · `INFERRED` · `UNKNOWN` · `DECISION_REQUIRED`.
- `OBSERVED` only with captured evidence that shows it.
- Anything about whether a behaviour is *intended* or *correct for the business* is `DECISION_REQUIRED`, with a **named route** (for example: finance domain authority). You don't decide it, and neither does the engineer.

## Step 4: Register assumptions and unknowns

Copy `harness/templates/assumptions-and-unknowns-register.md` → `docs/40-modernization/<object>/assumptions-and-unknowns.md`. Every `INFERRED`, `UNKNOWN` and `DECISION_REQUIRED` gets a row with basis, risk if wrong, route and blocking flag.

## Step 5: Impact

Delegate to the `lineage-impact-reviewer` subagent for the legacy output object and the target object. Remember that legacy systems outside Unity Catalog have no native lineage, so their consumers are `UNKNOWN` unless registered.

## Step 6: Draft the parity contract

Copy `harness/templates/parity-contract.md` → `docs/40-modernization/<object>/parity-contract.md`. One row per behaviour with **claim status and disposition side by side**. Propose `MUST_MATCH` / `ALLOWED_DIFFERENCE` only where the evidence and consumers support it. Anything that changes a number a consumer has relied on is `DECISION_REQUIRED` until someone with authority decides it.

Draft the reconciliation plan (§3) using `harness/standards/test-and-reconciliation-patterns.md`. Each `MUST_MATCH` behaviour with a captured case should become a characterization test.

## Step 7: Hand over

Report to the human:
- counts by status
- the `DECISION_REQUIRED` queue as questions ready to send, each with its route
- the readiness verdict (`READY_TO_REIMPLEMENT` / `NOT_READY — decision required` / `NOT_READY — insufficient evidence`), the evidence-ladder rung reached, and why
- the next step: every parity row becomes a business rule (or a §14 `ABSENT`) in the target contract via `/design-spec`, as mapped in the playbook

## Never

- Present the author's intent as observed behaviour.
- "Fix" a bug during recovery. Record it as `OBSERVED`, propose a disposition, and route it.
- Treat a reconciliation match as proof. Both systems can drop the same row.
