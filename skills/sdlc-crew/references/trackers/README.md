# Tracker references

Each file in this directory tells the crew how to do the same six operations with one
tracker. The orchestrator reads `tracker.kind` from `.sdlc-crew.yaml` and follows the
matching file. A persona never calls a tracker tool that its tracker file does not
name.

| Operation | Meaning |
|---|---|
| Read | Get the summary, the description, the acceptance criteria, the comments, the parent, and the links of a work item. |
| Create | Make a new work item from a plain-language description. Return its ID. |
| Create child | Make a child work item under a parent. Return its ID. |
| Comment | Add a comment to a work item from a file. |
| Set status | Move a work item to a status from `tracker.statuses`. |
| Link PR | Record the pull request URL on the work item. |

Rules for every tracker:

- Use the tools in the order that the file gives: the official CLI first, then an MCP
  server if the harness has one connected, then the REST API with a token from an
  environment variable. Do not skip to REST when the CLI is installed.
- Read a token from the environment only. Never print a token. Never write a token to
  a file in the repository.
- If an operation fails, stop that operation and return `STATUS: BLOCKED` with the
  command and the output. Do not retry with a different tool unless the file says so.
- A status name comes from `tracker.statuses`. If the tracker does not have that
  status, list the statuses that it has and ask the person which one to use.
- Write every comment in Simplified Technical English, for a reader who did not see
  the code.
