---
name: sdlc-loop
description: Do one pass of the sdlc-crew loop. A pass acts on one open crew pull request, or takes the next ready work item through the sdlc-crew workflow to a pull request, then applies a merge gate. The harness repeats the pass, for example with /loop in Claude Code. Use when the person runs /sdlc-loop, or asks for one pass of the crew loop. Works with GitHub Issues or a local backlog file, and with GitHub or no forge.
license: Apache-2.0
compatibility: Needs git and python3. Needs gh, logged in, for tracker.kind github or forge.kind github. Works in Claude Code, Codex CLI, Gemini CLI, GitHub Copilot CLI, and any harness that loads Agent Skills.
metadata:
  author: sdlc-crew
  role: orchestrator
---

This skill does one pass of the crew loop. A pass does one of these, then ends:

- It acts on one open crew pull request.
- It takes the next ready work item to a pull request with the `sdlc-crew` skill.
- It finds nothing to do, and stops the loop.

The skill does one pass only. The harness repeats it:

| Harness | How to repeat the pass |
|---|---|
| Claude Code | `/loop /sdlc-loop`, or `/loop /sdlc-crew:sdlc-loop` with the plugin. Add an interval, such as `/loop 30m /sdlc-loop`, for a fixed time between passes. |
| Other harnesses | A scheduler of the harness, if it has one. Otherwise the person runs `use the sdlc-loop skill` again. |

The loop is not unattended. Each new item goes through `sdlc-crew`, and the crew asks
the person to approve each plan and the first push.

`$ARGUMENTS`: none.

Write all prose in ASD-STE100 Simplified Technical English. Follow
`../sdlc-review/references/plain-language.md` in every message to the person.

## Words in this skill

- **Crew pull request**: an open pull request whose head branch starts with the
  prefix of `forge.branch_pattern`. The prefix is the text before the first `{`, for
  example `sdlc/`.
- **End the pass**: remove the lock of this pass (Step 0.3), add one line to
  `LOOP_DIR/loop-log.md`, and stop. The harness starts the next pass. If the harness
  lets you set the time of the next pass, use the time that the step gives, or 30
  minutes.
- **Stop the loop**: remove the lock of this pass, add one line to the log, tell the
  person why the loop stopped, and do not ask the harness for a next pass. In Claude
  Code, do not schedule a next wakeup.

## References

- `../sdlc-crew/references/config-schema.md` — the keys of `.sdlc-crew.yaml`, with
  the `loop` section.
- `../sdlc-crew/references/trackers/github.md` and
  `../sdlc-crew/references/trackers/local.md` — the tracker operations.
- `../sdlc-crew/references/forges/github.md` — the forge operations.
- `../sdlc-crew/references/feedback.md` — which pull request comments are open.
- `scripts/ready_queue.py` — the script that keeps the ready label in step with the
  blockers and prints the queue.

## Step 0 — Pass guard

Do this step before anything else. A harness can start a pass while an earlier pass
still runs, for example while the crew waits for a plan approval. Two passes at one
time can start the same item twice.

### Step 0.1 — Read the config

1. Read `.sdlc-crew.yaml` from the repository root. If it does not exist, stop the
   loop. Tell the person to run `sdlc-setup` first.
2. Apply the defaults of `config-schema.md` for each missing key, also in `loop`.
3. If `tracker.kind` is not `github` or `local`, or `forge.kind` is not `github` or
   `none`, stop the loop. Tell the person that the loop supports GitHub Issues or a
   local backlog, and GitHub or no forge. Name the key and its value.
4. Set `LOOP_DIR` to `~/.sdlc-crew/runs/<repo>/`, where `<repo>` is the directory
   name of the repository. If the harness cannot write there, use `.sdlc-crew-run/`
   in the repository, as `sdlc-crew` Step 0 says. Set `LOCK` to
   `LOOP_DIR/loop.lock`.

### Step 0.2 — Check the lock

