# Tracker: gitlab

The work items are GitLab Issues of the project in `tracker.project`, or of the
project that the `origin` remote names when `tracker.project` is empty. Labels give
the status. Linked issues give the parent and the children.

## Tools, in order

1. `glab`, the GitLab CLI. Check with `glab auth status`. For a self-hosted GitLab,
   set `tracker.url` and pass `--repo <host>/<group>/<project>` or set `GITLAB_HOST`.
2. A GitLab MCP server, if the harness has one connected.
3. The REST API with `GITLAB_TOKEN`, through
   `curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "<tracker.url>/api/v4/projects/<url-encoded path>/issues/<iid>"`.

The examples use `glab`. Run them in the repository directory. `<iid>` is the issue
number that the project shows.

## Status labels

The status is a label with the exact name from `tracker.statuses`. GitLab creates a
label on first use with `glab issue update --label`. If the project uses scoped
labels such as `status::In Progress`, set the names in `tracker.statuses` to the
scoped form.

## Operations

### Read

```bash
glab issue view <iid> --comments --output json
```

The parent is the issue that the body names with `Parent: #<iid>`, or a linked issue
whose body lists this issue under **Children**.

### Create

```bash
glab issue create --title "<summary>" --description-file "$RUN_DIR/issue-body.md" \
  --label "<tracker.statuses.todo>"
```

The command prints the URL. The iid is the last path segment.

### Create child

Create the issue as above with `Parent: #<parent>` at the top of the body, and link
it: `glab issue create ... --linked-issues <parent-iid>`. Add the child iid to a
**Children** list in the parent description with `glab issue update <parent> --description-file`.

### Comment

```bash
glab issue note <iid> --message "$(cat "$RUN_DIR/<file>.md")"
```

### Set status

```bash
glab issue update <iid> --label "<new status>" --unlabel "<old status>"
```

If `forge.assign_to_me` is true and the status is `in_progress`, add
`--assignee @me`.

### Link PR

Put `Closes #<iid>` in the merge request description. GitLab links the two and closes
the issue on merge.
