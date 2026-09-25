# AGENTS.md

Instructions for AI coding agents that work in this repository.

## What this repository is

`sdlc-crew` is a set of Agent Skills and thin per-harness adapters. There is no
application code. The product is the text in `skills/`, the scripts `install.sh` and
`uninstall.sh`, and the tests in `tests/`.

## Rules

- `skills/` is the single source of truth. Never put persona instructions in an
  adapter. An adapter points at a skill.
- Keep every `SKILL.md` frontmatter to the six fields of the Agent Skills
  specification: `name`, `description`, `license`, `compatibility`, `metadata`,
  `allowed-tools`. `tests/validate_skills.sh` rejects any other key.
- Keep each `SKILL.md` under 500 lines. Put detail in `references/` and templates
  in `assets/`.
- Write all prose in ASD-STE100 Simplified Technical English. Short sentences,
  active voice, one word for one meaning. Explain a term the first time.
- Shell scripts are POSIX `sh`, checked with `shellcheck -s sh`. Tests are `bash`.
- Verify a claim about a harness against its official documentation before you
  write it, and record the date in `CONTRIBUTING.md`.
- Add one line to `CHANGELOG.md` under `## [Unreleased]` for a change that a person
  who uses the workflow notices.

## Test

```bash
tests/validate_skills.sh
tests/install_test.sh
shellcheck -s sh install.sh uninstall.sh && shellcheck tests/*.sh
claude plugin validate .
```