If `LOCK` does not exist, go to Step 0.3. Otherwise read it. It holds the lines
`pass:`, `item:`, and `started:`.

1. If the lock is younger than `loop.lock_stale_hours`, another pass runs. Do not
   change anything. Say in one line: "A pass for <item> runs since <started>. This
   pass ends with no action." Stop. Do not remove the lock, and do not write the log.
2. If the lock is older than `loop.lock_stale_hours`, the earlier pass probably
   stopped before its end. Do not remove the lock. Stop the loop, and tell the
   person:
   - The path of the lock, the item, and the start time.
   - What to check: the state of the item, and its pull request if it has one.
   - The command that removes the lock when they are satisfied: `rm "<LOCK>"`.

To find the age, run:

```bash
find "$LOCK" -mmin +$(( LOCK_STALE_HOURS * 60 ))
```

The command prints the path when the lock is older than the limit.

### Step 0.3 — Take the lock

Make a pass ID from the time and a random part, for example
`20261112-0930-4821`. Write the lock so that the write fails when the file exists:

```bash
mkdir -p "$LOOP_DIR"
( set -C; printf 'pass: %s\nitem: none\nstarted: %s\n' "$PASS_ID" \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$LOCK" ) 2>/dev/null
```

If the write fails, another pass took the lock first. Go to Step 0.2.

When the pass picks an item or a pull request, replace the `item:` line. Before you
remove the lock, read it. Remove it only if its `pass:` line is your `PASS_ID`.

### Step 0.4 — Check the tracker

Find each open item whose status is `tracker.statuses.in_progress`:

- GitHub: `gh issue list --state open --label "<in_progress>" --json number,title`.
- Local: each item in `BACKLOG.md` with `- Status: <in_progress>`.

For each one, look for an open crew pull request that closes it (Step 5). If an
item is in progress and has no crew pull request, a session works on it now, or a
session stopped before it opened the pull request. Tell the person in one line:
"<ID> is in progress with no pull request. The loop waits. Set the item back to
<todo> to let the loop take it." End the pass.

## Step 1 — Refresh the queue

1. Run `git fetch origin`. Do not switch the branch of the checkout of the person,
   and do not pull into it.
2. Run the script of this skill in the repository root. For the local tracker, use
   the worktree of the default branch as `--root`, as "Commits to `BACKLOG.md`" in
   `trackers/local.md` says.

   ```bash
   python3 "<this skill directory>/scripts/ready_queue.py" --apply
   ```

   The script adds `loop.ready_label` to each item whose blockers are all closed,
   and removes it from the others. It prints the queue: the ready items that nobody
   works on, in the order of `loop.order`. Without `--apply`, it changes nothing.
3. If the script fails, show its output. Stop the loop.

A blocker is an item that must close first:

| Tracker | Where the blockers are |
|---|---|
| `github` | A body line that starts with `Blocked by`, for example `Blocked by #12, #15`, and the "blocked by" issue dependencies of GitHub. |
| `local` | The line `- Blocked by: LOCAL-2, LOCAL-5` of the item in `BACKLOG.md`. |

## Step 2 — Act on the open crew pull requests first

With `forge.kind: none`, skip this step. List the open crew pull requests:

```bash
gh pr list --state open --json number,headRefName,isDraft,autoMergeRequest,statusCheckRollup,closingIssuesReferences \
  --jq '[.[] | select(.headRefName | startswith("<prefix>"))]'
```

Find the item of each pull request from `closingIssuesReferences`, or from the
branch name. Then do the first rule that applies:

1. A pull request has a failed check, a merge conflict, or an open comment. An open
   comment is one that F2 of `feedback.md` does not skip. Run the `sdlc-crew` skill
   with `--feedback <PR>`. End the pass.
2. A pull request is a draft, and its item has no `loop.needs_human_label`. The crew
   stopped before the end of the run. Run the `sdlc-crew` skill with the item ID, to
   continue the saved run. End the pass.
3. A pull request has auto-merge on, and a check still runs. End the pass. The next
   pass can start in 20 minutes.
