# Prose pass: remove AI writing patterns

A person reads the pull request body, the work item comments, and the replies to
reviewers. Text that sounds generated makes the reader trust it less. The prose pass
removes those patterns before the text goes out.

The pass uses the `humanizer` skill when the harness has it. See
<https://github.com/blader/humanizer>.

## Which text gets the pass

| Text | Who runs the pass |
|---|---|
| `RUN_DIR/pr-body.md` | The engineer, before Open PR and before each Update PR |
| The UX sections of the pull request body | UX, before Update PR |
| `RUN_DIR/tracker-plan-comment.md` and `RUN_DIR/tracker-retro-comment.md` | The architect, before it returns |
| `RUN_DIR/feedback/replies.md` | The orchestrator, before it shows the replies |

QA does not change text. QA reports a pattern as a finding. See "QA check".

## Rules that always apply

- ASD-STE100 Simplified Technical English wins over the pass. Keep the sentences
  short, active, and in a simple tense. If a rewrite breaks a rule of STE, use the
  STE form.
- Do not change a fact, a name, a number, a link, a `path:line`, a commit hash, an
  acceptance criterion ID, or a quote of the person.
- Do not change code blocks, inline code, commands, file paths, or the headings and
  the checklist of the pull request template.
- Do not add an opinion, a joke, or a reaction. The text is technical.

## With the humanizer skill

Invoke the `humanizer` skill. Give it the text, not the file path, so that it returns
a rewrite and does not edit a file. Add this instruction:

```text
This is technical text in ASD-STE100 Simplified Technical English. Keep the STE
rules: sentences of 20 words or less for an instruction and 25 for a description,
active voice, simple tenses, one word for one meaning. Keep every fact. Return only
the final text.
```

Read the rewrite. Check it against "Rules that always apply". Write it back to the
file.

## Without the humanizer skill

Read the text once, and remove these patterns:

1. A contrast that only adds weight: "This is not just X, it is Y."
2. A closing line that repeats the point of the paragraph.
3. An opening that announces the content: "Here is what changed:".
4. A list of three where the meaning needs one or two.
5. Words that inflate a plain fact: "pivotal", "seamless", "robust", "comprehensive",
   "powerful", "crucial".
6. Bold labels at the start of each bullet, when the bullet is one fact.
7. Chat leftovers: "I hope this helps", "Let me know", "Great question".
8. A dash that joins two clauses. Use two sentences.

Record in the report which one you used: `humanizer` or the built-in list.

## QA check

QA reads the prose that the diff adds and the pull request body. That includes
documentation, docstrings, comments, and the body. For each pattern of "Without the
humanizer skill", add a SHOULD FIX finding with the `path:line` or the body section,
the pattern number, and a rewrite. If the `humanizer` skill is available, QA can give
it the text to get the rewrite. QA does not write to the file.
