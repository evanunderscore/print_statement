import sys
from setuptools import setup


assert sys.version_info >= (3, 4), 'print_statement requires Python 3.4+'


with open('README.rst') as readme:
    long_description = readme.read()


setup(
    name='print_statement',
    version='0.1.0',
    description='from __past__ import print_statement',
    long_description=long_description,
    author='evan_',
    author_email='evanunderscore@gmail.com',
    url='https://pypi.python.org/pypi/print_statement',
    license='GNU General Public License v3',
    py_modules=['print_statement'],
    test_suite='test_print_statement',
    tests_require=['coverage'],
    setup_requires=['nose'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    keywords='print statement',
)