4. Count the pull requests that wait for a person to merge them: each ready pull
   request whose item has `loop.human_merge_label`, and each ready pull request that
   the merge gate left for the person. If the count is `loop.max_waiting_human_merge`
   or more, stop the loop. List each pull request with its URL.

If no rule applies, go to Step 3.

## Step 3 — Pick the next item

Take the first item of the queue from Step 1 that no open pull request closes. The
queue already leaves out each item with a label of `loop.skip_labels`, and each
item in progress or in review.

- If no item is left and no crew pull request is open, stop the loop. Tell the
  person that the queue is empty.
- If no item is left and a crew pull request is open, end the pass. The next pass
  can start in 60 minutes.

Write the item ID to the `item:` line of the lock.

## Step 4 — Build it

Run the `sdlc-crew` skill with the item ID. The crew plans, asks the person to
approve the plan, builds, runs QA and UX, waits for CI, and marks the pull request
ready.

If the crew stops before the pull request is ready, for example on
`limits.max_qa_rounds`, on `limits.max_ci_rounds`, on a blocking plan finding, or
because the person stops it:

1. Add `loop.needs_human_label` to the item. For the local tracker, add the line
   `- Labels: <needs_human_label>` to the item, or add the label to that line.
2. Do the Comment operation of the tracker with the reason, in one or two
   sentences.
3. End the pass.

## Step 5 — Check that the pull request closes the item

With `forge.kind: none`, skip this step and Step 6. Tell the person the branch name.
End the pass.

```bash
gh pr view <PR> --json closingIssuesReferences --jq '[.closingIssuesReferences[].number]'
```

For the GitHub tracker, if the item number is not in the list, add the line
`Closes #<number>` to the pull request body with the Update PR operation. For the
local tracker, check that the `- Pull request:` line of the item holds the URL. If
it does not, do the Link PR operation.

## Step 6 — The merge gate

The loop never merges a pull request itself. It can ask GitHub to merge a pull
request after the required checks pass. Do the first rule that applies:

1. The item has `loop.human_merge_label`. Comment on the pull request: "This pull
   request needs a review and a merge by a person." Do not post the comment again
   if the pull request has it. End the pass.
2. Find out whether the base branch has required status checks. Run both:

   ```bash
   gh api "repos/{owner}/{repo}/branches/<base>/protection/required_status_checks" --jq '.contexts'
   gh api "repos/{owner}/{repo}/rules/branches/<base>" \
     --jq '[.[] | select(.type == "required_status_checks")] | length'
   ```

   The base branch has required checks if the first list is not empty, or the
   second count is more than 0. A failed call counts as no required checks.
3. The base branch has no required checks. Do not turn on auto-merge. Comment on the
   pull request: "Auto-merge stays off until <base> has required status checks. A
   person reviews and merges this pull request." Do not post the comment again if
   the pull request has it. End the pass.
4. The base branch has required checks. Run:

   ```bash
   gh pr merge <PR> --<loop.merge_method> --auto
   ```

   GitHub merges the pull request when the checks pass, and the merge closes the
   item. If the command fails, for example because the repository does not permit
   auto-merge, show the output. Comment on the pull request that a person merges
   it. Do not try a merge without `--auto`. End the pass.

## Never

- Never start a pass while the lock of another pass is younger than
  `loop.lock_stale_hours`.
- Never remove a lock that another pass wrote. Report a stale lock to the person.
- Never push to the default branch.
- Never merge without `--auto`. Never turn on auto-merge for an item with
  `loop.human_merge_label`, or for a base branch without required status checks.
- Never approve a pull request or request a reviewer.
- Never close an item directly. The merge closes it.
- Never change branch protection, rulesets, or repository settings.
- Never change a label other than `loop.ready_label`, `loop.needs_human_label`, and
  the status labels that `sdlc-crew` sets.
- Never answer a question of the crew for the person, such as the plan approval.
- Never switch the branch of the checkout of the person.
- Never delete a branch or a worktree.
