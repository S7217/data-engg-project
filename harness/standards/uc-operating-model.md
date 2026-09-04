# Unity Catalog Operating Model

*Harness standard · S3 · owner: see `OWNERS.md` · reviewed by Steward*

How catalogs, schemas, ownership, privileges and identities are arranged, so that every object an agent helps create has a known place, owner and boundary **before** it exists.

---

## 1 · Environments are catalogs

| Catalog | Purpose | Who writes | Agent access |
|---|---|---|---|
| `dev` | Engineering work, one schema per engineer or per feature | engineers, interactively | read + write, as the engineer |
| `test` | Integration, reconciliation, golden-data runs | the `test` service principal via CI | read |
| `prod` | Published data | the `prod` service principal via CI only | read, **metadata-only** unless the delivery envelope says otherwise |
| `sandbox` | Throwaway exploration | anyone | read + write |

If your workspace uses a different catalog layout (for example one catalog per domain, with an environment suffix), map it here once, and keep the bundle variable `catalog` per target aligned with it.

## 2 · Schemas are domain × layer

`<catalog>.<domain>_<layer>`: for example `prod.finance_gold`, `prod.finance_silver`, `prod.crm_bronze`.

| Layer | Holds | Prefix |
|---|---|---|
| bronze | Raw landing, source-shaped, append-only | `stg_` |
| silver | Cleaned, conformed, deduplicated entities | `int_`, `dim_` |
| gold | Published facts and dimensions for consumption | `dim_`, `fct_` |
| quarantine | Rows failing DQ rules with a `quarantine` disposition | `<object>_quarantine` |

## 3 · Ownership

- Every catalog, schema and published table is **owned by a group**, never a person and never a service principal. Ownership survives people leaving.
- The owning group is the one accountable for the object's contract (contract §10).
- Ownership transfer is a governance change: a decision record, not an `ALTER ... OWNER TO` run by an agent.

## 4 · Privileges

| Principal | dev | test | prod |
|---|---|---|---|
| Engineers (group) | ALL on their schemas | SELECT | SELECT on non-restricted; none on `restricted` |
| CI service principal per env | — | MODIFY on its catalog | MODIFY on its catalog |
| Consumers (group per domain) | — | — | SELECT on gold schemas they're granted |
| Stewards (group per domain) | SELECT | SELECT | SELECT + APPLY TAG on their domain |

Grants are expressed **in the bundle definition** (`permissions:` / `grants:` on the resource) or in the platform's grant automation, never executed ad hoc. The guard hook blocks agent-executed `GRANT`/`REVOKE`.

## 5 · Governed tags and ABAC

- The tag vocabulary is defined in `classification-taxonomy.md`. Tags outside it aren't governed tags.
- The policy-driving tag (`sensitivity` in v0) drives row filters and column masks through ABAC policies. Changing such a tag changes who can see data, so it's a **Tier 3** change.
- Agents **propose** tags (contract §9). A steward applies them. Column-level tags are a known v0 gap; impl spec §1 `Class.` records a column that may need one, as a proposal.

## 6 · Agent identities

- Interactive: the engineer's identity, dev only (see `placement-and-containment.md`).
- Automated (CI, jobs): one service principal per environment, named in the bundle target's `run_as`.
- No service principal is shared between environments. No agent session ever holds a prod credential.

## 7 · The delivery envelope

Nine facts must be known **before** an object is created. They're recorded in contract §13, or standalone in `templates/delivery-envelope.yaml`:

placement · ownership · classification · human access · agent data access · agent mutation rights · tag authority · identity per environment · publication approval.

An object without a completed envelope isn't ready to build. `contract_check.py` enforces this at tier 2–3.

## 8 · Lifecycle

| Event | Requires |
|---|---|
| New published object | gated contract + delivery envelope |
| Change to a published object | `lineage-impact-reviewer` assessment + re-gated contract if meaning changes |
| Deprecation | impact assessment, consumer notification (contract §10), a deprecation date tagged on the object |
| Drop | after the deprecation date, by a human, through a reviewed migration |
