"""For use in `test_print_statement.TestImport`."""
from __past__ import print_statement


def test(file):
    print >>file, __name__
