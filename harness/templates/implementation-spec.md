# Implementation Spec

### How it is built

*Harness template · implementation spec · **v1.1** · copy to `docs/20-impl-spec/<object>.impl.md`*

The second of two documents. The **Acceptance Contract** says what must be true; this says how it is built, and this is what code is generated from.

**Do not begin until the contract has cleared its gate.** Everything below either implements a `BR-` rule from the contract, or is unrequested logic.

> **Changed in 1.1** — mapping rows carry IDs (`M-nn`); `HUMAN_REVIEW` entry condition stated; §8 cites the contract's `tolerance` rules rather than deciding alone; §12 adds an acceptance-evidence check and states its relationship to §14.

---

## 0 · Header

| | |
|---|---|
| **Artefact** | `catalog.schema.object` |
| **Contract** | path · **version pinned:** `1.0` |
| **Contract gate decision** | `PASS` / `HUMAN_REVIEW` · date · decider |
| **Open items accepted?** | *if `HUMAN_REVIEW`: who accepted, which items, date* |
| **Author** | |
| **Reviewer** | |
| **Date** | |
| **Version** | `1.0` |

**Entry condition.**

| Contract verdict | This document |
|---|---|
| `PASS` | proceed |
| `HUMAN_REVIEW` | proceed **only** for the parts unaffected by the open items, and only where those items are accepted in writing by the publication authority. Anything touching an open item is blocked and listed in §14. |
| `FAIL` | do not begin |

> **Versioning rule.** A change here requires re-running §12 only. A change to the **contract** requires re-gating the contract *and* re-running §12 against the new version. A spec citing a contract version that has moved is stale.

**Tier rules.** The contract's tier governs how much of this is required.

| Section | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| 1 Mapping · 2 Joins · 12 Traceability · 13 Ready | required | required | required |
| 3 Dedup · 4 Historisation · 5 Bad rows | if applicable | required | required |
| 6 Physical · 7 Dependencies · 8 Decisions | brief | required | required |
| 9 DQ implementation · 10 Tests · 11 Deployment | minimal | required | required + sign-off |
| 14 Deviations · 15 Review | required | required | required |

---

## 1 · Source-to-target mapping
*The spine. One row per target column. Code is generated from this table.*

| # | Target column | Type | Null? | Default | Source object | Source column | Transformation | Implements | Class. |
|---|---|---|---|---|---|---|---|---|---|
| M-01 | | | | | | | | `BR-nn` | |

- **#** — a stable row ID. Tests and the traceability check cite these, so they must not be positional. Never renumber; retire an ID rather than reusing it.
- **Transformation** — the actual expression, not a description. `WHERE status = 'completed'` · `SUM(amount_cents)` · `CAST(x AS DATE)`.
- **Implements** — the `BR-` ID this row realises, or `PASSTHROUGH`, or `SURROGATE` for a generated key. **Anything else is unrequested logic**, caught in §12.
- **Class.** — only where a column carries a sensitivity different from the object default.

> Surrogate keys live here, not in the contract. They have no business meaning, so there is nothing for a steward to review — but they must still appear as a row, marked `SURROGATE`, or §12 will flag them as unrequested.

---

## 2 · Join specification

| # | Left | Right | Type | On | Expected cardinality | Fan-out risk | Assertion |
|---|---|---|---|---|---|---|---|
| J-01 | | | inner / left / … | | 1:1 · 1:N · N:1 | | test ID from §10 |

> **Expected cardinality is not documentation, it is a test.** A join whose stated cardinality is never asserted in code is the commonest way a grain changes silently. Every row here names a test in §10.

---

## 3 · Deduplication & survivorship

| | |
|---|---|
| Duplicates possible? | |
| Match key | |
| Tie-break order | |
| Survivorship rule | |
| Discarded records | dropped / quarantined / logged |
| Implements | `BR-nn` |
| **Signed by** | **Steward** *(Tier 2 and 3)* |

