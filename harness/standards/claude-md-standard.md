# CLAUDE.md Standard

*Harness standard · S1 · owner: see `OWNERS.md`*

A context layer is something you maintain, not something you write once. Every line in CLAUDE.md is paid for on every call, before the agent has read a single line of code.

## The earn-in test

A line belongs in CLAUDE.md only if it passes all three gates.

| Gate | The question | If it fails |
|---|---|---|
| **Stable** | Will this still be true in three months? | It is session context, not repository context |
| **Project-specific** | Would this be untrue of another repository? | The model already knows it, or it belongs in the organisation layer |
| **Violated when absent** | Does the agent actually get it wrong without this line? | Remove it. Run the task. See what happens |

Passes all three: it goes in CLAUDE.md. Fails any of them: it's a skill, a command, a hook or session context (see `placement-and-containment.md`).

Gate three is the one people skip. Removing a line and watching what happens is the only evidence that the line was doing any work.

## The one rule ratified in S1

> **"Your Claude API key lives in a Databricks secret scope, referenced at runtime. Never in CLAUDE.md. Never in a committed file. Never pasted into a prompt."**

CLAUDE.md is committed and loaded into context on every call, so a credential in it is a credential everywhere. The rule is enforced by the permission layers (`placement-and-containment.md`), not just stated.

## Bloat is duplication, not length

> A 200-line CLAUDE.md that says only what the repo can't tell you is lean.
> A 40-line one that restates the directory structure is bloated.

| Anti-pattern | What it looks like |
|---|---|
| README copy | Paragraphs pasted from the README. The agent can read the README |
| Generic best practice | "Write clean, maintainable code". True everywhere, so useful nowhere |
| Kitchen sink | Everything anyone might need, added by several people and removed by none |
| Aspirational rules | Standards nobody enforces in review. The agent follows them and the codebase doesn't |
| **Stale rules** | Worse than a missing rule. The agent follows it confidently, and people stop reading the file because they no longer trust it |

## What usually earns its place in a data repository

- Where the authoritative sources are, when the obvious name is wrong (`the "orders" view is deprecated; use fct_orders`)
- Grain and keys of the tables people get wrong
- Quirks of source systems: late-arriving data, soft deletes, timezone traps, reused IDs
- Which directories are generated and must not be edited
- Which commands actually validate a change here (`make check`, `databricks bundle validate -t dev`)
- What the agent must **not** decide, and who does decide it (stewards, the publication authority)

## Two layers

| Layer | Scope | Holds | Lives in |
|---|---|---|---|
| Organisation | Every repository | Rules true everywhere here and nowhere else | `harness/standards/`, imported by reference |
| Repository | One repository | Conventions, quirks, generated directories, where the real docs live | the repo's `CLAUDE.md` |

The repository CLAUDE.md **points to** the harness standards and doesn't paste them. A pasted standard goes stale the day the original changes.

## Maintenance

- Owned by the repository owner. Changes to it are reviewed like code.
- Review it whenever an incident or gate finding traces back to missing or wrong context. That finding goes into the failure library, and the fix goes here.
- Once a quarter, run gate three: remove a suspect line, rerun a representative task, keep the line only if the result got worse.

Start from `templates/CLAUDE.md`.
