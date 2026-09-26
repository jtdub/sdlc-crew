---
name: sdlc-crew
description: Run a work item through the full software development life cycle with four personas (architect, engineer, QA, UX), from a plain-language request or an issue to a pull request that is ready for a human to review. Use only when the person runs /sdlc-crew, or asks by name for the crew or the sdlc-crew workflow to build a feature, fix a bug, or set up infrastructure. Takes an issue ID or a quoted description as the argument. Works with a local backlog file, GitHub Issues, GitLab Issues, Jira, or Bitbucket.
license: Apache-2.0
compatibility: Needs git. Needs the tracker and forge tools that .sdlc-crew.yaml names. Works in Claude Code, Codex CLI, Gemini CLI, GitHub Copilot CLI, and any harness that loads Agent Skills.
metadata:
  author: sdlc-crew
  role: orchestrator
---

This skill runs one work item through the software development life cycle. The
current session is the orchestrator. The orchestrator talks to the person, keeps the
state, and moves the work between four personas:

| Persona | Skill | Model role | Job |
|---|---|---|---|
| Software architect | `sdlc-architect` | `plan` | Read or create the item, ask questions, write the plan, split a large item |
| Software engineer | `sdlc-engineer` | `build` | Build the plan with TDD, open a draft pull request, fix the findings |
| Quality assurance (QA) | `sdlc-qa` | `review` | Review against the plan and the security checklist, send findings to the engineer |
| User experience (UX) | `sdlc-ux` | `review` | Test the change as a user, take screenshots, finish the pull request body |

`$ARGUMENTS`: a work item ID, or a quoted plain-language description. An ID matches
`LOCAL-[0-9]+`, `#[0-9]+`, `[0-9]+`, or `[A-Z][A-Z0-9]+-[0-9]+`. Anything else is a
description. With no argument, ask the person what they want to build, in one
question.

Write all prose in ASD-STE100 Simplified Technical English. Follow
`../sdlc-review/references/plain-language.md` in every message to the person.

## References

Read these files from the `references/` directory of this skill when a step names
them:

- `config-schema.md` — the keys of `.sdlc-crew.yaml` and the experience levels.
- `delegation.md` — subagent mode and inline mode, and the harness notes.
- `models.md` — the model roles.
- `trackers/<kind>.md` — the six tracker operations.
- `forges/<kind>.md` and `forges/README.md` — the forge operations, the branch name,
  the template search, and the diff measurement.

## Rules for the orchestrator

- A persona cannot talk to the person. The orchestrator asks every question and
  sends the answers back. Quote the words of the person. Do not summarize them.
- Do not make a decision for the person. If a persona returns a question, ask.
- Keep all work inside the scope of the work item.
- If a persona returns `STATUS: BLOCKED`, show the reason to the person in plain
  words and ask what to do.
- Before the first push, before a child item is created, and before any action that
  deletes data or costs money, state the risk in one sentence and ask. Wait for the
  answer.
- Do not request a reviewer, approve, or merge a pull request. A human does that.

## Step 0 — Prepare the run

1. Read `.sdlc-crew.yaml` from the repository root. If it does not exist, tell the
   person in one sentence that a short setup comes first, and invoke the
   `sdlc-setup` skill. Then read the file. Apply the defaults of `config-schema.md`
   for missing keys.
2. Read `$ARGUMENTS`. Set `ID` or `DESCRIPTION`.
3. Make the run directory. Use the scratchpad directory of the session if the
   harness has one. Otherwise use `.sdlc-crew-run/` in the repository, which
   `.gitignore` must exclude; add the line if it is missing. Call the path
   `RUN_DIR`. Make the subdirectory `screenshots/`.
4. Run these checks:

   ```bash
   git rev-parse --show-toplevel
   git status --porcelain
   ```

   Then the Identify operation of the forge file, and the auth check of the tracker
   file.
5. If the working tree has changes, stop. Tell the person to commit or stash the
   changes, and offer to commit them with a message that the person approves. Do not
   stash for the person.
6. If a forge or tracker check fails, show the output in plain words. Offer
   `sdlc-setup` to change the config, or to continue with `forge.kind: none` and
   `tracker.kind: local` for this run.
7. Pick the delegation mode with `delegation.md`. Write `RUN_DIR/run.md` with the
   mode, the ID or description, the config values, the repository, the default
   branch, and the account.

Tell the person in two or three sentences what happens next: the architect asks
questions, then writes a plan, and nothing changes in the code before they approve
the plan.

### Step 0.1 — Set the item to In Progress

If `ID` is set, do the Set status operation with `tracker.statuses.in_progress`. If
the status is already that, continue. If the operation fails, show the output, and
ask whether to skip the status change. Do not stop the workflow.

## Step 1 — Architect: requirements and plan

Start the `sdlc-architect` persona with `models.plan`. The first message holds `ID`
or `DESCRIPTION`, `RUN_DIR`, `REPO_DIR`, and `CONFIG`.

The architect returns one of these status lines:

