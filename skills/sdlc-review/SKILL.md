---
name: sdlc-review
description: One consolidated review of a pull request or a branch before a human reads it. Measures the diff, proposes a split map when the change is too large, runs the code and security reviews that the harness has, applies the security checklist, judges the comments that the pull request already carries, checks the changelog entry, merges everything into one prioritized list, and posts the comments that the person selects. Use when the person asks for a review, a combined review, or a verdict on existing review comments. With --handoff, returns the findings as a report for the sdlc-qa persona and posts nothing.
license: Apache-2.0
compatibility: Needs git and the forge tool that .sdlc-crew.yaml names.
metadata:
  author: sdlc-crew
  role: review
---

Measure the diff first. If the diff is large, propose a map that splits the change
into child pull requests, and ask the person whether to post the map. If the map
posts, the review ends. Otherwise run the reviews, judge the comments that the pull
request already carries, check the changelog, merge all findings into one prioritized
list, and post the comments that the person selects.

`$ARGUMENTS`: an optional target (a pull request number, a branch, or a path), and
the optional flag `--handoff`. If the target is a pull request or a branch that is
not checked out, check it out first. A path target limits the reviews to that path.

`--handoff`: the `sdlc-qa` persona passes it. In handoff mode, the skill does not
talk to a human and does not write to the pull request:

- Step 2 measures the diff and reports the count. It builds no split map, and it
  asks no question.
- Steps 3 to 7 run as usual.
- Steps 8, 9, and 10 do not run.
- The skill ends with the handoff report below.
- If a step needs an answer, record the gap in the report and continue.

Write all prose in ASD-STE100 Simplified Technical English. Write each finding with
`references/plain-language.md`.

## Step 1 — Read the config

Read `.sdlc-crew.yaml` with `../sdlc-crew/references/config-schema.md`. Use
`forge.kind`, `project.changelog`, `project.test_command`, `limits.max_pr_lines`,
and `person.experience`. If the file does not exist, use the defaults and `gh` when
the `origin` remote is on GitHub, `glab` when it is on GitLab.

The forge operations are in `../sdlc-crew/references/forges/<forge.kind>.md`.

## Step 2 — Measure the diff and decide on a split

Measure with "Measure the diff" in `../sdlc-crew/references/forges/README.md`. The
base is the base branch of the pull request, or the default branch when the target
has no pull request. The result is `DIFF_LINES`.

If `DIFF_LINES` is `limits.max_pr_lines` or less, tell the person the count and
continue with Step 3. In handoff mode, record the count and continue for every count.

Otherwise:

1. Find the parent work item: an ID in the branch name, the pull request title, or
   the body. Read it with the tracker file of `tracker.kind`. If none is found, ask
   the person. If the read fails, build the map from the pull request body and the
   diff alone, and mark the map "parent item not read".
2. Group the diff and write the map with `references/size-limit.md`.
3. Show the map to the person. If the target has a pull request, ask: "Post the
   split map to the pull request and end the review?" with the options "Yes, post
   the map and stop" and "No, continue the full review". Do not post before the
   answer.
4. If yes, post the map as one general comment with the Comment PR operation, report
   the URL, and end the skill here.
5. If no, continue with Step 3. Do not ask about the map again.

The map creates no child item and opens no pull request.

## Step 3 — Run the reviews

Run each review. Collect the findings. Do not apply fixes. Do not let any review post
its own comments.

1. If the harness has a `security-review` skill, invoke it. Otherwise apply
   `references/security-checklist.md` to the diff yourself, and run the secret scan
   and the dependency audit that the checklist names, when the tools are installed.
2. If the harness has a `code-review` skill, invoke it with the target. Otherwise
   read the full diff and look for: a functional bug, a missing test, an error that
   is swallowed, a race, an unbounded loop or query, a wrong edge case, and a
   convention of the nearby code that the diff breaks.
3. Apply `references/security-checklist.md` in every case, even when a
   `security-review` skill ran, because the checklist holds items for a small
   project that a generic review can miss.
