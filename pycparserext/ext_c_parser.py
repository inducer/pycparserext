from __future__ import division

import pycparser.c_parser
import pycparser.c_ast as c_ast
try:
    import pycparser.ply.yacc as yacc
except ImportError:
    import ply.yacc as yacc


class CParserBase(pycparser.c_parser.CParser):
    OPT_RULES = [
        'abstract_declarator',
        'assignment_expression',
        'declaration_list',
        'declaration_specifiers',
        'designation',
        'expression',
        'identifier_list',
        'init_declarator_list',
        'initializer_list',
        'parameter_type_list',
        'specifier_qualifier_list',
        'block_item_list',
        'type_qualifier_list',
        'struct_declarator_list'
    ]

    def __init__(self, yacc_debug=False):
        self.clex = self.lexer_class(
                error_func=self._lex_error_func,
                on_lbrace_func=self._lex_on_lbrace_func,
                on_rbrace_func=self._lex_on_rbrace_func,
                type_lookup_func=self._lex_type_lookup_func)

        self.clex.build()
        self.tokens = self.clex.tokens

        for rule in self.OPT_RULES:
            self._create_opt_rule(rule)

        self.ext_start_symbol = "translation_unit_or_empty"

        self.cparser = yacc.yacc(
            module=self,
            start=self.ext_start_symbol,
            debug=yacc_debug, write_tables=False)

    def parse(self, text, filename='', debuglevel=0,
            initial_type_symbols=set()):
        self.clex.filename = filename
        self.clex.reset_lineno()

        # _scope_stack[-1] is the current (topmost) scope.

        initial_scope = dict((tpsym, 1) for tpsym in initial_type_symbols)
        initial_scope.update(
                dict((tpsym, 1) for tpsym in self.initial_type_symbols))
        self._scope_stack = [initial_scope]

        if not text or text.isspace():
            return c_ast.FileAST([])
        else:
            return self.cparser.parse(text, lexer=self.clex, debug=debuglevel)


# {{{ ast extensions

