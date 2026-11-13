"""Test the blocker parsing and the readiness logic of the sdlc-loop queue script."""

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "skills" / "sdlc-loop" / "scripts" / "ready_queue.py"
SPEC = importlib.util.spec_from_file_location("ready_queue", SCRIPT)
rq = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = rq
SPEC.loader.exec_module(rq)

CONFIG = """\
version: 1
tracker:
  kind: github  # GitHub Issues
  statuses:
    todo: "To Do"
    in_progress: "Doing"
forge:
  repo: "acme/widgets"
loop:
  ready_label: "ready"
  skip_labels: ["hold", "type:epic"]
  needs_human_label: "hold"
  priority_labels: ["P0", "P1"]
  order: [priority, number]
  lock_stale_hours: 6
"""

BACKLOG = """\
# Backlog

## Items

### LOCAL-1: Make the page

- Status: Done
- Created: 2026-09-25
- Parent: none
- Pull request: none

### LOCAL-2: Add a search box

- Status: To Do
- Blocked by: LOCAL-1
- Pull request: none

### LOCAL-3: Add a filter

- Status: To Do
- Blocked by: LOCAL-1, LOCAL-2
- Pull request: none

### LOCAL-4: Ask the client

- Status: To Do
- Labels: needs-human
- Blocked by: none
"""


def item(number, labels=(), closed=False, blockers=(), milestone=None, status=""):
    """Return a GitHub-style item for a test."""
    return rq.Item(key=str(number), number=number, title=f"Item {number}", closed=closed,
                   labels=set(labels), blockers=set(blockers), milestone=milestone, status=status)


class BodyBlockersTest(unittest.TestCase):
    def test_reads_plain_blocked_by_line(self):
        self.assertEqual(rq.body_blockers("Text\nBlocked by #49\n"), {"49"})

    def test_reads_bold_line_with_colon_and_many_refs(self):
        self.assertEqual(rq.body_blockers("**Blocked by:** #3, #7 and #12"), {"3", "7", "12"})

    def test_ignores_cross_repository_refs(self):
        self.assertEqual(rq.body_blockers("Blocked by other/repo#5, #6"), {"6"})

    def test_ignores_refs_outside_the_line(self):
        self.assertEqual(rq.body_blockers("See #4.\nPart of #2"), set())

    def test_empty_body_has_no_blockers(self):
        self.assertEqual(rq.body_blockers(""), set())


class ConfigTest(unittest.TestCase):
    def test_reads_loop_and_tracker_settings(self):
        settings = rq.settings_from_config(rq.parse_config(CONFIG))
        self.assertEqual(settings.tracker, "github")
        self.assertEqual(settings.repo, "acme/widgets")
        self.assertEqual(settings.in_progress, "Doing")
        self.assertEqual(settings.in_review, "In Review")
        self.assertEqual(settings.ready_label, "ready")
        self.assertEqual(settings.skip_labels, ["hold", "type:epic"])
        self.assertEqual(settings.order, ["priority", "number"])

    def test_missing_loop_section_uses_defaults(self):
        settings = rq.settings_from_config(rq.parse_config("tracker:\n  kind: local\n"))
        self.assertEqual(settings.ready_label, "status:ready")
        self.assertEqual(settings.skip_labels, ["needs-human", "type:epic"])
        self.assertEqual(settings.order, ["milestone", "priority", "number"])

    def test_hash_inside_quotes_is_not_a_comment(self):
        self.assertEqual(rq.parse_config('a: "x # y"  # note\n'), {"a": "x # y"})

    def test_repo_from_ssh_and_https_remotes(self):
        self.assertEqual(rq.repo_from_remote("git@github.com:acme/widgets.git\n"), "acme/widgets")
        self.assertEqual(rq.repo_from_remote("https://github.com/acme/widgets"), "acme/widgets")


