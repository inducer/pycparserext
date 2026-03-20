from pycparser.c_lexer import CLexer as CLexerBase


_COMMON_EXTRA_KEYWORDS = {
    "__attribute__": "__ATTRIBUTE__",
    "__attribute": "__ATTRIBUTE",
    "__asm__": "__ASM__",
    "__asm": "__ASM",
    "asm": "ASM",
}

_GNU_EXTRA_KEYWORDS = {
    "__typeof__": "__TYPEOF__",
    "typeof": "TYPEOF",
    "__typeof": "__TYPEOF",
    "__real__": "__REAL__",
    "__imag__": "__IMAG__",
    "__builtin_types_compatible_p": "__BUILTIN_TYPES_COMPATIBLE_P",
    "__const": "__CONST",
    "__restrict__": "__RESTRICT__",
    "__restrict": "__RESTRICT",
    "__inline__": "__INLINE__",
    "__inline": "__INLINE",
    "__extension__": "__EXTENSION__",
    "__volatile": "__VOLATILE",
    "__volatile__": "__VOLATILE__",
    "__alignof__": "__ALIGNOF__",
}

_OCL_BASE_KEYWORDS = {
    "kernel": "KERNEL",
    "constant": "CONSTANT",
    "global": "GLOBAL",
    "local": "LOCAL",
    "private": "PRIVATE",
    "read_only": "READ_ONLY",
    "write_only": "WRITE_ONLY",
    "read_write": "READ_WRITE",
}

_OCL_EXTRA_KEYWORDS = {
    **{f"__{k}": f"__{v}__" for k, v in _OCL_BASE_KEYWORDS.items()},
    **_OCL_BASE_KEYWORDS,
    # __kernel is a special case: maps to __KERNEL (without trailing __)
    "__kernel": "__KERNEL",
}


class GnuCLexer(CLexerBase):
    """GNU C lexer that recognizes GNU-specific keywords."""

    _extra_keywords = {**_COMMON_EXTRA_KEYWORDS, **_GNU_EXTRA_KEYWORDS}

    def token(self):
        tok = super().token()
        if tok is not None and tok.type == "ID":
            new_type = self._extra_keywords.get(tok.value)
            if new_type is not None:
                tok.type = new_type
        return tok


class GNUCLexer(GnuCLexer):
    def __init__(self, *args, **kwargs):
        from warnings import warn
        warn("GNUCLexer is now called GnuCLexer",
                DeprecationWarning, stacklevel=2)
        GnuCLexer.__init__(self, *args, **kwargs)


class OpenCLCLexer(CLexerBase):
    """OpenCL C lexer that recognizes OpenCL-specific keywords and line
    comments."""

    _extra_keywords = {**_COMMON_EXTRA_KEYWORDS, **_OCL_EXTRA_KEYWORDS}

    def token(self):
        tok = super().token()
        if tok is not None and tok.type == "ID":
            new_type = self._extra_keywords.get(tok.value)
            if new_type is not None:
                tok.type = new_type
        return tok

    def _match_token(self):
        """Override to silently consume // line comments."""
        text = self._lexdata
        pos = self._pos
        if text[pos:pos + 2] == "//":
            end = text.find("\n", pos)
            if end == -1:
                self._pos = len(text)
            else:
                self._pos = end
            return None
        return super()._match_token()


# Legacy helper - not needed for pycparser 3.0 but kept for API compatibility
def add_lexer_keywords(cls, keywords):
    """Add keywords to a lexer class's _extra_keywords dict.

    This modifies the class in place.
    """
    if not hasattr(cls, "_extra_keywords"):
        cls._extra_keywords = {}
    else:
        cls._extra_keywords = dict(cls._extra_keywords)
    cls._extra_keywords.update({kw: kw.upper() for kw in keywords})


# vim: fdm=marker
