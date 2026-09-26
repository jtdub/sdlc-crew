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

### Ready

```bash
glab mr update <MR> --ready
```

### Assign

```bash
glab mr update <MR> --assignee +@me
```

### Dependent merge requests

If a work unit depends on another unit in the same repository, its branch starts
from the branch of that unit, and its merge request targets that branch. Name the
dependency in the description. GitLab retargets the merge request to the default
branch when the base merges.
