import unittest
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yaml_reader import loads, load


class TestYamlReader(unittest.TestCase):
    """Tests for the hand-rolled YAML parser (yaml_reader.py)."""

    def test_empty_string(self):
        """Empty string returns empty dict."""
        result = loads("")
        self.assertEqual(result, {})

    def test_basic_mapping(self):
        """Simple key: value mapping."""
        yaml = "key: value"
        result = loads(yaml)
        self.assertEqual(result, {"key": "value"})

    def test_multiple_keys(self):
        """Multiple top-level keys."""
        yaml = "key1: value1\nkey2: value2"
        result = loads(yaml)
        self.assertEqual(result, {"key1": "value1", "key2": "value2"})

    def test_integer_value(self):
        """Integer scalar parsing."""
        yaml = "count: 42"
        result = loads(yaml)
        self.assertEqual(result, {"count": 42})

    def test_float_value(self):
        """Float scalar parsing."""
        yaml = "pi: 3.14"
        result = loads(yaml)
        self.assertEqual(result, {"pi": 3.14})

    def test_boolean_true(self):
        """Boolean true parsing."""
        yaml = "enabled: true"
        result = loads(yaml)
        self.assertEqual(result, {"enabled": True})

    def test_boolean_false(self):
        """Boolean false parsing."""
        yaml = "enabled: false"
        result = loads(yaml)
        self.assertEqual(result, {"enabled": False})

    def test_null_value(self):
        """Null value parsing."""
        yaml = "value: null"
        result = loads(yaml)
        self.assertEqual(result, {"value": None})

    def test_quoted_string(self):
        """Double-quoted string value."""
        yaml = 'name: "hello world"'
        result = loads(yaml)
        self.assertEqual(result, {"name": "hello world"})

    def test_single_quoted_string(self):
        """Single-quoted string value."""
        yaml = "name: 'hello world'"
        result = loads(yaml)
        self.assertEqual(result, {"name": "hello world"})

    def test_nested_mapping(self):
        """Nested mapping (dict in dict)."""
        yaml = "outer:\n  inner: value"
        result = loads(yaml)
        self.assertEqual(result, {"outer": {"inner": "value"}})

    def test_inline_sequence(self):
        """Inline sequence parsing."""
        yaml = "items: [a, b, c]"
        result = loads(yaml)
        self.assertEqual(result, {"items": ["a", "b", "c"]})

    def test_block_sequence(self):
        """Block sequence with - items."""
        yaml = "items:\n  - a\n  - b\n  - c"
        result = loads(yaml)
        self.assertEqual(result, {"items": ["a", "b", "c"]})

    def test_inline_mapping(self):
        """Inline mapping {...}."""
        yaml = "config: {key: val, num: 1}"
        result = loads(yaml)
        self.assertEqual(result, {"config": {"key": "val", "num": 1}})

    def test_literal_block(self):
        """Literal block | (preserves newlines)."""
        yaml = "text: |\n  line1\n  line2\n"
        result = loads(yaml)
        self.assertEqual(result, {"text": "line1\nline2\n"})

    def test_folded_block(self):
        """Folded block > (replaces newlines with spaces)."""
        yaml = "text: >\n  line1\n  line2\n"
        result = loads(yaml)
        self.assertEqual(result, {"text": "line1 line2\n"})

    def test_comments(self):
        """# comments are ignored."""
        yaml = "# this is a comment\nkey: value # inline comment"
        result = loads(yaml)
        self.assertEqual(result, {"key": "value"})

    def test_mixed_types(self):
        """Mixed types in a mapping."""
        yaml = "str: hello\nint: 42\nfloat: 3.14\nbool: true\nnull: null"
        result = loads(yaml)
        self.assertEqual(result, {
            "str": "hello",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "null": None
        })

    def test_value_with_colon(self):
        """Values containing colon (e.g. URLs)."""
        yaml = 'url: "https://example.com:8080/path"'
        result = loads(yaml)
        self.assertEqual(result, {"url": "https://example.com:8080/path"})

    def test_deeply_nested(self):
        """Deeply nested dicts."""
        yaml = "a:\n  b:\n    c:\n      d: value"
        result = loads(yaml)
        self.assertEqual(result, {"a": {"b": {"c": {"d": "value"}}}})

    def test_empty_dict_value(self):
        """Empty dict value."""
        yaml = "config: {}"
        result = loads(yaml)
        self.assertEqual(result, {"config": {}})

    def test_empty_list_value(self):
        """Empty list value."""
        yaml = "items: []"
        result = loads(yaml)
        self.assertEqual(result, {"items": []})

    def test_load_from_file(self):
        """File loading via load() function."""
        yaml_content = "key: value\nnested:\n  inner: 42"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            tmp_path = f.name
        try:
            result = load(tmp_path)
            self.assertEqual(result, {"key": "value", "nested": {"inner": 42}})
        finally:
            os.unlink(tmp_path)

    def test_yaml_frontmatter(self):
        """YAML frontmatter (--- ... ---)."""
        yaml = "---\nkey: value\n---"
        result = loads(yaml)
        self.assertEqual(result, {"key": "value"})

    def test_indented_list_in_value(self):
        """List values with varying indentation."""
        yaml = "items:\n  - one\n  - two\nother: value"
        result = loads(yaml)
        self.assertEqual(result, {"items": ["one", "two"], "other": "value"})


if __name__ == '__main__':
    unittest.main()
