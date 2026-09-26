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

## Fallback

If a persona start fails because the model is not available, or a usage limit is
reached:

1. Start the persona again with `inherit`.
2. Tell the person which role changed and why.
3. Use `inherit` for that role for the rest of the run.
