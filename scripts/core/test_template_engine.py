import unittest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from core.template_engine import TemplateEngine, TemplateError, render_file, convert_template


class TestTemplateEngine(unittest.TestCase):

    def setUp(self):
        self.engine = TemplateEngine()

    def test_render_simple_slot(self):
        result = self.engine.render('Hello {{name}}', {'name': 'World'})
        self.assertEqual(result, 'Hello World')

    def test_render_slot_default(self):
        result = self.engine.render('Hello {{name|Guest}}', {})
        self.assertEqual(result, 'Hello Guest')

    def test_render_nested_slot(self):
        result = self.engine.render('{{user.name}}', {'user': {'name': 'Alice'}})
        self.assertEqual(result, 'Alice')

    def test_render_if_true(self):
        result = self.engine.render('{{#if show}}visible{{/if}}', {'show': True})
        self.assertEqual(result, 'visible')

    def test_render_if_false(self):
        result = self.engine.render('{{#if show}}visible{{/if}}', {'show': False})
        self.assertEqual(result, '')

    def test_render_if_not(self):
        result = self.engine.render('{{#if !hidden}}visible{{/if}}', {'hidden': False})
        self.assertEqual(result, 'visible')

    def test_render_each(self):
        result = self.engine.render('{{#each items}}{{name}} {{/each}}',
                                     {'items': [{'name': 'a'}, {'name': 'b'}]})
        self.assertEqual(result, 'a b ')

    def test_render_each_scalar(self):
        result = self.engine.render('{{#each items}}{{item}} {{/each}}',
                                     {'items': ['x', 'y']})
        self.assertEqual(result, 'x y ')

    def test_render_each_not_iterable(self):
        result = self.engine.render('{{#each items}}body{{/each}}', {'items': None})
        self.assertEqual(result, '')

    def test_render_include(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('included content')
            inc_path = f.name
        try:
            result = self.engine.render('before {{#include "' + inc_path + '"}} after', {})
            self.assertIn('included content', result)
            self.assertTrue(result.startswith('before'))
            self.assertTrue(result.endswith('after'))
        finally:
            os.unlink(inc_path)

    def test_render_include_not_found(self):
        with self.assertRaises(TemplateError):
            self.engine.render('{{#include "/nonexistent/file.md"}}', {})

    def test_render_include_circular(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('{{#include "' + __file__ + '"}}')
            circ_path = f.name
        try:
            self.engine._included.add(__file__)
            with self.assertRaises(TemplateError):
                self.engine.render('{{#include "' + circ_path + '"}}', {})
        finally:
            os.unlink(circ_path)

    def test_validate_no_errors(self):
        errors = self.engine.validate('Hello {{name}}')
        self.assertEqual(errors, [])

    def test_validate_unbalanced_if(self):
        errors = self.engine.validate('{{#if x}}body')
        self.assertIn('Unbalanced', errors[0])

    def test_validate_unbalanced_each(self):
        errors = self.engine.validate('{{#each items}}body')
        self.assertIn('Unbalanced', errors[0])

    def test_list_slots(self):
        slots = self.engine.list_slots('Hello {{name}}, you are {{age|old}}')
        self.assertEqual(slots, ['age', 'name'])

    def test_detect_placeholders(self):
        ph = self.engine.detect_placeholders('<NAME> and {TITLE}')
        self.assertEqual(sorted(ph), ['NAME', 'TITLE'])

    def test_render_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('{{message}}')
            tmpl_path = f.name
        out_path = tmpl_path + '.out'
        try:
            render_file(tmpl_path, context_dict={'message': 'ok'}, output_path=out_path)
            self.assertTrue(os.path.exists(out_path))
            content = open(out_path).read()
            self.assertEqual(content, 'ok')
        finally:
            os.unlink(tmpl_path)
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_convert_template(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('<NAME> and {TITLE}')
            tmpl_path = f.name
        try:
            ph = convert_template(tmpl_path)
            self.assertEqual(sorted(ph), ['NAME', 'TITLE'])
            content = open(tmpl_path).read()
            self.assertIn('{{NAME}}', content)
            self.assertIn('{{TITLE}}', content)
        finally:
            os.unlink(tmpl_path)

    def test_convert_template_dry_run(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('<NAME>')
            tmpl_path = f.name
        try:
            ph = convert_template(tmpl_path, dry_run=True)
            self.assertEqual(ph, ['NAME'])
            content = open(tmpl_path).read()
            self.assertEqual(content, '<NAME>')  # unchanged
        finally:
            os.unlink(tmpl_path)


if __name__ == '__main__':
    unittest.main()
