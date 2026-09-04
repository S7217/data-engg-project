# Acceptance Contract

### What must be true before this publishes

*Harness template · acceptance contract · **v1.1** · copy to `docs/10-contract/<object>.contract.md`*

One of two documents. This one is graded by the gate. The **Implementation Spec** is written afterwards and generates the code.

| | This document | Implementation Spec |
|---|---|---|
| Answers | What must be true | How it is built |
| Language | Business | Technical |
| Led by | Steward | Engineer |
| Written | Before the gate | After this passes |
| Lifecycle | Stable — survives a change of platform, vendor or team | Changes with the platform |

**Keep expressions out of this document.** A `WHERE` clause here welds the meaning to one platform and makes the contract unreviewable by the person who owns it.

> **Changed in 1.1** — mandatory sections listed explicitly per tier rather than by range; surrogate key moved to the Implementation Spec; upstream contract reference added to Inputs; `tolerance` added as a business-rule type; `HUMAN_REVIEW` route stated.

---

## How to fill this in

**Every field gets a status. No field is left blank.**

| Status | Means | What happens next |
|---|---|---|
| `PRESENT` | Stated in a source. Cite it. | Settled |
| `INFERRED` | Reasonable, but no source says it | A human confirms before the gate passes |
| `ABSENT` | Nothing in any source answers this | **Goes back to the business.** Blocks the gate at Tier 2 and 3 |
| `N/A` | Genuinely does not apply | Say why in one line |

> **The rule this template exists to enforce:**
> **The agent may not fill a gap it discovered. It must name it.**
>
> An `INFERRED` value that should have been `ABSENT` produces a contract that passes review and fails in production, because nothing in the review had reason to question it.

**Check it mechanically before submitting to the gate:** `python3 harness/tools/contract_check.py docs/10-contract/<object>.contract.md`. It flags blank statuses, missing mandatory sections for the tier, `ABSENT`/`INFERRED` sections with no §14 row, and a `PASS` recorded over an `ABSENT` at Tier 2–3.

**Every `PRESENT` needs a citation** — document and section, or file and line. "The BRD says so" is not a citation.

**Business rules and DQ expectations carry IDs** (`BR-01`, `DQ-01`). The Implementation Spec references them, and its traceability check resolves them in both directions.

---

## 0 · Header

| | |
|---|---|
| **Artefact** | `catalog.schema.object` |
| **Requirement source** | BRD reference · Jira key |
| **Risk tier** | 1 · 2 · 3 |
| **Author** | |
| **Steward** | |
| **Date** | |
| **Version** | `1.0` |
| **Implementation Spec** | path · written after this passes |

**Tier rules.** 1 — internal, reversible. 2 — published to the catalogue, consumers rely on it. 3 — contractual, regulatory or money-adjacent.

| | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| **Mandatory sections** | 1 · 2 · 3 · 4 · 5 · 6 | 1–6 **plus** 7 · 8 · 9 · 10 · 11 · 12 · 13 | all |
| **Mandatory at every tier** | **14 · 15** | **14 · 15** | **14 · 15** |
| `ABSENT` blocks the gate | no | **yes** | **yes** |
| `INFERRED` needs sign-off | no | yes | yes, named |
| Verification level | self-review | context-separated | independent authority |

> A section that does not apply is marked `N/A` with a reason. It is never simply omitted — an omission and a deliberate exclusion look identical six months later.

> **Versioning rule.** A change to this document requires **re-gating**. The Implementation Spec pins the version it was written against; if this version moves, that pin is stale.

---

## 1 · Purpose
*Why this exists. Who consumes it, for what decision.*

| | |
|---|---|
| Value | |
| Status · Source | |

---

## 2 · Inputs
*Authoritative source objects. Not "the warehouse" — the actual objects.*

| # | Object | Authoritative? | Upstream contract | Status | Source |
|---|---|---|---|---|---|
| I-01 | | | path · version, or `none` | | |

> Two candidate sources for the same fact is an **escalation**, not a choice for the author.

> **Upstream contract** matters in a layered warehouse. If an input has its own contract, a change to that contract can invalidate this one. Pin the version; a change upstream re-opens this document.

---

## 3 · Outputs

| | |
|---|---|
| Object | |
| Columns | *listed at business level; the column-by-column mapping lives in the Implementation Spec* |
| Storage / format | |
| Status · Source | |

---

## 4 · Grain
*One row represents exactly what?*

| | |
|---|---|
| One row = | |
| Status · Source | |

---

## 5 · Keys

| | |
|---|---|
| Unique on | |
| Natural / business key | |
| Status · Source | |

> A stated grain with no uniqueness key is an assertion nobody can test. Both, or neither is done.

> **Surrogate keys are not stated here.** A surrogate key is a physical construct with no business meaning; it belongs in the Implementation Spec's mapping. If it appears here, this document has started describing how rather than what.

---

## 6 · Business rules
*The rules that change meaning. Each gets an ID. The Implementation Spec implements each one and cites it.*

| ID | Type | Statement | Status | Source | Glossary |
|---|---|---|---|---|---|
| BR-01 | inclusion | | | | |
| BR-02 | exclusion | | | | |
| BR-03 | derivation | | | | |
| BR-04 | edge case | | | | |
| BR-05 | tolerance | | | | |

