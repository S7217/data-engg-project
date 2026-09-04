# Placement and Containment

*Harness standard · S2 · owner: see `OWNERS.md`*

Two questions: **where does each piece of guidance live**, and **what is the agent *able* to do**?

---

## Placement: the ladder

*"What can you move out of the live conversation?"*

| Rung | Holds | Here |
|---|---|---|
| **CLAUDE.md** | permanent constraints | repo `CLAUDE.md` (`claude-md-standard.md`) |
| **Commands** | instructions you stopped retyping | `Makefile` targets (`make new`, `make check`, `make ready`) |
| **Skills** | knowledge you stopped repasting | `.claude/skills/`: `design-spec`, `gate`, `behaviour-recovery`, `incident` |
| **Hooks** | checks you stopped remembering | `.claude/hooks/`: guard, code gate, check-on-edit, session start |
| **Subagents** | investigations you stopped letting pollute the session | `.claude/agents/`: `acceptance-verifier`, `lineage-impact-reviewer`, `dq-reviewer`, `rca-investigator` |
| **Worktrees** | streams you stopped letting collide | `git worktree` / Claude Code worktree sessions, one per independent change |
| **Connectors** | the one thing you deliberately pull **in** | authorised per `connector-authorisation.md` |

### The three trigger rules

> **Third time you type it → it becomes a command.**
> **Third time you paste it → it becomes a skill.**
> **Third time it gets violated → it becomes a hook.**

*CLAUDE.md asks. Hooks guarantee.* A rule that keeps getting violated isn't a discipline problem. It's a placement error.

### The decision

Passes all three earn-in gates → **CLAUDE.md**. Fails *stable* → session context. Retyped instruction → **command**. Procedure plus reference material → **skill**. Repeatedly violated → **hook**. Bounded investigation that would flood context → **subagent**. Two independent streams → **worktree**. Lives in another system → **connector**.

**Don't rebuild what the platform ships.** Reference a Databricks or Claude Code capability where one exists, and add only the discipline around it.

---

## Containment: trusted versus able

**What the agent is trusted to do** is a judgement, revisited per task and held in your head. **What the agent is able to do** is a configuration, enforced the same whether you're watching or not.

> *"Approving every action is not containment. It is attendance."*

### Two profiles, not one setting

The stable `.claude/settings.json` holds the hooks and the always-on deny rules. Never swap it out. A **permission layer** ("profile" is our word; it's a settings file applied at launch) is merged on top:

```bash
harness/tools/claude-layer.sh exploration    # = claude --settings .claude/perms/exploration.json
harness/tools/claude-layer.sh delivery
```

*You switch profile when the task changes, not when you remember to.* The session-start hook tells the agent (and you) when no layer is active.

| | **Exploration** | **Delivery** |
|---|---|---|
| Is | read-heavy, sandboxed, no writes outside a scratch path, no network | explicit allowlist, no destructive commands, nothing prod-adjacent, gated |
| Use for | understanding a repo, questions, impact assessment | any session that saves something: specs, code, tests, recovery records, incident records |
| Starts in | plan mode. Plan mode stops writes; this layer adds the credential and egress denies, and keeps holding after you approve a plan | default mode |
| Writes | `scratch/` only | `src/`, `tests/`, `resources/`, `docs/`, `scratch/`. Pipeline code only past the code gate |
| Never writes | — | `harness/`, `.claude/` (harness changes go through the central harness) |
| Databricks | read-only CLI (list/get), `bundle validate` | same, plus `bundle deploy/run -t dev` |
| Egress | `curl`, `wget`, WebFetch denied | same |

Reviewer subagents are read-only by their **tool list**, whichever layer the session runs: `acceptance-verifier` and `dq-reviewer` have no Bash; `lineage-impact-reviewer` and `rca-investigator` have Bash for read-only queries, with the guard hook as backstop.

### The credential rule: now enforced, not just stated

> **"Your Claude API key lives in a Databricks secret scope, referenced at runtime. Never in CLAUDE.md. Never in a committed file. Never pasted into a prompt."** *(S1, ratified)*

**A rule stated is a rule violated. A rule in the profile is a rule enforced.** Always on, in every layer (`settings.json` + `hooks/guard_bash.py`):

- Reads of `.env`, `.env.*`, `secrets/`, `~/.databrickscfg` denied, and also matched in Bash and Python commands, because Read-deny rules cover the Read tool only.
- Writes to `.env*`, `secrets/`, `*.pem` and `*credentials*` denied. No secret get/put through the CLI.
- No deploy, run or destroy against **prod**, and no `bundle destroy` at all.
- No `DROP`, `TRUNCATE`, `DELETE FROM`, `RESTORE`, `VACUUM`, `GRANT`, `REVOKE` or `OWNER TO` executed by the agent. Write it into a reviewed migration; a human or CI runs it.
- No governed-tag writes. Agents **propose** in contract §9, and stewards apply.
- No force-push. A raw `databricks api` mutating call asks the user.
- No pipeline code before a gated contract (`hooks/gate_code.py`).
- After edits to contracts, specs or models, the matching check runs and the agent gets the first few failures.

**Right shape, not yet the right place.** These denies live in the project, so a user can remove them. Credential denies belong in **managed settings** (enterprise policy), where no project or user file can override them. Moving them there is a Platform action before this goes to production.

### Prove it

With **delivery** active: (1) ask the agent to write a file outside the working tree; (2) ask it to read a credentials file. **That refusal is the artefact. If you can't make it refuse, you haven't configured anything.** Outside-tree writes always ask for approval in Claude Code (nothing in the layers allows them). Turning that into a hard refusal needs managed settings or the sandbox. Verify against current Claude Code documentation.

## The agent's identity

The agent acts as **whoever's credentials the CLI uses**:
- Interactive work uses the engineer's own identity against **dev** only, ideally a dev-only profile (`DATABRICKS_CONFIG_PROFILE=dev`).
- Nothing the agent runs uses a production service principal. Prod runs as the bundle's `prod` `run_as`, triggered by CI.

## Changing a layer

A permission rule is a governance change: change it in the central harness, give the reason in `CHANGELOG.md`, and roll it out with `install.sh --upgrade`. Personal extras go in `.claude/settings.local.json` (never committed), not the shared layers.