- `STATUS: QUESTIONS` — a list of questions for the person.
- `STATUS: PLAN` — a complete plan in `RUN_DIR/plan.md`.
- `STATUS: CHILDREN` — the child items exist. Only in Step 1.4.
- `STATUS: BLOCKED` — a reason.

### Step 1.1 — Ask the questions

Ask as `delegation.md` says under "Questions to the person". Send all answers to the
architect. Repeat until the architect returns `STATUS: PLAN`.

### Step 1.2 — Agree on the plan

The person must read the full plan before the approval question. A file read by the
orchestrator is not visible to the person. For this reason:

1. Read `RUN_DIR/plan.md`.
2. Write the plan in your reply. For `person.experience: new` or `some`, write the
   sections Problem, Success measure, Chosen option, Scope, Acceptance criteria,
   Edge cases, New project, Infrastructure, and Follow-ups in full, then the reuse
   survey table with the Need and Mechanism columns, then this line: "The technical
   design and the test plan are in the file at <path>." For `professional`, write
   the full plan, with the reuse survey first and this sentence above it: "Check the
   reuse survey first. A wrong row costs nothing to change now."
3. Ask: "Do you approve this plan?" Offer "Approve the plan" and "Change the plan".
   If the plan splits the item, add: "Approval creates <N> child items, and the crew
   opens one pull request for each."
4. If the person wants changes, send them to the architect. Go back to Step 1.1.
5. Repeat until the person approves. Show the new plan each time.

Do not continue before the person approves.

### Step 1.3 — Post the plan to the tracker

Do the Comment operation with `RUN_DIR/tracker-plan-comment.md`. If the plan splits
the item, skip this step. Step 1.4 posts it after the children exist. If the
operation fails, show the output and continue.

### Step 1.4 — Create the children and list the work units

A work unit gives one pull request. If the plan says "No split", the item is the only
unit:

| Value | For an item with no split |
|---|---|
| `UNIT_ID` | `ID` |
| `CHILD` | `none` |
| `UNIT_DIR` | `RUN_DIR` |
| `REPO_DIR` | the top level of the current repository |
| `BASE_BRANCH` | the default branch |
| `DEPENDS_ON` | `none` |

If the plan splits the item:

1. Ask the person once more: "Create <N> child items in <tracker>?" Wait.
2. Resume the architect: "The person approved the plan. Do Step 5: create the child
   items."
3. The architect returns `STATUS: CHILDREN` and writes `RUN_DIR/children.json`.
   Show the list to the person.
4. Post `RUN_DIR/tracker-plan-comment.md` to the parent item.
5. For each repository in `children.json` that is not the current repository, find
   the local clone next to the current repository by its `origin` URL. If none
   matches, ask the person for the path, and offer to clone it next to the current
   repository.
6. Run the checks of Step 0 in each clone.
7. Make one unit for each child, in order:

| Value | For a child |
|---|---|
| `UNIT_ID` | the child key |
| `CHILD` | the child ID, for example `C2` |
| `UNIT_DIR` | `RUN_DIR/<UNIT_ID>/`, with `screenshots/` |
| `REPO_DIR` | the local clone of the child repository |
| `BASE_BRANCH` | the branch of the `same_repo_parent` child, or the default branch of the child repository |
| `DEPENDS_ON` | the pull request URLs of the `depends_on` children, or `none` |

Write the units to `RUN_DIR/units.md`. Update the file when a unit gets a branch or a
pull request. A new session can continue from this file.

## Work unit loop

Do Steps 2 to 5 one time for each unit, in order. Finish a unit before the next one.

For each unit:

1. If `UNIT_ID` is a child, set it to `in_progress`.
2. Start a new engineer, a new QA, and a new UX persona for the unit. Do not resume
   the personas of an earlier unit.
3. Give every persona `UNIT_ID`, `UNIT_DIR`, `CHILD`, `PLAN`, `REPO_DIR`,
   `BASE_BRANCH`, `DEPENDS_ON`, `CONFIG`, and for a child `PARENT_ID`.
4. Tell the person which unit starts: the ID, the summary, the repository, and the
   base branch.

If a unit ends with the pull request in draft, ask: "The pull request of <UNIT_ID>
stays in draft. Continue with the next child, or stop?" If the person stops, go to
Step 6.

## Step 2 — Engineer: build the plan and open a draft pull request

Before the engineer starts, if `forge.kind` is not `none` and this is the first push
of the run, say: "The engineer will push a branch to <forge.repo>. Everyone who can
see that repository can see the branch. Continue?" Wait.

Start the `sdlc-engineer` persona with `models.build`.

The engineer returns `STATUS: DRAFT_PR` with the pull request number and URL, the
base branch, the `STACK` result, `DIFF_LINES`, the test command, and the test result.
It can also return `STATUS: QUESTIONS` or `STATUS: BLOCKED`.

Record the branch and the pull request URL in `RUN_DIR/units.md`.

