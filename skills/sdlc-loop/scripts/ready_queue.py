#!/usr/bin/env python3
"""Keep the ready label of the work items in step with their blockers.

An open item is ready when every item that blocks it is closed and it has no skip
label other than the needs-human label. The script reads the settings from `.sdlc-crew.yaml`, prints the label
changes and the queue in pick order, and changes labels only with --apply.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_FILE = ".sdlc-crew.yaml"
BACKLOG_FILE = "BACKLOG.md"
SUPPORTED_TRACKERS = ("github", "local")

BODY_BLOCKED_BY = re.compile(r"^\s*\**Blocked by:?\**:?\s*(.+)$", re.IGNORECASE | re.MULTILINE)
SAME_REPO_REF = re.compile(r"(?<![\w/.-])#(\d+)\b")
LOCAL_HEADING = re.compile(r"^### (LOCAL-(\d+)):\s*(.*)$")
LOCAL_FIELD = re.compile(r"^- ([A-Za-z ]+):\s*(.*)$")
LOCAL_REF = re.compile(r"\bLOCAL-\d+\b")
REMOTE_REPO = re.compile(r"[:/]([^/:]+/[^/]+?)(?:\.git)?/?$")

ISSUES_QUERY = """
query($owner: String!, $name: String!, $endCursor: String) {
  repository(owner: $owner, name: $name) {
    issues(first: 100, after: $endCursor, states: [OPEN, CLOSED]) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number title state body
        labels(first: 50) { nodes { name } }
        milestone { number state }
        %BLOCKED_BY%
      }
    }
  }
}
"""
BLOCKED_BY_FIELD = "blockedBy(first: 50) { nodes { number state repository { nameWithOwner } } }"


class QueueError(Exception):
    """A problem that stops the script, with a message for the person."""


@dataclass
class Settings:
    """The values of `.sdlc-crew.yaml` that the queue needs."""

    tracker: str = "local"
    repo: str = ""
    todo: str = "To Do"
    in_progress: str = "In Progress"
    in_review: str = "In Review"
    done: str = "Done"
    ready_label: str = "status:ready"
    needs_human_label: str = "needs-human"
    skip_labels: list[str] = field(default_factory=lambda: ["needs-human", "type:epic"])
    order: list[str] = field(default_factory=lambda: ["milestone", "priority", "number"])
    priority_labels: list[str] = field(
        default_factory=lambda: ["priority:p0", "priority:p1", "priority:p2"]
    )


@dataclass
class Item:
    """One work item, in the form that every tracker gives."""

    key: str
    number: int
    title: str
    closed: bool
    labels: set[str] = field(default_factory=set)
    status: str = ""
    milestone: int | None = None
    blockers: set[str] = field(default_factory=set)
    closed_blockers: set[str] = field(default_factory=set)


def parse_scalar(text: str) -> object:
    """Return a YAML scalar or a flow list as a Python value."""
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        return [parse_scalar(part) for part in inner.split(",")] if inner else []
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    if text in ("true", "false"):
        return text == "true"
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return text


def strip_comment(line: str) -> str:
    """Return the line without a trailing YAML comment outside quotes."""
    quote = ""
    for index, char in enumerate(line):
        if quote:
            quote = "" if char == quote else quote
        elif char in "\"'":
            quote = char
        elif char == "#" and (index == 0 or line[index - 1].isspace()):
            return line[:index].rstrip()
    return line.rstrip()


def parse_config(text: str) -> dict:
    """Parse the block mappings and flow lists that `.sdlc-crew.yaml` uses.

    The parser covers the template format only. It does not install or need a YAML
    library.
    """
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for raw in text.splitlines():
        line = strip_comment(raw)
        if not line.strip() or line.lstrip().startswith("- "):
            continue
        indent = len(line) - len(line.lstrip())
        key, _, value = line.strip().partition(":")
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if value.strip():
            parent[key.strip()] = parse_scalar(value)
        else:
            child: dict = {}
            parent[key.strip()] = child
            stack.append((indent, child))
    return root


def settings_from_config(config: dict) -> Settings:
    """Return the settings, with the default for each key that the config omits."""
    settings = Settings()
    tracker = config.get("tracker") or {}
    statuses = tracker.get("statuses") or {}
    forge = config.get("forge") or {}
    loop = config.get("loop") or {}
    settings.tracker = tracker.get("kind") or settings.tracker
    settings.repo = forge.get("repo") or ""
    for name in ("todo", "in_progress", "in_review", "done"):
        setattr(settings, name, statuses.get(name) or getattr(settings, name))
    for name in ("ready_label", "needs_human_label", "skip_labels", "order", "priority_labels"):
        if name in loop:
            setattr(settings, name, loop[name])
    return settings


def repo_from_remote(url: str) -> str:
    """Return `owner/name` from a git remote URL."""
    match = REMOTE_REPO.search(url.strip())
    if not match:
        raise QueueError(f"Cannot read owner/name from the origin remote: {url.strip()}")
    return match.group(1)


def body_blockers(body: str) -> set[str]:
    """Return the same-repository issue numbers in the "Blocked by" lines of a body."""
    numbers: set[str] = set()
    for match in BODY_BLOCKED_BY.finditer(body or ""):
        numbers.update(SAME_REPO_REF.findall(match.group(1)))
    return numbers


def is_ready(item: Item, closed_keys: set[str], settings: Settings) -> bool:
    """Return True if the item is open, not skipped, and has no open blocker.

    The needs-human label does not remove readiness, so the item goes back to the
    queue when a person removes that label.
    """
    held = set(settings.skip_labels) - {settings.needs_human_label}
    if item.closed or item.labels & held:
        return False
    return all(key in closed_keys or key in item.closed_blockers for key in item.blockers)


def in_queue(item: Item, settings: Settings) -> bool:
    """Return True if the loop can pick the ready item now."""
    working = {settings.in_progress, settings.in_review}
    blocked_labels = working | set(settings.skip_labels)
    return item.status not in working and not item.labels & blocked_labels


def sort_key(item: Item, settings: Settings) -> tuple:
    """Return the key that puts the item in the configured pick order."""
    unknown = sys.maxsize
    parts: dict[str, int] = {
        "milestone": item.milestone if item.milestone is not None else unknown,
        "priority": next(
            (rank for rank, label in enumerate(settings.priority_labels) if label in item.labels),
            unknown,
        ),
        "number": item.number,
    }
    return tuple(parts[name] for name in settings.order if name in parts) + (item.number,)


def run(command: list[str]) -> str:
    """Run a command and return its output."""
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise QueueError(f"`{' '.join(command[:3])} ...` failed: {result.stderr.strip()}")
    return result.stdout


def github_nodes(repo: str, with_blocked_by: bool) -> list[dict]:
    """Return every issue of the repository from the GitHub GraphQL API."""
    owner, name = repo.split("/", 1)
    query = ISSUES_QUERY.replace("%BLOCKED_BY%", BLOCKED_BY_FIELD if with_blocked_by else "")
    output = run([
        "gh", "api", "graphql", "--paginate",
        "-F", f"owner={owner}", "-F", f"name={name}", "-f", f"query={query}",
        "--jq", ".data.repository.issues.nodes[] | @json",
    ])
    return [json.loads(line) for line in output.splitlines() if line.strip()]


def github_items(repo: str) -> list[Item]:
    """Return the issues of a GitHub repository, with the blockers of both sources."""
    try:
        nodes = github_nodes(repo, with_blocked_by=True)
    except QueueError as error:
        if "blockedBy" not in str(error):
            raise
        print("note: this GitHub has no issue dependencies; only body lines count.", file=sys.stderr)
        nodes = github_nodes(repo, with_blocked_by=False)
    items = []
    for node in nodes:
        item = Item(
            key=str(node["number"]),
            number=node["number"],
            title=node["title"],
            closed=node["state"] == "CLOSED",
            labels={label["name"] for label in node["labels"]["nodes"]},
            blockers=body_blockers(node.get("body") or ""),
        )
        milestone = node.get("milestone")
        if milestone and milestone.get("state") == "OPEN":
            item.milestone = milestone["number"]
        for blocker in (node.get("blockedBy") or {}).get("nodes", []):
            same_repo = blocker["repository"]["nameWithOwner"].lower() == repo.lower()
            key = str(blocker["number"]) if same_repo else f"{blocker['repository']['nameWithOwner']}#{blocker['number']}"
            item.blockers.add(key)
            if blocker["state"] == "CLOSED":
                item.closed_blockers.add(key)
        items.append(item)
    return items


def local_items(text: str, settings: Settings) -> list[Item]:
    """Return the items of a BACKLOG.md file.

    An item can hold `- Blocked by: LOCAL-2, LOCAL-5` and `- Labels: needs-human`.
    """
    items: list[Item] = []
    for line in text.splitlines():
        heading = LOCAL_HEADING.match(line)
        if heading:
            items.append(Item(key=heading.group(1), number=int(heading.group(2)),
                              title=heading.group(3).strip(), closed=False))
            continue
        field_match = LOCAL_FIELD.match(line)
        if not items or not field_match:
            continue
        name, value = field_match.group(1).strip().lower(), field_match.group(2).strip()
        item = items[-1]
        if name == "status":
            item.status = value
            item.closed = value == settings.done
        elif name == "blocked by":
            item.blockers = set(LOCAL_REF.findall(value))
        elif name == "labels" and value.lower() != "none":
            item.labels = {label.strip() for label in value.split(",") if label.strip()}
    return items


def label_changes(items: list[Item], settings: Settings) -> list[tuple[Item, bool]]:
    """Return each item whose ready label is wrong, with True to add it."""
    closed_keys = {item.key for item in items if item.closed}
    changes = []
    for item in sorted(items, key=lambda each: each.number):
        ready = is_ready(item, closed_keys, settings)
        if ready != (settings.ready_label in item.labels):
            changes.append((item, ready))
    return changes


def ready_queue(items: list[Item], settings: Settings) -> list[Item]:
    """Return the ready items that nobody works on, in pick order."""
    closed_keys = {item.key for item in items if item.closed}
    ready = [item for item in items if is_ready(item, closed_keys, settings) and in_queue(item, settings)]
    return sorted(ready, key=lambda item: sort_key(item, settings))


def display(item: Item) -> str:
    """Return the ID of the item as the tracker shows it."""
    return item.key if item.key.startswith("LOCAL-") else f"#{item.key}"


def read_settings(root: Path, tracker: str | None, repo: str | None = None) -> Settings:
    """Return the settings of the repository at root.

    Without a config file, a repo argument selects the GitHub tracker.
    """
    path = root / CONFIG_FILE
    config = parse_config(path.read_text(encoding="utf-8")) if path.is_file() else {}
    settings = settings_from_config(config)
    if tracker:
        settings.tracker = tracker
    elif repo and not config:
        settings.tracker = "github"
    return settings


def main(argv: list[str] | None = None) -> int:
    """Print the label changes and the queue, and make the changes with --apply."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", help="owner/name. Default: forge.repo, then the origin remote.")
    parser.add_argument("--tracker", choices=SUPPORTED_TRACKERS, help="Default: tracker.kind.")
    parser.add_argument("--root", default=".", help="The repository root. Default: the current directory.")
    parser.add_argument("--apply", action="store_true", help="Change the labels. Default: a dry run.")
    args = parser.parse_args(argv)
    root = Path(args.root)

    try:
        settings = read_settings(root, args.tracker, args.repo)
        if settings.tracker == "github":
            repo = args.repo or settings.repo or repo_from_remote(
                run(["git", "-C", str(root), "remote", "get-url", "origin"]))
            items = github_items(repo)
        elif settings.tracker == "local":
            backlog = root / BACKLOG_FILE
            if not backlog.is_file():
                raise QueueError(f"{backlog} does not exist.")
            items = local_items(backlog.read_text(encoding="utf-8"), settings)
        else:
            raise QueueError(
                f"tracker.kind '{settings.tracker}' is not supported yet. "
                f"The loop supports: {', '.join(SUPPORTED_TRACKERS)}."
            )
        changes = label_changes(items, settings) if settings.tracker == "github" else []
        for item, add in changes:
            flag = "--add-label" if add else "--remove-label"
            print(f"{display(item)}: {flag} {settings.ready_label}")
            if args.apply:
                run(["gh", "issue", "edit", item.key, "-R", repo, flag, settings.ready_label])
    except QueueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if settings.tracker == "local":
        print("The local tracker has no ready label. Nothing to change.")
    elif not changes:
        print("No label changes.")
    elif not args.apply:
        print("Dry run. Run again with --apply to change the labels.")

    queue = ready_queue(items, settings)
    print(f"Queue: {len(queue)} ready")
    for item in queue:
        print(f"  {display(item)}: {item.title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
