# Tracker: local

The work items live in `BACKLOG.md` at the root of the repository. No account and no
network are needed. This is the default for a person who has no issue tracker.

## Item format

Each item is one section under `## Items`. Keep this format exactly, because the
crew and the person both read it:

```markdown
### LOCAL-3: Add a page that lists my recipes

- Status: To Do
- Created: 2026-09-25
- Parent: none
- Pull request: none

**Why:** I keep my recipes in notes on my phone and I cannot search them.

**Acceptance criteria:**

1. The Recipes page shows every recipe with its name and its main ingredient.
2. A search box filters the list as the user types.

**Definition of done:** The page is on the site, the tests pass, and I can find a
recipe by ingredient.

**Comments:**

- 2026-09-25 architect: Plan approved. See `docs/plans/LOCAL-3.md`.
```

The ID is `LOCAL-<n>`. `<n>` is one more than the largest number in the file.

## Operations

### Read

Read `BACKLOG.md`. Find the section whose heading starts with the ID. Take every line
until the next `### ` heading. If the ID is not in the file, return `STATUS: BLOCKED`
with the IDs that the file has.

### Create

1. If `BACKLOG.md` does not exist, copy `assets/BACKLOG.md` from the `sdlc-crew` skill
   directory to the repository root.
2. Compute the next ID.
3. Write the section in the format above. The architect fills **Why**, the
   acceptance criteria, and the definition of done from the description of the person
   and from the answers to the readiness questions. Set the status to
   `tracker.statuses.todo`.
4. Commit the file on the default branch only if the person agrees. Otherwise leave
   it in the working tree and tell the person.

### Create child

Same as Create. Set `Parent:` to the parent ID. Add the child ID to a `**Children:**`
list in the parent section.

### Comment

Append one line to the **Comments** list of the item: the date, the persona name, and
one or two sentences. If the comment is long, write it to `docs/plans/<ID>.md` or
`docs/plans/<ID>-retrospective.md` and link that file from the comment line.

### Set status

Replace the `- Status:` line of the item.

### Link PR

Replace the `- Pull request:` line with the URL. With `forge.kind: none`, write the
branch name in place of the URL.

## Commits to `BACKLOG.md`

The workflow changes `BACKLOG.md` on the default branch, not on the feature branch,
so the tracker state does not wait for the merge. Before each write:

1. `git stash` nothing. If the working tree has changes outside `BACKLOG.md` and
   `docs/plans/`, stop and tell the person.
2. Switch to the default branch, edit the file, commit with the message
   `<ID>: <what changed>`, and switch back.
3. Push only if the person agreed to pushes in `sdlc-setup`. Otherwise tell the person
   that the commit is local.
