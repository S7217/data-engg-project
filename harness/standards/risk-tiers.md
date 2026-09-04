# Risk Tiers

*Harness standard · S3 · owner: Steward · see `OWNERS.md`*

Three tiers. The tier is a property of **what the artefact is and who consumes it**, not of how hard it was to produce, how confident the author feels, or how the grade came out.

The tier is decided **before** the work is graded, in contract §0 or decision record §1. A tier assigned after the grade is just a description of the grade.

---

## Tier 1: contained

**Consequence.** A wrong result is noticed by the person who reads it, and costs them time. It doesn't leave the team, doesn't reach a decision, and doesn't change anything downstream. Correcting it is a re-run.

**Example.** A column description on a staging table that one team reads while developing against it.

**Required evidence.** The rubric applied, with every claim cited above level 4 of the evidence hierarchy. For an artefact at this tier:

> an automated check may be sufficient, subject to your publication policy.

That sentence says the *check* may be automated. It doesn't say the publication may be.

**Who may publish.** The named delivering engineer, under your publication policy.

## Tier 2: propagating

**Consequence.** A wrong result isn't visible at the point where it's wrong. Something else consumes it (a downstream model, a dashboard, an agent answering questions), and the error reaches a reader who has no way to check it and no reason to suspect it. Correcting it means finding everywhere it went.

**Example.** Published column descriptions on a gold table that Genie Agents answer questions from. A gold table feeding a dashboard.

**Required evidence.** Everything required at Tier 1, and:
- a golden set written **before** the artefact was graded, not after;
- a **context-separated** grade: the grader saw the artefact, the evidence pack and the rubric, and **didn't see the golden set or the author's reasoning**;
- a completed decision record with a named decider;
- no unresolved `HUMAN_REVIEW` on anything the artefact covers (unless the open items are accepted in writing, contract §15).

An automated check is **not** sufficient at this tier. The grade is an input to the decision. It isn't the decision.

**Who may publish.** The artefact owner named in delivery-envelope decision 2, with the steward notified before publication rather than after.

## Tier 3: governing

**Consequence.** The artefact changes what other people are permitted to do, or feeds a number that's reported outside the organisation. A wrong result isn't a wrong answer but a wrong permission or a wrong statement of record. It may be irreversible, and the people affected by it aren't the people who can detect it.

**Example.** A change to a governed tag. A financial metric reported externally. Billing, regulatory returns.

**Required evidence.** Everything required at Tier 2, and:
- independent human review by the named steward, who didn't author the artefact;
- the delivery envelope completed in full, with decision 7 (tag authority) answered explicitly;
- the change reviewable and reversible, with the prior state recorded;
- deterministic tests for every rule, plus reconciliation against an independent source where numbers are involved;
- sign-off recorded **before** the change is applied, not after it's observed.

**Who may publish.** The named steward, **jointly** with whoever owns the platform deployment. Two named people, both recorded.

---

## What no tier grants

> **No tier in this policy permits publication without a named human accountable for it.**

Tier 1 lets an automated check carry the *evidence*. It doesn't remove the person from the decision, and it doesn't make publication automatic. Automating the check and automating the decision are different changes. The first is a productivity question. The second is a governance one, and you don't make it by writing a rubric.

## Choosing the tier

Ask what happens when the artefact is wrong and nobody notices for a month.

- Someone re-runs something: **Tier 1**.
- Somebody acts on a wrong answer and can't tell they did: **Tier 2**.
- Somebody gains access they shouldn't have, or a reported figure is wrong: **Tier 3**.

Where two tiers both look arguable, take the higher one and record why. Over-tiering costs time. Under-tiering costs whatever's in the consequence column.

## Tiering isn't grading

A Tier 3 artefact that passes every criterion is still Tier 3. A Tier 1 artefact that fails is still Tier 1. The tier sets what evidence is required and who may publish. The grade says whether that evidence was met. Collapsing the two is how "it passed" turns into "it may be published".

---

## How the tier maps onto the harness

| | Tier 1: contained | Tier 2: propagating | Tier 3: governing |
|---|---|---|---|
| Contract sections mandatory (v1.1) | 1–6, 14, 15 (`make new` marks 7–13 N/A) | 1–15 | 1–15 |
| `ABSENT` | allowed, listed in §14 | **blocks the gate** | **blocks the gate** |
| `INFERRED` | allowed | needs sign-off | needs **named** sign-off |
| Verification level | self-review (`/gate` runs it inline) | **context-separated** (`acceptance-verifier`, no golden set) | **independent authority**: the steward, plus platform owner sign-off |
| Golden set | optional | required, written before grading | required, plus edge and adversarial cases |
| Decider in §15 | named engineer | named owner | steward **and** platform owner |
| Enforced by | `contract_check.py` (sections, level ≥ tier, decider) · `ready.py` · code-gate hook | same | same |

**A fresh session isn't independent authority.** Same model family, same biases, same reading of the same source. It counts as context separation (Tier 2), never as Tier 3.
