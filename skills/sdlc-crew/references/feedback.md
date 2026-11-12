# Feedback mode: get a pull request ready for the next review

`/sdlc-crew --feedback [TARGET]` collects three kinds of open items on an open pull
request: the review comments, the CI checks that failed, and a merge conflict with
the base branch. The crew fixes the valid items, and replies to each comment. The
crew does the work in the worktree of the pull request, so the checkout of the
person does not change.

`TARGET` is a pull request number, a pull request URL, or a work item ID. With no
target, use the pull request of the current branch.

Feedback mode needs a forge. With `forge.kind: none`, stop and tell the person that
there are no pull request comments to read.

## F1 — Prepare

1. Do Step 0 items 1, 3, 4, 6, 7, and 8 of the skill. Record `MODE: feedback` in
   `RUN_DIR/run.md`.
2. Find the pull request:
   - A number or a URL: use it.
   - A work item ID: read `RUN_DIR/units.md` of an earlier run for that ID. If the
     file does not exist, list the open pull requests whose branch name or title
     holds the ID. If more than one matches, ask the person which one.
   - No target: the pull request of the current branch. If there is none, ask the
     person for the number.
3. If the pull request is closed or merged, stop and tell the person.
4. Read the head branch and the base branch of the pull request. Set `UNIT_ID` from
   the branch name or the title, and `BASE_BRANCH` from the base branch.
5. Find or add the worktree of the head branch, as "Worktree" in `forges/README.md`
   says. Call its path `WORK_DIR`. Run `git pull --ff-only` in `WORK_DIR`. If the
   pull fails, stop and show the output to the person.
6. Set `PLAN` to the plan of the earlier run if it exists, or to `none`.

The head branch is already on the remote. The push question of the skill does not
apply in this mode.

## F2 — Collect the open items

### Comments

Do the Read comments operation of the forge file. Write every open thread and every
general comment to `RUN_DIR/feedback/comments.md`, with the id, the author, the
`path:line`, and the full text.

Skip these:

- A thread that is resolved.
- A thread or a comment whose last comment ends with the line `— sdlc-crew`. The
  crew already replied, and nobody wrote after the reply.
- A comment from the account that runs the workflow, when the crew posted it, for
  example the UX screenshots.
- A system note, or a bot comment that asks for no change.

Keep the comments of review bots, for example Copilot or CodeRabbit, that ask for a
change.

### Failed checks

Do the Checks operation of the forge file once. Do not wait for a check that is
`pending`. F5 waits for the checks after the push. Write each check with the result
`fail` to `RUN_DIR/feedback/checks.md`, with an ID `F1`, `F2`, and so on, the name,
and the link. If the forge reports no checks, write "No checks".

### Merge conflict

Find out, in `WORK_DIR`, whether the head branch merges into the base branch without
a conflict. This command changes no file and no branch:

```bash
git fetch origin "$BASE_BRANCH" --quiet
git merge-tree --write-tree --name-only --no-messages HEAD "origin/$BASE_BRANCH"
```

- Exit code 0: no conflict.
- Exit code 1: a conflict. The lines after the first line are the files with a
  conflict. Write them to `RUN_DIR/feedback/conflict.md` under the ID `M1`.
- Another exit code: record "Merge state: unknown" and the output. Git 2.38 or later
  is necessary for this command.

### Nothing to do

If no comment, no failed check, and no conflict remains, tell the person, and stop.

## F3 — QA: judge each comment

If no comment remains after F2, skip this step.

Start the `sdlc-qa` persona with `models.review`. Give it `UNIT_ID`, `PLAN`,
`RUN_DIR`, `REPO_DIR`, `WORK_DIR`, `BASE_BRANCH`, `CONFIG`, `PR`, and
`FEEDBACK: RUN_DIR/feedback/comments.md`. QA follows "Feedback mode" in its skill,
writes `RUN_DIR/feedback/triage.md`, and returns `STATUS: FIX` or `STATUS: CLEAN`.

## F4 — Agree on the fixes

Show the person one table:

- One row for each comment, with the author, the `path:line`, the verdict, and the
  reason.
- One row for each failed check, with the name and the link.
- One row for the conflict `M1`, with the files.

Ask: "Fix these items?" Offer "Fix the VALID comments, the failed checks, and the
conflict (Recommended)", "Let me change the verdicts", and "Do not fix anything".

If the person changes a verdict, quote the words of the person in `triage.md` next to
that row, and use the new verdict. Do not change a verdict for the person.

## F5 — Engineer: fix

Start the `sdlc-engineer` persona with `models.build`. Give it the values of F3. Send
the work in this order, one instruction at a time:

1. If `M1` exists: "Merge the base branch. Follow Step 8." The merge comes first, so
   that the other fixes and the checks run on the merged code. If the engineer
   returns `STATUS: QUESTIONS` about a conflict, ask the person.
2. If one or more comments are VALID: "Fix the VALID comments in
   RUN_DIR/feedback/triage.md. Do not change code outside the scope of <UNIT_ID>."
   The engineer follows Step 6.
3. If one or more checks failed: "Fix the failed checks." Give the name and the link
   of each one. The engineer follows Step 7. Handle `STATUS: BLOCKED` as Step 4.1 of
   the skill says.

Then, if the engineer changed code for a comment, do Step 3 of the skill, the QA
review and fix loop, on the new commits. Give QA `ROUND` from 1, and the triage file
as the scope.

Then do Step 4.1 of the skill, the CI loop, on the last commit. New failures can come
from the merge or from the fixes.

## F6 — Reply and resolve

Write one reply for each comment to `RUN_DIR/feedback/replies.md`. End each reply
with the line `— sdlc-crew`. Do the prose pass of
`../sdlc-review/references/prose-pass.md` on the replies. Do not reply about a
failed check or the conflict. The commits show them.

| Verdict | Reply |
|---|---|
| VALID, fixed | "Fixed in `<short commit>`." and one sentence about the change. |
| VALID, not applied | The reason from the engineer, with the evidence. |
| VALID, RESOLVED | "An earlier commit fixed this: `<short commit>`." |
| INVALID | The reason, with a `path:line` or the test output. Ask the author to reply if they disagree. |
| OUT OF SCOPE | "This is outside the scope of <UNIT_ID>." and the follow-up item, if the person creates one. |
| UNCLEAR | The question that QA wrote for the author. |

Show the replies to the person. Ask: "Post these replies?" Offer "Post the replies
and resolve the fixed threads (Recommended)", "Post the replies only", and "Do not
post".

Then:

1. Do Reply comment for each reply.
2. If the person selected resolve, do Resolve thread for each thread with the verdict
   VALID, fixed or VALID, RESOLVED. Do not resolve another thread. Its author decides.
3. For each OUT OF SCOPE comment, ask whether to create a follow-up work item with
   the Create operation of the tracker file.

## F7 — Report

Tell the person: the pull request URL, the count of comments by verdict, the checks
that the engineer fixed, the merge result, the CI result, the commits that the
engineer pushed, the threads that stay open, and the worktree path. Do not
mark the pull request ready, approve it, or request a reviewer.
