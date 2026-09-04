#!/usr/bin/env python3
"""PreToolUse guard for Bash. Blocks what no permission layer should let an agent do.

BLOCK (exit 2, reason returned to the agent):
  - deploy / run / destroy against prod (-t prod*, --target=prod*, *BUNDLE_TARGET=prod*); any bundle destroy
  - executed SQL that is destructive or changes privilege: DROP, TRUNCATE, DELETE FROM, RESTORE, VACUUM,
    GRANT, REVOKE, ALTER ... OWNER TO
  - governed-tag writes (SET/UNSET TAGS, tag-assignment APIs): agents propose tags, stewards apply
  - permission / grant changes through the Databricks CLI
  - reading or writing secrets and credential files (shell or python)
  - force-push (--force, -f, +refspec); rm -rf on /, ~, $HOME, . or ./
ASK (the user decides): raw `databricks api` mutating calls, which can carry any SQL or change.

SQL patterns are skipped when the command only *reads text*: grep/rg/cat/head/tail/less/sed -n/awk,
git log/show/diff/grep/commit. Searching legacy SQL for "DROP TABLE" is behaviour recovery, not a drop.

A human who needs a blocked command runs it themselves (prefix `!` in Claude Code) or through CI.
Defence in depth. The permission layers are the first line. Note: Read-deny rules in settings
cover the Read tool only, not Bash. That's why credential reads are also matched here.
"""

import json
import re
import sys

I = re.IGNORECASE | re.DOTALL

TEXT_ONLY = re.compile(
    r"^\s*(grep|egrep|rg|ag|cat|head|tail|less|more|wc|awk|sed\s+-n|git\s+(log|show|diff|grep|blame|commit))\b", I)

ALWAYS = [
    (r"(databricks\s+bundle\s+(deploy|run|destroy)\b.*(-t|--target)[\s=]+[\"']?prod\w*)|(BUNDLE_TARGET=[\"']?prod\w*.*databricks\s+bundle)",
     "Prod deploys and runs go through CI or a human, never the agent (standards/automation-standard.md)."),
    (r"databricks\s+bundle\s+destroy\b",
     "bundle destroy deletes deployed resources. A human runs it."),
    (r"databricks\s+(entity-tag-assignments|tag-policies)\s+(create|update|delete)",
     "Governed tags are propose-only for agents (standards/classification-taxonomy.md)."),
    (r"databricks\s+(grants|permissions)\s+(update|set)\b",
     "Permission changes belong in the bundle definition or the UC operating model process."),
    (r"databricks\s+secrets\s+(get-secret|put-secret|delete-secret|put-acl)",
     "Agents do not read or write secrets."),
    (r"(\.databrickscfg|(^|[\s/'\"])\.env(\.\w+)?([\s'\")]|$)|/secrets/)",
     "Agents do not read credential files: .env, .databrickscfg, secrets/."),
    (r"\bgit\s+push\b.*(\s--force\b|\s-f\b|--force-with-lease|\s\+\S+)",
     "No force-push from the agent."),
    (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*\s+(/|~|\$HOME|\.|\./)(\s|$)",
     "Recursive delete of a root, home or the repository."),
]

SQL = [
    (r"\bDROP\s+(TABLE|VIEW|SCHEMA|CATALOG|DATABASE|VOLUME|FUNCTION|MATERIALIZED\s+VIEW)\b",
     "Destructive DDL. Write it into a reviewed migration file instead of executing it."),
    (r"\bTRUNCATE\s+TABLE\b|\bDELETE\s+FROM\b",
     "Destructive DML. Write it into a reviewed migration file instead of executing it."),
    (r"\bRESTORE\s+(TABLE\s+)?\S+\s+TO\s+(VERSION|TIMESTAMP)\b",
     "RESTORE is a rollback. A human or CI executes it (standards/incident-and-rollback.md)."),
    (r"\bVACUUM\b",
     "VACUUM removes the history that rollback depends on. A human or CI runs it."),
    (r"\b(GRANT|REVOKE)\s+[\w\s,]+\bON\b",
     "Privilege changes belong in the bundle definition or the UC operating model process (standards/uc-operating-model.md)."),
    (r"\bALTER\s+.*\bOWNER\s+TO\b",
     "Ownership changes are a governance decision (standards/uc-operating-model.md)."),
    (r"\b(SET|UNSET)\s+TAGS?\b",
     "Governed tags are propose-only for agents. Write the proposal into contract §9 for the steward to apply."),
]

ASK = [
    (r"databricks\s+api\s+(post|put|patch|delete)\b",
     "Raw Databricks API call that can change state or execute SQL. Confirm it's read-only and dev-only."),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    cmd = (payload.get("tool_input") or {}).get("command", "")
    text_only = TEXT_ONLY.match(cmd) and not re.search(r";|&&|\|\||\$\(|`", cmd)  # no chaining
    rules = ALWAYS + ([] if text_only else SQL)
    for pattern, reason in rules:
        if re.search(pattern, cmd, I):
            print(f"BLOCKED by harness guard: {reason}\nCommand: {cmd[:200]}", file=sys.stderr)
            return 2
    for pattern, reason in ASK:
        if re.search(pattern, cmd, I):
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                     "permissionDecision": "ask",
                                                     "permissionDecisionReason": f"Harness guard: {reason}"}}))
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