> Which record wins is a business decision wearing technical clothing. If the contract does not answer it, that is an `ABSENT` in the contract — not a choice to make here.

---

## 4 · Historisation

| | |
|---|---|
| Pattern | snapshot / append-only / SCD1 / SCD2 / merge |
| Business key | *from contract §5* |
| Change detection | |
| Effective-dating columns | |
| Late-arriving data | |
| Restatement policy | |
| Implements | `BR-nn` |

---

## 5 · Bad-row handling & quarantine
*The mechanism. The behaviour was chosen in the contract.*

| | |
|---|---|
| Behaviour | *per `DQ-nn` where stated; otherwise the §8 default* |
| **Quarantine target** | `catalog.schema.object` |
| Retention | |
| Who reviews quarantined rows | |
| Reprocessing path | |
| Implements | `BR-nn` *(the tolerance rule)* |

> A quarantine with no named reviewer is a table that grows forever.

> **Three places mention bad rows; the hierarchy is fixed.** Contract §8 `On failure` is per-rule and wins. Contract §6 `tolerance` sets what the business will accept. This section and §8 implement both. If they disagree, the contract is right and this document is wrong.

---

## 6 · Physical design

| | |
|---|---|
| Table type | managed / external / view / materialized view / streaming table |
| Format | |
| Partitioning / clustering | and why |
| Expected volume · growth | |
| Retention / vacuum | |
| Compute profile | |

---

## 7 · Dependencies & run order

| # | Depends on | Type | Upstream contract | If unavailable |
|---|---|---|---|---|
| | | upstream table / job / external | path · version | fail / wait / proceed with stale |

| | |
|---|---|
| Runs after | |
| Triggers | |
| Idempotent? | yes / no — **if no, say why and how re-runs are made safe** |

---

## 8 · Design decisions
*The agent will make all four. It will not ask. Record the choice, the reason, and the rule it serves.*

| Decision | Choice | Why | Implements | Decided by |
|---|---|---|---|---|
| Batch or streaming | | | | Engineer |
| Full refresh, incremental or CDC | | | | Engineer |
| Schema evolution behaviour | reject / accept and widen / route to review | | `BR-nn` tolerance | **Steward, via the contract** |
| Bad-row default | warn / drop / fail / quarantine | | `BR-nn` tolerance | **Steward, via the contract** |

> **The bottom two implement a contract rule; they do not originate here.** Schema evolution and bad-row handling are business decisions about what the organisation will accept without noticing, and the steward's authority sits in the contract, before the gate — not in a sign-off loop after it.
>
> If the contract has no `tolerance` rule covering these, stop. That is an `ABSENT` in the contract, and the contract re-gates. Choosing here is exactly the silent gap-filling this chain exists to prevent.
>
> The bad-row default applies where a `DQ-` rule does not state its own `On failure`.

---

## 9 · DQ implementation
*Contract expectation → executable check. One row per `DQ-` in the contract.*

| Contract ref | Expectation | Executable check | Where it runs | On failure |
|---|---|---|---|---|
| `DQ-01` | | | pipeline expectation / test / monitor | per rule, else §8 default |

---

## 10 · Test inventory

| Test ID | Type | Asserts | Traces to |
|---|---|---|---|
| T-01 | unit / grain / reconciliation / negative / mutation | | `M-nn` · `BR-nn` · `DQ-nn` · `J-nn` · `AE-nn` |

> Every test traces to a mapping row, a rule, a DQ expectation, a join, or an acceptance-evidence item. A test that traces to none of those is testing the framework.

---

## 11 · Deployment

| | |
|---|---|
| Project / bundle | |
| Resources defined | jobs · pipelines |
| Targets | dev · test · prod |
| Identity per target | |
| Permissions in the definition | |
| Promotion gate | |
| Rollback | |

> These answers come from the contract's delivery envelope. Express them in the project definition, in source control — not in a runbook.

---

## 12 · Traceability check
*Run both directions before submitting. Mechanical — an agent can run it, a human confirms it.*

