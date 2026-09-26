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
