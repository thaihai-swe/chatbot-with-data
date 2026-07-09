import unittest
import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from core.harness import (
    Gate, GateResult, Phase, Lifecycle, HarnessConfig, HarnessError, ConfigError,
    resolve_artifact_path, cmd_gates, cmd_lifecycle, cmd_phase_gate,
    cmd_config_validate, cmd_doctor, _read_version, _VALID_ON_FAIL,
)


class TestGate(unittest.TestCase):

    def test_gate_construction(self):
        g = Gate('lint', 'echo ok', stack='python', on_fail='continue', config={})
        self.assertEqual(g.name, 'lint')
        self.assertEqual(g.command, 'echo ok')

    def test_gate_on_fail_defaults_to_block(self):
        g = Gate('lint', 'echo ok', stack='', on_fail='', config={})
        self.assertEqual(g.on_fail, 'block')
        g2 = Gate('lint', 'echo ok', stack='', on_fail=None, config={})
        self.assertEqual(g2.on_fail, 'block')

    def test_gate_run_success(self):
        g = Gate('lint', 'echo ok', stack='', on_fail='', config={})
        result = g.run('/tmp')
        self.assertTrue(result.passed)
        self.assertIn('ok', result.output)

    def test_gate_run_failure(self):
        g = Gate('fail', 'false', stack='', on_fail='', config={})
        result = g.run('/tmp')
        self.assertFalse(result.passed)

    def test_gate_dry_run(self):
        g = Gate('lint', 'echo ok', stack='', on_fail='', config={})
        result = g.run('/tmp', dry_run=True)
        self.assertTrue(result.passed)
        self.assertIn('dry-run', result.output)

    def test_gate_result_to_dict(self):
        r = GateResult('lint', True, 'ok')
        d = r.to_dict()
        self.assertEqual(d['name'], 'lint')
        self.assertTrue(d['passed'])
        self.assertIsNone(d['error'])


