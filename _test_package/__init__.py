"""For use in `test_print_statement.TestImport`."""


def test(file):
    print >>file, __name__
