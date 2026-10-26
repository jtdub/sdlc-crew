# Changelog

All notable changes to this project are in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added a CI step. The crew waits for the checks of the code host, and the engineer fixes failed checks, up to `limits.max_ci_rounds` rounds, before the pull request becomes ready.
- Added an evidence report of the engineer. It lists the framework code that the engineer read, the callers that it updated, and the real test output. QA spot-checks it.
- Added a result for each acceptance criterion in the QA report: pass, fail, or unverified, with evidence.
- Added an accessibility check with axe-core and a keyboard-only check to the user experience test.
- Added `ask` as a model value. The crew asks at the start of each run which model a role uses.
- Added a saved run in `~/.sdlc-crew/runs/<repo>/<ID>/`. A new session continues from the saved plan, or plans again and keeps the old files in an archive.
- Added the `sdlc-crew` workflow: one command takes a work item from a plain-language description or an issue to a pull request that is ready for a human to review.
- Added the `sdlc-setup` skill. It asks plain questions and writes the `.sdlc-crew.yaml` config file.
- Added `/sdlc-crew --feedback <PR>`. The crew reads the review comments of a pull request, fixes the valid ones, and replies to each comment.
- Added a git worktree for each pull request. Your own checkout keeps its branch and its files. Set `forge.worktree_dir` to change the place.
- Added the `install.sh` script. It installs the skills and the persona agents for Claude Code, Codex CLI, Gemini CLI, and GitHub Copilot.