class TypeList(c_ast.Node):
    def __init__(self, types, coord=None):
        self.types = types
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.types or []):
            nodelist.append(("types[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()


class AttributeSpecifier(c_ast.Node):
    def __init__(self, exprlist):
        self.exprlist = exprlist

    def children(self):
        return [("exprlist", self.exprlist)]

    attr_names = ()


class Asm(c_ast.Node):
    def __init__(self, asm_keyword, template, output_operands,
            input_operands, clobbered_regs, coord=None):
        self.asm_keyword = asm_keyword
        self.template = template
        self.output_operands = output_operands
        self.input_operands = input_operands
        self.clobbered_regs = clobbered_regs
        self.coord = coord

    def children(self):
        nodelist = []
        if self.template is not None:
            nodelist.append(("template", self.template))
        if self.output_operands is not None:
            nodelist.append(("output_operands", self.output_operands))
        if self.input_operands is not None:
            nodelist.append(("input_operands", self.input_operands))
        if self.clobbered_regs is not None:
            nodelist.append(("clobbered_regs", self.clobbered_regs))
        return tuple(nodelist)

    attr_names = ('asm_keyword',)


class PreprocessorLine(c_ast.Node):
    def __init__(self, contents, coord=None):
        self.contents = contents
        self.coord = coord

    def children(self):
        return ()

    attr_names = ("contents",)


class TypeOfDeclaration(c_ast.Node):
    def __init__(self, declaration, coord=None):
        self.declaration = declaration
        self.coord = coord

    def children(self):
        nodelist = []
        if self.declaration is not None:
            nodelist.append(("declaration", self.declaration))
        return tuple(nodelist)

    attr_names = ()


class TypeOfExpression(c_ast.Node):
    def __init__(self, expr, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None:
            nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    attr_names = ()


# These are the same as pycparser's, but it does *not* declare __slots__--
# so we can poke in attributes at our leisure.
class TypeDeclExt(c_ast.TypeDecl):
    @staticmethod
    def from_pycparser(td):
        assert isinstance(td, c_ast.TypeDecl)
        return TypeDeclExt(td.declname, td.quals, td.type, td.coord)


class ArrayDeclExt(c_ast.TypeDecl):
    @staticmethod
    def from_pycparser(ad):
        assert isinstance(ad, c_ast.ArrayDecl)
        return ArrayDeclExt(ad.type, ad.dim, ad.dim_quals, ad.coord)


def to_decl_ext(d):
    if isinstance(d, c_ast.TypeDecl):
        return TypeDeclExt.from_pycparser(d)
    elif isinstance(d, c_ast.ArrayDecl):
        return ArrayDeclExt.from_pycparser(d)
    else:
        raise TypeError("unexpected decl type: %s" % type(d).__name__)


class FuncDeclExt(c_ast.Node):
    def __init__(self, args, type, attributes, asm, coord=None):
        self.args = args
        self.type = type
        self.attributes = attributes
        self.asm = asm
        self.coord = coord

    def children(self):
        nodelist = []
        if self.args is not None:
            nodelist.append(("args", self.args))
        if self.type is not None:
            nodelist.append(("type", self.type))
        if self.attributes is not None:
            nodelist.append(("attributes", self.attributes))
        if self.asm is not None:
            nodelist.append(("asm", self.asm))
        return tuple(nodelist)

    attr_names = ()

# }}}


# {{{ attributes

class _AttributesMixin(object):
    def p_attributes_opt_1(self, p):
        """ attributes_opt : attribute_decl attributes_opt
        """
        p[1].exprs.extend(p[2].exprs)
        p[0] = p[1]

    def p_attributes_opt_2(self, p):
        """ attributes_opt : empty
        """
        p[0] = c_ast.ExprList([], self._coord(p.lineno(1)))

    def p_attribute_decl(self, p):
        """ attribute_decl : __ATTRIBUTE__ LPAREN LPAREN attribute_list RPAREN RPAREN
                           | __ATTRIBUTE LPAREN LPAREN attribute_list RPAREN RPAREN
        """
        p[0] = p[4]

    def p_attribute_list_1(self, p):
        """ attribute_list : attribute
        """
        p[0] = c_ast.ExprList([p[1]], self._coord(p.lineno(1)))

    def p_attribute_list_2(self, p):
        """ attribute_list : attribute_list COMMA attribute
        """
        p[1].exprs.append(p[3])
        p[0] = p[1]

    def p_attribute_1(self, p):
        """ attribute : CONST
        """
        p[0] = c_ast.ID(name="const", coord=self._coord(p.lineno(1)))

    def p_attribute_3(self, p):
        """ attribute : assignment_expression
        """
        p[0] = p[1]

    # {{{ /!\ names must match C parser to override

    def p_declarator_1(self, p):
        """ declarator  : direct_declarator attributes_opt
        """
        if p[2].exprs:
            if isinstance(p[1], c_ast.ArrayDecl):
                p[1].type = to_decl_ext(p[1].type)
                p[1].type.attributes = p[2]
            elif isinstance(p[1], c_ast.FuncDecl):
                p[1].type = to_decl_ext(p[1].type)
                p[1].type.attributes = p[2]
            elif not isinstance(p[1], c_ast.TypeDecl):
                raise NotImplementedError(
                        "cannot attach attributes to nodes of type '%s'"
                        % type(p[1]))
            else:
                p[1] = to_decl_ext(p[1])
                p[1].attributes = p[2]

        p[0] = p[1]

    # }}}
    def p_declarator_2(self, p):
        """declarator  : pointer direct_declarator attributes_opt
                       | pointer attributes_opt direct_declarator
        """
        if hasattr(p[3], "exprs"):
            attr_decl = p[3]
            decl = p[2]
        elif hasattr(p[2], "exprs"):
            attr_decl = p[2]
            decl = p[3]
        else:
            attr_decl = None
            decl = p[2]

        if not attr_decl.exprs:
            attr_decl = None

        if attr_decl:
            if isinstance(decl, c_ast.ArrayDecl):
                decl.type = to_decl_ext(decl.type)
                decl.type.attributes = attr_decl
            elif isinstance(decl, c_ast.FuncDecl):
                decl.type = to_decl_ext(decl.type)
                decl.type.attributes = attr_decl
            elif not isinstance(p[2], c_ast.TypeDecl):
                raise NotImplementedError(
                        "cannot attach attributes to nodes of type '%s'"
                        % type(p[1]))
            else:
                decl = to_decl_ext(decl)
                decl.attributes = attr_decl

        p[0] = self._type_modify_decl(decl, p[1])

    def p_function_specifier_attr(self, p):
        """ function_specifier  : attribute_decl
        """
        p[0] = AttributeSpecifier(p[1])

# }}}


# {{{ asm

class _AsmMixin(object):
    def p_asm_opt_1(self, p):
        """ asm_opt : empty
        """
        p[0] = None

    def p_asm_opt_2(self, p):
        """ asm_opt : asm_no_semi
        """
        p[0] = p[1]

    def p_asm_1(self, p):
        """ asm_no_semi : asm_keyword LPAREN asm_argument_expression_list RPAREN
        """
        p[0] = Asm(p[1], p[3], None, None, None, coord=self._coord(p.lineno(1)))

    def p_asm_2(self, p):
        """ asm_no_semi : asm_keyword LPAREN asm_argument_expression_list COLON \
                asm_argument_expression_list RPAREN
        """
        p[0] = Asm(p[1], p[3], p[5], None, None, coord=self._coord(p.lineno(1)))

    def p_asm_3(self, p):
        """ asm_no_semi : asm_keyword LPAREN asm_argument_expression_list COLON \
                asm_argument_expression_list COLON asm_argument_expression_list \
                RPAREN
        """
        p[0] = Asm(p[1], p[3], p[5], p[7], None, coord=self._coord(p.lineno(1)))

    def p_asm_4(self, p):
        """ asm_no_semi : asm_keyword LPAREN asm_argument_expression_list COLON \
                asm_argument_expression_list COLON asm_argument_expression_list \
                COLON asm_argument_expression_list RPAREN
        """
        p[0] = Asm(p[1], p[3], p[5], p[7], p[9], coord=self._coord(p.lineno(1)))

    def p_asm_keyword(self, p):
        """ asm_keyword : __ASM__ asm_volatile
                        | __ASM asm_volatile
                        | ASM asm_volatile
        """
        p[0] = p[1]
        if p[2]:
            p[0] += ' ' + p[2]

    def p_asm_volatile(self, p):
        """ asm_volatile : VOLATILE
                         | empty
        """
        p[0] = p[1]

    def p_asm_argument_expression_list(self, p):
        """asm_argument_expression_list : argument_expression_list
                                        | empty
        """
        p[0] = p[1]

    def p_statement_gnu(self, p):
        """ statement   : asm_no_semi
                        | asm_no_semi SEMI
        """
        p[0] = p[1]

#    def p_asm_with_semi(self, p):
#        """ asm : asm SEMI
#        """
#        p[0] = p[1]


class _AsmAndAttributesMixin(_AsmMixin, _AttributesMixin):
    # {{{ /!\ names must match C parser to override

    def p_direct_declarator_5(self, p):
        """ direct_declarator   : direct_declarator LPAREN parameter_type_list \
                                        RPAREN asm_opt attributes_opt
                                | direct_declarator LPAREN identifier_list_opt \
                                        RPAREN asm_opt attributes_opt
        """
        func = FuncDeclExt(
            args=p[3],
            type=None,
            attributes=p[6],
            asm=p[5],
            coord=p[1].coord)

        p[0] = self._type_modify_decl(decl=p[1], modifier=func)

    def p_direct_abstract_declarator_6(self, p):
        """ direct_abstract_declarator  : direct_abstract_declarator \
                LPAREN parameter_type_list_opt RPAREN asm_opt attributes_opt
        """
        func = FuncDeclExt(
            args=p[3],
            type=None,
            attributes=p[6],
            asm=p[5],
            coord=p[1].coord)

        p[0] = self._type_modify_decl(decl=p[1], modifier=func)

    # }}}
# }}}


# {{{ gnu parser

class GnuCParser(_AsmAndAttributesMixin, CParserBase):
    # TODO: __extension__

    from pycparserext.ext_c_lexer import GnuCLexer as lexer_class  # noqa

    initial_type_symbols = set(["__builtin_va_list"])

    def p_function_specifier_gnu(self, p):
        """ function_specifier  : __INLINE
                                | __INLINE__
        """
        p[0] = p[1]

    def p_type_qualifier_gnu(self, p):
        """ type_qualifier  : __CONST
                            | __RESTRICT
                            | __EXTENSION__
        """
        p[0] = p[1]

    def p_type_specifier_gnu_typeof_expr(self, p):
        """ type_specifier  : __TYPEOF__ LPAREN expression RPAREN
        """
        if isinstance(p[3], c_ast.TypeDecl):
            pass

        p[0] = TypeOfExpression(p[3])

    def p_type_specifier_gnu_typeof_decl(self, p):
        """ type_specifier  : __TYPEOF__ LPAREN parameter_declaration RPAREN
        """
        p[0] = TypeOfDeclaration(p[3])

    def p_unary_operator_gnu(self, p):
        """ unary_operator  : __REAL__
                            | __IMAG__
        """
        p[0] = p[1]

    def p_postfix_expression_gnu_tcp(self, p):
        """ postfix_expression  : __BUILTIN_TYPES_COMPATIBLE_P \
                LPAREN parameter_declaration COMMA parameter_declaration RPAREN
        """
        p[0] = c_ast.FuncCall(c_ast.ID(p[1], self._coord(p.lineno(1))),
                TypeList([p[3], p[5]], self._coord(p.lineno(2))))

    def p_gnu_statement_expression(self, p):
        """ gnu_statement_expression : LPAREN compound_statement RPAREN
        """
        p[0] = p[2]

    def p_gnu_primary_expression_6(self, p):
        """ primary_expression : gnu_statement_expression """
        p[0] = p[1]

    def p_statement(self, p):
        """ statement   : labeled_statement
                        | expression_statement
                        | compound_statement
                        | selection_statement
                        | iteration_statement
                        | jump_statement
                        | gnu_statement_expression
        """
        p[0] = p[1]

    def p_attribute_const(self, p):
        """ attribute : __CONST
        """
        p[0] = c_ast.ID(name="__const", coord=self._coord(p.lineno(1)))

    def p_struct_declaration_list_1(self, p):
        """ struct_declaration_list : empty """
        p[0] = None

# }}}


class OpenCLCParser(_AsmAndAttributesMixin, CParserBase):
    from pycparserext.ext_c_lexer import OpenCLCLexer as lexer_class  # noqa

    INT_BIT_COUNTS = [8, 16, 32, 64]
    initial_type_symbols = (
            set([
                "%s%d" % (base_name, count)
                for base_name in [
                    'char', 'uchar', 'short', 'ushort', 'int', 'uint',
                    'long', 'ulong', 'float', 'double', 'half']
                for count in [2, 3, 4, 8, 16]
                ])
            | set([
                "intptr_t", "uintptr_t",
                "intmax_t", "uintmax_t",
                "size_t", "ptrdiff_t",
                "uint", "ulong", "ushort", "uchar",
                "half", "bool"])
            | set(["int%d_t" % bc for bc in INT_BIT_COUNTS])
            | set(["uint%d_t" % bc for bc in INT_BIT_COUNTS])
            | set(["int_least%d_t" % bc for bc in INT_BIT_COUNTS])
            | set(["uint_least%d_t" % bc for bc in INT_BIT_COUNTS])
            | set(["int_fast%d_t" % bc for bc in INT_BIT_COUNTS])
            | set(["uint_fast%d_t" % bc for bc in INT_BIT_COUNTS])
            | set([
                "image1d_t", "image1d_array_t", "image1d_buffer_t",
                "image2d_t", "image2d_array_t",
                "image3d_t",
                "sampler_t", "event_t"
                ])
            | set(["cfloat_t", "cdouble_t"])  # PyOpenCL extension
            )

    def p_pp_directive(self, p):
        """ pp_directive  : PPHASH
        """
        p[0] = [PreprocessorLine(p[1], coord=self._coord(p.lineno(1)))]

    def p_external_declaration_comment(self, p):
        """ external_declaration    : LINECOMMENT
        """
        p[0] = None

    def p_statement_comment(self, p):
        """ statement    : LINECOMMENT
        """
        p[0] = None

    def p_type_qualifier_cl(self, p):
        """ type_qualifier  : __GLOBAL
                            | GLOBAL
                            | __LOCAL
                            | LOCAL
                            | __CONSTANT
                            | CONSTANT
                            | __PRIVATE
                            | PRIVATE
                            | __READ_ONLY
                            | READ_ONLY
                            | __WRITE_ONLY
                            | WRITE_ONLY
                            | __READ_WRITE
                            | READ_WRITE
        """
        p[0] = p[1]

    def p_function_specifier_cl(self, p):
        """ function_specifier  : __KERNEL
                                | KERNEL
        """
        p[0] = p[1]

# vim: fdm=marker