```bash
python3 harness/tools/trace_check.py docs/10-contract/<object>.contract.md docs/20-impl-spec/<object>.impl.md
```

The script runs checks 1–8 plus check 0 (the documents parse: nothing parsed is a failure, not a pass) and check 9 (every test ID in §10 exists in `tests/`). It exits non-zero if any failure has no §14 row of its own: a row naming the failing ID, or one row per failure naming `§12 #n` in the *From check* column.

| # | Check | Result |
|---|---|---|
| 1 | Every `BR-` in the contract is cited by at least one row in §1, §3, §4, §5 or §8 | ☐ |
| 2 | Every row in §1 cites a `BR-`, or is `PASSTHROUGH` / `SURROGATE` | ☐ |
| 3 | Every join in §2 states a cardinality **and** names a test in §10 | ☐ |
| 4 | Every `DQ-` in the contract appears in §9 | ☐ |
| 5 | Every `AE-` in the contract §11 is realised by a test in §10 | ☐ |
| 6 | Every glossary term in the contract still resolves | ☐ |
| 7 | Contract version in §0 matches the current contract | ☐ |
| 8 | Every input in contract §2 with an upstream contract is pinned in §7 | ☐ |

**§12 detects. §14 records and routes.** Every failure found here becomes a row in §14 with a type and an action. A check that fails here and has no row there means the check was run and ignored — which is worse than not running it.

| Finding | §14 type |
|---|---|
| A `BR-` with no implementation | `NOT-IMPLEMENTED` |
| A mapping row with no rule | `UNREQUESTED` |
| Anything else that cannot be satisfied | `deviation from contract` |

> **Unrequested logic is the quiet one.** No test suite finds it, because the tests were written from the same spec.

---

## 13 · Ready to generate
*Code generation should not start until every line is yes.*

- [ ] Contract cleared its gate; version pinned in §0; open items accepted if `HUMAN_REVIEW`
- [ ] Every target column has a mapping row with an ID, type and nullability
- [ ] Every transformation is an expression, not a sentence
- [ ] Every join states expected cardinality and names its assertion
- [ ] Load pattern, historisation and deduplication all answered
- [ ] Schema evolution and bad-row default each cite a `tolerance` rule
- [ ] Quarantine target named, with a named reviewer
- [ ] Every `DQ-` has an executable check; every `AE-` has a test
- [ ] Deployment targets and identities stated
- [ ] §12 run in both directions; every failure has a §14 row

**If any line is unchecked, the agent will fill the gap for you — and it will not ask.**

---

## 14 · Deviations & open items

| # | Item | Type | From check | Reason | Action | Blocking? |
|---|---|---|---|---|---|---|
| | | NOT-IMPLEMENTED · UNREQUESTED · deviation from contract · blocked by contract open item | §12 #n | | back to contract / steward / accepted with note | |

> A deviation is not a failure. An **unrecorded** deviation is. If the implementation cannot satisfy the contract, the contract changes — through the gate — rather than this spec quietly diverging.

---

## 15 · Implementation review

| | |
|---|---|
| **Decision** | `PASS` / `FAIL` / `HUMAN_REVIEW` |
| §12 clean? | *or: every failure has a §14 row with an action* |
| Failed criteria | |
| Evidence cited | |
| Confidence | high / medium / low — and what would raise it |
| Reviewer | |
| Steward sign-off | *required for §3 at Tier 2 and 3* |
| Date | |

---

## Where the work usually is

| Mechanical | Engineering judgement | Business decisions in technical clothing |
|---|---|---|
| Mapping rows · types · passthrough columns · surrogate keys | Physical design · partitioning · dependencies · load pattern | Survivorship · schema evolution · bad-row behaviour |

**The right-hand column belongs to the contract.** All three look like settings. All three decide what the organisation will accept without noticing — so all three are decided before the gate, not after it.

---

## Change log

| Version | Date | Change | Contract version | §12 re-run? | By |
|---|---|---|---|---|---|
| 1.0 | | Initial | `1.0` | | |