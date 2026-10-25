# Forge references

A forge is the service that holds the git repository and the pull requests. Each file
in this directory tells the crew how to do the same operations with one forge. The
orchestrator reads `forge.kind` from `.sdlc-crew.yaml` and follows the matching file.

| Operation | Meaning |
|---|---|
| Identify | Find `owner/name`, the default branch, and the account that runs the workflow. |
| Worktree | Create the work branch from the base branch in a new git worktree. |
| Open PR | Push the branch and open a draft pull request from the template. |
| Update PR | Replace the pull request body from a file. |
| Comment PR | Add a comment, for example with screenshots. |
| Read comments | List the open review threads and the general comments of a pull request. |
| Reply comment | Add a reply to one review thread or one general comment. |
| Resolve thread | Mark one review thread as resolved. |
| Ready | Mark the draft pull request ready for review. |
| Assign | Make the account that runs the workflow an assignee. |

Rules for every forge:

- Never force-push. Never rewrite a commit that is on the remote.
- Never merge, approve, or request a reviewer. A human does the review.
- Before the first push to a remote, tell the person in one sentence that the push
  makes the branch visible to everyone who can see the repository.
- With `forge.kind: none`, do Worktree only. Commit on the branch. Tell the person the
  branch name, the worktree path, and how to open a pull request by hand, if they
  have a forge later.
- Never switch the branch of the main checkout of the person. All work for a unit
  happens in its worktree.

## Branch name

`forge.branch_pattern` with `{id}` and `{slug}`. Default: `sdlc/{id}-{slug}`.

## Worktree

A git worktree is a second working directory of the same repository. It has its own
branch and its own files. The person can keep their work in the main checkout while
the crew works in the worktree.

`WORK_DIR` is `forge.worktree_dir`, with `{repo}` replaced by the directory name of
`REPO_DIR`, then `/`, then the branch name with each `/` replaced by `-`. A relative
`forge.worktree_dir` starts at `REPO_DIR`. Run these commands in `REPO_DIR`:

```bash
git fetch origin "$BASE_BRANCH"
git worktree add -b "$BRANCH" "$WORK_DIR" "origin/$BASE_BRANCH"
```

If the repository has no `origin` remote, use `"$BASE_BRANCH"` as the start point in
place of `"origin/$BASE_BRANCH"`.

To find the worktree of a branch that exists, read `git worktree list --porcelain`.
Git checks out a branch in one worktree only. If the branch already has a worktree,
use it. If the branch has none, add one without `-b`:

```bash
git fetch origin "$BRANCH"
git worktree add "$WORK_DIR" "$BRANCH"
```

Do not remove a worktree without the consent of the person. To remove it, use
`git worktree remove "$WORK_DIR"`, without `--force`. The command refuses when the
worktree has changes that are not committed. The branch and its commits stay.

## Pull request template

Look for a template in this order: `.github/pull_request_template.md`,
`.github/PULL_REQUEST_TEMPLATE.md`, `.gitlab/merge_request_templates/Default.md`,
`PULL_REQUEST_TEMPLATE.md`, `docs/pull_request_template.md`,
`.github/PULL_REQUEST_TEMPLATE/`. If the repository has none, use
`assets/pull_request_template.md` from the `sdlc-crew` skill directory, and say so in the
report.

## Measure the diff

Count the changed lines against the base branch. Exclude generated and vendored files,
because a human does not review them line by line. Run the command in `WORK_DIR`.

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
