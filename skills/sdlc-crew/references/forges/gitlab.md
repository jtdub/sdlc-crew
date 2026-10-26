# Forge: gitlab

GitLab calls a pull request a merge request. The two words mean the same thing here.

## Tool

`glab`, the GitLab CLI. Check with `glab auth status`. For a self-hosted GitLab, set
`GITLAB_HOST` or pass `--repo`.

## Operations

### Identify

```bash
glab repo view --output json --jq '.path_with_namespace, .default_branch'
glab api user --jq '.username'
```

### Open PR

```bash
git push -u origin HEAD
glab mr create --draft --target-branch "$BASE_BRANCH" --title "<ID>: <summary>" \
  --description-file "$RUN_DIR/pr-body.md" --assignee @me
```

Drop `--assignee @me` when `forge.assign_to_me` is false. The command prints the URL.

### Update PR

```bash
glab mr view <MR> --output json --jq '.description' > "$RUN_DIR/pr-body.md"
glab mr update <MR> --description-file "$RUN_DIR/pr-body.md"
```

### Comment PR

```bash
glab mr note <MR> --message "$(cat "$RUN_DIR/<file>.md")"
```

### Read comments

Each discussion is one thread. Keep the discussions that have a note that is
resolvable and not resolved, and the general notes that are not system notes:

```bash
glab api --paginate "projects/:fullpath/merge_requests/<MR>/discussions" \
  --jq '.[] | select(any(.notes[]; (.resolvable and (.resolved | not)) or (.individual_note and (.system | not))))
        | {id, notes: [.notes[] | {id, author: .author.username, body, path: .position.new_path, line: .position.new_line, created_at}]}'
```

### Reply comment

```bash
glab api -X POST "projects/:fullpath/merge_requests/<MR>/discussions/<discussion id>/notes" \
  -f body="$(cat "$RUN_DIR/<file>.md")"
```

### Resolve thread

```bash
glab api -X PUT "projects/:fullpath/merge_requests/<MR>/discussions/<discussion id>" -f resolved=true
```

A general note is not resolvable. Reply only.

### Ready

```bash
glab mr update <MR> --ready
```

### Assign

```bash
glab mr update <MR> --assignee +@me
```

### Checks

Read the latest pipeline of the merge request, then its jobs:

```bash
glab api "projects/:fullpath/merge_requests/<MR>/pipelines" --jq '.[0] | {id, status, web_url}'
glab api --paginate "projects/:fullpath/pipelines/<pipeline id>/jobs" \
  --jq '.[] | {id, name, status, allow_failure, web_url}'
```

Each job is one check. `success` is `pass`. `skipped` and `manual` are `skip`. `failed`
with `allow_failure: true` is `skip`. Other `failed` jobs and `canceled` jobs are
`fail`. Every other status is `pending`. If the first command returns nothing, the
merge request has no checks.

### CI log

```bash
glab api "projects/:fullpath/jobs/<job id>/trace" | tail -n 200
```

### Rerun

```bash
glab api -X POST "projects/:fullpath/jobs/<job id>/retry"
```

### Dependent merge requests

If a work unit depends on another unit in the same repository, its branch starts
from the branch of that unit, and its merge request targets that branch. Name the
dependency in the description. GitLab retargets the merge request to the default
branch when the base merges.
