import io
import os
import unittest
import sys

import print_statement
from print_statement import refactor


class TestRefactor(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(refactor('print 1'), 'print(1)')

    def test_multiple(self):
        self.assertEqual(refactor('print 1, 2, 3'), 'print(1, 2, 3)')

    def test_file(self):
        self.assertEqual(refactor('print >>f, 1'), 'print(1, file=f)')

    def test_end(self):
        self.assertEqual(refactor('print 1,'), "print(1, end=' ')")

    def test_newline(self):
        self.assertEqual(refactor('print 1\n'), 'print(1)\n')

    def test_continued(self):
        self.assertEqual(refactor('print 1,\\\n2'), 'print(1,\\\n2)')

    def test_multiline(self):
        self.assertEqual(refactor('print (\n1)'), 'print((\n1))')

    def test_multiline_string(self):
        self.assertEqual(refactor('print """\n1"""'), 'print("""\n1""")')

    def test_condition(self):
        self.assertEqual(refactor('if True:\n print 1'), 'if True:\n print(1)')

    def test_function(self):
        self.assertEqual(refactor('def f():\n print 1'), 'def f():\n print(1)')

    def test_class(self):
        self.assertEqual(refactor('class F:\n print 1'), 'class F:\n print(1)')


class TestPrinterpreter(unittest.TestCase):
    def setUp(self):
        self.printerpreter = print_statement._Printerpreter()
        self.refactor = self.printerpreter.refactor

    def test_simple(self):
        self.assertEqual(self.refactor('print 1\n'), 'print(1)\n')

    def test_multiple(self):
        self.assertEqual(self.refactor('print 1, 2, 3\n'), 'print(1, 2, 3)\n')

    def test_file(self):
        self.assertEqual(self.refactor('print >>f, 1\n'), 'print(1, file=f)\n')

    def test_end(self):
        self.assertEqual(self.refactor('print 1,\n'), "print(1, end=' ')\n")

    def test_continued(self):
        self.assertEqual(self.refactor('print 1,\\\n'), '#\n')
        self.assertEqual(self.refactor('2\n'), 'print(1,\\\n2)\n')

    def test_multiline(self):
        self.assertEqual(self.refactor('print (\n'), '#\n')
        self.assertEqual(self.refactor('1)\n'), 'print((\n1))\n')

    def test_multiline_string(self):
        self.assertEqual(self.refactor('print """\n'), '#\n')
        self.assertEqual(self.refactor('1"""\n'), 'print("""\n1""")\n')

    def test_condition(self):
        self.assertEqual(self.refactor('if True:\n'), '#\n')
        self.assertEqual(self.refactor(' print 1\n'), 'if True:\n print(1)\n')

    def test_function(self):
        self.assertEqual(self.refactor('def f():\n'), '#\n')
        self.assertEqual(self.refactor(' print 1\n'), 'def f():\n print(1)\n')

    def test_class(self):
        self.assertEqual(self.refactor('class F:\n'), '#\n')
        self.assertEqual(self.refactor(' print 1\n'), 'class F:\n print(1)\n')

    def test_with(self):
        self.assertEqual(self.refactor('with x:\n'), '#\n')
        self.assertEqual(self.refactor(' print 1\n'), 'with x:\n print(1)\n')

    def test_try(self):
        self.assertEqual(self.refactor('try:\n'), '#\n')
        self.assertEqual(self.refactor(' print 1\n'), '#\n')
        self.assertEqual(self.refactor('except:\n'), '#\n')
        self.assertEqual(self.refactor(' pass\n'), 'try:\n print(1)\nexcept:\n pass\n')

    def test_eof(self):
        self.assertEqual(self.refactor(''), '')

    def test_no_print_function(self):
        self.assertEqual(self.refactor('print print\n'), 'print ?print\n')

    def test_no_print_kwargs(self):
        self.assertEqual(self.refactor('print(1, file=f)\n'), 'print(1, file?=f)\n')

    def test_no_print_assignment(self):
        self.assertEqual(self.refactor('print = 1\n'), 'print ?= 1\n')

    def test_error(self):
        self.assertEqual(self.refactor('return return\n'), 'return ?return\n')

    def test_empty_block(self):
        """Test an empty block is allowed to end."""
        self.assertEqual(self.refactor('if True:\n'), '#\n')
        self.assertEqual(self.refactor('\n'), 'if True:\n\n')

    def test_bad_try(self):
        """Test a try with no except is allowed to end."""
        self.assertEqual(self.refactor('try:\n'), '#\n')
        self.assertEqual(self.refactor(' pass\n'), '#\n')
        self.assertEqual(self.refactor('\n'), 'try:\n pass\n\n')


class TestImport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert '_test_package' not in sys.modules

    def test_import_package(self):
        import _test_package
        buffer = io.StringIO()
        _test_package.test(buffer)
        buffer.seek(0)
        self.assertEqual(buffer.read(), '_test_package\n')
        self.assertEqual(_test_package.test.__module__, '_test_package')

    def test_import_module(self):
        from _test_package import test_module
        buffer = io.StringIO()
        test_module.test(buffer)
        buffer.seek(0)
        self.assertEqual(buffer.read(), '_test_package.test_module\n')
        self.assertEqual(test_module.test.__module__, '_test_package.test_module')

    def test_token_error(self):
        with self.assertRaises(SyntaxError) as err:
            from _test_package import token_error
        filename = os.path.basename(err.exception.filename)
        self.assertEqual(filename, 'token_error.py')

    def test_syntax_error(self):
        with self.assertRaises(SyntaxError) as err:
            from _test_package import parse_error
        filename = os.path.basename(err.exception.filename)
        self.assertEqual(filename, 'parse_error.py')
