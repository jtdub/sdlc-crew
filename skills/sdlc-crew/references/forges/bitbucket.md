# Forge: bitbucket

Bitbucket Cloud has no official CLI. Use a Bitbucket MCP server if the harness has one
connected. Otherwise use the REST API 2.0 with
`curl -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD"`. `BASE` is
`https://api.bitbucket.org/2.0/repositories/<workspace>/<repo>`.

## Operations

### Identify

Read `workspace/repo` from the `origin` remote URL. Read the default branch:

```bash
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" "$BASE" | jq -r '.mainbranch.name'
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" https://api.bitbucket.org/2.0/user | jq -r '.username'
```

### Open PR

```bash
git push -u origin HEAD
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" -X POST \
  -H "Content-Type: application/json" "$BASE/pullrequests" \
  --data "$(jq -n --arg t "<ID>: <summary>" --arg s "$BRANCH" --arg d "$BASE_BRANCH" \
    --rawfile b "$RUN_DIR/pr-body.md" \
    '{title: $t, draft: true, source: {branch: {name: $s}}, destination: {branch: {name: $d}}, description: $b}')"
```

The response holds the `id` and `links.html.href`. If the API rejects the `draft`
field, create the pull request without it, and put `Draft:` at the start of the title.

### Update PR

```bash
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" -X PUT \
  -H "Content-Type: application/json" "$BASE/pullrequests/<id>" \
  --data "$(jq -n --rawfile b "$RUN_DIR/pr-body.md" '{description: $b}')"
```

### Comment PR

```bash
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" -X POST \
  -H "Content-Type: application/json" "$BASE/pullrequests/<id>/comments" \
  --data "$(jq -n --rawfile c "$RUN_DIR/<file>.md" '{content: {raw: $c}}')"
```

### Read comments

Read every page. Follow the `next` URL until the response has none:

```bash
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" "$BASE/pullrequests/<id>/comments?pagelen=100" \
  | jq '.values[] | select(.deleted | not)
        | {id, parent: .parent.id, user: .user.display_name, body: .content.raw,
           path: .inline.path, line: .inline.to, resolved: (.resolution != null)}'
```

A comment with no `parent` starts a thread. Group the replies under it. Keep the
threads whose first comment is not resolved.

### Reply comment

```bash
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" -X POST \
  -H "Content-Type: application/json" "$BASE/pullrequests/<id>/comments" \
  --data "$(jq -n --rawfile c "$RUN_DIR/<file>.md" --argjson p <comment id> '{content: {raw: $c}, parent: {id: $p}}')"
```

### Resolve thread

Use the `id` of the first comment of the thread:

```bash
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" -X POST \
  "$BASE/pullrequests/<id>/comments/<comment id>/resolve"
```

If the call fails, reply only, and tell the person that the thread stays open.

### Ready

```bash
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" -X PUT \
  -H "Content-Type: application/json" "$BASE/pullrequests/<id>" --data '{"draft": false}'
```

If the title starts with `Draft:`, remove that prefix with the same call and a `title`
field.

### Assign

Bitbucket pull requests have an author and reviewers, not an assignee. Do nothing.
Do not add a reviewer.

### Checks

```bash
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" "$BASE/pullrequests/<id>/statuses?pagelen=100" \
  | jq '.values[] | {key, name, state, url}'
```

Each status is one check. `SUCCESSFUL` is `pass`. `FAILED` and `STOPPED` are `fail`.
`INPROGRESS` is `pending`. If `values` is empty, the pull request has no checks.

### CI log

For Bitbucket Pipelines, find the pipeline of the branch, its failed step, and the
log of that step. Each UUID has braces. Write them as `%7B` and `%7D` in a URL.

```bash
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" "$BASE/pipelines/?sort=-created_on&pagelen=20" \
  | jq '.values[] | select(.target.ref_name == "<branch>") | {uuid, result: .state.result.name}'
curl -s -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" "$BASE/pipelines/<pipeline uuid>/steps/" \
  | jq '.values[] | {uuid, name, result: .state.result.name}'
curl -sL -u "$BITBUCKET_USER:$BITBUCKET_APP_PASSWORD" "$BASE/pipelines/<pipeline uuid>/steps/<step uuid>/log" \
  | tail -n 200
```

For a check of another service, the log is at the `url` of the status. If you cannot
read it, give the link to the person.

### Rerun

The API has no call that runs only the failed steps. Give the person the `url` of
each failed check, and ask them to run it again from that page.