If `DIFF_LINES` is more than `limits.max_pr_lines`, tell the person the count, the
limit, and the plan estimate. Ask: "Continue with this pull request, or leave it in
draft and stop?" Record the count in `UNIT_DIR/workflow-notes.md`.

If the engineer returns `STATUS: QUESTIONS`, send the question to the architect
first. A `SURVEY GAP` question means that the reuse survey is wrong. If the architect
cannot answer from the plan and the decisions, ask the person. Then send the answer
to the engineer. Record each plan change in `RUN_DIR/plan-changes.md`.

## Step 3 — QA: review and fix loop

For `ROUND` from 1 to `limits.max_qa_rounds`:

1. If `ROUND` is 1, start the `sdlc-qa` persona with `models.review`. Otherwise
   resume it. Give it `PR` and `ROUND`.
2. QA writes `UNIT_DIR/qa-round-<ROUND>.md` and returns `STATUS: CLEAN` or
   `STATUS: FIX`.
3. If `CLEAN`, end the loop.
4. If `FIX`, tell the person the round number, the count of findings, and the "For
   the person" paragraph of the QA file. Resume the engineer with the file path and
   this instruction: "Fix all in-scope findings in this file. Do not change code
   outside the scope of <UNIT_ID>."
5. The engineer returns `STATUS: FIXED` and pushes the commits.

If the last round ends with `FIX`, the engineer applies the fixes, but QA does not
review them again. Record "QA round limit reached; the last fixes did not get a QA
review" in `UNIT_DIR/workflow-notes.md`.

Do not send out-of-scope findings to the engineer. Collect them for Step 5.

## Step 4 — UX: test the user experience

Start the `sdlc-ux` persona with `models.review`. Give it `PR`.

UX returns `STATUS: PASS`, `STATUS: NO_UI`, or `STATUS: DEFECTS`.

If `DEFECTS`:

1. Show the defects to the person.
2. Ask: "Send the defects to the engineer to fix, mark the pull request ready anyway,
   or leave it in draft and stop?"
3. If the person selects the fix, resume the engineer with the defects, then resume
   UX to test again. Ask again if UX finds more defects.
4. If the person stops, skip Step 5 for this unit.

## Step 5 — Finish the pull request and hand it to a human

1. Read the pull request body with the Update PR operation.
2. Add a section `## Workflow notes` at the end. It holds:
   - The count of QA rounds, and the count of fixed findings.
   - The contents of `UNIT_DIR/workflow-notes.md`, if the file exists.
   - For a stacked pull request: "Base: <BASE_BRANCH>. Merge <base URL> first."
   - The out-of-scope QA findings, one line each, or "None".
   - The plan changes from `RUN_DIR/plan-changes.md`, if the file exists.
3. Write the body, and do the Ready operation.
4. Do the Assign operation when `forge.assign_to_me` is true.
5. Do the Link PR operation, then set `UNIT_ID` to `in_review`. Do this only after
   Ready completes without an error.
6. If `UNIT_ID` is a child and the last unit, set the parent to `in_review` only if
   the pull request of every child is ready.

With `forge.kind: none`, skip 1 to 4. Tell the person the branch name, and that the
change is in the local repository only.

## Step 6 — Retrospective

1. Resume the architect with the paths of the plan, the plan changes, every QA round
   file, and each UX report. If the plan split the item, add `DIFF_LINES` of each
   child.
2. The architect writes `RUN_DIR/tracker-retro-comment.md`.
3. Show the "For you" line of the retrospective to the person, and the path of the
   full file.
4. Do the Comment operation with the retrospective on the parent item only.
5. Report to the person: the pull request URL, its state, the item status, the QA
   round count, the UX status, and each item that the workflow did not complete. If
   the plan split the item, give one row for each child and the merge order.
6. For `person.experience: new`, end with what to do next in three sentences: open
   the pull request page, read the User impact section, and press the merge button
   when they are satisfied, or ask the crew for a change.

If the architect cannot resume, start a new architect with the same files, and tell
it to write the retrospective only.

## Continue a run

If the person runs `/sdlc-crew <ID>` and `RUN_DIR/units.md` exists for that ID,
read it and continue from the first unit that has no ready pull request. Tell the
person where the run continues.

## Common mistakes

- Do not start the engineer before the person approves the plan.
- Do not create a child item before the person approves the plan and answers the
  second question.
- Do not push before the person answers the push question.
- Do not start a unit before the unit that it depends on has a pull request.
- Do not use the default branch as the base of a child that has a
  `same_repo_parent`.
- Do not resume the engineer, QA, or UX persona of one unit for another unit.
- Do not ask for approval of a plan that you did not write in your reply.
- Do not answer an architect question for the person.
- Do not paraphrase the answers of the person. Quote them.
- Do not run more than `limits.max_qa_rounds` QA rounds for one unit.
- Do not send out-of-scope QA findings to the engineer.
- Do not mark the pull request ready if the person selected "leave it in draft".
- Do not set the item to `in_review` while the pull request is a draft.
- Do not stash, reset, or discard the changes of the person.
- Do not approve, merge, or request a reviewer on the pull request.
