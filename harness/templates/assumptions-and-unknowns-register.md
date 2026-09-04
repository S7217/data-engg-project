# Assumptions and Unknowns Register

*Harness template · S5 · copy to `docs/40-modernization/<object>/assumptions-and-unknowns.md` (or one per migration wave)*

Everything we're relying on but haven't proved, and everything we know we don't know. Each item has an owner and a route. **An assumption that isn't written down turns into a requirement by default.**

| ID | Statement | Kind | Status | Basis | Risk if wrong | Route to | Owner | Due | Blocking? | Resolution |
|---|---|---|---|---|---|---|---|---|---|---|
| AU-01 | | assumption · unknown · open question | `INFERRED` / `UNKNOWN` / `DECISION_REQUIRED` | evidence or reasoning | what breaks, for whom | business · steward · engineering · platform | | | yes / no | answer · date · by whom · new status |

## Rules

1. **Assumptions get a basis.** "Seemed reasonable" isn't one. Cite the reasoning or the partial evidence.
2. **Unknowns get the evidence that would settle them.** For example: "Needs 12 months of lineage. Current window is 11."
3. **Business-semantics items are `DECISION_REQUIRED`** and routed to the domain authority. The register records the question. It doesn't answer it.
4. **Resolved items stay in the register,** with the answer and the new status. Deleting a resolved row deletes the reason the code looks the way it does.
5. **Review at every wave boundary.** An open blocking item stops the wave.
