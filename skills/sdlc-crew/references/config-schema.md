# The `.sdlc-crew.yaml` file

The workflow reads `.sdlc-crew.yaml` from the root of the repository. If the file
does not exist, the orchestrator runs the `sdlc-setup` skill first.

Read the file with a tool that shows the text. Do not assume a value that the file
does not set. Each key has the default in the table.

## Keys

| Key | Default | Meaning |
|---|---|---|
| `version` | `1` | The schema version of this file. |
| `person.experience` | `new` | `new`, `some`, or `professional`. See "Experience levels". |
| `tracker.kind` | `local` | `local`, `github`, `gitlab`, `jira`, or `bitbucket`. Selects the file in `trackers/`. |
| `tracker.url` | `""` | The base URL of a Jira site or a self-hosted GitLab. Empty for GitHub, GitLab.com, and Bitbucket Cloud. |
| `tracker.project` | `""` | The Jira project key, the GitLab project path, or the Bitbucket `workspace/repo`. Empty for `local` and `github`. |
| `tracker.statuses.todo` | `To Do` | The status name for new work. |
| `tracker.statuses.in_progress` | `In Progress` | The status name while the crew works. |
| `tracker.statuses.in_review` | `In Review` | The status name when the pull request is ready. |
| `tracker.statuses.done` | `Done` | The status name after the merge. The workflow does not set it. |
| `tracker.child_issue_type` | `Subtask` | The issue type for a child issue in Jira. Other trackers ignore it. |
| `forge.kind` | `github` | `github`, `gitlab`, `bitbucket`, or `none`. Selects the file in `forges/`. |
| `forge.repo` | `""` | `owner/name`. Empty means: read it from the `origin` remote. |
| `forge.default_branch` | `""` | Empty means: ask the forge. |
| `forge.branch_pattern` | `sdlc/{id}-{slug}` | `{id}` is the work item ID in lowercase. `{slug}` is the summary, lowercase, words joined with `-`, 40 characters or less. |
| `forge.assign_to_me` | `true` | Assign the pull request to the account that runs the workflow. |
| `models.plan` | `inherit` | The model of the architect. |
| `models.build` | `inherit` | The model of the engineer. |
| `models.review` | `inherit` | The model of QA, UX, and `sdlc-review`. |
| `project.run_command` | `""` | The command that starts the application for a local test. |
| `project.test_command` | `""` | The command that runs the test suite. |
| `project.app_url` | `""` | The URL of the local application after `run_command`. |
| `project.changelog` | `none` | `none`, `keep-a-changelog`, or `towncrier`. |
| `project.screenshots` | `pr-comment` | `pr-comment`, `docs/screenshots`, or `none`. Where the UX persona puts screenshots. |
| `limits.max_pr_lines` | `500` | The maximum count of non-generated changed lines in one pull request. |
| `limits.max_qa_rounds` | `3` | The maximum count of QA review and fix rounds for one pull request. |

## Experience levels

The `person.experience` value changes the behavior of every persona:

| Behavior | `new` | `some` | `professional` |
|---|---|---|---|
| Explain a technical term the first time | Yes | Uncommon terms only | No |
| Options in one question | 2 or 3 | 2 to 4 | 2 to 4 |
| State the recommended option and the reason | Yes | Yes | Yes |
| Add missing project basics: `.gitignore`, README, license, tests, CI | Yes, and say so in one sentence | Yes, and say so | Ask first |
| WARNING gate before an action that deletes data, spends money, or pushes to a shared branch | Yes | Yes | Yes |
| Plain-language lesson at the end of the retrospective | Yes | Yes | Optional |

## Read the file

Read the file with the file tool of the harness, or with `cat .sdlc-crew.yaml`. Parse
it by eye. The file is small. Do not install a YAML parser for it.

If a key is missing, use the default. If a value is not in the accepted set, stop and
tell the person which key is wrong and which values are accepted.

## Environment variables for tokens

A tracker or a forge that has no CLI needs a token. The references name these
variables. Never write a token into `.sdlc-crew.yaml` or into any file in the
repository.

| Variable | Used by |
|---|---|
| `GITHUB_TOKEN` | GitHub REST fallback, when `gh` is not installed |
| `GITLAB_TOKEN` | GitLab REST fallback, when `glab` is not installed |
| `JIRA_EMAIL`, `JIRA_API_TOKEN` | Jira Cloud REST fallback |
| `JIRA_PAT` | Jira Server or Data Center REST fallback |
| `BITBUCKET_USER`, `BITBUCKET_APP_PASSWORD` | Bitbucket Cloud REST |
