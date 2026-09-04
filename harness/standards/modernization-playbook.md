# Modernization Playbook

*Harness standard · S5 · owner: see `OWNERS.md` · reviewed by Steward*

> **Never let modernization silently turn an observation into an assumption, or an assumption into a requirement.**

Modernization has two problems. **Converting the implementation** (syntax, dialect, structure) is a tooling problem: use platform tooling (Lakebridge: assess → transpile → reconcile) wherever it's supported. **Deciding which behaviour survives** (semantics, parity, intent) is not a tooling problem. Even a perfect semantic conversion can't tell you whether an undocumented behaviour belongs in the target contract. This playbook is about the second problem.

---

## Two axes, kept apart

**Claim status: what we know** (every recovered behaviour gets exactly one)

| Status | Means | Evidence required |
|---|---|---|
| `OBSERVED` | Evidence proves it happens | captured input → output, query result, platform lineage |
| `DOCUMENTED` | An authoritative spec says it | cited document, with level per `evidence-hierarchy.md` |
| `INFERRED` | A likely interpretation | the reasoning, stated, plus what would confirm it |
| `UNKNOWN` | Can't be established with available evidence | what was tried; what evidence would settle it |
| `DECISION_REQUIRED` | Needs someone with authority | the question, the options, the **named route** |

**Parity disposition: what we do about it** (every behaviour that reaches the target gets exactly one)

| Disposition | Means | Example |
|---|---|---|
| `MUST_MATCH` | Target must reproduce it | regional exclusion that finance relies on |
| `INTENTIONAL_CHANGE` | Target deliberately differs; the difference is approved and communicated | fixing an integer-division truncation, with a documented restatement |
| `ALLOWED_DIFFERENCE` | Differs, and nobody depends on the difference | row order; whitespace in a free-text field |
| `DECISION_REQUIRED` | Disposition can't be set without authority | "Finance has reconciled against this for ten years. Do we fix it?" |

**Claim status ≠ disposition.** An `OBSERVED` bug can be `MUST_MATCH` (consumers depend on it) or `INTENTIONAL_CHANGE` (fix it and restate). Record both, side by side, for every behaviour.

---

## The evidence ladder

How much evidence the agent works from decides what it can honestly claim. Climb before you convert.

| Rung | Evidence | What the agent can claim |
|---|---|---|
| 0 | Wholesale translate: source in, target out | nothing about behaviour; a syntax conversion |
| 1 | Source-only reverse engineering | the author's apparent **intent**: `DOCUMENTED` / `INFERRED` at best |
| **2** | **Source + captured behaviour** (real inputs, parameters, outputs) | **`OBSERVED` behaviour. The minimum before conversion starts** |
| 3 | Source + runtime + golden data | behaviour across the cases that matter |
| 4 | Production shadow run | parity under real load |

> At rung 3, an agent looping until new matches old will faithfully reproduce every bug. Parity is decided in the parity contract, not by convergence.

## The sequence

| # | Step | Layer | Produces | Template |
|---|---|---|---|---|
| 1 | **Scope**: what's being replaced, who consumes it | exploration (read-only) | impact assessment (`lineage-impact-reviewer`) | — |
| 2 | **Capture**: inputs, parameters and actual outputs from the legacy system | human, or delivery | captured I/O under `docs/40-modernization/<object>/captured/` | — |
| 3 | **Characterize**: what the legacy actually does, facts only | delivery (writes `docs/40-modernization/`) | behaviour-recovery record | `behaviour-recovery-record.md` |
| 4 | **Classify** each claim (five statuses) | delivery | statuses in the record | — |
| 5 | **Register** every assumption and unknown, with a route | delivery | assumptions and unknowns register | `assumptions-and-unknowns-register.md` |
| 6 | **Decide parity**: disposition per behaviour; route every `DECISION_REQUIRED` | — | parity contract | `parity-contract.md` |
| 7 | **Convert**: transpile or rewrite against the parity contract | delivery | candidate implementation | — |
| 8 | **Characterization tests**: legacy captured I/O becomes target tests *before* the rewrite is trusted | delivery | tests tracing to parity rows | — |
| 9 | **Reconcile** source vs target per `test-and-reconciliation-patterns.md` | delivery | reconciliation report | — |
| 10 | **Accept**: every parity row becomes a contract business rule (below); gate as normal | — | gated acceptance contract | `acceptance-contract.md` |

Run `/behaviour-recovery` for steps 3–6. Investigation is read-only either way: the `lineage-impact-reviewer` subagent has no write tools. The session runs under **delivery** only so the records can be saved to `docs/40-modernization/`.

**Parity rows → acceptance contract §6.** `MUST_MATCH` → an `inclusion` / `exclusion` / `derivation` rule stating the behaviour. `INTENTIONAL_CHANGE` → a `derivation` rule for the new behaviour, plus the affected consumers in contract §10. `ALLOWED_DIFFERENCE` → a `tolerance` rule stating what may differ. `DECISION_REQUIRED` → contract §14, and the rule stays `ABSENT` until decided.

## Rules

1. **Give the agent evidence, not just code.** Without captured inputs and outputs, an agent narrates the author's *intent*. With them, it characterizes *behaviour*. Always capture first.
2. **Facts before interpretation.** The recovery record lists what happens. Why, and whether it should, comes later and gets a status.
3. **Every business-semantics question is `DECISION_REQUIRED` with a named route.** Engineers don't decide it, and neither does the agent. Leaving it as `DECISION_REQUIRED` is the correct output, not a failure to finish.
4. **Absences aren't evidence of safety.** A missing row, an empty lineage result, a record both systems dropped: none of these prove anything is safe. Reconciliation compares system to system, so it can't find a row both dropped. Characterization compares system to evidence.
5. **Every surprise becomes a test.** An `OBSERVED` behaviour with a `MUST_MATCH` disposition gets a characterization test before conversion starts.
6. **Three questions, three tools:** reconciliation (*did target reproduce source?*), characterization (*what did source actually do?*), parity (*which behaviours must the target keep?*).

## Readiness verdict: S5's gate

| Verdict | When |
|---|---|
| `READY_TO_REIMPLEMENT` | every behaviour has a claim status **and** a disposition; no `DECISION_REQUIRED` sits on anything being reimplemented now; evidence is at rung 2 or above; characterization tests exist for the `MUST_MATCH` rows |
| `NOT_READY — decision required` | a `DECISION_REQUIRED` blocks the behaviour being reimplemented. It's routed to a named authority, with a due date. Parts it doesn't touch may proceed, and the parity contract §4 lists which |
| `NOT_READY — insufficient evidence` | below rung 2 (no captured behaviour); any behaviour without a status; anything `UNKNOWN` on the path being reimplemented |
