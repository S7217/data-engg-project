# Rubric: <artefact family> for `<object>`

*Harness template · S3 · copy to `docs/10-contract/<object>.rubric.md`, or a shared `docs/rubrics/<family>.rubric.md`*

A rubric says how an artefact is judged. It doesn't say what the artefact should contain. If it did, you'd be grading a copy of the answer rather than the work. *(What it must contain goes in the golden set, which the grader never sees.)*

Each criterion is written so that two people applying it to the same artefact reach the same verdict. If you can't apply a criterion without already knowing the subject matter, it isn't finished.

**Write the rubric before the artefact is generated.** The steward owns the semantic criteria. The engineer owns the technical ones.

---

## Writing criteria: the semantic defects to cover

Every rubric for a business-facing artefact has at least one criterion for each defect category that applies. These are the ways a fluent artefact is wrong:

| Category | The defect | Typical condition |
|---|---|---|
| **Unit** | A number without its unit, currency or scale | "Unit is named" |
| **Inclusion / exclusion** | What's counted, and what's silently left out | "Inclusion boundary is stated, naming the values" |
| **Grain / meaning** | What one row or one value represents | "Grain is stated as one row per …" |
| **Boundary** | Dates, periods, timezones, inclusive/exclusive edges | "Period boundary and timezone are stated" |
| **Evidence** | A claim no source supports | "Evidence is cited, and the source contains the claim" |

---

## C1: `<what this criterion applies to>`

*Worked example (column description for a money column). Replace it with your own.*

**Applies to:** any description of `customer_lifetime_value_cents`.

**An artefact passes C1 only if all three conditions hold.**

| # | Condition | Satisfied when | Not satisfied when |
|---|---|---|---|
| 1 | **Unit is named** | The description states the unit the figure is expressed in. | The description says only "value", "amount", "total" or "spend". A number without a unit isn't a fact. |
| 2 | **Inclusion boundary is stated** | The description says explicitly which order statuses contribute to the figure and which don't, naming them. | The boundary is implied, partial, or given as a summary phrase that doesn't name statuses. |
| 3 | **Evidence is cited** | The description cites a file and a section or line range, and the cited source contains the claim. | No citation; a citation to a file with no section; a citation to a source that doesn't contain the claim; or the only support offered is the column's name. |

**What C1 doesn't do.** C1 doesn't state which inclusion boundary is correct. It requires that the description commit to one, name the statuses it covers, and cite the evidence it rests on. Whether that boundary is the right one is settled by the evidence, not by this rubric.

**Failure mode this catches.** A fluent, confident description that no source supports. Condition 3 is the one that catches it, and it's the one most often waived under time pressure.

**Severity if failed:** material

---

## C2: `_______________________`

**Applies to:** _______________________

| # | Condition | Satisfied when | Not satisfied when |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

**What C2 doesn't do:** _______________________

**Failure mode this catches:** _______________________

**Severity if failed:** _____________

---

## Applying the rubric

An artefact is graded against every criterion that applies to it. A criterion is either met or failed, never partially met: if any condition isn't satisfied, the criterion fails, and the condition that failed is named.

Where the evidence supports two readings and the artefact commits to one without saying so, the verdict is `HUMAN_REVIEW`, not `FAIL`. The artefact isn't wrong. The question just isn't settled yet (`standards/evidence-hierarchy.md`).

> **A criterion that can't be checked against any source is a rubric defect.** Fix the rubric. It doesn't count as a pass.

## Change log

| Version | Date | Change | By |
|---|---|---|---|
| 1.0 | | Initial | |
