from pycparser.c_lexer import CLexer as CLexerBase
from ply.lex import TOKEN




class GNUCLexer(CLexerBase):
    # support '3i' for imaginary literal
    floating_constant = '(((('+CLexerBase.fractional_constant+')'+CLexerBase.exponent_part+'?)|([0-9]+'+CLexerBase.exponent_part+'))i?[FfLl]?)'

    @TOKEN(floating_constant)
    def t_FLOAT_CONST(self, t):
        return t


class OpenCLCLexer(CLexerBase):
    pass

def add_lexer_keywords(cls, keywords):
    cls.keywords = cls.keywords + tuple(
            kw.upper() for kw in keywords)

    cls.keyword_map = cls.keyword_map.copy()
    cls.keyword_map.update(dict(
        (kw, kw.upper()) for kw in keywords))

    cls.tokens = cls.tokens + tuple(
            kw.upper() for kw in keywords)

add_lexer_keywords(GNUCLexer, [
    '__attribute__', '__asm__', '__asm', '__typeof__',
    '__real__', '__imag__', '__builtin_types_compatible_p',
    '__const', '__restrict', '__inline', '__inline__',
    '__extension__'])

add_lexer_keywords(OpenCLCLexer, [
    '__attribute__', '__asm__', '__asm',
    '__kernel', 'kernel',
    '__constant', 'constant',
    '__global', 'global',
    '__local', 'local',
    '__private', 'private',
    ])

