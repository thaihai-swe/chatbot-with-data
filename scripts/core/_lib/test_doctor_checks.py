import unittest
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doctor_checks import read_thresholds, build_path_map, check_manifest_drift


class TestReadThresholds(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def _make_core_policies(self, content):
        d = os.path.join(self.root, 'core-zero', 'project')
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'harness-config.yaml'), 'w') as f:
            f.write(content)

    def test_defaults_when_missing(self):
        ew, tb, hc = read_thresholds(self.root)
        self.assertEqual(ew, 100)
        self.assertEqual(tb, 200)
        self.assertEqual(hc, 3200)

    def test_defaults_when_file_has_no_section(self):
        self._make_core_policies('thresholds:\n  other: 5\n')
        ew, tb, hc = read_thresholds(self.root)
        self.assertEqual(ew, 100)
        self.assertEqual(tb, 200)
        self.assertEqual(hc, 3200)

    def test_parses_canonical_thresholds(self):
        self._make_core_policies(
            'thresholds:\n'
            '  memory_warn_lines: 100\n'
            '  memory_breach_lines: 200\n'
            '  memory_hard_lines: 3200\n'
        )
        ew, tb, hc = read_thresholds(self.root)
        self.assertEqual(ew, 100)
        self.assertEqual(tb, 200)
        self.assertEqual(hc, 3200)


class TestBuildPathMap(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def _touch(self, path):
        full = os.path.join(self.root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, 'w').close()

    def test_returns_empty_map_for_empty_root(self):
        pm = build_path_map(self.root)
        self.assertEqual(pm, {})

    def test_finds_md_in_standard_dirs(self):
        self._touch('core-zero/memories/repo/core-policies.md')
        self._touch('core-zero/project/architecture.md')
        pm = build_path_map(self.root)
        self.assertIn('core-policies.md', pm)
        self.assertIn('architecture.md', pm)

    def test_finds_domain_packs(self):
        self._touch('core-zero/memories/domain/example/glossary.md')
        pm = build_path_map(self.root)
        self.assertEqual(pm.get('glossary.md'),
                         'core-zero/memories/domain/example/glossary.md')

    def test_ignores_non_md_files(self):
        self._touch('core-zero/project/harness-config.yaml')
        pm = build_path_map(self.root)
        self.assertNotIn('harness-config.yaml', pm)


class TestCheckManifestDrift(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def _add_manifest(self, overwrite=None, copy_if_missing=None):
        data = {'files': {}}
        if overwrite:
            data['files']['overwrite'] = overwrite
        else:
            data['files']['overwrite'] = []
        if copy_if_missing:
            data['files']['copyIfMissing'] = copy_if_missing
        else:
            data['files']['copyIfMissing'] = []
        with open(os.path.join(self.root, 'manifest.json'), 'w') as f:
            json.dump(data, f)

    def _touch(self, path):
        full = os.path.join(self.root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, 'w').close()

    def test_ok_when_manifest_and_disk_match(self):
        self._add_manifest(overwrite=['scripts/harness/doctor.sh'])
        self._touch('scripts/harness/doctor.sh')
        result = check_manifest_drift(self.root)
        self.assertEqual(result, 'OK')

    def test_skips_when_no_manifest(self):
        result = check_manifest_drift(self.root)
        self.assertEqual(result, 'SKIP')

    def test_flags_uncovered_file(self):
        self._add_manifest(overwrite=['scripts/harness/doctor.sh'])
        self._touch('scripts/harness/doctor.sh')
        self._touch('scripts/install.sh')
        result = check_manifest_drift(self.root)
        self.assertIn('FAIL', result)
        self.assertIn('install.sh', result)

    def test_flags_missing_manifest_entry(self):
        self._add_manifest(overwrite=['scripts/harness/doctor.sh', 'scripts/missing.sh'])
        self._touch('scripts/harness/doctor.sh')
        result = check_manifest_drift(self.root)
        self.assertIn('FAIL', result)
        self.assertIn('missing.sh', result)


if __name__ == '__main__':
    unittest.main()
