# Tracker: jira

The work items are Jira issues in the project `tracker.project` on the site
`tracker.url`. Jira calls them work items or issues. Both words mean the same thing
here.

## Tools, in order

1. `acli`, the Atlassian CLI. Check with `acli jira auth status`.
2. `jira`, the community JiraCLI by ankitpokhrel. Check with `jira me`.
3. A Jira or Atlassian MCP server, if the harness has one connected.
4. The REST API v3 with `curl`:
   - Jira Cloud: `-u "$JIRA_EMAIL:$JIRA_API_TOKEN"`.
   - Jira Server or Data Center: `-H "Authorization: Bearer $JIRA_PAT"`, and API v2.

The examples show `acli` first and `jira` second. Use the one that is installed.

## Operations

### Read

```bash
acli jira workitem view <KEY> --fields '*all' --json
jira issue view <KEY> --comments 20
```

Read the summary, the description, the acceptance criteria, the comments, the issue
type, the parent, the linked issues, and the attachment names. If the issue has a
parent or linked issues, read them too.

REST: `GET <tracker.url>/rest/api/3/issue/<KEY>?expand=renderedFields&fields=*all`.

### Create

```bash
acli jira workitem create --project <PROJECT> --type Task --summary "<summary>" \
  --description "$(cat "$RUN_DIR/issue-body.md")"
jira issue create --type Task --summary "<summary>" --body "$(cat "$RUN_DIR/issue-body.md")" --no-input
```

The description holds **Why**, **Acceptance criteria**, and **Definition of done**.

### Create child

```bash
acli jira workitem create --project <PROJECT> --type "<tracker.child_issue_type>" \
  --parent <PARENT-KEY> --summary "<summary>" --description "<acceptance criteria>"
jira issue create --type "<tracker.child_issue_type>" --parent <PARENT-KEY> \
  --summary "<summary>" --body "<acceptance criteria>" --no-input
```

If the project has no issue type with that name, read the name of the child type from
the error output, for example `Sub-task`, and try again with that name. Tell the
person to put the working name in `tracker.child_issue_type`.

Before you create a child, list the existing children of the parent. A child with the
same summary exists from an earlier run. Use it again. Do not create a duplicate.

### Comment

```bash
acli jira workitem comment create --key <KEY> --body-file "$RUN_DIR/<file>.md"
jira issue comment add <KEY> "$(cat "$RUN_DIR/<file>.md")"
```

### Set status

```bash
acli jira workitem transition --key <KEY> --status "<status>" --yes
jira issue move <KEY> "<status>"
```

Compare status names without case. If the transition fails, show the output to the
person and ask which status to use, or whether to skip the transition. Do not stop the
workflow for a failed transition.

### Link PR

Add a comment with the pull request URL. If the Jira site has the GitHub, GitLab, or
Bitbucket integration, put the issue key in the branch name and the pull request
title, which is what `forge.branch_pattern` does by default, and the integration
links the two.