4. If the diff changes infrastructure files, apply the "What QA checks" table of
   `references/infrastructure.md`.
5. Run the test suite with `project.test_command`. A failure is a MUST FIX finding.

Pass a path target to each review. If a review does not accept a path, run it on the
full diff, and drop its findings outside the path.

## Step 4 — Judge the existing pull request comments

If the target has no pull request, skip this step.

Read every comment that the pull request carries. With `gh`:

```bash
PR=$(gh pr view --json number --jq '.number')
gh api "repos/{owner}/{repo}/pulls/$PR/comments" --paginate \
  --jq '.[] | {id, user: .user.login, path, line, in_reply_to_id, body}'
gh api "repos/{owner}/{repo}/pulls/$PR/reviews" --paginate \
  --jq '.[] | select(.body != "") | {id, user: .user.login, state, body}'
gh api "repos/{owner}/{repo}/issues/$PR/comments" --paginate \
  --jq '.[] | {id, user: .user.login, body}'
```

With `glab`: `glab mr view <MR> --comments --output json`. With another forge, use
the comment list call of its forge file.

Skip a comment that an earlier run of this skill posted, a comment from a bot, and a
comment that asks for no change.

Judge each remaining comment. Read the file at the commented path and line first.
Assign one verdict:

| Verdict | Criteria |
|---|---|
| VALID | The defect exists in the current code, and the requested change is correct. |
| VALID, RESOLVED | The comment was correct, and a later commit applied the change. |
| INVALID | The current code does not hold the defect, or the claim is wrong. |
| OUT OF SCOPE | The claim is correct, but it is about code that this change does not touch. |
| UNCLEAR | The comment does not state enough for a verdict. |

Rules:

- Judge by the code only. The identity of the author does not change the verdict.
- Give a reason of one or two sentences, with evidence: a `path:line`, or the commit
  that applied the change, found with `git log --oneline -S '<text>' -- <path>`.
- Add each VALID comment to the consolidated list as a finding, marked
  `[from PR comment by @<login>]`. Do not add the other verdicts. An UNCLEAR comment
  becomes a CONSIDER FIXING item that asks the author for the missing detail.

Show a table with one row for each judged comment: the id, the author, `path:line`,
the verdict, and the reason. Show it before the consolidated list.

## Step 5 — Check the changelog

Skip this step when `project.changelog` is `none`.

`keep-a-changelog`: the diff adds at least one line under `## [Unreleased]` in
`CHANGELOG.md`, under `### Added`, `### Changed`, `### Fixed`, `### Removed`,
`### Deprecated`, or `### Security`. The line says what the user notices, not what the
code does. A missing line is SHOULD FIX. A line that names a class or a file is
CONSIDER FIXING.

`towncrier`: read the fragment directory and the types from `pyproject.toml`
(`[tool.towncrier]`), or use `changes/` and the types `added`, `changed`, `fixed`,
`removed`, `security`, `dependencies`, `documentation`. Each fragment that the diff
adds must match `^[0-9]+\.<type>(\.[0-9]+)?$`, where the number is the work item
number of the branch, the title, or the body, or the pull request number. A missing
fragment, a wrong name, or a wrong number is SHOULD FIX. State the correct name in the
finding.

## Step 6 — Check the user interface

If the diff changes a template, a page, a component, a style sheet, or a script that
a browser runs, and the review is not in handoff mode, start the app with
`project.run_command` and open each changed page as `sdlc-ux` Step 3 does. A page
error or a console error is MUST FIX. A defect that hides information or blocks an
action is SHOULD FIX. A cosmetic defect is CONSIDER FIXING. Mark each such finding
`[verified in the browser]`. If the app cannot start, say which pages did not get a
check.

In handoff mode, skip this step. The `sdlc-ux` persona does it.

## Step 7 — Consolidate the findings

Merge the findings from Steps 3 to 6 into one list:

- **Deduplicate.** Two findings that report the same defect at the same file and line
  are one item with both sources and the highest priority.
- **Assign one priority.** If an item matches two rows, use the higher one. Map a
  security finding by severity only: critical or high is MUST FIX, medium is SHOULD
  FIX, low is CONSIDER FIXING.

