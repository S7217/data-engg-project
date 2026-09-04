---
name: design-spec
description: Turn a data requirement (BRD, ticket, email, verbal ask) into a gated acceptance contract and then an implementation spec, before any pipeline code is written. Use when a new table, column, metric or pipeline change is requested, or when asked to "design", "spec", or "build" a Databricks data product.
argument-hint: <object name e.g. fct_subscription_revenue> [path to requirement]
---

# design-spec

From requirement to an executable design that can be reviewed: **contract (what must be true) → gate → implementation spec (how it's built) → code**. Your job here is to make every gap visible. Don't fill gaps in.

> **The agent may not fill a gap it discovered. It must name it.**
> An `INFERRED` value that should have been `ABSENT` produces a contract that passes review and fails in production.

## Phase 0: Set up

1. Object name in `snake_case` with its layer prefix (`harness/standards/naming-conventions.md`). Ask if it isn't clear.
2. Save the requirement verbatim to `docs/00-brd/<object>.brd.md` if it isn't already in the repo. Never paraphrase the source.
3. Read the sources: the requirement, `docs/glossary.yml` (or the organisation glossary, if the team points `trace_check.py --glossary` at it), upstream contracts in `docs/10-contract/`, and existing code that touches the inputs.
4. Propose the risk tier with `harness/standards/risk-tiers.md` ("what happens when it's wrong and nobody notices for a month?"). State it with the reason, and get the human to confirm before scaffolding: the tier decides how much of the chain is required.
5. Scaffold: `make new OBJ=<object> TIER=<n>` (= `python3 harness/tools/scaffold.py`). This creates the BRD stub, the contract (header filled; at Tier 1, §7–§13 pre-marked N/A), the impl spec (contract pinned), a test stub, and at Tier 2–3 the golden-set file.

## Phase 1: Acceptance contract

Fill in `docs/10-contract/<object>.contract.md`. Work only in the sections the tier makes mandatory.

- **Every field gets a status:** `PRESENT` (with a citation: document + section or line) · `INFERRED` (with reasoning) · `ABSENT` · `N/A` (with a reason).
- **Business language only.** No `WHERE` clauses, no column expressions. Those belong in the impl spec.
- **Hunt for the usual gaps** and mark them `ABSENT` when the requirement is silent:
  - Grain ambiguity ("revenue by customer": per account? per subscription? per month?)
  - Terms used but not defined, or used differently from the glossary. A conflict goes to §14 as an escalation
  - **Exclusions**: refunds, credit notes, cancellations, test/internal accounts, deleted records
  - Freshness ("kept up to date" isn't an SLA)
  - **Tolerance**: schema evolution, and what happens to bad rows
  - Ownership, classification, publication authority
- **Classification:** propose a value with its evidence (`harness/standards/classification-taxonomy.md`). Never apply tags.
- Fill §13 (delivery envelope) from `harness/standards/uc-operating-model.md`.
- List every `ABSENT`, `INFERRED` and conflict in §14, each with *question for* (business / steward / engineering) and *blocking?*.
- Leave §15 empty. `/gate` completes it.
- **Tier 2–3:** ask the steward to write the golden records in `tests/golden/<object>/README.md` **before** grading. You don't write them: the generator mustn't author the answer key it'll be graded against.

Then run `python3 harness/tools/contract_check.py docs/10-contract/<object>.contract.md` and fix every mechanical error.

**Stop and show the human:** the tier, a count of statuses, the §14 open items as questions ready to send to the business, and the recommendation to run `/gate`. Don't continue to Phase 2 in the same turn unless the human says so.

## Phase 2: Gate

Run `/gate docs/10-contract/<object>.contract.md`. Only these verdicts allow Phase 3:
- `PASS`
- `HUMAN_REVIEW` with the open items **accepted in writing** by the publication authority (recorded in §15). Phase 3 then covers only the parts those items don't affect.

`FAIL` → back to Phase 1 with the failed criteria.

## Phase 3: Implementation spec

Fill in `docs/20-impl-spec/<object>.impl.md` (scaffolded, contract version already pinned).

- §0 pins the contract version and records the gate decision.
- §1 mapping: one row per target column with a stable `M-` ID. *Transformation* is an expression. *Implements* is a `BR-` ID, `PASSTHROUGH` or `SURROGATE`. **Anything else is unrequested logic**: either remove it or record it in §14 as `UNREQUESTED` for design review.
- §2 every join states its cardinality and names a `T-` test.
- §3 survivorship, §8 schema evolution and bad-row default **cite contract `tolerance` rules**. If no rule covers them, stop: that's an `ABSENT` in the contract, and the contract re-gates.
- §6 / §11: physical design and deployment follow `harness/standards/automation-standard.md` and the delivery envelope.
- §9: every `DQ-` → an executable check (Lakeflow expectation / test / monitor) with the contract's disposition.
- §10: every `AE-` → a `T-` test.

Run `python3 harness/tools/trace_check.py docs/10-contract/<object>.contract.md docs/20-impl-spec/<object>.impl.md`. Every failure gets fixed or gets a §14 row. Work through §13 *Ready to generate*. Any unchecked line means stop.

## Phase 4: Code

Only after `make ready OBJ=<object>` shows the code gate (C1–C7) passing, under the **delivery** layer. The `gate_code` hook blocks writes to `src/pipelines/<layer>/<object>.*` until then, so don't work around it. If it blocks, its message names the missing step. Then:
- Model files: `src/pipelines/<layer>/<object>.(py|sql)`, with grain on line 1 and `# implements: BR-…` / `# M-nn` comments at the relevant lines.
- Bundle resource: `resources/<object>.job.yml` (or pipeline) from the project template's pattern.
- Tests: `tests/unit/test_<object>.py`, each test carrying its `T-` ID and `traces to` comment (`harness/standards/test-and-reconciliation-patterns.md`).
- Finish with `make check` and `make test`. Then recommend running `dq-reviewer` and the implementation review (`/gate docs/20-impl-spec/<object>.impl.md`).

## Never

- Write code before the contract has cleared the gate.
- Turn an `ABSENT` into `INFERRED` because the answer seems obvious.
- Decide survivorship, schema-evolution tolerance, bad-row disposition, exclusions or classification yourself.
- Paste glossary definitions. Reference them by `GL-` ID.