class ReadinessTest(unittest.TestCase):
    def setUp(self):
        self.settings = rq.Settings()

    def test_open_item_with_closed_blockers_is_ready(self):
        self.assertTrue(rq.is_ready(item(2, blockers={"1"}), {"1"}, self.settings))

    def test_open_blocker_makes_item_not_ready(self):
        self.assertFalse(rq.is_ready(item(3, blockers={"1", "2"}), {"1"}, self.settings))

    def test_closed_cross_repository_blocker_counts_as_closed(self):
        blocked = item(3, blockers={"o/r#9"})
        blocked.closed_blockers = {"o/r#9"}
        self.assertTrue(rq.is_ready(blocked, set(), self.settings))

    def test_epic_is_never_ready(self):
        self.assertFalse(rq.is_ready(item(4, labels={"type:epic"}), set(), self.settings))

    def test_needs_human_keeps_ready_but_leaves_queue(self):
        held = item(5, labels={"needs-human"})
        self.assertTrue(rq.is_ready(held, set(), self.settings))
        self.assertEqual(rq.ready_queue([held], self.settings), [])

    def test_closed_item_is_not_ready(self):
        self.assertFalse(rq.is_ready(item(6, closed=True), set(), self.settings))

    def test_item_in_progress_leaves_queue(self):
        working = item(7, labels={"In Progress"})
        self.assertEqual(rq.ready_queue([working], self.settings), [])

    def test_label_changes_add_and_remove(self):
        items = [item(1, closed=True), item(2, blockers={"1"}),
                 item(3, labels={"status:ready"}, blockers={"2"})]
        changes = [(each.number, add) for each, add in rq.label_changes(items, self.settings)]
        self.assertEqual(changes, [(2, True), (3, False)])


class OrderTest(unittest.TestCase):
    def test_milestone_then_priority_then_number(self):
        items = [
            item(10, labels={"priority:p1"}, milestone=1),
            item(11, labels={"priority:p0"}, milestone=2),
            item(12, labels={"priority:p0"}, milestone=1),
            item(5),
            item(13, labels={"priority:p0"}, milestone=1),
        ]
        queue = rq.ready_queue(items, rq.Settings())
        self.assertEqual([each.number for each in queue], [12, 13, 10, 11, 5])

    def test_configured_order_without_milestone(self):
        settings = rq.Settings(order=["priority", "number"])
        items = [item(1, milestone=1), item(2, labels={"priority:p2"}, milestone=9)]
        self.assertEqual([each.number for each in rq.ready_queue(items, settings)], [2, 1])


class LocalTrackerTest(unittest.TestCase):
    def test_parses_status_blockers_and_labels(self):
        items = {each.key: each for each in rq.local_items(BACKLOG, rq.Settings())}
        self.assertTrue(items["LOCAL-1"].closed)
        self.assertEqual(items["LOCAL-3"].blockers, {"LOCAL-1", "LOCAL-2"})
        self.assertEqual(items["LOCAL-4"].labels, {"needs-human"})
        self.assertEqual(items["LOCAL-4"].blockers, set())

    def test_queue_holds_only_unblocked_items(self):
        queue = rq.ready_queue(rq.local_items(BACKLOG, rq.Settings()), rq.Settings())
        self.assertEqual([each.key for each in queue], ["LOCAL-2"])

    def test_main_reports_local_queue(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root, "BACKLOG.md").write_text(BACKLOG, encoding="utf-8")
            Path(root, ".sdlc-crew.yaml").write_text("tracker:\n  kind: local\n", encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = rq.main(["--root", root])
        self.assertEqual(code, 0)
        self.assertIn("LOCAL-2: Add a search box", out.getvalue())


class UnsupportedTrackerTest(unittest.TestCase):
    def test_jira_fails_with_clear_message(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root, ".sdlc-crew.yaml").write_text("tracker:\n  kind: jira\n", encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code = rq.main(["--root", root])
        self.assertEqual(code, 2)
        self.assertIn("tracker.kind 'jira' is not supported yet", err.getvalue())


if __name__ == "__main__":
    unittest.main()
