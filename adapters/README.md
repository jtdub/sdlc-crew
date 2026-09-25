# Adapters

Each directory holds the thin files that point one harness at the skills in
`skills/`. `install.sh` links or renders them. No persona text lives here. If a
harness needs a change in behavior, change the skill.

| Directory | Harness | What `install.sh` does with it |
|---|---|---|
| `claude-code/agents/` | Claude Code | Links each file into `~/.claude/agents/`, or `.claude/agents/` with `--project`. The plugin manifest at the repository root also lists these files. |
| `codex/agents/` | Codex CLI | Renders each `.toml.tmpl` into `~/.codex/agents/<name>.toml`, or `.codex/agents/` with `--project`. The skill body goes into `developer_instructions`. |
| `gemini/agents/` | Gemini CLI | Links each file into `~/.gemini/agents/`, or `.gemini/agents/` with `--project`. |
| `copilot/agents/` | GitHub Copilot | Copies each file into `.github/agents/` with `--project`. Copilot reads repository agents only. |

The skills go to every harness in the same way: a link from the harness skills
directory to `skills/<name>`. `~/.agents/skills/` is shared by Codex, Gemini CLI, and
Copilot, so one link there serves all three.
