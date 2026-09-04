# Connector Authorisation

*Harness standard · S3 · owner: see `OWNERS.md` · reviewed by Security*

A connector (an MCP server, a Claude Code plugin, a vendor skill, any tool that reaches outside the repository) widens what the agent can see and do. Each one is authorised once, recorded, and reviewed.

---

## Classes

| Class | Reaches | Example | Approval |
|---|---|---|---|
| **A**: read-only, internal metadata | catalogue metadata, lineage, docs | Databricks `databricks-unity-catalog` skill against dev; internal wiki read | Engineer lead |
| **B**: read-only, data | table contents, query results, logs | SQL warehouse query tool; observability read | Engineer lead + Steward for the data's domain |
| **C**: write, internal | tickets, PR comments, dev workspace objects | issue tracker, Git hosting | Engineer lead + Platform |
| **D**: write to governed or external surfaces | prod objects, tags, grants, external messaging, third-party SaaS | anything that publishes or notifies outside the team | Platform + Security + publication authority. **Default: not authorised** |

## The inversion

Everything else on the ladder moves things *out* of the conversation. A connector pulls something *in*, and charges for it before the first call: its schemas load into context on every request.

## The seven questions (S2)

Answer all seven in writing before a connector is authorised. Questions 8–10 are the harness additions.

| # | Question | Must be |
|---|---|---|
| 1 | **Does it need access?** | a task that can't be done by pasting or a one-off export |
| 2 | **What can it read?** | the narrowest scope that works, written down |
| 3 | **What can it change?** | nothing, unless the task requires it, and then written down |
| 4 | **Under whose identity?** | a scoped identity; never a personal admin token, never prod |
| 5 | **Can we audit it?** | its calls show up in an audit log someone reads |
| 6 | **Can we undo it?** | revocation in one step, and any write reversible |
| 7 | **What happens when it fails?** | a failure mode you can describe, and that fails closed |
| 8 | Is the source pinned to a version, and who maintains it? | named, pinned |
| 9 | Can its tool descriptions or outputs carry instructions into the agent's context? | treated as untrusted input; its write tools never auto-approved |
| 10 | Which permission layer may use it? | exploration, delivery or neither |

**When not to use a connector:** one-off lookups · anything you can paste · anything whose failure mode you can't describe.

## The register

Record each authorised connector here. A connector not in this table isn't authorised.

| Connector | Version | Class | Identity | Scope (read / write) | Layers | Approved by | Date | Review by |
|---|---|---|---|---|---|---|---|---|
| Databricks CLI | ≥ 1.0 | A/B | engineer's own, dev profile | read: metadata, dev data · write: dev bundle only | exploration, delivery | Platform | | |
| `databricks-unity-catalog` skill (databricks/databricks-agent-skills) | pin on install | A | engineer's own, dev profile | read: system tables, lineage | exploration | Platform | | |

## Rules

- **Pin versions.** An unpinned connector can change behaviour under you between sessions.
- **Write tools are never auto-approved.** Leave them out of the `allow` lists in `.claude/perms/`.
- **Review every 6 months**, or immediately after the connector changes publisher, scope or identity.
- A connector involved in an incident is suspended until the post-incident review closes.
