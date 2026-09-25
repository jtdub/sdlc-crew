# sdlc-crew

A crew of four AI personas that builds software the careful way, for people who are
not software developers, and for developers who want the same discipline every time.

You describe what you want in plain words. The crew asks a few questions, writes a
plan, waits for your approval, builds the change with tests, reviews it, tests it as a
user, and opens a pull request for you to read and accept. Nothing changes in your
code before you approve the plan. Nothing merges without you.

```text
/sdlc-crew "Add a page that lists my recipes, with a search box"
```

The crew works in Claude Code, Codex CLI, Gemini CLI, GitHub Copilot CLI, and any
other tool that loads [Agent Skills](https://agentskills.io). It tracks work in a
file in your repository, in GitHub Issues, GitLab Issues, Jira, or Bitbucket. It
uses the models that your tool already has.

## If this is your first software project

You do not need to know git, pull requests, or tests. The crew explains each of these
the first time it comes up, in one sentence. It also adds the things a project needs
that nobody tells a beginner about: a place for secrets that is not in the code, a
test setup, a check that runs the tests on each change, and a license. It tells you
what it added and why.

The crew never deletes data, spends money, or publishes your code without a warning
first and your answer.

## Install

You need `git` and one of the supported tools. Open a terminal and run:

```bash
git clone https://github.com/jtdub/sdlc-crew.git ~/sdlc-crew
~/sdlc-crew/install.sh
```

The script finds the tools on your computer and installs the crew for each one. Start
a new session of your tool afterwards. To update later, run `git -C ~/sdlc-crew pull`.
The install uses links, so the update is immediate.

Claude Code users can install the plugin instead:

```text
/plugin marketplace add jtdub/sdlc-crew
/plugin install sdlc-crew@sdlc-crew
```

With the plugin, the commands have a prefix: `/sdlc-crew:sdlc-setup` and
`/sdlc-crew:sdlc-crew`.

## First run

Open your project in your tool. If you do not have a project yet, make an empty
folder, run `git init` in it, and open that. Then run:

```text
/sdlc-setup
```

The setup asks how much software development you have done, where you want to keep
the list of things to build, and how the project runs. It writes one file,
`.sdlc-crew.yaml`, and explains each value. Then:

```text
/sdlc-crew "what you want, in your own words"
```

In Codex CLI, Gemini CLI, and Copilot CLI, type the same thing without the slash,
for example `use the sdlc-setup skill` and `use the sdlc-crew skill: "what you
want"`.

## What happens in a run

```text
You describe the change, or name a work item
   │
   ▼
Architect ◄──► You         questions until nothing is unclear, then plan approval
   │  plan posted to the work item; a large change splits into child items
   ▼
┌─ for each work item, in dependency order ────────────────────────────────────
Engineer                   branch, test first, smallest change, draft pull request
   │
   ▼
QA ◄──► Engineer           review against the plan and a security checklist,
   │                       fix all in-scope findings, up to 3 rounds
   ▼
UX                         uses the app as a user, screenshots in the pull request
   │
   ▼
Pull request ready for you ──► work item set to In Review
└──────────────────────────────────────────────────────────────────────────────
   │
   ▼
Retrospective posted to the work item, with one lesson for you
```

| Persona | Skill | What it does |
|---|---|---|
| Software architect | `sdlc-architect` | Checks that the request is complete. Asks why. Finds code that already exists. Offers options with cost and value. Writes the plan. |
| Software engineer | `sdlc-engineer` | Writes a test, then the smallest code that passes it. Adds the project basics that are missing. Opens a draft pull request. Fixes findings. |
| Quality assurance | `sdlc-qa` | Reviews the change against the plan and a security checklist. Sends only in-scope findings to the engineer. |
| User experience | `sdlc-ux` | Starts the app and uses the change as a person does. Takes screenshots. Writes what changes for the user. |

Two more skills stand alone:

- `sdlc-setup` — the first-run setup. Run it again with `--change tracker` or
  `--change models` to change one part.
- `sdlc-review` — one consolidated review of any pull request or branch, with
  findings you can post as comments.

## Where the work is tracked

| `tracker.kind` | What it needs | Notes |
|---|---|---|
| `local` | Nothing | A `BACKLOG.md` file in the repository. The default. |
| `github` | `gh`, logged in | Issues of the repository. Labels hold the status. Child items are sub-issues. |
| `gitlab` | `glab`, logged in | Issues of the project. Labels hold the status. |
| `jira` | `acli` or `jira`, logged in | Any project. Set the site URL and the project key in the setup. |
| `bitbucket` | An app password in the environment | Bitbucket Cloud issues. Most Bitbucket users choose `jira` here and `bitbucket` as the code host. |

The code host (`forge.kind`) is `github`, `gitlab`, `bitbucket`, or `none`. With
`none`, the crew makes branches on your computer and opens no pull request. That is
fine for a first project.

## Tools and models

| Tool | Skills | Personas | How the crew runs |
|---|---|---|---|
| Claude Code | `~/.claude/skills/` or the plugin | `~/.claude/agents/` | Each persona is a subagent. The orchestrator relays questions. |
| Codex CLI | `~/.agents/skills/` | `~/.codex/agents/*.toml` | Subagents when `[agents] enabled = true` in `config.toml`, otherwise inline. |
| Gemini CLI | `~/.agents/skills/` | `~/.gemini/agents/` | Subagents. |
| GitHub Copilot CLI | `~/.agents/skills/` | `~/.copilot/agents/` | Inline: the orchestrator plays each persona in turn. |
| Any other Agent Skills tool | Its skills directory | Not needed | Inline. |

Models are set per role in `.sdlc-crew.yaml`: `plan` for the architect, `build` for
the engineer, `review` for QA and UX. The default, `inherit`, uses the model of your
session, so the crew works with any provider your tool supports, including
OpenRouter and self-hosted models. The setup helps you choose a stronger model for
`plan` and `review` when your tool has one.

## Rules the crew keeps for you

- Nothing changes in the code before you approve the plan.
- Each pull request is small enough to read: 500 changed lines or less. A larger
  change becomes several pull requests, in order.
- Every change in behavior has a test.
- No secret goes into the code. Secrets come from environment variables.
- Before an action that deletes data, costs money, or pushes code where others can
  see it, the crew states the risk and asks.
- The crew never merges, approves, or requests a reviewer. You do.
- Every message to you is in plain, short sentences. Technical names come last, in
  parentheses.

## Layout

```text
skills/                 the single source of truth, one Agent Skill per directory
  sdlc-crew/            the orchestrator, its references, and the templates (assets/)
  sdlc-setup/
  sdlc-architect/
  sdlc-engineer/
  sdlc-qa/
  sdlc-ux/
  sdlc-review/
adapters/               thin per-tool files that point at the skills
.claude-plugin/         the Claude Code plugin and marketplace manifests
install.sh              links the skills and the adapters; renders the Codex agents
uninstall.sh
tests/
```

## Uninstall

```bash
~/sdlc-crew/uninstall.sh
```

The script removes only the links and the files that the install created.

## Frequently asked questions

**Does the crew need an account with an AI provider?** No account beyond the one
your tool already uses. The crew is a set of instructions for the tool you have.

**Can I use it on an existing project?** Yes. Run `/sdlc-setup` in the project. The
architect reads the code before it plans.

**What if I do not like the plan?** Say what to change. The architect writes a new
plan. Nothing happens until you approve one.

**What if the crew gets stuck?** It stops and tells you why, in plain words, with the
options. You can also close the session. The next `/sdlc-crew <ID>` continues from
the last work unit that has no pull request.

**Is my code sent anywhere?** Only where your tool already sends it, and to your code
host when the crew pushes a branch, after it asks.

## License

Apache-2.0. See `LICENSE`.
