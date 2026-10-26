# Models: which model plays which role

The crew has three roles for models. `.sdlc-crew.yaml` maps each role to a model
name that the harness accepts, or to `inherit`.

| Role | Personas | What it needs |
|---|---|---|
| `plan` | architect | The strongest model that the person can use. It reads code, asks the questions, and makes the design decisions. |
| `build` | engineer | A fast model that follows a plan and writes tests and code. A mid-tier model is enough when the plan is good. |
| `review` | QA, UX, `sdlc-review` | A strong model. It must find what the engineer missed. |

`inherit` means the model of the current session. It is the default, because it works
in every harness without configuration.

## How to pass the model

| Harness | Where the model goes |
|---|---|
| Claude Code | The `model` argument of the `Agent` tool when the orchestrator starts the persona. In inline mode, the session model. |
| Codex CLI | The `model` key of the persona agent TOML. `install.sh` writes the value from the config when you run it with `--project`. Otherwise `default_subagent_model` in `config.toml`. |
| Gemini CLI | The `model` key in the persona agent frontmatter. |
| GitHub Copilot | The `model` key in the persona agent frontmatter, where the client supports it. |
| Other | The session model. Tell the person which role runs now, so they can switch the model by hand if they want. |

## Choose a model

`sdlc-setup` asks the person. Give this guidance in plain words:

- If the person does not know, keep `inherit` for all three roles.
- If the harness has a model picker with tiers, put the top tier on `plan` and
  `review`, and the middle tier on `build`.
- Do not name a model version in a persona file. Model names change. The config file
  is the only place for them.
- For a provider that the harness reaches through OpenRouter or a custom endpoint,
  the model name is the provider's name for it, for example `anthropic/claude-sonnet-5`
  on OpenRouter. The harness must already be configured for that provider. The crew
  does not configure providers.

## Ask at each run

`ask` is for work where the data rules of a customer or a project limit which model
can read the work item and the code. The person decides at the start of each run,
because the rules can differ from one work item to the next.

1. At Step 0 of `sdlc-crew`, ask: "Which model does the <role> use for <ID>?" Offer
   the model names that the harness accepts, if it can list them, and "The model of
   this session". Do not mark an option as recommended. The person knows the rules;
   the crew does not.
2. Tell the person in one line which model each role uses.
3. Use the answer for every start of a persona of that role in this run.
4. If the harness cannot pass a model when it starts a persona, tell the person the
   chosen model, and ask them to switch the session model by hand before the persona
   starts.

## Fallback

If a persona start fails because the model is not available, or a usage limit is
reached:

1. If the value of the role is `ask`, do not choose a model for the person. Tell the
   person the error, and ask which model to use, or whether to stop the run. The run
   directory stays, so a later run can continue.
2. Otherwise, start the persona again with `inherit`. Tell the person which role
   changed and why. Use `inherit` for that role for the rest of the run.
