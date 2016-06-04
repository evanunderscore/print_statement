import sys
from setuptools import setup


assert sys.version_info >= (3, 4), 'print_statement requires Python 3.4+'


setup(
    name='print_statement',
    py_modules=['print_statement'],
)
