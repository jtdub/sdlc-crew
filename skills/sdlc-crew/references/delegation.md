# Delegation: how the orchestrator runs a persona

The `sdlc-crew` skill is the orchestrator. It runs in the session of the person. A
persona is a skill: `sdlc-architect`, `sdlc-engineer`, `sdlc-qa`, or `sdlc-ux`. The
orchestrator runs a persona in one of two modes. Pick the mode once at the start of
the run, and record it in `RUN_DIR/run.md`.

## Subagent mode

The harness can start a subagent from a persona definition, wait for its reply, and
send it a follow-up message with its context intact. Use this mode when it is
available. The persona works in its own context, so the orchestrator context stays
small, and the person can read the orchestrator replies.

Rules:

- Start each persona with the agent tool of the harness and the persona name. The
  install put a persona definition in the place that the harness reads.
- Give the persona every value that it needs in the first message: the work item ID,
  the absolute path of `RUN_DIR`, the repository path, the base branch, and the
  values from `.sdlc-crew.yaml` that the persona skill lists.
- A persona cannot talk to the person. When the persona returns `STATUS: QUESTIONS`,
  ask the person, then send the answers back to the same persona instance. Quote the
  words of the person. Do not summarize them.
- Record the instance name or id of each persona. Reuse it for the follow-ups of the
  same work unit. Start a new instance for a new work unit.
- If the harness cannot resume a persona instance, start a new instance with the same
  first message, plus every question and answer so far, quoted, plus the paths of the
  files that the earlier instance wrote in `RUN_DIR`.
- If a start fails because the persona definition is missing, or the model of the
  role is not available, fall back to inline mode for that persona. Tell the person.

## Inline mode

The harness has no subagents, or the subagent start failed. The orchestrator loads
the persona skill and plays the role itself, one persona at a time.

Rules:

- Before you play a persona, say in one line which persona speaks now.
- Follow the persona skill from its first step. Write the same files to `RUN_DIR`.
  Begin the reply of the persona with the same `STATUS:` line.
- When the persona has questions, ask the person directly. Then continue as the
  persona with the answers.
- Do not mix two personas in one reply. Finish the reply of one persona before the
  orchestrator speaks again.
- QA and the engineer are different roles. When QA reviews, do not fix. When the
  engineer fixes, do not review. Write the QA report to a file before the engineer
  reads it, so the two roles talk through the file as they do in subagent mode.

## Harness notes

| Harness | Mode | How to start a persona | How to resume | How to ask the person |
|---|---|---|---|---|
| Claude Code | Subagent | The `Agent` tool with `subagent_type` set to the persona name, for example `sdlc-architect`. Pass `model` from `.sdlc-crew.yaml` when the value is not `inherit`. | `SendMessage` to the agent id. | `AskUserQuestion` for questions with options, up to four in one call. Plain text for open questions. |
| Codex CLI | Subagent, when `[agents] enabled = true` in `config.toml` | Ask Codex to have the named agent do the task, for example "Have sdlc-architect do this: ...". | Send a follow-up to the same agent thread. If the thread is gone, start a new one with the transcript. | Plain text. Codex asks the person from the parent thread. |
| Gemini CLI | Subagent | The subagent appears as a tool named after the persona. Call it with the task. | Gemini subagents run to completion. Start a new one with the transcript. | Plain text. |
| GitHub Copilot CLI | Inline | `/agent sdlc-crew` selects the orchestrator for the session. The personas are custom agents, but the orchestrator plays them inline. | Not needed. | Plain text. |
| Other harness with Agent Skills | Inline | Load the persona skill. | Not needed. | Plain text. |

## Questions to the person

The architect and the other personas write each question with a short header, and
with two to four options when the answer is a choice. The recommended option comes
first and is marked `(Recommended)`.

- With a question tool: put up to four questions in one call. Keep the recommended
  option first. The person can always type a different answer.
- Without a question tool: write the questions as a numbered list. Put the options
  under each question with letters. Ask the person to reply with the number and the
  letter, or with their own words. Then stop the turn and wait.

For `person.experience: new`, add one sentence under a question that uses a term the
person has not seen in this run, with the meaning of the term.

## The STATUS protocol

Every persona reply starts with one line: `STATUS: <WORD>`. The orchestrator reads
that line first. The words for each persona are in its skill. A reply without a
`STATUS:` line is a defect. Ask the persona to reply again with the line.
