import unittest
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from core.context_engine import (
    Scorer, BudgetTracker, Compressor, parse_tier,
    extract_section, _path_for_source, parse_phase_matrix,
    ContextEngine, load_context_config, resolve_route,
)


class TestScorer(unittest.TestCase):

    def test_no_keywords_returns_base(self):
        s = Scorer([])
        self.assertEqual(s.score('/nonexistent', base_score=50), 50)

    def test_score_by_word(self):
        s = Scorer(['auth'])
        path = '/dev/null'
        # score 50 base + 0 keyword hits on /dev/null
        self.assertEqual(s.score(path, base_score=50), 50)

    def test_score_with_phrase(self):
        s = Scorer(['access control'])
        self.assertEqual(s.words, [])
        self.assertEqual(s.phrases, ['access control'])

    def test_score_caps_at_100(self):
        s = Scorer(['auth', 'user', 'login', 'token', 'permission', 'role', 'session'])
        self.assertEqual(s.words, [r'auth', r'user', r'login', r'token', r'permission', r'role', r'session'])
        self.assertEqual(s.phrases, [])


class TestBudgetTracker(unittest.TestCase):

    def test_default_thresholds(self):
        bt = BudgetTracker(warn=100, hard=200)
        self.assertEqual(bt.warn, 100)
        self.assertEqual(bt.hard, 200)

    def test_check_under_budget(self):
        bt = BudgetTracker(warn=100, hard=200)
        ok, msg = bt.check('/some/file', 50)
        self.assertTrue(ok)

    def test_check_over_hard(self):
        bt = BudgetTracker(warn=100, hard=200)
        ok, msg = bt.check('/some/file', 250)
        self.assertFalse(ok)
        self.assertIn('BUDGET_HARD', msg)

    def test_add_tracks_total(self):
        bt = BudgetTracker(warn=100, hard=200)
        bt.add('/a', 50, 30)
        bt.add('/b', 30, 20)
        self.assertEqual(bt.total, 80)
        self.assertEqual(len(bt.loaded), 2)

    def test_evict_to_budget(self):
        bt = BudgetTracker(warn=100, hard=100)
        bt.add('/a', 60, 10)
        bt.add('/b', 60, 5)
        evicted = bt.evict_to_budget()
        self.assertEqual(len(evicted), 1)
        self.assertLessEqual(bt.total, 100)


