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

### Ready

```bash
gh pr ready <PR>
```

### Assign

```bash
gh pr edit <PR> --add-assignee @me
```

### Stacked pull requests

If a work unit depends on another unit in the same repository, its branch starts
from the branch of that unit, and its pull request uses that branch as the base. If
`gh stack --help` succeeds, link the two with
`gh stack link "<base PR URL>" "<PR URL>"`. Use no other `gh stack` command. Do not
install the extension. If the command is not available, the pull request stays a
plain pull request with the dependency named in its body.
