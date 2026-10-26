# Forge: github

## Tool

`gh`, the GitHub CLI. Check with `gh auth status`. Do not use `curl` against the
GitHub API when `gh` is installed. If `gh` is not installed, tell the person how to
install it, and offer `forge.kind: none` until then.

## Operations

### Identify

```bash
gh repo view --json nameWithOwner,defaultBranchRef --jq '.nameWithOwner, .defaultBranchRef.name'
gh api user --jq '.login'
```

### Open PR

```bash
git push -u origin HEAD
gh pr create --draft --base "$BASE_BRANCH" --title "<ID>: <summary>" \
  --body-file "$RUN_DIR/pr-body.md"
```

Add `--assignee @me` when `forge.assign_to_me` is true. The command prints the URL.

### Update PR

```bash
gh pr view <PR> --json body --jq '.body' > "$RUN_DIR/pr-body.md"
gh pr edit <PR> --body-file "$RUN_DIR/pr-body.md"
```

### Comment PR

```bash
gh pr comment <PR> --body-file "$RUN_DIR/<file>.md"
```

To attach a screenshot, the comment body needs a URL. `gh` cannot upload an image.
Use `project.screenshots: docs/screenshots` to commit the images on the branch and
link them with a relative path, or describe the result in words.

### Read comments

Read the review threads that are not resolved. The GraphQL API is the only one that
shows the resolved state:

```bash
gh api graphql --paginate -F owner='{owner}' -F name='{repo}' -F number=<PR> -f query='
query($owner: String!, $name: String!, $number: Int!, $endCursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $endCursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id isResolved isOutdated path line
          comments(first: 50) { nodes { databaseId author { login } body createdAt } }
        }
      }
    }
  }
}' --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved | not)'
```

Then read the review summaries and the general comments:

```bash
gh api "repos/{owner}/{repo}/pulls/<PR>/reviews" --paginate \
  --jq '.[] | select(.body != "") | {id, user: .user.login, state, body}'
gh api "repos/{owner}/{repo}/issues/<PR>/comments" --paginate \
  --jq '.[] | {id, user: .user.login, body, created_at}'
```

### Reply comment

For a review thread, use the thread `id` from Read comments:

```bash
gh api graphql -f id="<thread id>" -f body="$(cat "$RUN_DIR/<file>.md")" -f query='
mutation($id: ID!, $body: String!) {
  addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $id, body: $body}) {
    comment { url }
  }
}'
```

For a review summary or a general comment, do Comment PR. Start the body with a
quote of the first line of the comment and the `@login` of its author.

### Resolve thread

```bash
gh api graphql -f id="<thread id>" -f query='
mutation($id: ID!) { resolveReviewThread(input: {threadId: $id}) { thread { isResolved } } }'
```

A review summary and a general comment have no resolved state. Reply only.

### Ready

```bash
gh pr ready <PR>
```

### Assign

```bash
gh pr edit <PR> --add-assignee @me
```

### Checks

Wait for the checks, then read them:

```bash
gh pr checks <PR> --watch --interval 60
gh pr checks <PR> --json name,bucket,link,workflow
```

The `bucket` gives the result: `pass` is `pass`, `skipping` is `skip`, `pending` is
`pending`, and `fail` or `cancel` is `fail`. If the output says that no checks are
reported, the pull request has no checks.

### CI log

For a GitHub Actions check, the `link` holds `/actions/runs/<run id>/`. Read the log of
the failed jobs:

```bash
gh run view <run id> --log-failed
```

For a check of another service, the log is at the `link`. If you cannot read it,
give the link to the person.

### Rerun

```bash
gh run rerun <run id> --failed
```

A check of another service runs again from its own page. Give the link to the person.

### Stacked pull requests

If a work unit depends on another unit in the same repository, its branch starts
from the branch of that unit, and its pull request uses that branch as the base. If
`gh stack --help` succeeds, link the two with
`gh stack link "<base PR URL>" "<PR URL>"`. Use no other `gh stack` command. Do not
install the extension. If the command is not available, the pull request stays a
plain pull request with the dependency named in its body.
