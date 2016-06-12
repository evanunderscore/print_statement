print_statement
===============

Have you switched to Python 3, only to be repeatedly told this? ::

    SyntaxError: Missing parentheses in call to 'print'

Finally your troubles are over! Reclaim your lost productivity and countless
extra keystrokes by installing the print statement into your Python 3
interpreter today!

Usage
-----

Install the module on your machine::

    $ pip install print_statement

Install `print_statement` into your interpreter::

    >>> import print_statement
    >>> print_statement.install()

Import the print statement and enjoy pure efficiency::

    >>> from __past__ import print_statement
    >>> print 'Hello, world!'

Because you'll never have a reason to not use this, you can have
`print_statement` automatically install itself every time the interpreter
starts (interactively or otherwise)::

    $ python -m print_statement install

In the extremely unlikely event that you later want to remove
`print_statement` from your machine, remember to undo this first::

    $ python -m print_statement uninstall
    $ pip uninstall print_statement

Features
--------

Need to render text to the screen? ::

    print 'Who has time for parentheses?'

How about printing to a file? You don't need keyword arguments taking up
valuable bytes! ::

    print >>file, 'And of course you want to use this cool chevron!'

Need to suppress that trailing newline? With a single comma, you can save a
massive *eight* characters! ::

    print 'feel', 'that', 'efficiency',

FAQ
---

**Q: Will this work in scripts?**

A: Yes, as long as ``print_statement.install()`` is called before your script
is imported. You can do this automatically with
``python -m print_statement install``.

**Q: Is this a hack?**

A: Absolutely.

**Q: Can I use this in production?**

A: Please don't. (``2to3 -f print <module or package>`` will convert your
scripts for use by the unenlightened.)