**Types.** `inclusion` · `exclusion` · `derivation` · `edge case` · `tolerance`.

> **Exclusions are the trap.** A rule that says what is included rarely says what is left out, and the omission survives review.

> **`tolerance` rules state what the business will accept without being told.** Schema evolution and bad-row handling are the two that matter most, and both read as technical settings when they are not. Write them here, in business language:
>
> *"A new column in the source must not reach the published surface without steward review."*
> *"Rows failing DQ-02 must not be silently dropped; they are retained and reviewable."*
>
> The Implementation Spec then chooses the mechanism and cites the rule. Without a `tolerance` rule, an engineer makes the decision alone, after the gate, where the steward has no authority.

> **Business language, not expressions.** Write *"refunded orders are excluded from lifetime value"*, not `WHERE status <> 'refunded'`. The expression belongs in the Implementation Spec's mapping, citing this rule ID.

---

## 7 · Freshness

| | |
|---|---|
| Expected latency | |
| Schedule | |
| Behaviour when late | |
| Status · Source | |

---

## 8 · DQ expectations
*Each one testable. Each one owned.*

| ID | Expectation | Threshold | Severity | On failure | Alert owner | Status |
|---|---|---|---|---|---|---|
| DQ-01 | | | | warn / drop / fail / quarantine | | |

> A DQ rule nobody owns is a monitoring cost, not a control.

> `On failure` here is **per rule**. Where a rule does not state one, the default comes from the `tolerance` rule in §6 and is implemented in the Implementation Spec §8. Two places, one hierarchy: the specific rule wins.

---

## 9 · Classification

| | |
|---|---|
| `sensitivity` | `public` / `internal` / `confidential` / `restricted` |
| Other governed tags | |
| Column-level exceptions | *named here, applied in the mapping* |
| Rationale | |
| Status · Source | |

---

## 10 · Ownership

| | |
|---|---|
| Object owner | |
| Publication authority | |
| Consumers to notify on change | |
| Status · Source | |

---

## 11 · Acceptance evidence
*What proves this correct. Not "it ran."*

| ID | Evidence | What it proves | Where it lives | Status |
|---|---|---|---|---|
| AE-01 | Reconciliation | | | |
| AE-02 | Tests | | | |
| AE-03 | Golden set | | | |
| AE-04 | Sign-off | | | |

> IDs matter here for the same reason they matter on `BR-` and `DQ-`: the Implementation Spec's traceability check resolves every `AE-` to a test in its §10.

---

## 12 · Glossary references
*Reference by ID. **Never copy a definition into this document** — a copied definition goes stale the day the glossary changes, and nobody notices.*

| Term as used here | Glossary ID | Used in | Status |
|---|---|---|---|
| | `GL-nnnn` | BR-01, §4 | |

> A term used here with no glossary entry is `ABSENT` and goes back to the steward. If the glossary and the BRD disagree, that is an escalation — section 14.

---

## 13 · Delivery envelope
*The nine governance facts that must be known before the artefact is created.*

| Decision | Answer |
|---|---|
| Placement — catalog and schema | |
| Ownership — role or group | |
| Classification — governed attributes | |
| Human access — who may read or change | |
| Agent data access — data / metadata only / neither | |
| Agent mutation — code / data / metadata | |
| Tag authority — may the agent assign governed tags | |
| Environment — identity in dev vs prod | |
| Publication — what approval permits promotion | |

---

## 14 · Open items
*Everything `ABSENT` or `INFERRED`, and every source conflict. The honest part of the document.*

| # | Section | Status | Question for | Blocking? | Resolved |
|---|---|---|---|---|---|
| | | | business / steward / engineering | | |

---

## 15 · Gate submission
*Completed by the verifier, not the author.*

| | |
|---|---|
| **Decision** | `PASS` / `FAIL` / `HUMAN_REVIEW` |
| Failed criteria | |
| Evidence cited | |
| Explanation | one sentence |
| Confidence | high / medium / low — and what would raise it |
| Verification level used | self-review / context-separated / independent authority |
| Decider | |
| Date | |

> A verdict without a named decider and a cited piece of evidence is an opinion.

**What each verdict permits:**

| Verdict | The Implementation Spec may… |
|---|---|
| `PASS` | begin, pinned to this version |
| `HUMAN_REVIEW` | begin **only** where the named open items in §14 are accepted in writing by the publication authority, and only for the parts unaffected by them. Record the acceptance below. |
| `FAIL` | not begin |

| | |
|---|---|
| Open items accepted by | *name · date · which items* |

> `HUMAN_REVIEW` with accepted open items is the normal case for real work. It is not a soft `PASS` — the accepted items stay open, stay listed, and block the publication of anything that depends on them.

---

## Field map — where the work usually is

| Usually answered by the BRD | Usually decided by the steward | Usually goes back to the business |
|---|---|---|
| Purpose · Inputs · Outputs | Grain · Keys · DQ expectations · Classification · Ownership | Business rules · Tolerance · Freshness · Acceptance evidence |

**The right-hand column is where contracts die.** All of it semantic, all of it what a generating agent will confidently invent if nobody stops it.

---

## Change log

| Version | Date | Change | Re-gated? | By |
|---|---|---|---|---|
| 1.0 | | Initial | | |