class TestCompressor(unittest.TestCase):

    def setUp(self):
        self.c = Compressor()

    def test_compress_nonexistent(self):
        result, tokens = self.c.compress('/nonexistent')
        self.assertIsNone(result)
        self.assertEqual(tokens, 0)

    def test_compress_preserves_ids(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('CC-001 rule\nCC-002 rule\n')
            tmp_path = f.name
        try:
            result, tokens = self.c.compress(tmp_path)
            self.assertIn('CC-001', result)
            self.assertIn('CC-002', result)
            self.assertGreater(tokens, 0)
        finally:
            os.unlink(tmp_path)

    def test_compress_deduplicates_ids(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('CC-001 original\nCC-001 duplicate\nmore text\n')
            tmp_path = f.name
        try:
            result, tokens = self.c.compress(tmp_path)
            self.assertIn('CC-001 original', result)
            self.assertNotIn('CC-001 duplicate', result)
        finally:
            os.unlink(tmp_path)

    def test_compress_truncates_long_lines(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('x' * 300)
            tmp_path = f.name
        try:
            result, tokens = self.c.compress(tmp_path)
            self.assertIn('...', result)
            self.assertLess(len(result.rstrip('\n')), 300)
        finally:
            os.unlink(tmp_path)


class TestParseTier(unittest.TestCase):

    def test_simple_tier(self):
        tier, sec = parse_tier('Must')
        self.assertEqual(tier, 'Must')
        self.assertIsNone(sec)

    def test_tier_with_sections(self):
        tier, sec = parse_tier('Must {## Purpose, ## Rules}')
        self.assertEqual(tier, 'Must')
        self.assertEqual(sec, ['Purpose', 'Rules'])

    def test_skip_tier(self):
        tier, sec = parse_tier('Skip')
        self.assertEqual(tier, 'Skip')
        self.assertIsNone(sec)


class TestExtractSection(unittest.TestCase):

    def test_extract_existing_section(self):
        text = '# Header\n\n## Purpose\ncontent here\n\n## Rules\nmore'
        result = extract_section(text, 'Purpose')
        self.assertIn('## Purpose', result)
        self.assertIn('content here', result)
        self.assertNotIn('## Rules', result)

    def test_extract_nonexistent_returns_none(self):
        result = extract_section('## Some header\ncontent', 'Missing')
        self.assertIsNone(result)

    def test_extract_case_insensitive(self):
        text = '## PURPOSE\nxyz'
        result = extract_section(text, 'purpose')
        self.assertIsNotNone(result)


class TestPathForSource(unittest.TestCase):

    def test_bare_name(self):
        self.assertEqual(_path_for_source('core-policies.md'),
                         'core-zero/memories/repo/core-policies.md')

    def test_with_prefix(self):
        self.assertEqual(_path_for_source('core-zero/project/architecture.md'),
                         'core-zero/project/architecture.md')

    def test_domain_path(self):
        self.assertEqual(_path_for_source('domain/example/glossary.md'),
                         'core-zero/memories/domain/example/glossary.md')

    def test_telemetry(self):
        self.assertEqual(_path_for_source('harness-telemetry.md'),
                         'core-zero/memories/repo/harness-telemetry.md')

    def test_session_extracts(self):
        self.assertIsNone(_path_for_source('session-extracts.md'))


class TestParsePhaseMatrix(unittest.TestCase):

    def test_empty_when_no_matrix(self):
        rows = parse_phase_matrix('# Just a header')
        self.assertEqual(rows, [])

    def test_parses_table(self):
        md = """## 3. Phase × Guidance Matrix

| Source | Spec | Plan | Implement | Verify |
|--------|------|------|-----------|--------|
| `core-policies.md` | Must | Should | Must | Should |
| `harness-config.md` | Skip | Should {## Routing} | Skip | Skip |
"""
        rows = parse_phase_matrix(md)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0].strip(), '`core-policies.md`')
        self.assertEqual(rows[0][1], 'Must')
        self.assertEqual(rows[1][1], 'Skip')
        self.assertEqual(rows[1][3], 'Should')
        self.assertEqual(rows[1][4], ['Routing'])


class TestScorerKeywordMatch(unittest.TestCase):

    def test_keyword_match_boosts_score(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('auth module handles login tokens and sessions\n')
            path = f.name
        try:
            s = Scorer(['auth', 'login'])
            score = s.score(path, base_score=0)
            self.assertGreater(score, 0)
            self.assertLessEqual(score, 100)
        finally:
            os.unlink(path)

    def test_score_caps_at_100_with_hits(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            # many repeats of keywords to max out score
            f.write('auth user login token permission role session\n' * 20)
            path = f.name
        try:
            s = Scorer(['auth', 'user', 'login', 'token', 'permission', 'role', 'session'])
            score = s.score(path, base_score=40)
            self.assertEqual(score, 100)
        finally:
            os.unlink(path)


class TestLoadContextConfig(unittest.TestCase):

    def test_defaults_when_no_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = load_context_config(tmp)
            self.assertEqual(cfg['tier_boost']['Must'], 40)
            self.assertEqual(cfg['summary_budget'], 800)

    def test_overrides_from_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_dir = os.path.join(tmp, 'core-zero', 'project')
            os.makedirs(cfg_dir)
            with open(os.path.join(cfg_dir, 'harness-config.yaml'), 'w') as f:
                f.write("""phases: []
gates: []
context:
  summary_budget: 500
  partial_budget: 900
  tier_boost:
    Must: 50
""")
            cfg = load_context_config(tmp)
            self.assertEqual(cfg['summary_budget'], 500)
            self.assertEqual(cfg['partial_budget'], 900)
            self.assertEqual(cfg['tier_boost']['Must'], 50)


class TestResolveRouteAndSessionStart(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        # Create AGENTS.md + core-zero/memories/repo/ markers so resolve_root finds this dir
        os.makedirs(os.path.join(self.root, 'core-zero', 'memories', 'repo'), exist_ok=True)
        Path(os.path.join(self.root, 'AGENTS.md')).touch()
        # Minimal MASTER_INDEX with phase matrix
        with open(os.path.join(self.root, 'MASTER_INDEX.md'), 'w') as f:
            f.write("""# Index

## 3. Phase × Guidance Matrix

| Source | Spec | Plan | Implement | Verify |
|--------|------|------|-----------|--------|
| `core-policies.md` | Must | Should | Must | Should |
| `harness-config.md` | Skip | Should | Skip | Skip |
""")
        # Always-group files
        mem = os.path.join(self.root, 'core-zero', 'memories', 'repo')
        rules = os.path.join(self.root, 'core-zero', 'rules')
        os.makedirs(mem, exist_ok=True)
        os.makedirs(rules, exist_ok=True)
        with open(os.path.join(mem, 'core-policies.md'), 'w') as f:
            f.write('## Purpose\npolicy body\n## Normative Rules\nrules\n')
        with open(os.path.join(mem, 'harness-config.md'), 'w') as f:
            f.write('## Artifact Routing\nroutes\n')
        with open(os.path.join(rules, 'caveman.md'), 'w') as f:
            f.write('# Caveman\n')
        with open(os.path.join(rules, 'headroom.md'), 'w') as f:
            f.write('# Headroom\n')

    def tearDown(self):
        self.tmp.cleanup()

    def test_resolve_route_spec(self):
        entries = resolve_route(self.root, 'spec')
        paths = [e[0] for e in entries]
        self.assertTrue(any('core-policies.md' in p for p in paths))
        # harness-config is Skip for Spec
        self.assertFalse(any('harness-config.md' in p for p in paths))

    def test_resolve_route_plan_includes_should(self):
        entries = resolve_route(self.root, 'plan')
        paths = [e[0] for e in entries]
        self.assertTrue(any('harness-config.md' in p for p in paths))

    def test_run_session_start_loads_always(self):
        engine = ContextEngine(self.root, mode='summary')
        # Should not raise; loads Always group if present
        engine.run_session_start(phase=None, mode='summary')
        # Budget tracker should have loaded at least Always files that exist
        self.assertGreaterEqual(len(engine.budget_tracker.loaded), 1)


if __name__ == '__main__':
    unittest.main()
