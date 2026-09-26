# Tracker: github

The work items are GitHub Issues of `forge.repo`. Sub-issues give the child items.
Labels give the status.

## Tools, in order

1. `gh`, the GitHub CLI. Check with `gh auth status`.
2. A GitHub MCP server, if the harness has one connected. Use its issue tools with the
   same fields as below.
3. The REST API with `GITHUB_TOKEN`, through `curl -H "Authorization: Bearer $GITHUB_TOKEN"`.

The examples use `gh`. Run them in the repository directory.

## Status labels

The status is a label with the exact name from `tracker.statuses`, for example
`In Progress`. Create a missing label once:

```bash
gh label create "In Progress" --color 0E8A16 --description "sdlc-crew status" --force
```

Setting a status removes the other status labels of the item.

## Operations

### Read

```bash
gh issue view <number> --json number,title,body,labels,assignees,comments,url,state
gh api "repos/{owner}/{repo}/issues/<number>/sub_issues" --jq '.[] | {number, title, state}'
```

The parent, if any, is in the body as `Parent: #<n>`, or is the issue whose
sub-issues list holds this number. Read linked issues that the body names with `#<n>`.

### Create

```bash
gh issue create --title "<summary>" --body-file "$RUN_DIR/issue-body.md" \
  --label "<tracker.statuses.todo>"
```

The body holds **Why**, **Acceptance criteria**, and **Definition of done**, in that
order. The command prints the URL. The number is the last path segment.

### Create child

Create the issue as above with the line `Parent: #<parent>` at the top of the body.
Then add it as a sub-issue. The API needs the issue `id`, not the number:

```bash
CHILD_ID=$(gh api "repos/{owner}/{repo}/issues/<child-number>" --jq '.id')
gh api --method POST "repos/{owner}/{repo}/issues/<parent-number>/sub_issues" \
  -F sub_issue_id="$CHILD_ID"
```

If the sub-issue call fails, keep the `Parent:` line and continue. Record the output.

### Comment

```bash
gh issue comment <number> --body-file "$RUN_DIR/<file>.md"
```

### Set status

```bash
gh issue edit <number> --add-label "<new status>" --remove-label "<old status>"
```

If `forge.assign_to_me` is true and the status is `in_progress`, also run
`gh issue edit <number> --add-assignee @me`.

### Link PR

Put `Closes #<number>` in the pull request body. GitHub links the two and closes the
issue on merge. For a child issue, use `Closes #<child>` and `Part of #<parent>`.
