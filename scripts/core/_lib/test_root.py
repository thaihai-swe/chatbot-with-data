import unittest
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from root import resolve_root


class TestRootResolution(unittest.TestCase):

    def _create_fake_root(self, use_kit_subdir=False):
        tmp = tempfile.TemporaryDirectory()
        if use_kit_subdir:
            kit_dir = os.path.join(tmp.name, 'kit')
            os.makedirs(os.path.join(kit_dir, 'core-zero/memories/repo'))
            open(os.path.join(kit_dir, 'AGENTS.md'), 'w').close()
        else:
            os.makedirs(os.path.join(tmp.name, 'core-zero/memories/repo'))
            open(os.path.join(tmp.name, 'AGENTS.md'), 'w').close()
        return tmp

    def test_resolve_with_hint(self):
        tmp = self._create_fake_root()
        try:
            result = resolve_root(tmp.name)
            self.assertEqual(result, tmp.name)
        finally:
            tmp.cleanup()

    def test_resolve_with_kit_subdir(self):
        tmp = self._create_fake_root(use_kit_subdir=True)
        try:
            result = resolve_root(tmp.name)
            self.assertEqual(result, os.path.join(tmp.name, 'kit'))
        finally:
            tmp.cleanup()

    def test_resolve_no_markers(self):
        tmp = tempfile.TemporaryDirectory()
        try:
            result = resolve_root(tmp.name)
            self.assertIsNone(result)
        finally:
            tmp.cleanup()

    def test_resolve_hint_no_markers(self):
        tmp = tempfile.TemporaryDirectory()
        try:
            result = resolve_root(tmp.name)
            self.assertIsNone(result)
        finally:
            tmp.cleanup()

    def test_resolve_nonexistent_falls_to_cwd(self):
        result = resolve_root('/nonexistent/path')
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
