# order_revenue

Databricks bundle project created from the harness project template. **S7 demo:** one gated Tier 2 object, `fct_daily_order_revenue`, built through the full spec chain, plus an open incident (`docs/50-incidents/_evidence/2026-09-29-revenue-up/`).

```bash
uv sync                                       # dev dependencies (pytest, pyspark, ruff)
harness/tools/claude-layer.sh exploration     # or: delivery
make help
```

| Path | Holds |
|---|---|
| `docs/00-brd` → `10-contract` → `20-impl-spec` | the spec chain: requirement → gated contract → implementation spec |
| `docs/30-decisions` | ADRs (`harness/templates/adr.md`) |
| `docs/40-modernization` | behaviour recovery, parity contracts |
| `docs/50-incidents`, `docs/60-runbooks` | post-incident reviews, runbooks |
| `src/pipelines/<layer>/` | models; start from `src/pipelines/_templates/model.py.tmpl` |
| `resources/` | bundle resources; start from `resources/_templates/` |
| `tests/unit`, `tests/golden` | transformation tests, golden data |
| `harness/` | the installed harness. Don't edit it here; upgrade from the central harness |
