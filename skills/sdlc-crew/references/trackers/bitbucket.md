# Tracker: bitbucket

The work items are issues of the Bitbucket Cloud issue tracker of the repository
`tracker.project` in the form `workspace/repo`. The issue tracker must be enabled in
the repository settings. Many Bitbucket users track work in Jira instead. If the
person uses Jira, set `tracker.kind: jira` and `forge.kind: bitbucket`.

## Tools, in order

1. A Bitbucket MCP server, if the harness has one connected.
2. The REST API 2.0 with `curl -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD"`.

Bitbucket has no official CLI. The examples use the REST API. `BASE` is
`https://api.bitbucket.org/2.0/repositories/<workspace>/<repo>`.

## Status

Bitbucket issue states are fixed: `new`, `open`, `resolved`, `on hold`, `invalid`,
`duplicate`, `wontfix`, `closed`. Map the config statuses to them:

| `tracker.statuses` | Bitbucket state |
|---|---|
| `todo` | `new` |
| `in_progress` | `open` |
| `in_review` | `open`, plus a comment "Ready for review: <PR URL>" |
| `done` | `resolved` |

## Operations

### Read

```bash
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" "$BASE/issues/<id>"
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" "$BASE/issues/<id>/comments"
```

The parent, if any, is in the description as `Parent: #<id>`.

### Create

```bash
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" -X POST \
  -H "Content-Type: application/json" "$BASE/issues" \
  --data "$(jq -n --arg t "<summary>" --rawfile c "$RUN_DIR/issue-body.md" \
    '{title: $t, kind: "task", priority: "major", content: {raw: $c}}')"
```

The response holds the `id`.

### Create child

Same as Create, with `Parent: #<parent>` at the top of the description.

### Comment

```bash
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" -X POST \
  -H "Content-Type: application/json" "$BASE/issues/<id>/comments" \
  --data "$(jq -n --rawfile c "$RUN_DIR/<file>.md" '{content: {raw: $c}}')"
```

### Set status

```bash
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" -X PUT \
  -H "Content-Type: application/json" "$BASE/issues/<id>" \
  --data '{"state": "<bitbucket state>"}'
```

### Link PR

Add a comment with the pull request URL. Put `#<id>` in the pull request description.
