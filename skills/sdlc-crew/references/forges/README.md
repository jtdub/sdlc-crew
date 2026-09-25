# Forge references

A forge is the service that holds the git repository and the pull requests. Each file
in this directory tells the crew how to do the same operations with one forge. The
orchestrator reads `forge.kind` from `.sdlc-crew.yaml` and follows the matching file.

| Operation | Meaning |
|---|---|
| Identify | Find `owner/name`, the default branch, and the account that runs the workflow. |
| Branch | Create the work branch from the base branch. |
| Open PR | Push the branch and open a draft pull request from the template. |
| Update PR | Replace the pull request body from a file. |
| Comment PR | Add a comment, for example with screenshots. |
| Ready | Mark the draft pull request ready for review. |
| Assign | Make the account that runs the workflow an assignee. |

Rules for every forge:

- Never force-push. Never rewrite a commit that is on the remote.
- Never merge, approve, or request a reviewer. A human does the review.
- Before the first push to a remote, tell the person in one sentence that the push
  makes the branch visible to everyone who can see the repository.
- With `forge.kind: none`, do Branch only. Commit on the branch. Tell the person the
  branch name and how to open a pull request by hand, if they have a forge later.

## Branch name

`forge.branch_pattern` with `{id}` and `{slug}`. Default: `sdlc/{id}-{slug}`.

```bash
git fetch origin "$BASE_BRANCH"
git switch -c "$BRANCH" "origin/$BASE_BRANCH"
```

## Pull request template

Look for a template in this order: `.github/pull_request_template.md`,
`.github/PULL_REQUEST_TEMPLATE.md`, `.gitlab/merge_request_templates/Default.md`,
`PULL_REQUEST_TEMPLATE.md`, `docs/pull_request_template.md`,
`.github/PULL_REQUEST_TEMPLATE/`. If the repository has none, use
`assets/pull_request_template.md` from the `sdlc-crew` skill directory, and say so in the
report.

## Measure the diff

Count the changed lines against the base branch. Exclude generated and vendored files,
because a human does not review them line by line.

```bash
git fetch origin "$BASE_BRANCH" --quiet
git diff --numstat "origin/$BASE_BRANCH...HEAD" | awk '
  $1 == "-" { next }
  $3 ~ /(^|\/)(poetry\.lock|package-lock\.json|yarn\.lock|pnpm-lock\.yaml|Cargo\.lock|go\.sum|uv\.lock|Gemfile\.lock|composer\.lock)$/ { next }
  $3 ~ /\/migrations\/[0-9]/ { next }
  $3 ~ /\.(min\.js|min\.css|map|mo|po|pot|svg|snap)$/ { next }
  $3 ~ /(^|\/)(dist|build|vendor|node_modules)\// { next }
  { total += $1 + $2 }
  END { print total + 0 }'
```

The result is `DIFF_LINES`. Compare it with `limits.max_pr_lines`.
