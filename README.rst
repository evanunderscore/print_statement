print_statement
===============

Usage
-----

Simply import in your interpreter to make print behave as a statement::

    >>> import print_statement
    >>> print 'Hello, world!'
    Hello, world!
    >>> with open('/tmp/file.txt', 'w') as f:
    ...     print >>f, 'file contents'
    ...
    >>> open('/tmp/file.txt').read()
    'file contents\n'
    >>> print 1, 2, 3,
    1, 2, 3 >>>

(NOTE: This only works in the interpreter.)
