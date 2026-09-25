---
name: sdlc-setup
description: First-run setup of the sdlc-crew workflow for a repository. Detects the harness, the git remote, and the installed tools, asks a few plain questions about who uses it, where the work is tracked, and how the project runs, then writes the .sdlc-crew.yaml config file and, for the local tracker, the BACKLOG.md file. Use when the person runs /sdlc-setup, when .sdlc-crew.yaml is missing, or when the person wants to change the tracker, the forge, or the models.
license: Apache-2.0
compatibility: Needs git.
metadata:
  author: sdlc-crew
  role: orchestrator
---

This skill sets up `sdlc-crew` for the current repository. It asks a few questions in
plain words, and it writes `.sdlc-crew.yaml`. The keys are in
`../sdlc-crew/references/config-schema.md`. Read that file first.

Write all prose in ASD-STE100 Simplified Technical English. Follow
`../sdlc-review/references/plain-language.md`.

`$ARGUMENTS`: optional. `--change <section>` asks the questions of one section only,
and keeps the other values of the existing file.

## Step 1 — Look around

Run these checks. Do not show the raw output. Use the results in the questions.

```bash
git rev-parse --show-toplevel
git remote get-url origin
git symbolic-ref --short refs/remotes/origin/HEAD
ls
command -v gh glab acli jira docker npx uvx
gh auth status
glab auth status
acli jira auth status
```

From the results, know:

- `REPO_DIR`, and whether the repository is empty (no commit, or only a README).
- The forge from the `origin` URL: `github.com` gives `github`, `gitlab` in the host
  gives `gitlab`, `bitbucket.org` gives `bitbucket`, no remote gives `none`.
- Which CLIs are installed and logged in.
- The project type from the files: `package.json`, `pyproject.toml`,
  `requirements.txt`, `go.mod`, `Cargo.toml`, `Gemfile`, `composer.json`,
  `compose.yaml`, `Dockerfile`.
- The run and test commands from `package.json` scripts, `Makefile`, `Taskfile.yml`,
  `justfile`, or `README.md`.

If `.sdlc-crew.yaml` exists, read it. The existing values are the defaults for the
questions.

## Step 2 — Ask

Ask the questions with the question tool of the harness, or as a numbered list. Put
the recommended option first. Ask at most four questions in one turn. Skip a question
whose answer is certain from Step 1, and say what you assumed.

### Section `person`

1. **[You]** "How much software development have you done?" Options: "I am new to
   it (Recommended if unsure) — the crew explains each term and adds safety steps",
   "Some — the crew explains uncommon terms only", "I am a professional — no
   explanations".

### Section `tracker`

2. **[Tracking]** "Where do you want to keep the list of things to build?" Options,
   in this order when the CLI for each is installed and logged in, otherwise with
   "(needs setup)" after the name:
   - "A file in this repository (Recommended for a personal project) — no account
     needed; the crew keeps a BACKLOG.md file"
   - "GitHub Issues — the issues page of this repository"
   - "GitLab Issues"
   - "Jira — asks for the site URL and the project key next"
   - "Bitbucket issues"
3. For Jira: "What is the URL of your Jira site, and the project key?" Explain: "The
   project key is the letters before the dash in an issue number, such as PROJ in
   PROJ-12."
4. For a tracker other than local, when the status names of the project are known
   from the tracker, show them and ask which ones mean To Do, In Progress, and In
   Review. Otherwise keep the defaults and say so.

### Section `forge`

5. **[Code host]** Confirm the forge from the remote in one sentence. If there is no
   remote: "Your code is only on this computer. Do you want the crew to put it on a
   code host, so it is backed up and you can review changes on a web page?" Options:
   "Not now (Recommended) — the crew makes branches on this computer only", "Yes,
   GitHub — I will create the repository, or the crew can with `gh repo create`".
6. For `person.experience: new`, explain in one sentence what a pull request is, and
   that the crew opens one for each change and never merges it.

### Section `models`

7. **[Models]** Read `../sdlc-crew/references/models.md`. Ask: "Which model should
   each role use?" Options: "The model of this session for every role
   (Recommended)", "Let me choose per role". For the second option, ask for `plan`,
   `build`, and `review` with the model names that the harness accepts, and the
   guidance of `models.md`.

### Section `project`

8. **[Run]** "How do you start the app on this computer?" Offer the command from
   Step 1 as the first option, "The project has no app to run yet", and "Other".
9. **[Test]** "How do you run the tests?" Offer the command from Step 1, "There are
   no tests yet (the crew adds a test setup with the first change)", and "Other".
10. **[URL]** If there is a run command: "Which address shows the app after it
    starts?" Offer the URL from the project files, or `http://localhost:3000`.
11. **[Changelog]** If `CHANGELOG.md` exists or `[tool.towncrier]` is in
    `pyproject.toml`, detect the type and confirm. Otherwise ask: "Do you want a
    changelog, a file that lists what changed in each release, in plain words?"
    Options: "Yes, Keep a Changelog format (Recommended)", "No".

### Section `limits`

Do not ask. Keep the defaults. Mention them in one sentence at the end.

## Step 3 — Write the files

1. Write `.sdlc-crew.yaml` at `REPO_DIR`. Start from `../sdlc-crew/assets/sdlc-crew.yaml`, and set each value from the
   answers. Keep the comments of the template, so the person can edit the file later.
2. For `tracker.kind: local`, copy `../sdlc-crew/assets/BACKLOG.md` to `REPO_DIR/BACKLOG.md`
   if it does not exist.
3. If the repository has no `.gitignore`, add one with the common entries of the
   project type and `.sdlc-crew-run/`. If it has one, add `.sdlc-crew-run/` when it
   is missing.
4. If the repository has no `AGENTS.md`, offer `../sdlc-crew/assets/AGENTS.md` as a starter, and write it if the person agrees.
5. Show the person the file `.sdlc-crew.yaml` and the meaning of each value in one
   line each.
6. Ask whether to commit the new files with the message
   `Add the sdlc-crew configuration`. Commit only if the person agrees. Do not push.

## Step 4 — Check the tools

For each tool that the chosen tracker and forge need, check that it is installed and
logged in. If one is not, give the install command and the login command, in a code
block, with one sentence for each. Do not install a tool. Do not run a login.

| Need | Install | Login |
|---|---|---|
| `gh` | `brew install gh` or see https://cli.github.com | `gh auth login` |
| `glab` | `brew install glab` or see https://gitlab.com/gitlab-org/cli | `glab auth login` |
| `acli` | see https://developer.atlassian.com/cloud/acli/ | `acli jira auth login` |
| `docker` | see https://docs.docker.com/get-docker/ | none |

End with: "Setup is complete. Start a change with `/sdlc-crew "<what you want>"`."
Give one example that fits the project.