class TestResolveArtifactPath(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.feature_dir = os.path.join(self.root, 'artifacts', 'features', 'my-feat')
        os.makedirs(self.feature_dir, exist_ok=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_bare_name_relative_to_feature_dir(self):
        path = resolve_artifact_path(self.feature_dir, 'spec.md')
        self.assertEqual(path, os.path.join(self.feature_dir, 'spec.md'))

    def test_slug_placeholder_substituted(self):
        path = resolve_artifact_path(self.feature_dir, 'features/<slug>/status.md')
        expected = os.path.join(self.root, 'artifacts', 'features', 'my-feat', 'status.md')
        self.assertEqual(path, expected)
        self.assertNotIn('<slug>', path)

    def test_feature_brace_placeholder_substituted(self):
        path = resolve_artifact_path(self.feature_dir, 'features/{feature}/status.md')
        expected = os.path.join(self.root, 'artifacts', 'features', 'my-feat', 'status.md')
        self.assertEqual(path, expected)

    def test_explicit_slug_overrides_dirname(self):
        path = resolve_artifact_path(self.feature_dir, 'features/<slug>/x.md', feature_slug='other')
        self.assertIn(os.path.join('features', 'other', 'x.md'), path)


class TestPhase(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.feature_dir = os.path.join(self.root, 'artifacts', 'features', 'test-feat')
        os.makedirs(self.feature_dir, exist_ok=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_precondition_exists_pass(self):
        open(os.path.join(self.feature_dir, 'spec.md'), 'w').close()
        p = Phase('Spec', [{'artifact': 'spec.md', 'check': 'exists'}], config={})
        fails = p.check_preconditions(self.feature_dir)
        self.assertEqual(fails, [])

    def test_precondition_exists_fail(self):
        p = Phase('Spec', [{'artifact': 'spec.md', 'check': 'exists'}], config={})
        fails = p.check_preconditions(self.feature_dir)
        self.assertEqual(len(fails), 1)
        self.assertIn('spec.md', fails[0])

    def test_precondition_halt_detection(self):
        spec = os.path.join(self.feature_dir, 'spec.md')
        with open(spec, 'w') as f:
            f.write('[:HALT STALE — spec amended 2026-07-03]')
        p = Phase('Spec', [{'artifact': 'spec.md', 'check': 'contains_stale'}], config={})
        fails = p.check_preconditions(self.feature_dir)
        self.assertEqual(len(fails), 1)

    def test_precondition_dry_run(self):
        p = Phase('Spec', [{'artifact': 'spec.md', 'check': 'exists'}], config={})
        fails = p.check_preconditions(self.feature_dir, dry_run=True)
        self.assertEqual(fails, [])

    def test_slug_path_resolves_under_artifacts(self):
        status = os.path.join(self.feature_dir, 'status.md')
        open(status, 'w').close()
        p = Phase('Spec', [{'artifact': 'features/<slug>/status.md', 'check': 'exists'}], config={})
        fails = p.check_preconditions(self.feature_dir, feature_slug='test-feat')
        self.assertEqual(fails, [])

    def test_slug_path_missing_fails_without_literal_placeholder(self):
        p = Phase('Spec', [{'artifact': 'features/<slug>/status.md', 'check': 'exists'}], config={})
        fails = p.check_preconditions(self.feature_dir, feature_slug='test-feat')
        self.assertEqual(len(fails), 1)
        self.assertNotIn('<slug>', fails[0])
        self.assertIn('test-feat', fails[0])


class TestLifecycle(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.feature_dir = os.path.join(self.root, 'artifacts', 'features', 'test-feat')
        os.makedirs(self.feature_dir, exist_ok=True)
        config = {
            'phases': [
                {'name': 'Research', 'preconditions': []},
                {'name': 'Spec', 'preconditions': [{'artifact': 'spec.md', 'check': 'exists'}]},
                {'name': 'Plan', 'preconditions': []},
                {'name': 'Verify', 'preconditions': []},
            ]
        }
        self.lifecycle = Lifecycle(config)

    def tearDown(self):
        self.tmp.cleanup()

    def test_get_phase_names(self):
        names = self.lifecycle.get_phase_names()
        self.assertEqual(names, ['Research', 'Spec', 'Plan', 'Verify'])

    def test_circuit_breaker_defaults_to_last_phase(self):
        block, reset, max_f = self.lifecycle.circuit_breaker_config()
        self.assertEqual(block, 'Verify')
        self.assertIsNone(reset)
        self.assertEqual(max_f, 2)

    def test_circuit_breaker_from_config(self):
        lc = Lifecycle({
            'phases': [
                {'name': 'Spec', 'preconditions': []},
                {'name': 'Plan', 'preconditions': []},
                {'name': 'Verify', 'preconditions': []},
            ],
            'circuit_breaker': {
                'block_phase': 'Verify',
                'reset_phase': 'Plan',
                'max_failures': 3,
            },
        })
        block, reset, max_f = lc.circuit_breaker_config()
        self.assertEqual(block, 'Verify')
        self.assertEqual(reset, 'Plan')
        self.assertEqual(max_f, 3)

    def test_transition_forward(self):
        result = self.lifecycle.transition(
            '', 'Research', self.feature_dir, root=self.root
        )
        self.assertIn('Research', result)

    def test_transition_skip_raises(self):
        with self.assertRaises(HarnessError) as ctx:
            self.lifecycle.transition('', 'Plan', self.feature_dir, root=self.root)
        self.assertIn('skip', str(ctx.exception).lower())

    def test_transition_backwards_raises(self):
        self.lifecycle.transition('', 'Research', self.feature_dir, root=self.root)
        with self.assertRaises(HarnessError) as ctx:
            self.lifecycle.transition('Research', 'Research', self.feature_dir, root=self.root)
        self.assertIn('forward', str(ctx.exception).lower())

    def test_circuit_breaker_blocks_last_phase(self):
        self.lifecycle.transition('', 'Research', self.feature_dir, root=self.root)
        self.lifecycle.record_gate_failure(self.root, 'test-feat', 'lint')
        self.lifecycle.record_gate_failure(self.root, 'test-feat', 'lint')
        with self.assertRaises(HarnessError) as ctx:
            self.lifecycle.transition('Plan', 'Verify', self.feature_dir, root=self.root)
        self.assertIn('CIRCUIT_BREAKER', str(ctx.exception))

    def test_circuit_breaker_reset_phase_clears_failures(self):
        lc = Lifecycle({
            'phases': [
                {'name': 'Spec', 'preconditions': []},
                {'name': 'Plan', 'preconditions': []},
                {'name': 'Verify', 'preconditions': []},
            ],
            'circuit_breaker': {
                'block_phase': 'Verify',
                'reset_phase': 'Plan',
                'max_failures': 2,
            },
        })
        feature_dir = self.feature_dir
        lc.transition('', 'Spec', feature_dir, root=self.root)
        lc.record_gate_failure(self.root, 'test-feat', 'lint')
        lc.record_gate_failure(self.root, 'test-feat', 'lint')
        lc.transition('Spec', 'Plan', feature_dir, root=self.root)
        state = lc.get_state('test-feat', root=self.root)
        self.assertEqual(state.get('consecutive_gate_failures'), 0)
        msg = lc.transition('Plan', 'Verify', feature_dir, root=self.root)
        self.assertIn('Verify', msg)

    def test_record_gate_failure_tracks_count(self):
        self.lifecycle.transition('', 'Research', self.feature_dir, root=self.root)
        c1 = self.lifecycle.record_gate_failure(self.root, 'test-feat', 'lint')
        self.assertEqual(c1, 1)
        c2 = self.lifecycle.record_gate_failure(self.root, 'test-feat', 'lint')
        self.assertEqual(c2, 2)

    def test_record_gate_success_resets(self):
        self.lifecycle.transition('', 'Research', self.feature_dir, root=self.root)
        self.lifecycle.record_gate_failure(self.root, 'test-feat', 'lint')
        c = self.lifecycle.record_gate_success(self.root, 'test-feat')
        self.assertEqual(c, 0)

    def test_get_state(self):
        state = self.lifecycle.get_state('test-feat', root=self.root)
        self.assertEqual(state, {})

    def test_precondition_failure_during_transition(self):
        self.lifecycle.transition('', 'Research', self.feature_dir, root=self.root)
        with self.assertRaises(HarnessError) as ctx:
            self.lifecycle.transition('Research', 'Spec', self.feature_dir, root=self.root)
        self.assertIn('precondition', str(ctx.exception).lower())

    def test_slug_precondition_during_transition(self):
        lc = Lifecycle({
            'phases': [
                {'name': 'Spec', 'preconditions': [
                    {'artifact': 'features/<slug>/status.md', 'check': 'exists'},
                ]},
            ]
        })
        with self.assertRaises(HarnessError) as ctx:
            lc.transition('', 'Spec', self.feature_dir, root=self.root)
        self.assertNotIn('<slug>', str(ctx.exception))
        open(os.path.join(self.feature_dir, 'status.md'), 'w').close()
        msg = lc.transition('', 'Spec', self.feature_dir, root=self.root)
        self.assertIn('Spec', msg)

    def test_list_features_empty(self):
        rows = self.lifecycle.list_features(self.root)
        self.assertEqual(rows, [])

    def test_list_features_after_transition(self):
        self.lifecycle.transition('', 'Research', self.feature_dir, root=self.root)
        self.lifecycle.record_gate_failure(self.root, 'test-feat', 'lint')
        rows = self.lifecycle.list_features(self.root)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['slug'], 'test-feat')
        self.assertEqual(rows[0]['phase'], 'Research')
        self.assertEqual(rows[0]['consecutive_gate_failures'], 1)

    def test_reset_action_via_cli(self):
        # Create markers so resolve_root finds this dir
        core_dir = os.path.join(self.root, 'core-zero', 'project')
        os.makedirs(os.path.join(self.root, 'core-zero', 'memories', 'repo'))
        os.makedirs(core_dir)
        Path(os.path.join(self.root, 'AGENTS.md')).touch()
        # Minimal harness-config.yaml for the config path that cmd_lifecycle reads
        with open(os.path.join(core_dir, 'harness-config.yaml'), 'w') as f:
            f.write("phases:\n  - name: Spec\n    preconditions: []\ngates: []\n")
        args = type('A', (), {
            'root': self.root, 'config': '', 'dry_run': False,
            'action': 'reset', 'feature': 'test-feat',
            'phase': '', 'current_phase': '', 'gate': '', 'json': False,
        })()
        cmd_lifecycle(args)
        state = self.lifecycle.get_state('test-feat', root=self.root)
        self.assertIn(state.get('consecutive_gate_failures'), (0, None))


class TestOnFailGates(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.config_path = os.path.join(self.root, 'harness-config.yaml')

    def tearDown(self):
        self.tmp.cleanup()

    def _write_config(self, on_fail=None, gate_defaults=None):
        gd = f"  on_fail: {gate_defaults}\n" if gate_defaults else ""
        of = f"    on_fail: {on_fail}\n" if on_fail is not None else ""
        with open(self.config_path, 'w') as f:
            f.write(f"""phases:
  - name: Spec
    preconditions: []
gate_defaults:
{gd}gates:
  - name: failgate
    command: "false"
    stack: node
{of}stack_detection:
  node:
    files: []
    gates:
      - failgate
""")

    def _run_gates(self):
        args = type('A', (), {
            'root': self.root, 'config': self.config_path,
            'stack': 'node', 'dry_run': False, 'json': False,
        })()
        cmd_gates(args)

    def test_on_fail_block_exits(self):
        self._write_config('block')
        with self.assertRaises(SystemExit) as ctx:
            self._run_gates()
        self.assertEqual(ctx.exception.code, 1)

    def test_on_fail_warn_continues(self):
        self._write_config('warn')
        self._run_gates()

    def test_on_fail_continue_continues(self):
        self._write_config('continue')
        self._run_gates()

    def test_gate_defaults_used_when_omitted(self):
        # Omit per-gate on_fail; gate_defaults.warn should apply
        self._write_config(on_fail=None, gate_defaults='warn')
        args = type('A', (), {
            'root': self.root, 'config': self.config_path,
            'stack': 'node', 'dry_run': False, 'json': False,
        })()
        cmd_gates(args)


class TestHarnessConfig(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.tmp.name, 'harness-config.yaml')

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, content):
        with open(self.config_path, 'w') as f:
            f.write(content)

    def test_loads_valid_config(self):
        self._write("phases:\n  - name: Spec\n    preconditions: []\ngates: []\n")
        config = HarnessConfig(self.config_path)
        self.assertEqual(len(config.data['phases']), 1)

    def test_missing_config_raises(self):
        with self.assertRaises(HarnessError):
            HarnessConfig('/nonexistent/config.yaml')

    def test_validate_no_phases_raises(self):
        self._write("gates: []\n")
        with self.assertRaises(HarnessError):
            HarnessConfig(self.config_path)

    def test_detect_stack_explicit(self):
        self._write("stack: python\nphases: []\ngates: []\n")
        config = HarnessConfig(self.config_path)
        self.assertEqual(config.detect_stack(self.tmp.name), 'python')

    def test_detect_stack_auto_no_match(self):
        self._write("phases: []\ngates: []\n")
        config = HarnessConfig(self.config_path)
        self.assertIsNone(config.detect_stack(self.tmp.name))

    def test_get_preflight_checks(self):
        self._write("""phases: []
gates: []
preflight_tools:
  node_check:
    command: node --version
    stack: node
    optional: true
""")
        config = HarnessConfig(self.config_path)
        checks = config.get_preflight_checks('node')
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0][0], 'node_check')

    def test_get_preflight_checks_stack_filter(self):
        self._write("""phases: []
gates: []
preflight_tools:
  py_check:
    command: python3 --version
    stack: python
    optional: true
""")
        config = HarnessConfig(self.config_path)
        checks = config.get_preflight_checks('node')
        self.assertEqual(len(checks), 0)

    def test_validate_bad_gate_stack(self):
        self._write("""phases:
  - name: Spec
    preconditions: []
gates:
  - name: x
    command: echo
    stack: nonexistent
stack_detection:
  python: {files: [], gates: []}
""")
        with self.assertRaises(ConfigError) as ctx:
            HarnessConfig(self.config_path)
        self.assertIn('stack', str(ctx.exception).lower())

    def test_validate_bad_on_fail(self):
        self._write("""phases:
  - name: Spec
    preconditions: []
gates:
  - name: x
    command: echo
    on_fail: explode
""")
        with self.assertRaises(ConfigError) as ctx:
            HarnessConfig(self.config_path)
        self.assertIn('on_fail', str(ctx.exception).lower())

    def test_validate_stack_detection_references_unknown_gate(self):
        self._write("""phases:
  - name: Spec
    preconditions: []
gates:
  - name: lint
    command: echo
stack_detection:
  node:
    files: []
    gates:
      - lint
      - missing-gate
""")
        with self.assertRaises(ConfigError) as ctx:
            HarnessConfig(self.config_path)
        self.assertIn('missing-gate', str(ctx.exception))

    def test_validate_token_warn_lt_hard(self):
        self._write("""phases: []
gates: []
thresholds:
  token_warn: 200000
  token_hard: 100000
""")
        with self.assertRaises(ConfigError) as ctx:
            HarnessConfig(self.config_path)
        self.assertIn('token_warn', str(ctx.exception))

    def test_validate_memory_ladder_order(self):
        self._write("""phases: []
gates: []
thresholds:
  memory_warn_lines: 200
  memory_breach_lines: 100
  memory_hard_lines: 3200
""")
        with self.assertRaises(ConfigError) as ctx:
            HarnessConfig(self.config_path)
        self.assertIn('memory', str(ctx.exception))

    def test_validate_negative_threshold(self):
        self._write("""phases: []
gates: []
thresholds:
  timeout_seconds: -1
""")
        with self.assertRaises(ConfigError) as ctx:
            HarnessConfig(self.config_path)
        self.assertIn('positive', str(ctx.exception))


class TestJsonOutput(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.config_path = os.path.join(self.root, 'harness-config.yaml')

    def tearDown(self):
        self.tmp.cleanup()

    def _write_minimal(self):
        with open(self.config_path, 'w') as f:
            f.write("phases:\n  - name: Spec\n    preconditions: []\ngates: []\n")

    def test_config_validate_json(self):
        self._write_minimal()
        args = type('A', (), {
            'root': self.root, 'config': self.config_path,
            'json': True,
        })()
        cmd_config_validate(args)

    def test_lifecycle_list_json_empty(self):
        self._write_minimal()
        # Create markers so resolve_root finds this dir
        os.makedirs(os.path.join(self.root, 'core-zero', 'memories', 'repo'))
        Path(os.path.join(self.root, 'AGENTS.md')).touch()
        args = type('A', (), {
            'root': self.root, 'config': self.config_path,
            'action': 'list', 'feature': '', 'phase': '',
            'current_phase': '', 'gate': '', 'dry_run': False, 'json': True,
        })()
        cmd_lifecycle(args)

    def test_read_version_missing_manifest(self):
        # Patch to a dir with no manifest and no repo fallback
        from unittest.mock import patch
        with patch('core.harness._SCRIPT_DIR', Path('/nonexistent')):
            self.assertEqual(_read_version(self.root), 'unknown')

    def test_read_version_from_manifest(self):
        with open(os.path.join(self.root, 'manifest.json'), 'w') as f:
            f.write('{"version": "9.9.9"}')
        from unittest.mock import patch
        with patch('core.harness._SCRIPT_DIR', Path('/nonexistent')):
            self.assertEqual(_read_version(self.root), '9.9.9')


class TestDoctorSubcommand(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_doctor_passes_on_minimal_root(self):
        # doctor should at least not crash
        args = type('A', (), {
            'root': self.root, 'json': False,
        })()
        try:
            cmd_doctor(args)
        except SystemExit as e:
            # May exit non-zero if checks fail, but should not crash
            self.assertIn(e.code, (0, 1, 2))


if __name__ == '__main__':
    unittest.main()
