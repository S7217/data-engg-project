# Naming Conventions

*Harness standard · S4 · owner: see `OWNERS.md` · enforced by `tools/lint_naming.py`*

Every rule comes with its reason. A bare rule gets dropped the moment a case looks slightly different, but a rule with a reason tells you when an exception is justified.

## Objects

| Rule | Reason | Check |
|---|---|---|
| Layer prefix: `stg_` (bronze), `int_` / `dim_` (silver), `dim_` / `fct_` (gold) | The layer tells you the contract strength at a glance | N1 |
| `snake_case` everywhere: tables, columns, files | Case-sensitivity differs between engines; one form makes grep and tooling reliable | N3 |
| Every `dim_` / `fct_` model states its grain on **line 1**: `-- grain: one row per subscription per month` | Grain is the contract, not metadata. Line 1 is where a reviewer can't miss it | N2 |
| Quarantine tables: `<object>_quarantine` in the same schema's quarantine counterpart | Bad rows stay next to what they failed | — |
| Model file name = table name | One name to search for | — |

## Columns

| Rule | Reason | Check |
|---|---|---|
| Money: `_cents`, stored as integer (`BIGINT`) | Integers don't drift through floating-point rounding. Round for display in the presentation layer | N6 |
| Currency travels with money: `<name>_currency_code` (ISO 4217) when more than one currency is possible | A number without a currency is a guess | — |
| Timestamps: `_at`, always UTC | A timestamp without a zone is wrong somewhere | N4 |
| Dates (no time): `_date` | Distinguishes a calendar day from an instant | N4 |
| Booleans: `is_` / `has_` | Reads as a question; unambiguous in filters | N5 |
| Foreign / natural keys: `<entity>_id` | Joins become obvious | — |
| Surrogate keys: `<entity>_sk` | Never confused with a business key | — |
| Counts `_count`, ratios `_rate` / `_pct` | Unit in the name | — |
| No abbreviations outside the approved list | `cst` means customer, cost or Central Standard Time | — |

**Approved abbreviations:** `id`, `sk`, `sla`, `kpi`, `mrr`, `arr`, `dq`, `scd`, `cdc`, `utc`, `etl`, `api`, `url`, `iso`, plus any glossary term marked `abbreviation_approved: true`.

## When legacy names win

During modernization, a target column may keep a legacy name if the parity contract says consumers depend on it (`MUST_MATCH`). Record it as a §14 deviation in the implementation spec and add a column comment pointing to the parity contract. Never rename silently, and never keep a non-conforming name silently either.

## Changing a rule

Change this file and the constants at the top of `tools/lint_naming.py` **in the same commit**. A standard the checker doesn't enforce turns into an aspirational rule.
