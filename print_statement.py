import argparse
import importlib
import importlib.machinery
import importlib.util
import logging
import os
import sys
from ctypes import c_char_p, c_size_t, c_void_p, cast, memmove, pythonapi, CFUNCTYPE
from lib2to3.refactor import RefactoringTool
from lib2to3.pgen2.parse import ParseError
from lib2to3.pgen2.tokenize import TokenError


assert sys.version_info >= (3, 4), 'print_statement requires Python 3.4+'


logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)


def refactor(script, name='<string>'):
    # RefactoringTool.refactor_string seems to have problems parsing
    # if the input string doesn't end with a newline.
    script += '\n'
    try:
        script = _refactor(script, name)
    except TokenError as err:
        msg, (lineno, offset) = err.args
        raise _syntax_error(msg, name, lineno, offset, script) from None
    except ParseError as err:
        msg = 'invalid syntax'
        _, (lineno, offset) = err.context
        raise _syntax_error(msg, name, lineno, offset, script) from None
    assert script[-1] == '\n'
    return script[:-1]


def _refactor(script, name):
    rt = RefactoringTool(['lib2to3.fixes.fix_print'])
    tree = rt.refactor_string(script, name)
    return str(tree)


def _syntax_error(msg, name, lineno, offset, script):
    line = script.split('\n')[lineno - 1]
    return SyntaxError(msg, (name, lineno, offset + 1, line))


class _Printerpreter:
    _MARKER = '### ^^^ context | vvv buffer ###\n'

    def __init__(self):
        self._print_statement = False
        self._context = []
        self._buffer = []

    def refactor(self, line, prompt=None):
        """Refactor a line from the interpreter.

        :param str line: a single line of input coming from the interpreter.
            Assumed to end with a newline or be the empty string.
        :param str prompt: the prompt the interpreter used when getting input.
            Used to determine when to reset code context.
        """
        ps1 = getattr(sys, 'ps1', '>>> ')
        ps2 = getattr(sys, 'ps2', '... ')
        if prompt is not None:
            # Ignore input from anything that doesn't look like the interpreter.
            # WARNING: input('>>> ') looks like the interpreter.
            if prompt not in [ps1, ps2]:
                return line
            if prompt == ps1:
                self.reset()
        assert not line or line.endswith('\n')
        if self._check_past_import(line):
            return '\n'
        self._buffer.append(line)
        if self._print_statement:
            try:
                line = ''.join(self._context + [self._MARKER] + self._buffer)
                line = self._refactor(line)
                _, line = line.split(self._MARKER)
            except _IncompleteInputException:
                # The user hasn't finished typing their statement -
                # return a no-op and keep the line in the buffer.
                return '#\n'
        self._context.extend(self._buffer)
        self._buffer.clear()
        return line

    def _check_past_import(self, line):
        if self._context or self._buffer:
            return False
        if line.split() == 'from __past__ import print_statement'.split():
            self._print_statement = True
            return True

    @staticmethod
    def _refactor(line):
        try:
            return _refactor(line, '<stdin>')
        except TokenError as err:
            if err.args[0].startswith('EOF in multi-line '):
                logger.debug('token error involving eof - need more input')
                raise _IncompleteInputException
            logger.exception('unknown token error - interpeter should handle')
            return line
        except ParseError as err:
            if err.value == '':
                if line.endswith('\n\n'):
                    logger.exception('unknown parse error - interpreter should handle')
                    return line
                logger.debug('incomplete block - may need more input')
                raise _IncompleteInputException
            # No way to consistently treat print as a statement and function,
            # so we have to make sure the interpreter throws some exception.
            # e.g. 'var = print' => 'var = ?print'
            # e.g. 'print(var, file=f)' => 'print(var, file?=f)'
            logger.error('parse error - invalidating token')
            row, col = err.context[1]
            lines = []
            for lineno, line in enumerate(line.split('\n'), start=1):
                if lineno == row:
                    line = line[:col] + '?' + line[col:]
                lines.append(line)
            return '\n'.join(lines)

    def reset(self):
        assert not self._buffer
        self._context.clear()

_printerpreter = _Printerpreter()


class _IncompleteInputException(Exception):
    """More input is required for a complete parse."""


# Return type should be c_char_p but we need access to the pointer.
PyOS_ReadlineFunctionPointer_t = CFUNCTYPE(c_void_p, c_void_p, c_void_p, c_char_p)

pythonapi.PyMem_Realloc.argtypes = [c_void_p, c_size_t]
pythonapi.PyMem_Realloc.restype = c_void_p


@PyOS_ReadlineFunctionPointer_t
def _call_readline(stdin, stdout, prompt):
    ptr = _original(stdin, stdout, prompt)
    prompt = prompt.decode()
    line = cast(ptr, c_char_p).value.decode(sys.stdin.encoding)
    logger.debug('input line %r', line)
    line = _printerpreter.refactor(line, prompt)
    logger.debug('updated line %r', line)
    line = line.encode(sys.stdout.encoding)
    # ptr points to a buffer allocated with PyMem_Malloc.
    size = len(line) + 1
    ptr = pythonapi.PyMem_Realloc(ptr, size)
    memmove(ptr, line, size)
    return ptr


class _PathFinder(importlib.machinery.PathFinder):
    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        logger.info('loading %s', fullname)
        if fullname == 'rlcompleter':
            _install_readline()
        spec = super().find_spec(fullname, path=path, target=target)
        if not spec:
            return spec
        loader = spec.loader
        if isinstance(loader, importlib.machinery.SourceFileLoader):
            spec.loader = _SourceFileLoader(loader.name, loader.path)
        return spec


class _SourceFileLoader(importlib.machinery.SourceFileLoader):
    def source_to_code(self, data, path, *, _optimize=-1):
        source = importlib.util.decode_source(data)
        source = self._refactor(source, path)
        return super().source_to_code(source, path, _optimize=_optimize)

    def _refactor(self, source, name):
        lines = []
        do_refactor = False
        for line in source.split('\n'):
            if line.split() == 'from __past__ import print_statement'.split():
                do_refactor = True
                line = ''
            lines.append(line)
        if do_refactor:
            source = '\n'.join(lines)
            source = refactor(source, name=name)
        return source


_installed = False


def install():
    global _installed
    if _installed:
        logger.warning('print_statement already installed')
        return
    _installed = True
    _install_readline()
    index = sys.meta_path.index(importlib.machinery.PathFinder)
    sys.meta_path[index] = _PathFinder


_original = None


def _install_readline():
    global _original
    assert _installed
    if _original is not None:
        logger.warning('readline hook already installed')
        return
    logger.info('installing readline hook')
    rfp = c_void_p.in_dll(pythonapi, 'PyOS_ReadlineFunctionPointer')
    _original = rfp.value
    if _original is None:
        logger.warning('could not install - will wait for _PathFinder')
        return
    _original = PyOS_ReadlineFunctionPointer_t(_original)
    rfp.value = cast(_call_readline, c_void_p).value


def main():
    path = os.path.dirname(__file__)
    path = os.path.join(path, 'print_statement.pth')
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['install', 'uninstall'])
    parser.add_argument('--path', default=path)
    args = parser.parse_args()
    if args.action == 'install':
        with open(args.path, 'w') as f:
            f.write('import print_statement; print_statement.install()')
        print('created ' + args.path)
    else:
        os.remove(args.path)
        print('deleted ' + args.path)


if __name__ == '__main__':
    main()
