import unittest
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_counter import estimate_tokens, count_tokens, process_text, read_with_budget


class TestTokenCounter(unittest.TestCase):

    def test_estimate_empty(self):
        self.assertEqual(estimate_tokens(''), 0)

    def test_estimate_short(self):
        self.assertEqual(estimate_tokens('hello'), 1)  # 5/4 = 1

    def test_estimate_exact_4_chars(self):
        self.assertEqual(estimate_tokens('abcd'), 1)

    def test_estimate_8_chars(self):
        self.assertEqual(estimate_tokens('abcdefgh'), 2)

    def test_count_tokens_alias(self):
        self.assertEqual(count_tokens('hello'), 1)

    def test_process_summary_with_index(self):
        text = '## Index\n- item1\n- item2\n## Content\nbody text here'
        result, tokens = process_text(text, budget=1000, mode='summary')
        self.assertIn('## Index', result)
        self.assertIn('## Content', result)
        self.assertGreater(tokens, 0)

    def test_process_summary_without_index(self):
        text = '# No Index header\n\nsome content\nmore\n' * 20
        result, tokens = process_text(text, budget=1000, mode='summary')
        self.assertGreater(tokens, 0)

    def test_process_partial(self):
        text = 'header\n\n## Section 1\nbody1\n## Section 2\nbody2\n## Section 3\nbody3\n## Section 4\nbody4'
        result, tokens = process_text(text, budget=10000, mode='partial')
        self.assertIn('## Section 1', result)

    def test_process_head(self):
        text = '\n'.join(f'line{i}' for i in range(100))
        half_tokens = estimate_tokens(text) // 2
        result, tokens = process_text(text, budget=half_tokens, mode='head')
        self.assertLessEqual(tokens, half_tokens * 2)  # approximate

    def test_read_with_budget(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('# Test\n\nsome content here')
            tmp_path = f.name
        try:
            result, tokens = read_with_budget(tmp_path, budget=1000)
            self.assertIn('# Test', result)
            self.assertGreater(tokens, 0)
        finally:
            os.unlink(tmp_path)

    def test_process_outline(self):
        text = '# Top\n\n## Section 1\nbody\n## Section 2\nbody\n### Sub 2a\nmore\n## Section 3\nbody'
        result, tokens = process_text(text, budget=1, mode='outline')
        self.assertIn('## Section 1', result)
        self.assertIn('## Section 2', result)
        self.assertNotIn('body', result)

    def test_process_outline_empty_fallback(self):
        text = 'no headers here\n' * 20
        result, tokens = process_text(text, budget=1, mode='outline')
        self.assertGreater(tokens, 0)

    def test_estimate_tiktoken_fallback(self):
        from token_counter import _HAVE_TIKTOKEN
        text = 'hello world'
        count = estimate_tokens(text)
        if _HAVE_TIKTOKEN:
            self.assertGreater(count, 1)
        else:
            self.assertEqual(count, 2)  # 11/4 = 2

    def test_process_budget_exceeded_returns_full(self):
        text = 'short'
        result, tokens = process_text(text, budget=100, mode='full')
        self.assertEqual(result, text)
        self.assertEqual(tokens, 1)


if __name__ == '__main__':
    unittest.main()
