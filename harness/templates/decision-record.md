# Decision Record

### Publish, reject, or send to review

*Harness template · decision record · **v1.1** · copy to `docs/10-contract/<object>.<artefact>.decision.md`*

One record per decision. Completed by the **verifier**, not the author.

Use this for any AI-produced artefact that reaches a gate: a column description, a DQ rule, a glossary term, a metadata batch, a data contract, an implementation spec.

> Contracts and implementation specs carry their own §15 blocks, which are this record embedded in the document it grades. Everything else uses this file.

**A verdict without a named decider and a cited piece of evidence is an opinion.**

---

## 1 · What is being decided

| | |
|---|---|
| **Artefact** | the specific thing — `catalog.schema.object.column`, `BR-02`, `GL-0051` |
| **Artefact family** | column description · DQ rule · glossary term · contract · impl spec · metadata batch |
| **Produced by** | model · prompt or capability · version |
| **Risk tier** | 1 · 2 · 3 |
| **Rubric** | path · version |
| **Golden set** | path · version, or `none` |
| **Related contract** | path · version, or `none` |

---

## 2 · Verification

| | |
|---|---|
| **Level used** | self-review · context-separated · independent authority |
| Verifier | person, or the capability and context used |
| Did the verifier see the generator's reasoning? | yes / **no** |

**Required level by tier:** Tier 1 — self-review. Tier 2 — context-separated. Tier 3 — independent authority.

> If the level used is below the level the tier requires, the verdict cannot be `PASS`. Record the shortfall in section 6 and route it.
>
> **A fresh session is context separation, not independent authority.** Same model family, same biases, same reading of the same source. Do not record it as level three.

---

## 3 · Grading

| # | Criterion (from the rubric) | Met? | Evidence — source and line |
|---|---|---|---|
| 1 | | ✅ / ❌ / ⚠ | |

**Required facts:** _n_ of _n_ present.

**Forbidden claims found:**

| Claim | Where | Contradicted by |
|---|---|---|
| | | |

> Naming the evidence is the point. "It looks right" is not a row. If a criterion cannot be checked against a source, mark it ⚠ and treat it as an open item — an uncheckable criterion is a rubric defect, not a pass.

**If sources disagree,** apply the evidence hierarchy: approved business definition > implemented transformation > architecture documentation > naming inference. A genuine conflict is an **escalation**, not a judgement call — record it in section 6.

---

## 4 · Verdict

| | |
|---|---|
| **Decision** | `PASS` · `FAIL` · `HUMAN_REVIEW` |
| Failed criteria | by number |
| Explanation | one sentence |
| **Confidence** | high · medium · low |
| What would raise the confidence | |
| **Decider** | named person |
| Date | |

**What each verdict permits:**

| Verdict | Means |
|---|---|
| `PASS` | Publishes. Every required criterion met, evidence cited, verification at or above the tier's level |
| `HUMAN_REVIEW` | Not wrong, not sufficient. Publishes **only** with section 5 completed |
| `FAIL` | Does not publish. Goes back with the failed criteria named |

> `HUMAN_REVIEW` is a verdict, not a hedge. An artefact that is true but omits something business-critical is the normal case for this outcome — and recording it is more useful than forcing a binary.

---

## 5 · Acceptance — `HUMAN_REVIEW` only

| | |
|---|---|
| Open items accepted | which ones, by number |
| Accepted by | **publication authority**, named |
| Date | |
| Conditions | what must still happen, and by when |
| What is blocked meanwhile | anything downstream that cannot proceed |

> Acceptance is not a formality. It is the record that someone with authority looked at a known gap and decided to publish anyway. Six months later, that record is the difference between a governed decision and an unexplained defect.

---

## 6 · Open items and escalations

| # | Item | Type | Route to | Blocking? | Resolved |
|---|---|---|---|---|---|
| | | ambiguity · source conflict · missing evidence · verification shortfall · rubric defect | business / steward / engineering | | |

---

## 7 · Failure library

*Copy the completed block into `registers/failure-library.md` in the central harness. Recording it here alone doesn't make it a harness asset.*

*Complete only where this decision found a defect worth remembering.*

| Field | |
|---|---|
| Trigger | what was being produced |
| Incorrect behaviour | what the artefact claimed |
| **Why it looked plausible** | |
| Detection mechanism | which criterion or check caught it |
| Root cause | |
| Preventive control | |
| **Regression asset** | the test, golden case, rubric line or rule this produced |

> **Why it looked plausible** is the field everyone skips and the one that makes a failure recognisable next time.
>
> **Regression asset** is what makes the harness compound rather than accumulate. A failure that produces nothing executable will be found again.

---

## Filling this in the first time

Five minutes, in this order:

1. **Section 1** — what and which rubric. Thirty seconds.
2. **Section 2** — what level did you actually use, not what you meant to.
3. **Section 3** — grade, citing sources. Most of the five minutes.
4. **Section 4** — verdict, confidence, your name.
5. **Section 5** only if `HUMAN_REVIEW`. **Section 6** if anything is open. **Section 7** only if you found something worth remembering.

Sections 1 to 4 are always completed. Five, six and seven are conditional.

---

## Change log

| Version | Date | Change | By |
|---|---|---|---|
| 1.1 | | Aligned with contract and impl spec v1.1 — verification levels, `HUMAN_REVIEW` acceptance block, seven-field failure library | |
