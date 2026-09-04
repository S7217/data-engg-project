# Parity Contract

*Harness template · S5 · copy to `docs/40-modernization/<object>/parity-contract.md`*

> **Parity doesn't mean byte-for-byte identical. It means agreeing explicitly on what must stay equivalent and what may differ.**

| | |
|---|---|
| **Legacy component** | |
| **Target object** | `catalog.schema.object` |
| **Behaviour-recovery record** | path · date |
| **Impact assessment** | path (`lineage-impact-reviewer`) |
| **Decision authority** | named domain authority for semantic decisions |
| **Version** | `1.0` |

---

## 1 · Behaviours and dispositions

**Two axes, kept apart.** Claim status = what we know. Disposition = what we do about it.

| ID | Behaviour (from recovery record) | Claim status | Disposition | Rationale | Consumers affected | Routed to | Decided by · date | Test |
|---|---|---|---|---|---|---|---|---|
| P-01 | B-01 … | `OBSERVED` | `MUST_MATCH` | | | | | `T-nn` |
| P-02 | | `OBSERVED` | `DECISION_REQUIRED` | | | finance domain authority | | |

**Dispositions.** `MUST_MATCH`: target reproduces it · `INTENTIONAL_CHANGE`: target deliberately differs, approved and communicated · `ALLOWED_DIFFERENCE`: differs, and nobody depends on it · `DECISION_REQUIRED`: needs authority.

## 2 · Intentional changes

Every `INTENTIONAL_CHANGE` states how history and consumers are handled.

| ID | Change | History | Consumer notice | Approved by |
|---|---|---|---|---|
| P-nn | | preserve old · restate history · break going forward, documented | who, when, how | |

## 3 · Reconciliation plan

| Check | Scope | Pass condition | Explains differences via |
|---|---|---|---|
| Row count by period | | equal | `P-` rows with `INTENTIONAL_CHANGE` / `ALLOWED_DIFFERENCE` |
| Control totals | | diff = 0 per period | |
| Key set difference | | both directions empty | |
| Full-row hash on `MUST_MATCH` columns | | no mismatches | |

> Reconciliation tells you whether the systems differ. This contract tells you whether that difference is acceptable.

## 4 · Readiness verdict

| | |
|---|---|
| **Verdict** | `READY_TO_REIMPLEMENT` · `NOT_READY — decision required` · `NOT_READY — insufficient evidence` |
| Open `DECISION_REQUIRED` | ids · routed to · due |
| Blocks | which parts of the conversion can't proceed |
| Decided by · date | |

Every row feeds acceptance contract §6. `MUST_MATCH` becomes a rule stating the behaviour, `INTENTIONAL_CHANGE` a derivation rule plus a §10 consumer notice, `ALLOWED_DIFFERENCE` a tolerance rule, and `DECISION_REQUIRED` goes to §14 as `ABSENT`. The acceptance contract is then gated as normal (`standards/modernization-playbook.md`).
