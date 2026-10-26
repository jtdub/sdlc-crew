# Feedback mode: act on the review comments of a pull request

`/sdlc-crew --feedback [TARGET]` reads the review comments of an open pull request,
fixes the problems that the comments raise, and replies to each comment. The crew
does the work in the worktree of the pull request, so the checkout of the person
does not change.

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

## F2 — Read the comments

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

If nothing remains, tell the person that the pull request has no open comments, and
stop.

## F3 — QA: judge each comment

Start the `sdlc-qa` persona with `models.review`. Give it `UNIT_ID`, `PLAN`,
`RUN_DIR`, `REPO_DIR`, `WORK_DIR`, `BASE_BRANCH`, `CONFIG`, `PR`, and
`FEEDBACK: RUN_DIR/feedback/comments.md`. QA follows "Feedback mode" in its skill,
writes `RUN_DIR/feedback/triage.md`, and returns `STATUS: FIX` or `STATUS: CLEAN`.

## F4 — Agree on the fixes

Show the triage table to the person: one row for each comment, with the author, the
`path:line`, the verdict, and the reason. Ask: "Fix the VALID comments?" Offer
"Fix all VALID comments (Recommended)", "Let me change the verdicts", and "Do not fix
anything".

If the person changes a verdict, quote the words of the person in `triage.md` next to
that row, and use the new verdict. Do not change a verdict for the person.

## F5 — Engineer: fix

If one or more comments are VALID, start the `sdlc-engineer` persona with
`models.build`. Give it the values of F3 and this instruction: "Fix the VALID
comments in RUN_DIR/feedback/triage.md. Do not change code outside the scope of
<UNIT_ID>." The engineer follows Step 6 of its skill and returns `STATUS: FIXED`.

Then do Step 3 of the skill, the QA review and fix loop, on the new commits. Give QA
`ROUND` from 1, and the triage file as the scope.

## F6 — Reply and resolve

Write one reply for each comment to `RUN_DIR/feedback/replies.md`. End each reply
with the line `— sdlc-crew`.

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

Tell the person: the pull request URL, the count of comments by verdict, the commits
that the engineer pushed, the threads that stay open, and the worktree path. Do not
mark the pull request ready, approve it, or request a reviewer.
