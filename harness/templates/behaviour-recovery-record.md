# Behaviour-Recovery Record

*Harness template · S5 · copy to `docs/40-modernization/<object>/behaviour-recovery.md` · see `standards/modernization-playbook.md`*

What the legacy component **actually does**, recovered from evidence. Facts first. Each claim carries exactly one status. Whether a behaviour *should* survive is decided in the parity contract, not here.

| | |
|---|---|
| **Legacy component** | e.g. `dbo.usp_monthly_revenue`, `PKG_Monthly_Customer_Revenue.dtsx` |
| **Platform / location** | |
| **Target object** | `catalog.schema.object` |
| **Captured evidence** | path to inputs, parameters, outputs (`captured/`) |
| **Recovered by** | person · agent + session |
| **Date** | |

---

## 1 · Interface

| | Value | Status | Evidence |
|---|---|---|---|
| Inputs (tables, files, parameters) | | | |
| Outputs | | | |
| Schedule / trigger | | | |
| Side effects (logs, temp tables, emails, other writes) | | | |

## 2 · Behaviours

One row per observable behaviour. **Write each one as a fact:** *"rows with region = 'EMEA' are excluded"*, not *"filters out EMEA because they're handled elsewhere"*.

| ID | Behaviour | Where in source | Status | Evidence | Confirmed by |
|---|---|---|---|---|---|
| B-01 | | file:line | `OBSERVED` / `DOCUMENTED` / `INFERRED` / `UNKNOWN` / `DECISION_REQUIRED` | captured case, doc ref | |

**Statuses.** `OBSERVED`: captured input → output proves it · `DOCUMENTED`: an authoritative spec says it · `INFERRED`: likely, with the reasoning stated · `UNKNOWN`: can't be established yet · `DECISION_REQUIRED`: needs someone with authority.

**Look for these specifically**, because they're the behaviours nobody documents:
- [ ] Implicit filters (`WHERE`, `INNER JOIN` dropping unmatched rows)
- [ ] NULL handling: dropped, coalesced, or propagated
- [ ] Integer division, rounding, truncation, implicit casts
- [ ] Date boundaries: inclusive/exclusive, timezone, month-end, fiscal calendar
- [ ] Deduplication and "latest record wins" logic
- [ ] Error handling: what happens to bad rows, partial failures, retries
- [ ] Hard-coded values: IDs, dates, thresholds, exchange rates
- [ ] Order dependence: cursors, `TOP 1` without `ORDER BY`

## 3 · Characterization cases

Captured legacy input → output pairs that become target tests (playbook step 8).

| Case | Input | Legacy output | Shows behaviour | Becomes test |
|---|---|---|---|---|
| C-01 | `captured/c01_in.csv` | `captured/c01_out.csv` | B-01 | `T-nn` |

## 4 · Discrepancies with documentation

| Behaviour | Documentation says | Legacy actually does | Status |
|---|---|---|---|
| | | | `DECISION_REQUIRED` |

## 5 · Handover

| | |
|---|---|
| Behaviours recovered | n (`OBSERVED` n · `DOCUMENTED` n · `INFERRED` n · `UNKNOWN` n · `DECISION_REQUIRED` n) |
| Unknowns and assumptions registered | `assumptions-and-unknowns.md` rows |
| Ready for parity contract? | yes / no: what's missing |
