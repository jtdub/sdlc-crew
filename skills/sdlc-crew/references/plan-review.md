# Plan review with fresh reviewers

The architect writes the plan after a long conversation with the person. That
conversation holds assumptions that the plan does not state. A reviewer that did not
see the conversation reads only the plan and the code that it cites. It finds those
assumptions before the person approves the plan.

This is the "goldfish" review of the Elephant-Goldfish Model (EGM). The architect is
the elephant: it has the full context. Each reviewer is a goldfish: it starts with no
history. See <https://github.com/google/elephant-goldfish-model>.

## Who runs it

The orchestrator runs the review, not the architect. A persona cannot always start a
subagent of its own, and the reviewers must not share the context of the architect.

## Select the mode

Read `plan_review` from `.sdlc-crew.yaml`. Record the mode that you use in
`RUN_DIR/run.md`.

| Value | Mode |
|---|---|
| `auto` | `egm` if the EGM reviewers are installed. Otherwise `fresh`. |
| `egm` | The EGM reviewers. If they are not installed, tell the person how to install EGM, and use `fresh` for this run. |
| `fresh` | The built-in reviewer of "Fresh mode". |
| `none` | No review. Record "Plan review: off". |

A review in the same context is not a fresh review. If the delegation mode is inline,
do not do the review. Record "Plan review: not run, the harness has no subagents",
and tell the person in one sentence.

### Find the EGM reviewers

- Claude Code: the agent types `egm:egm-implementation-readiness`,
  `egm:egm-codebase-details`, `egm:egm-design`, and `egm:egm-comprehension` exist when
  the `egm` plugin is installed. The agent tool lists them.
- Other harnesses: find the EGM install directory. It holds
  `agents/implementation_readiness.md` and `resources/document_standards/`. Look in
  the plugin directories of the harness, for example `~/.codex/plugins/`,
  `~/.gemini/config/plugins/egm/`, and `~/.claude/plugins/`. Call the path
  `EGM_DIR`.

If neither is found, EGM is not installed.

## Prepare the reading list

Write `RUN_DIR/plan-review/context.md`. It lists the absolute paths that a reviewer
may read:

- `RUN_DIR/plan.md`.
- Each file of the "Verified at" column of the reuse survey.
- Each file of the "Design" section that exists.
- The repository instructions: `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, if they
  exist.

Do not add the transcript, the questions, or the answers. The "Decisions" section of
the plan holds the answers that the plan depends on.

## EGM mode

Start these reviewers at the same time. Give each one the same first message:

```text
Review the document <RUN_DIR>/plan.md. It is an implementation plan for one pull
request. Read every file in <RUN_DIR>/plan-review/context.md before you write a
finding. Use only those files. Apply the standard <standard>. Return your findings
only. Do not edit any file.
```

| Reviewer | Standard | Plan sections |
|---|---|---|
| `egm-design` | `feature-spec-standard` | Problem to Edge cases |
| `egm-comprehension` | none | All |
| `egm-implementation-readiness` | `implementation-readiness-standard` | Reuse survey to Changelog |
| `egm-codebase-details` | `implementation-readiness-standard` | Reuse survey and Design |

Add the plan sections to the message of each reviewer: "Review these sections only:
<sections>."

- Claude Code: use the agent type `egm:<reviewer>`. The standard resolves inside the
  plugin.
- Other harnesses: start a general-purpose subagent. Begin the message with "First
  read `<EGM_DIR>/agents/<file>.md` and follow it." Use the file whose `name` is the
  reviewer. Give the standard as
  `<EGM_DIR>/resources/document_standards/<standard>.md`.

Write each reply to `RUN_DIR/plan-review/<reviewer>.md`.

## Fresh mode

Start one general-purpose subagent with `models.review` and no earlier context. Give
it this message:

```text
You review an implementation plan. You did not see the conversation that produced it.
Read <RUN_DIR>/plan.md, then every file in <RUN_DIR>/plan-review/context.md. Use only
those files. Do not edit any file.

Report each of these problems that you find:

1. An assumption that the plan needs but does not state.
2. An acceptance criterion that a test cannot prove, or that two engineers can read
   in two different ways.
3. A reuse survey row whose "Verified at" citation does not show the mechanism that
   the row names.
4. A design decision that the plan leaves to the engineer.
5. A test plan item that does not prove the criterion or the edge case that it names.
6. An acceptance criterion or a "handle now" edge case that no test plan item covers.
7. A term that the plan uses but does not explain.
8. A risk that the plan does not name: data loss, security, cost, or a break of an
   existing caller.

For each problem give: a number, BLOCKER or MAJOR or MINOR, the plan section, the
evidence (a quote or a path:line), and the change that fixes it. If you find no
problem in a category, do not mention the category. Do not praise the plan.
```

Write the reply to `RUN_DIR/plan-review/fresh.md`.

## Merge the findings

Write `RUN_DIR/plan-review.md`:

```markdown
# Plan review

Mode: <egm | fresh>

| # | Priority | Section | Finding | Evidence | Suggested change | Source |
|---|---|---|---|---|---|---|
```

- Map the EGM priorities: Blocker is BLOCKER, Major is MAJOR, Nit is MINOR.
- Merge two findings that name the same problem. List both sources.
- Drop a finding that only asks for more words, praise, or style.

If no finding remains, record "Plan review: no findings" and go back to the skill.

## Resolve the findings

Resume the architect with the path of `RUN_DIR/plan-review.md` and this instruction:
"Resolve the plan review findings. Follow Step 4.2." The architect returns
`STATUS: PLAN` or `STATUS: QUESTIONS`. Ask the questions as Step 1.1 of the skill
says, then resume the architect with the answers.

Do one review for each plan. Do not review the resolved plan again, unless the person
asks for it. If the person changes the plan in the approval step, do not review
again.
