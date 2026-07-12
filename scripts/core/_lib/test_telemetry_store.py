import unittest
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from telemetry_store import (records_path, md_path, iter_records, count_open,
                              compute_next_id, append_record, update_record,
                              render_md, insights)


class TestTelemetryStore(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        os.makedirs(os.path.join(self.root, 'core-zero/memories/repo'), exist_ok=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _add_record(self, record):
        fp = records_path(self.root)
        with open(fp, 'a') as f:
            f.write(json.dumps(record) + '\n')

    def test_records_path(self):
        p = records_path(self.root)
        self.assertTrue(p.endswith('harness-telemetry.jsonl'))

    def test_md_path(self):
        p = md_path(self.root)
        self.assertTrue(p.endswith('harness-telemetry.md'))

    def test_iter_records_empty(self):
        records = list(iter_records(self.root))
        self.assertEqual(records, [])

    def test_iter_records(self):
        self._add_record({'id': 'OBS-001', 'task': 'TASK-001', 'status': 'open'})
        self._add_record({'id': 'OBS-002', 'task': 'TASK-002', 'status': 'closed'})
        records = list(iter_records(self.root))
        self.assertEqual(len(records), 2)

    def test_iter_records_skips_invalid_json(self):
        fp = records_path(self.root)
        with open(fp, 'w') as f:
            f.write('{"id": "OBS-001"}\nnot-json\n{"id": "OBS-002"}\n')
        records = list(iter_records(self.root))
        self.assertEqual(len(records), 2)

    def test_count_open_matches(self):
        self._add_record({'id': 'OBS-001', 'task': 'TASK-001', 'status': 'open', 'feature': 'feat-a'})
        self._add_record({'id': 'OBS-002', 'task': 'TASK-001', 'status': 'open', 'feature': 'feat-b'})
        self._add_record({'id': 'OBS-003', 'task': 'TASK-001', 'status': 'closed', 'feature': 'feat-a'})
        self.assertEqual(count_open(self.root, 'TASK-001'), 2)
        self.assertEqual(count_open(self.root, 'TASK-001', feature='feat-a'), 1)

    def test_compute_next_id_starts_at_001(self):
        nid = compute_next_id(self.root)
        self.assertEqual(nid, 'OBS-001')

    def test_compute_next_id_increments(self):
        self._add_record({'id': 'OBS-001'})
        self._add_record({'id': 'OBS-005'})
        nid = compute_next_id(self.root)
        self.assertEqual(nid, 'OBS-006')

    def test_append_record_creates_file(self):
        append_record(self.root, 'TASK-001', 'feat-a', 'gate-failure',
                      'test failure', severity='high', recurrence_risk='medium')
        records = list(iter_records(self.root))
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['task'], 'TASK-001')
        self.assertEqual(records[0]['status'], 'open')

    def test_append_record_wires_skill_and_root_cause(self):
        append_record(self.root, 'TASK-001', 'feat-a', 'gate-failure',
                      'boom', skill='spec-implement', root_cause='missing fixture')
        rec = list(iter_records(self.root))[0]
        self.assertEqual(rec['skill'], 'spec-implement')
        self.assertEqual(rec['root_cause'], 'missing fixture')

    def test_append_record_ids_unique_under_lock(self):
        append_record(self.root, 'T1', 'f', 'c', 'a')
        append_record(self.root, 'T2', 'f', 'c', 'b')
        append_record(self.root, 'T3', 'f', 'c', 'c')
        ids = [r['id'] for r in iter_records(self.root)]
        self.assertEqual(ids, ['OBS-001', 'OBS-002', 'OBS-003'])

    def test_update_record_changes_status(self):
        self._add_record({'id': 'OBS-001', 'task': 'TASK-001', 'status': 'open'})
        update_record(self.root, 'OBS-001', status='closed', fix_applied='re-ran gate')
        records = list(iter_records(self.root))
        self.assertEqual(records[0]['status'], 'closed')
        self.assertEqual(records[0]['fix_applied'], 're-ran gate')

    def test_update_record_nonexistent(self):
        self._add_record({'id': 'OBS-001', 'status': 'open'})
        update_record(self.root, 'OBS-999', status='closed')
        records = list(iter_records(self.root))
        self.assertEqual(records[0]['status'], 'open')

    def test_render_md_creates_file(self):
        self._add_record({'id': 'OBS-001', 'task': 'TASK-001', 'feature': 'feat-a',
                          'classification': 'gate-failure', 'severity': 'high',
                          'recurrence_risk': 'low', 'description': 'test desc',
                          'status': 'open', 'fix_applied': 'none yet'})
        render_md(self.root)
        out_path = md_path(self.root)
        self.assertTrue(os.path.exists(out_path))
        content = open(out_path).read()
        self.assertIn('OBS-001', content)
        self.assertIn('TASK-001', content)
        self.assertIn('1 | Open: 1 | Closed: 0', content)

    def test_insights_returns_empty_when_no_records(self):
        top, high, stale = insights(self.root)
        self.assertEqual(top, [])
        self.assertEqual(high, [])
        self.assertEqual(stale, [])

    def test_insights_with_data(self):
        self._add_record({'id': 'OBS-001', 'classification': 'gate-failure',
                          'recurrence_risk': 'high', 'status': 'open',
                          'timestamp': '2020-01-01T00:00:00Z'})
        self._add_record({'id': 'OBS-002', 'classification': 'gate-failure',
                          'recurrence_risk': 'low', 'status': 'open',
                          'timestamp': '2020-01-01T00:00:00Z'})
        top, high, stale = insights(self.root)
        self.assertEqual(len(top), 1)
        self.assertEqual(top[0][0], 'gate-failure')
        self.assertEqual(len(high), 1)
        self.assertEqual(len(stale), 2)


if __name__ == '__main__':
    unittest.main()