| Priority | Criteria |
|---|---|
| MUST FIX | A functional bug, a critical or high security finding, data loss, a secret in the diff, a test failure, or a CI failure |
| SHOULD FIX | A convention violation that can cause a problem, a missing test, a missing migration, a missing project basic, or a medium security finding |
| CONSIDER FIXING | A style improvement, a simplification, a performance improvement, or a low security finding |
| NIT PICK | A cosmetic item: a typo, wording, whitespace |

- **Write the PRAISE paragraph.** Two to four sentences about real work in the diff
  that is done well. Do not invent praise.
- **Sort** by priority. **Number** each item across the list.
- **Write each item** with the number, the priority, `path:line`, one sentence for
  the person that says what happens and what the fix is, the technical name in
  parentheses, and the sources.
- **Mark simple fixes** with `[suggested fix available]` when the fix replaces one
  line or a few adjacent lines and has no design decision. Prepare the replacement.

Show the full list to the person. In handoff mode, return the handoff report and
stop.

## Handoff report (handoff mode only)

Keep the headings exactly as shown. Put no text after the last section.

````markdown
## QA findings

Diff size: <count> non-generated lines

| # | Priority | Location | Defect | Required change | Sources |
|---|---|---|---|---|---|
| 1 | MUST FIX | path/to/file.py:42 | <one sentence> | <one sentence> | code-review, security-checklist |

### Suggested fixes

#### 1
```suggestion
<replacement lines>
```

### Gaps

- <a review that did not run, a check that was unconfirmed, or "None">
````

Include every item, of all priorities. Write "Required change" so that an engineer
can apply it with no other context. If the list is empty, write one row:
`| — | — | — | No findings | — | — |`. Do not include the PRAISE paragraph.

## Step 8 — Ask which items get comments

Ask with multi-select: "All MUST FIX items", "All MUST FIX and SHOULD FIX items",
"All items", "No comments". In the same question set, ask "Post the PRAISE
comment?" with "Yes" and "No". Do not post before the answer.

## Step 9 — Post the comments

Find the pull request of the current branch. If none exists, print the comments in
the terminal instead. Compare `git rev-parse HEAD` with the head of the pull request.
If they differ, stop and tell the person to push first, because the line numbers can
be wrong.

Post the PRAISE paragraph first as one general comment, if selected.

Post each selected item as an inline comment on the changed line. With `gh`:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments \
  -f body="$BODY" -f commit_id="$HEAD_SHA" -f path="$FILE" -F line="$LINE" -f side=RIGHT
```

With `glab` or another forge, use the inline comment call of its forge file, or one
general comment when the forge has none.

Comment rules:

- The body holds the priority in bold, then one or two sentences for the person, then
  the technical name in parentheses. Do not repeat the path.
- Add a `suggestion` block after the prose for a simple fix, with the exact
  indentation of the file.
- An inline comment must target a line that the diff changed. Collect the items
  outside the diff into one general comment.

Report the count and the pull request URL. Do not apply the fixes unless the person
asks.

## Step 10 — Set the review state (only on request)

Do not set a review state unless the person asks for it in an explicit instruction.
A request for a review, for comments, or for a verdict is not such an instruction.
Do not approve a pull request that you wrote; the forge refuses it. When asked,
write two or three sentences with the result and the count by priority, and run the
approve or request-changes command of the forge.

## Common mistakes

- Do not ask a question, post a comment, or set a review state in handoff mode.
- Do not run a review before Step 2 ends. The split question comes first.
- Do not continue the review after the split map posts.
- Do not agree with an existing comment because of the author. Read the code.
- Do not post a reply in an existing comment thread. Report the verdict only.
- Do not accept a changelog line that names a class or a file as the change.
- Do not post comments before the person selects the items.
- Do not put a design decision in a suggestion block. Offer prose instead.
- Do not propose a split for a diff at or under the limit.
- Do not count a generated file toward the limit.
- Do not create a child item or open a pull request in this skill.
- Do not test against a production instance.
