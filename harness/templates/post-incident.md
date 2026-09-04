# Post-Incident Review: <short title>

*v0: drafted ahead of Session 7. Re-align after delivery.*

*Harness template · S7 · copy to `docs/50-incidents/<yyyy-mm-dd>-<slug>.md` · see `standards/incident-and-rollback.md`*

Blameless and evidence-led. Every causal statement has a status and evidence behind it.

| | |
|---|---|
| **Incident ID** | |
| **Severity** | SEV1 consumers misled or data exposed · SEV2 published data late/wrong, contained · SEV3 internal only |
| **Objects affected** | `catalog.schema.object` (tier) |
| **Detected at / by** | timestamp UTC · DQ rule / consumer / monitor |
| **Resolved at** | |
| **Technical owner** | |
| **Business owner** | |
| **Status** | investigating · mitigated · resolved · review complete |

---

## 1 · Impact
Who saw what wrong data, for how long, and which decisions may have used it. *Business owner completes this.*

## 2 · Timeline (UTC)

| Time | Event | Source |
|---|---|---|
| | last known good | job run / table version |
| | change deployed | git sha, bundle deploy |
| | first known bad | |
| | detected | |
| | mitigated / rolled back | |

## 3 · Root cause

| # | Hypothesis | Status | Evidence for | Evidence against / eliminated by |
|---|---|---|---|---|
| H1 | | `OBSERVED` / `INFERRED` / `UNKNOWN` | | |
| H2 | | | | |

**Root cause (one sentence):**
**Why it wasn't caught earlier (which control was missing or bypassed):**

## 4 · Rollback / remediation

| | |
|---|---|
| Rollback criteria met | R1 · R2 · R3 · R4 · none (fixed forward, because…) |
| Action taken | redeploy version … · `RESTORE TABLE … VERSION AS OF …` · quarantine · halt |
| Executed by | |
| Verified by | the check that proves it worked |
| Restatement decision | none needed · restated · declined. Decided by |
| Consumers notified | who · when |

## 5 · If an agent was involved

| | |
|---|---|
| What it was asked | |
| What context it had (and lacked) | |
| What it produced | |
| **Why that output looked plausible** | |
| Which control should have caught it | |

## 6 · Actions and regression assets

| # | Action | Type | Owner | Due | Done |
|---|---|---|---|---|---|
| A1 | | **regression asset** (test · DQ rule · golden case · guard rule · CLAUDE.md line) | | | |
| A2 | | process / standard change | | | |

At least one regression asset is mandatory. Copy the failure into `registers/failure-library.md` in the central harness.
