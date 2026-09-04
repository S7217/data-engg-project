# Review Gate

*Harness standard · S3 · owner: see `OWNERS.md` · reviewed by Steward*

> **"Generated is not a state we care about. The states are unverified, rejected, human-review, and accepted."**

What has to be true before anything AI-produced is published, and how the decision is recorded. **Run it:** `/gate <path-to-artefact>`.

---

## States

| State | Means | Reached by |
|---|---|---|
| **UNVERIFIED** | Produced, not yet graded. Everything starts here | generation |
| **REJECTED** | Graded `FAIL` | the gate |
| **HUMAN_REVIEW** | Graded `HUMAN_REVIEW`: the evidence doesn't settle it, or the tier needs a human who hasn't decided yet | the gate |
| **ACCEPTED** | Graded `PASS` **and** a named decider recorded, or `HUMAN_REVIEW` with the open items accepted in writing by the publication authority | the gate + a named human |

Only ACCEPTED may publish. `make ready OBJ=<object>` checks this mechanically, and the code-gate hook enforces it before pipeline code is written.

## Inputs

| Required | Conditional |
|---|---|
| Candidate artefact | Golden set: Tier 2–3, written before grading |
| Risk tier, decided before grading (`risk-tiers.md`) | Upstream contracts, if inputs have their own |
| Acceptance contract | |
| Rubric (`templates/rubric.md`) | |
| Evidence pack: the sources the artefact claims to rest on | |

A missing required input gives `HUMAN_REVIEW` with the input named.

## Decisions

| Verdict | When | Permits |
|---|---|---|
| `PASS` | every applicable criterion met with cited evidence; verification level ≥ tier; no unresolved contradiction | ACCEPTED once a named decider is recorded |
| `FAIL` | any applicable criterion clearly contradicted by evidence, or a forbidden claim present | nothing. Back to the author with criterion IDs |
| `HUMAN_REVIEW` | the evidence conflicts and no amount of further reading would resolve it; required evidence missing; tier needs human authority not yet given | publish **only** the parts unaffected, once the publication authority accepts the named open items in writing |

`HUMAN_REVIEW` with accepted open items is the **normal** outcome for real work. It isn't a soft pass. The accepted items stay open and listed, and they block anything that depends on them.

## Context separation and verification levels

The grader sees **the artefact, the evidence pack and the rubric**. It doesn't see **the golden set, the author's reasoning, or any earlier grade**. The golden comparison happens after the grade, in `/gate`.

| Level | What it is | Satisfies |
|---|---|---|
| Self-review | The author checks against the rubric | Tier 1 |
| Context-separated | The `acceptance-verifier` subagent, given only the artefact, evidence and rubric | Tier 2 |
| Independent authority | The named steward, who didn't produce it, plus platform owner sign-off | Tier 3 |

A fresh session is context separation, not independent authority. `contract_check.py` rejects a `PASS` recorded at a level below the tier.

## Outputs: two shapes, one decision

**The grade** (from the grader): five fields, nothing else. `decision` · `failed_criteria` · `evidence` · `explanation` · `confidence`. See `.claude/agents/acceptance-verifier.md`.

**The record** (by `/gate`): contract or impl spec §15, or `templates/decision-record.md` for other artefacts. It adds the context the grade leaves out: tier, verification level, required facts met n/n, forbidden claims found, **decider**, date, accepted open items, failure-library entry.

> **A verdict without a named decider and a cited piece of evidence is an opinion.**

## Measure the gate, not just the artefact

`/gate` appends a row to `docs/gate-log.md`. Each month these roll up into the team scorecard (`registers/scorecard.md`). Don't optimize the first-pass acceptance rate on its own: a gate that passes everything is just a rubber stamp.
