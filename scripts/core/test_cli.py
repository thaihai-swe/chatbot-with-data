import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cli


class TestCoreZeroCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "AGENTS.md").write_text("# Agents\n")
        (self.root / "core-zero/memories/repo").mkdir(parents=True)
        (self.root / "artifacts/features/demo").mkdir(parents=True)
        (self.root / "artifacts/features/demo/status.md").write_text("# Status\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        with patch.object(cli, "resolve_root", return_value=str(self.root)):
            return cli.main(list(args))

    def test_start_creates_session_and_json_result(self):
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(self.run_cli("session-start", "--feature", "demo", "--json"), 0)
        session = self.root / ".corezero/sessions/demo/session.md"
        self.assertTrue(session.exists())
        self.assertEqual(json.loads(output.getvalue())["command"], "session-start")
        self.assertIn("COREZERO_CONTEXT", session.read_text())

    def test_checkpoint_preserves_human_notes_and_updates_handoff(self):
        self.assertEqual(self.run_cli("session-start", "--feature", "demo"), 0)
        session = self.root / ".corezero/sessions/demo/session.md"
        text = session.read_text().replace("## Progress\n", "## Progress\n\nHuman progress\n")
        session.write_text(text)
        self.assertEqual(self.run_cli(
            "session-checkpoint", "--feature", "demo",
            "--next-action", "run verification", "--decision", "keep the schema",
        ), 0)
        refreshed = session.read_text()
        self.assertIn("Human progress", refreshed)
        self.assertIn("run verification", refreshed)
        self.assertIn("keep the schema", refreshed)
        self.assertEqual(json.loads(refreshed.split("---\n", 2)[1])["next_action"], "run verification")

    def test_end_appends_explicit_candidates_without_deleting_existing(self):
        self.assertEqual(self.run_cli("session-start", "--feature", "demo"), 0)
        extracts = self.root / "artifacts/features/demo/session-extracts.md"
        extracts.write_text("# Existing\n\n## Pending Candidates\n\nold candidate\n")
        self.assertEqual(self.run_cli(
            "session-end", "--feature", "demo", "--candidate", "new candidate",
        ), 0)
        content = extracts.read_text()
        self.assertIn("old candidate", content)
        self.assertIn("new candidate", content)

    def test_missing_feature_fails(self):
        self.assertEqual(self.run_cli("session-start", "--feature", "missing"), 1)

    def test_init_creates_deterministic_scaffold(self):
        self.assertEqual(self.run_cli("init", "--root", str(self.root), "--json"), 0)
        self.assertTrue((self.root / "core-zero/project/architecture.md").exists())
        self.assertIn("core-zero/generated/*", (self.root / ".gitignore").read_text())

    def test_task_next_returns_unblocked_task_as_json(self):
        (self.root / "artifacts/features/demo/tasks.md").write_text(
            "- [ ] TASK-001 First\n\nStatus: Not Started\n\n"
            "- [ ] TASK-002 Second\n\nDepends on: TASK-001\n\nStatus: Not Started\n"
        )
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(self.run_cli("task-next", "--feature", "demo", "--json"), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["details"]["tasks"][0]["id"], "TASK-001")

    def _write_tasks(self):
        (self.root / "artifacts/features/demo/tasks.md").write_text(
            "- [ ] TASK-001 First\n"
            "  Status: Not Started\n"
            "  Summary: first task\n\n"
            "- [ ] TASK-002 Second\n"
            "  Status: Not Started\n"
            "  Depends on: TASK-001\n"
        )

    def test_task_start_updates_checkbox_and_status(self):
        self._write_tasks()
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(self.run_cli("task-start", "--feature", "demo", "--task", "TASK-001", "--json"), 0)
        text = (self.root / "artifacts/features/demo/tasks.md").read_text()
        self.assertIn("- [ ] TASK-001 First", text)
        self.assertIn("Status: In Progress", text)
        self.assertEqual(json.loads(output.getvalue())["details"]["task"]["to"], "In Progress")

    def test_task_done_requires_and_records_evidence(self):
        self._write_tasks()
        self.assertEqual(self.run_cli("task-start", "--feature", "demo", "--task", "TASK-001"), 0)
        self.assertEqual(self.run_cli("task-done", "--feature", "demo", "--task", "TASK-001"), 1)
        self.assertEqual(self.run_cli(
            "task-done", "--feature", "demo", "--task", "TASK-001",
            "--evidence", "pytest -q: 3 passed",
        ), 0)
        text = (self.root / "artifacts/features/demo/tasks.md").read_text()
        self.assertIn("- [x] TASK-001 First", text)
        self.assertIn("Status: Done", text)
        self.assertIn("Validation evidence: pytest -q: 3 passed", text)

    def test_task_block_requires_reason_and_preserves_other_task(self):
        self._write_tasks()
        self.assertEqual(self.run_cli("task-block", "--feature", "demo", "--task", "TASK-001"), 1)
        self.assertEqual(self.run_cli(
            "task-block", "--feature", "demo", "--task", "TASK-001", "--note", "waiting on API access",
        ), 0)
        text = (self.root / "artifacts/features/demo/tasks.md").read_text()
        self.assertIn("Status: Blocked", text)
        self.assertIn("Session note: waiting on API access", text)
        self.assertIn("TASK-002 Second", text)

    def test_task_update_dry_run_does_not_write(self):
        self._write_tasks()
        before = (self.root / "artifacts/features/demo/tasks.md").read_text()
        self.assertEqual(self.run_cli(
            "task-update", "--feature", "demo", "--task", "TASK-001",
            "--status", "In Progress", "--dry-run",
        ), 0)
        self.assertEqual(before, (self.root / "artifacts/features/demo/tasks.md").read_text())

    def test_status_reports_features_and_supports_dry_run(self):
        fake_dashboard = type("Dashboard", (), {
            "scan_workspace": staticmethod(lambda root: [{
                "slug": "demo", "phase": "Implementing", "progress": {"completed": 1, "total": 2},
                "next_step": "corezero task-next --feature demo", "has_blocker": False,
            }]),
            "get_html_template": staticmethod(lambda payload: "<html>status</html>"),
        })
        output = StringIO()
        with patch.object(cli, "_load_dashboard_module", return_value=fake_dashboard), redirect_stdout(output):
            self.assertEqual(self.run_cli("status", "--feature", "demo", "--dry-run", "--json"), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["details"]["features"][0]["slug"], "demo")
        self.assertEqual(result["next_action"], "corezero task-next --feature demo")

    def test_context_pack_reports_selected_sections_and_omissions(self):
        (self.root / "core-zero/rules").mkdir(parents=True)
        (self.root / "core-zero/rules/caveman.md").write_text("# Caveman\n")
        (self.root / "core-zero/rules/headroom.md").write_text("# Headroom\n")
        (self.root / "core-zero/memories/repo/core-policies.md").write_text(
            "## Purpose\nshort purpose\n\n## Normative Rules\nCC-001\n\n## Security Policy\nprivate section\n"
        )
        (self.root / "core-zero/memories/repo/learned-heuristics.md").write_text("# Heuristics\nLH-001\n")
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(self.run_cli(
                "context-pack", "--feature", "demo", "--intent", "implement",
                "--budget", "10000", "--json",
            ), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["command"], "context-pack")
        self.assertIn("selected", result["details"])
        self.assertIn("estimated_tokens", result["details"])
        policy = next(item for item in result["details"]["selected"] if item["path"].endswith("core-policies.md"))
        self.assertEqual(policy["sections"], ["Purpose", "Normative Rules"])
        self.assertTrue(any(item["path"].endswith("learned-heuristics.md") for item in result["details"]["selected"]))
        self.assertNotIn("skills/spec-", " ".join(item["path"] for item in result["details"]["selected"]))

    def _write_context_sources(self):
        (self.root / "core-zero/rules").mkdir(parents=True, exist_ok=True)
        (self.root / "core-zero/rules/caveman.md").write_text("# Caveman\n")
        (self.root / "core-zero/rules/headroom.md").write_text("# Headroom\n")
        (self.root / "core-zero/memories/repo/core-policies.md").write_text(
            "## Purpose\nshort purpose\n\n## Normative Rules\nCC-001\n\n## Security Policy\nprivate section\n"
        )

    def test_context_load_prints_selected_content(self):
        self._write_context_sources()
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(self.run_cli(
                "context-load", "--feature", "demo", "--intent", "implement",
                "--budget", "10000",
            ), 0)
        content = output.getvalue()
        self.assertIn("[core-zero/memories/repo/core-policies.md :: Purpose, Normative Rules]", content)
        self.assertIn("short purpose", content)
        self.assertNotIn("private section", content)

    def test_context_load_json_contains_content_and_stable_fields(self):
        self._write_context_sources()
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(self.run_cli(
                "context-load", "--feature", "demo", "--phase", "Implement",
                "--json", "--budget", "10000",
            ), 0)
        result = json.loads(output.getvalue())
        for field in ("command", "status", "feature", "selected", "omitted",
                      "estimated_tokens", "budget", "current_state", "next_action"):
            self.assertIn(field, result)
        policy = next(item for item in result["selected"] if item["path"].endswith("core-policies.md"))
        self.assertIn("short purpose", policy["content"])

    def test_context_load_reports_budget_omissions_without_writing(self):
        self._write_context_sources()
        before = sorted(str(path.relative_to(self.root)) for path in self.root.rglob("*"))
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(self.run_cli(
                "context-load", "--feature", "demo", "--budget", "1", "--json",
            ), 0)
        result = json.loads(output.getvalue())
        self.assertTrue(result["omitted"])
        self.assertTrue(any(item["reason"] == "budget exceeded" for item in result["omitted"]))
        after = sorted(str(path.relative_to(self.root)) for path in self.root.rglob("*"))
        self.assertEqual(before, after)

    def test_context_load_missing_repository_fails(self):
        with patch.object(cli, "resolve_root", return_value=None):
            self.assertEqual(cli.main(["context-load"]), 1)

    def test_context_load_missing_feature_fails(self):
        self._write_context_sources()
        self.assertEqual(self.run_cli("context-load", "--feature", "missing"), 1)

    def test_memory_audit_reports_tokens_and_thresholds(self):
        (self.root / "core-zero/memories/repo/learned-heuristics.md").write_text("# Heuristics\n")
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(self.run_cli("memory-audit", "--json"), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["command"], "memory-audit")
        self.assertIn("total_tokens", result["details"])
        self.assertTrue(any(item["path"].endswith("learned-heuristics.md") for item in result["details"]["files"]))


if __name__ == "__main__":
    unittest.main()
