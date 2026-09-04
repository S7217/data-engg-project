# Evidence Hierarchy

*Harness standard · S4 · owner: Steward · see `OWNERS.md`*

When sources disagree, this decides which one wins, and when nobody may decide without escalating.

| Level | Source | Examples | Trust |
|---|---|---|---|
| **1** | **Approved business definition** | gated contract; recorded gate acceptance; glossary entry; steward-signed decision | highest |
| **2** | **Implemented transformation** | the code that runs in production; observed output of that code | high |
| **3** | **Architecture documentation** | ADRs, design docs, READMEs | medium |
| **4** | **Naming inference** | conclusions drawn from a column or table name alone | lowest. Never cite it on its own |

An **implementation spec** isn't on this ladder: it's the bridge between level 1 (the gated contract it pins) and level 2 (the code generated from it). It inherits its authority from the contract.

**Why business beats code:** the business can be wrong and know it. Code can be wrong without anyone noticing. If they disagree, one of them is stale, and you can't tell which without asking.

## A conflict is an escalation, not a judgement call

| Conflict | Route to | What happens |
|---|---|---|
| Level 1 vs Level 2 (contract says X, code does Y) | Steward + engineer | Code is fixed to match, **or** the contract is re-gated. Never resolved by editing whichever is easier |
| Level 1 vs Level 1 (glossary vs BRD, two approvals disagree) | Steward | Escalation. The agent marks it in contract §14 and doesn't pick |
| Implementation spec vs code (spec says X, code does Y) | Engineer | **The spec governs the code** (code is generated from it, and `trace_check` holds them together): fix the code, or change the spec and re-run §12. Record which in the spec's change log |
| Level 3/4 vs Level 2 (ADR, README or a name disagrees with the code) | Engineer | Trust the code; correct the doc or the name |

## Rules for agents

1. Cite the level with the evidence: *"PRESENT · contract §6 BR-03 (L1)"*.
2. Never present a level-4 inference as a finding. A column called `is_deleted` might mean "failed DQ".
3. Two candidate sources for the same fact is an escalation, not a choice.
4. Observed behaviour (level 2) can show you what the code does. It can't tell you whether that behaviour is **intended**. That's a level-1 question (see `modernization-playbook.md`).
5. Code comments should cite the level-1 source they implement: `# implements BR-03 (contract §6)`.
