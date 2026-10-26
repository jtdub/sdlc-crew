# Changelog

All notable changes to this project are in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
