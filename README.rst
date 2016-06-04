print_statement
===============

Usage
-----

Install the module on your machine::

    $ pip install print_statement

Install `print_statement` into your interpreter::

    >>> import print_statement
    >>> print_statement.install()

Now you can make print behave as a statement::

    >>> from __past__ import print_statement
    >>> print 'Hello, world!'
    Hello, world!
    >>> with open('/tmp/file.txt', 'w') as f:
    ...     print >>f, 'file contents'
    ...
    >>> open('/tmp/file.txt').read()
    'file contents\n'
    >>> print 1, 2, 3,
    1, 2, 3 >>>

You can choose to have `print_statement` automatically install itself every
time the interpreter starts (interactively or otherwise)::

    $ python -m print_statement install

If you later want to remove print_statement from your machine, remember to
undo this first::

    $ python -m print_statement uninstall
    $ pip uninstall print_statement
