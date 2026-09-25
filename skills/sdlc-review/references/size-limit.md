# The size limit and the split map

A pull request must have `limits.max_pr_lines` non-generated changed lines or less.
The default is 500. A larger pull request is hard for a human to review, and a review
that is hard does not happen.

Measure with the command in `sdlc-crew/references/forges/README.md`, "Measure the
diff". The result is `DIFF_LINES`.

## When the limit applies

- The architect estimates the size of the plan. If the estimate is more than the
  limit, or the change is in more than one repository, the plan splits the work item
  into child items. Each child gives one pull request.
- The engineer measures the diff before it opens the pull request. If the count is
  more than the limit, the orchestrator asks the person whether to continue.
- `sdlc-review` measures the diff first. If the count is more than the limit, and the
  review is not in handoff mode, it proposes a split map.

## How to group a change

Group the changed files and hunks by intent. Each group maps to one requirement or
one acceptance criterion. Apply these rules:

1. Keep each group under about 80 percent of the limit. Split a larger group.
2. Make each group merge on its own. The application starts. The test suite passes.
3. Give each group its own tests, its documentation, and its changelog entry.
4. Put a shared helper in the earliest group that needs it.
5. Fold a group under about 30 lines into a neighbour group.
6. Keep a generated file with the change that generates it. A migration goes with
   its model change.
7. Order the groups so that a dependency comes first.
8. Put the work for different repositories in different groups.
9. Give each group a maximum of one direct dependency in the same repository. The
   groups in one repository make one chain of stacked pull requests.

If every hunk depends on every other hunk, the change is atomic. Report that fact and
the reason. Do not force a split.

## The split map

The map opens with the measured line count, the parent work item, and the group
count. Then one section for each group:

- **Summary** — one imperative sentence. This becomes the child item summary.
- **Serves** — the requirement or the acceptance criterion of the parent.
- **Files** — the file paths. Name the functions when one file splits across groups.
- **Size** — the approximate non-generated line count.
- **Branch** — from `forge.branch_pattern`, with `<CHILD-ID>` as a placeholder.
- **Order** — the merge position, and the groups that this group depends on.

The map is a proposal. It creates no child item and opens no pull request.
