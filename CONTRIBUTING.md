# Contributing

## What this repository holds

The `skills/` directory is the single source of truth. Each persona and each command
is one skill in the [Agent Skills](https://agentskills.io/specification) format. The
`adapters/` directory holds thin files that point a harness at those skills.
`install.sh` links or renders them.

Do not put persona text in an adapter. Put it in the skill, and let the adapter point
at it.

## Verified facts about the harnesses

Check these against the official documentation when you change an adapter. Record
the date.

| Harness | Skills directory | Agent files | Verified |
|---|---|---|---|
| Claude Code | `~/.claude/skills/<name>/SKILL.md`; plugin `skills/` | `~/.claude/agents/<name>.md`; plugin `agents/`; frontmatter `name`, `description`, `model`, `tools`, `disallowedTools`, `skills` | 2026-09-25 |
| Codex CLI | `~/.agents/skills/<name>/SKILL.md`; repo `.agents/skills/` | `~/.codex/agents/<name>.toml`; repo `.codex/agents/`; keys `name`, `description`, `developer_instructions`, `model` | 2026-09-25 |
| Gemini CLI | `~/.gemini/skills/` or `~/.agents/skills/`; repo `.gemini/skills/` or `.agents/skills/` | `~/.gemini/agents/<name>.md`; repo `.gemini/agents/`; frontmatter `name`, `description`, `tools`, `model`, `max_turns` | 2026-09-25 |
| GitHub Copilot | `~/.copilot/skills/` or `~/.agents/skills/`; repo `.github/skills/`, `.claude/skills/`, `.agents/skills/` | repo `.github/agents/<name>.agent.md`; frontmatter `name`, `description`, `tools`, `model` | 2026-09-25 |

Sources: agentskills.io/specification, code.claude.com/docs/en/skills and
/sub-agents and /plugins, learn.chatgpt.com/docs/build-skills and
/agent-configuration/subagents, geminicli.com/docs/cli/skills and
/core/subagents, docs.github.com/en/copilot/concepts/agents/about-agent-skills and
the custom agents page.

## Style

- Write all documentation and all persona prose in ASD-STE100 Simplified Technical
  English: short sentences, active voice, one word for one meaning.
- Keep each `SKILL.md` under 500 lines. Move detail to `references/`.
- Shell scripts are POSIX `sh`. Run `shellcheck -s sh` on them.
- No runtime dependency. A person installs with one shell command.

## Tests

```bash
tests/validate_skills.sh
tests/install_test.sh
shellcheck -s sh install.sh uninstall.sh
shellcheck tests/*.sh
claude plugin validate --strict .claude-plugin/plugin.json
```

`tests/validate_skills.sh` runs the reference validator through
`uvx --from skills-ref agentskills validate <skill>` when `uvx` is installed. Without
`uvx`, only the built-in checks run.

## Pull requests

Use the template. Fill `# Closes:` with the issue, or `DNE` when there is none. Add
one line to `CHANGELOG.md` under `## [Unreleased]` when the change is visible to a
person who uses the workflow.
