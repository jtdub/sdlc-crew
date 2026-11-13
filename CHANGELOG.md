# Changelog

All notable changes to this project are in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-11-12

### Added

- Added the `sdlc-loop` skill. Each pass fixes an open crew pull request or takes the next ready item to a pull request. Run it with `/loop /sdlc-loop`.
- Added the `loop` section to `.sdlc-crew.yaml`, with the labels, the pick order, and the lock timeout. Auto-merge stays off until you set `loop.auto_merge: true`.
- Added a review of the plan before you approve it, by reviewers that did not see the conversation. Set `plan_review`; the crew uses the `egm` plugin when it is installed.
- Added a pass that removes AI writing patterns from pull request bodies and comments. The crew uses the `humanizer` skill when it is installed.
- Added failed CI checks and merge conflicts to `/sdlc-crew --feedback`. The crew merges the base branch, fixes the checks, and waits for them again.
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
- Added `project.local_files`. The crew copies these local files, such as `.env`, into each new worktree, but only when git ignores them.
- Added two user experience checks: a form keeps what the user typed after an error, and each changed page works at the width of a phone.

### Changed

- Changed the secret scan of `sdlc-review` to read only the commits of the branch, so that it does not report a local `.env` file that git ignores.
- Changed the dependency audit of `sdlc-review` to report a finding only for a package that the change adds or updates.
