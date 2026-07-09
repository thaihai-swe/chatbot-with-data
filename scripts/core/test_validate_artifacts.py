import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from core.validate_artifacts import (
    check_structure, traceability, extract_ids, feature_dir, main, PHASE_FILES,
)


class TestValidateArtifacts(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.slug = 'demo-feat'
        self.fdir = Path(self.root) / 'artifacts' / 'features' / self.slug
        self.fdir.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_files(self):
        errors, warns = check_structure(self.fdir, 'Plan')
        self.assertTrue(any('spec.md' in e for e in errors))

    def test_structure_pass(self):
        (self.fdir / 'status.md').write_text('# Status\n')
        (self.fdir / 'spec.md').write_text('## Metadata\n\n## Problem Statement\n\nREQ-001\nAC-001\n')
        (self.fdir / 'plan.md').write_text('## Metadata\n')
        (self.fdir / 'tasks.md').write_text('## Metadata\n\n- [ ] TASK-001\n  Linked acceptance criteria: AC-001\n')
        errors, warns = check_structure(self.fdir, 'Plan')
        self.assertEqual(errors, [])

    def test_traceability_ok(self):
        (self.fdir / 'spec.md').write_text('REQ-001 AC-001\n')
        (self.fdir / 'tasks.md').write_text('TASK-001 AC-001\n')
        (self.fdir / 'plan.md').write_text('')
        (self.fdir / 'status.md').write_text('')
        lines, errors = traceability(self.fdir)
        self.assertEqual(errors, [])
        self.assertTrue(any('OK' in l for l in lines))

    def test_extract_ids(self):
        self.assertEqual(extract_ids('see REQ-12 and REQ-12 again', 'REQ'), {'REQ-12'})

    def test_orphan_acs_flagged(self):
        (self.fdir / 'spec.md').write_text('REQ-001 AC-001\n')
        (self.fdir / 'tasks.md').write_text('TASK-001 AC-001 AC-999\n')
        (self.fdir / 'plan.md').write_text('')
        (self.fdir / 'status.md').write_text('')
        lines, errors = traceability(self.fdir)
        self.assertTrue(any('orphan' in e.lower() for e in errors))
        self.assertTrue(any('AC-999' in e for e in errors))

    def test_task_without_ac_flagged(self):
        (self.fdir / 'spec.md').write_text('REQ-001 AC-001\n')
        (self.fdir / 'tasks.md').write_text('TASK-001 has no nearby acceptance criteria at all\n')
        (self.fdir / 'plan.md').write_text('')
        (self.fdir / 'status.md').write_text('')
        lines, errors = traceability(self.fdir)
        self.assertTrue(any('without AC' in e or 'without nearby' in e.lower() for e in errors))

    def test_phase_file_sets(self):
        self.assertIn('status.md', PHASE_FILES['Spec'])
        self.assertIn('spec.md', PHASE_FILES['Spec'])
        self.assertNotIn('plan.md', PHASE_FILES['Spec'])
        self.assertIn('plan.md', PHASE_FILES['Plan'])
        self.assertIn('tasks.md', PHASE_FILES['Plan'])
        self.assertEqual(PHASE_FILES['Implement'], PHASE_FILES['Plan'])

    def test_spec_phase_only_requires_status_and_spec(self):
        (self.fdir / 'status.md').write_text('# Status\n')
        (self.fdir / 'spec.md').write_text('## Metadata\n\n## Problem Statement\n')
        errors, warns = check_structure(self.fdir, 'Spec')
        self.assertEqual(errors, [])

    def test_missing_heading_warns(self):
        (self.fdir / 'status.md').write_text('# Status\n')
        (self.fdir / 'spec.md').write_text('# No headings\n')
        (self.fdir / 'plan.md').write_text('## Metadata\n')
        (self.fdir / 'tasks.md').write_text('## Metadata\n')
        errors, warns = check_structure(self.fdir, 'Plan')
        self.assertEqual(errors, [])
        self.assertTrue(any('Metadata' in w or 'Problem Statement' in w for w in warns))

    def test_feature_dir_path(self):
        p = feature_dir(self.root, self.slug)
        self.assertEqual(p, self.fdir)

    def test_cli_strict_exits_on_warns(self):
        (self.fdir / 'status.md').write_text('# Status\n')
        (self.fdir / 'spec.md').write_text('# No required headings\n')
        (self.fdir / 'plan.md').write_text('## Metadata\n')
        (self.fdir / 'tasks.md').write_text('## Metadata\n')
        # Patch resolve_root and argv
        with patch('core.validate_artifacts.resolve_root', return_value=self.root):
            with patch('sys.argv', [
                'validate_artifacts.py',
                '--feature', self.slug,
                '--phase', 'Plan',
                '--strict',
            ]):
                with self.assertRaises(SystemExit) as ctx:
                    main()
                self.assertEqual(ctx.exception.code, 1)

    def test_cli_trace_emits_report(self):
        (self.fdir / 'status.md').write_text('# Status\n')
        (self.fdir / 'spec.md').write_text('## Metadata\n\n## Problem Statement\n\nREQ-001 AC-001\n')
        (self.fdir / 'plan.md').write_text('## Metadata\n')
        (self.fdir / 'tasks.md').write_text('## Metadata\n\nTASK-001 AC-001\n')
        with patch('core.validate_artifacts.resolve_root', return_value=self.root):
            with patch('sys.argv', [
                'validate_artifacts.py',
                '--feature', self.slug,
                '--phase', 'Plan',
                '--trace',
            ]):
                buf = StringIO()
                with patch('sys.stdout', buf):
                    with self.assertRaises(SystemExit) as ctx:
                        main()
                    # pass expected
                    self.assertEqual(ctx.exception.code, 0)
                out = buf.getvalue()
                self.assertIn('Traceability Report', out)
                self.assertIn('REQ-001', out)


if __name__ == '__main__':
    unittest.main()
