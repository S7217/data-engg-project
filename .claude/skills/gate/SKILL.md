---
name: gate
description: Run the harness review gate on an artefact (acceptance contract, implementation spec, column descriptions, DQ rules, glossary terms, metadata) and record a PASS / FAIL / HUMAN_REVIEW decision. Use when asked to gate, review for publication, approve or sign off an artefact.
argument-hint: <path to artefact> [rubric path]
---

# gate

Generated isn't a state. The states are **UNVERIFIED → REJECTED · HUMAN_REVIEW · ACCEPTED**, and this skill moves an artefact between them. It doesn't do the grading itself, because the generator never certifies its own work.

## 1. Mechanical checks (always, deterministic)

- Contract: `python3 harness/tools/contract_check.py <contract>`
- Impl spec: `python3 harness/tools/trace_check.py <contract> <impl>`

Keep the output. Unrecorded failures mean the verdict can't be `PASS`. Tell the author now. Don't spend a grade on a document that fails its own checks.

## 2. Tier → path

Read the tier from contract §0 (or ask, for artefacts without a contract). The tier was decided before grading, so don't change it now.

| Tier | Grade by | Golden set |
|---|---|---|
| **1: contained** | **You**, inline: self-review against the rubric (or the verifier's VC- criteria in `.claude/agents/acceptance-verifier.md`), output in the five-field format | optional |
| **2: propagating** | the **`acceptance-verifier`** subagent (context-separated) | required, written before grading |
| **3: governing** | the `acceptance-verifier` subagent, then **independent human review** by the steward, **plus** platform owner sign-off | required |

For Tier 2–3, invoke `acceptance-verifier` with **only**: the artefact path, the evidence paths (BRD in `docs/00-brd/`, `docs/glossary.yml`, upstream contracts from contract §2, the code it describes), the rubric path, and the mechanical-check output. **Don't pass on the golden set, your opinion, or how the artefact was produced.** That separation is the control.

## 3. Golden comparison (Tier 2–3, after the grade)

Only once the grade is back, compare the artefact against `tests/golden/<object>/` Part 1: required facts present (n/n), required exclusions respected, forbidden claims found. A forbidden claim found means the verdict is `FAIL`, whatever the grade said. Any disagreement between the grade and the golden comparison goes to the decider as `HUMAN_REVIEW`, adjudicated against the evidence.

## 4. Record

- **Contract or impl spec:** fill §15 with the decision, failed criteria, evidence cited, explanation, confidence, verification level used, and a **Decider**. The decider is a named human. Leave it `pending: <publication authority from §10>` unless that person, in this session, explicitly decides. `contract_check` rejects a Tier 2–3 `PASS` without a named decider.
- **Other artefacts:** `docs/10-contract/<object>.<artefact>.decision.md` from `harness/templates/decision-record.md`.
- Put open items into §14 (or decision record §6). If something was a defect worth remembering, fill decision record §7 (failure library).
- Append one row to `docs/gate-log.md`.

## 5. Report to the human

The verdict and state, the failed criteria, required facts met n/n, and what happens next:

| Verdict | State | Next |
|---|---|---|
| `PASS` | ACCEPTED once a named decider confirms | `make ready OBJ=<object>`: the implementation spec / publication may proceed |
| `HUMAN_REVIEW` | HUMAN_REVIEW | the publication authority accepts the named open items in writing in §15 ("Open items accepted by"), or doesn't. Only the unaffected parts proceed |
| `FAIL` | REJECTED | back to the author with the failed criteria |
