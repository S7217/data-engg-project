# CLAUDE.md

<!-- Repository context. Every line here is loaded on every call. Apply the earn-in test
     (harness/standards/claude-md-standard.md): stable, project-specific, violated when absent.
     Delete these comments and fill the last section with what only this repo can tell you. -->

## How work is done here

This repo uses the harness (`harness/VERSION`). The rules and their reasons are in `harness/standards/`.

- **Requirement → contract → gate → impl spec → code.** Start with `/design-spec <object>`. Code under `src/pipelines/<layer>/` is blocked by a hook until `make ready OBJ=<object>` passes the code gate.
- **Don't fill a gap you find. Name it.** Missing business facts are `ABSENT` and routed. Don't infer them.
- **The steward decides:** grain, exclusions, survivorship, schema-evolution tolerance, bad-row disposition, classification. You propose. Governed tags are propose-only.
- **Before changing a published object,** run `lineage-impact-reviewer`. Zero rows isn't zero dependencies.
- **The credential rule:** "Your Claude API key lives in a Databricks secret scope, referenced at runtime. Never in CLAUDE.md. Never in a committed file. Never pasted into a prompt."

## Commands

```bash
make new OBJ=fct_x TIER=2      # scaffold the spec chain for one object
make check                     # contracts, traceability, naming (also runs after every edit)
make ready OBJ=fct_x           # the one answer to "is this ready?"
make test                      # unit tests, JUnit evidence in reports/
make validate                  # databricks bundle validate -t dev; test/prod deploy through CI only
```

Layout: `docs/00-brd → 10-contract → 20-impl-spec` (the spec chain) · `docs/30-decisions` ADRs · `docs/40-modernization` · `docs/50-incidents` · `docs/60-runbooks` · `src/pipelines/<bronze|silver|gold>/<object>.(py|sql)` · `resources/<object>.(job|pipeline).yml` (templates in `resources/_templates/`) · `scratch/` is the only place the exploration layer writes.

## Repository-specific context

- One published object: `prod.sales_gold.fct_daily_order_revenue` (Tier 2). Consumers are listed in contract §10.
- Both inputs belong to other teams. `int_orders` belongs to sales-platform and `dim_customer` to crm-platform, and their contracts live in those repos. The versions this repo relies on are pinned in impl spec §7. A change upstream re-opens our contract.
- Revenue is integer cents, USD, before tax. Days are UTC. Tests pin the process to UTC (`tests/conftest.py`).
- The training workspace has **no system-table access**. For incidents, platform evidence is provided as files under `docs/50-incidents/_evidence/<incident>/`, each named for the query it stands in for. Read those instead of running Databricks queries.
