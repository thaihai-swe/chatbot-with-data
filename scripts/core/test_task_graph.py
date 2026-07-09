import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from core.task_graph import parse_tasks, detect_cycle, next_tasks


SAMPLE = """
# Task Breakdown

## Phases

- [ ] TASK-001 setup
  Status: Done
  Depends on:
  Proving command or proof: true

- [x] TASK-002 base
  Status: Done
  Depends on: TASK-001

- [ ] TASK-003 feature
  Status: Not Started
  Depends-on: TASK-002
  Proving command or proof: pytest

- [ ] TASK-004 polish
  Status: Not Started
  Depends on: TASK-003, TASK-002
"""

LINEAR = """
- [ ] TASK-001 a
  Status: Not Started
- [ ] TASK-002 b
  Status: Not Started
"""

CYCLE = """
- [ ] TASK-001 a
  Status: Not Started
  Depends on: TASK-002
- [ ] TASK-002 b
  Status: Not Started
  Depends on: TASK-001
"""


class TestTaskGraph(unittest.TestCase):
    def test_parse_depends_variants(self):
        tasks = parse_tasks(SAMPLE)
        by = {t["id"]: t for t in tasks}
        self.assertTrue(by["TASK-001"]["done"])
        self.assertTrue(by["TASK-002"]["done"])
        self.assertEqual(by["TASK-003"]["depends"], ["TASK-002"])
        self.assertEqual(by["TASK-004"]["depends"], ["TASK-003", "TASK-002"])
        self.assertFalse(by["TASK-003"]["done"])

    def test_next_with_deps(self):
        ready = next_tasks(parse_tasks(SAMPLE))
        self.assertEqual([t["id"] for t in ready], ["TASK-003"])

    def test_linear_fallback(self):
        ready = next_tasks(parse_tasks(LINEAR))
        self.assertEqual([t["id"] for t in ready], ["TASK-001"])

    def test_cycle(self):
        cyc = detect_cycle(parse_tasks(CYCLE))
        self.assertIsNotNone(cyc)
        self.assertTrue(set(cyc) >= {"TASK-001", "TASK-002"})

    def test_all_done(self):
        text = "- [x] TASK-001\n  Status: Done\n"
        self.assertEqual(next_tasks(parse_tasks(text)), [])


if __name__ == "__main__":
    unittest.main()
