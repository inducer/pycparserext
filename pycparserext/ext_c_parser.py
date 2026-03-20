import pycparser.c_parser
from pycparser import c_ast
from pycparser.c_parser import (
    _DECL_START,
    _FUNCTION_SPEC,
    _STORAGE_CLASS,
    _TYPE_QUALIFIER,
    _TYPE_SPEC_SIMPLE,
)


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

    def __iter__(self):
        yield from (self.types or [])

    attr_names = ()


class AttributeSpecifier(c_ast.Node):
    def __init__(self, exprlist):
        self.exprlist = exprlist

    def __eq__(self, other):
        if not isinstance(other, AttributeSpecifier):
            return False
        return self._compare_ast_nodes(self.exprlist, other.exprlist)

    def _compare_ast_nodes(self, node1, node2):
        if type(node1) is not type(node2):
            return False
        if hasattr(node1, "attr_names"):
            for attr in node1.attr_names:
                if getattr(node1, attr) != getattr(node2, attr):
                    return False
        if hasattr(node1, "children"):
            children1 = node1.children()
            children2 = node2.children()
            if len(children1) != len(children2):
                return False
            for (name1, child1), (name2, child2) in zip(
                                children1, children2, strict=False):
                if name1 != name2:
                    return False
                if not self._compare_ast_nodes(child1, child2):
                    return False
        return True

    def children(self):
        return [("exprlist", self.exprlist)]

    def __iter__(self):
        return
        yield

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

    def __iter__(self):
        if self.template is not None:
            yield self.template
        if self.output_operands is not None:
            yield self.output_operands
        if self.input_operands is not None:
            yield self.input_operands
        if self.clobbered_regs is not None:
            yield self.clobbered_regs

    attr_names = ("asm_keyword",)


class PreprocessorLine(c_ast.Node):
    def __init__(self, contents, coord=None):
        self.contents = contents
        self.coord = coord

    def children(self):
        return ()

    def __iter__(self):
        return
        yield

    attr_names = ("contents",)


class TypeOfDeclaration(c_ast.Node):
    def __init__(self, typeof_keyword, declaration, coord=None):
        self.typeof_keyword = typeof_keyword
        self.declaration = declaration
        self.coord = coord

    def children(self):
        nodelist = []
        if self.declaration is not None:
            nodelist.append(("declaration", self.declaration))
        return tuple(nodelist)

    def __iter__(self):
        if self.declaration is not None:
            yield self.declaration

    attr_names = ("typeof_keyword",)


class TypeOfExpression(c_ast.Node):
    def __init__(self, typeof_keyword, expr, coord=None):
        self.typeof_keyword = typeof_keyword
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None:
            nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    def __iter__(self):
        if self.expr is not None:
            yield self.expr

    attr_names = ("typeof_keyword",)


class RangeExpression(c_ast.Node):
    def __init__(self, first, last, coord=None):
        self.first = first
        self.last = last
        self.coord = coord

    def children(self):
        nodelist = []
        if self.first is not None:
            nodelist.append(("first", self.first))
        if self.last is not None:
            nodelist.append(("last", self.last))
        return tuple(nodelist)

    def __iter__(self):
        if self.first is not None:
            yield self.first
        if self.last is not None:
            yield self.last

    attr_names = ()


class TypeDeclExt(c_ast.TypeDecl):
    __slots__ = ("asm", "attributes", "init")

    @staticmethod
    def from_pycparser(td):
        assert isinstance(td, c_ast.TypeDecl)
        return TypeDeclExt(
            declname=td.declname,
            quals=td.quals,
            align=td.align,
            type=td.type,
            coord=td.coord
        )


class ArrayDeclExt(c_ast.ArrayDecl):
    __slots__ = ("asm", "attributes", "init")

    @staticmethod
    def from_pycparser(ad):
        assert isinstance(ad, c_ast.ArrayDecl)
        return ArrayDeclExt(
            type=ad.type,
            dim=ad.dim,
            dim_quals=ad.dim_quals,
            coord=ad.coord
        )


class StructExt(c_ast.Struct):
    """Extended Struct that can hold attributes."""
    @staticmethod
    def from_pycparser(st):
        assert isinstance(st, c_ast.Struct)
        return StructExt(
            name=st.name,
            decls=st.decls,
            coord=st.coord
        )


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

    def __iter__(self):
        if self.args is not None:
            yield self.args
        if self.type is not None:
            yield self.type
        if self.attributes is not None:
            yield self.attributes
        if self.asm is not None:
            yield self.asm

    attr_names = ()

# }}}


# {{{ base parser

class CParserBase(pycparser.c_parser.CParser):
    """Base class for extended C parsers."""

    initial_type_symbols = frozenset()

    def __init__(self, **kwds):
        kwds["lexer"] = self.lexer_class
        pycparser.c_parser.CParser.__init__(self, **kwds)

    def parse(self, text, filename="", debuglevel=0,
            initial_type_symbols=frozenset()):
        self._pending_initial_type_symbols = (
            dict.fromkeys(initial_type_symbols, True)
            | dict.fromkeys(self.initial_type_symbols, True)
        )
        return pycparser.c_parser.CParser.parse(self, text, filename)

    def _parse_translation_unit_or_empty(self):
        if hasattr(self, "_pending_initial_type_symbols"):
            self._scope_stack[0].update(self._pending_initial_type_symbols)
            del self._pending_initial_type_symbols
        return super()._parse_translation_unit_or_empty()

    def _parse_attribute_list(self):
        exprs = [self._parse_attribute()]
        while self._accept("COMMA"):
            exprs.append(self._parse_attribute())
        coord = exprs[0].coord if exprs else None
        return c_ast.ExprList(exprs, coord)

    def _parse_attribute(self):
        tok = self._peek()
        if tok is None:
            return c_ast.ID(name="", coord=self._coord(0))
        if tok.type in {"COMMA", "RPAREN"}:
            return c_ast.ID(name="", coord=self._tok_coord(tok))
        if tok.type == "CONST":
            self._advance()
            return c_ast.ID(name="const", coord=self._tok_coord(tok))
        if tok.type == "__CONST":
            self._advance()
            return c_ast.ID(name="__const", coord=self._tok_coord(tok))
        return self._parse_assignment_expression()

    def _parse_attribute_decl(self):
        self._advance()  # consume __ATTRIBUTE__ or __ATTRIBUTE
        self._expect("LPAREN")
        self._expect("LPAREN")
        attr_list = self._parse_attribute_list()
        self._expect("RPAREN")
        self._expect("RPAREN")
        return attr_list

    def _parse_attributes_opt(self):
        tok = self._peek()
        coord = self._tok_coord(tok) if tok else self.clex.filename
        result = c_ast.ExprList([], coord)
        while self._peek_type() in {"__ATTRIBUTE__", "__ATTRIBUTE"}:
            attr_list = self._parse_attribute_decl()
            result.exprs.extend(attr_list.exprs)
        return result

    def _parse_asm_keyword(self):
        tok = self._advance()
        kw = tok.value
        if self._peek_type() in {"VOLATILE", "__VOLATILE", "__VOLATILE__"}:
            vol_tok = self._advance()
            kw += " " + vol_tok.value
        return kw

    def _is_asm_keyword_token(self, tok_type):
        return tok_type in {"ASM", "__ASM__", "__ASM"}

    def _parse_asm_argument_expression_list(self):
        if self._peek_type() in {"COLON", "RPAREN"}:
            return None
        return self._parse_argument_expression_list()

    def _parse_asm_no_semi(self):
        coord = self._tok_coord(self._peek())
        asm_kw = self._parse_asm_keyword()
        self._expect("LPAREN")
        template = self._parse_asm_argument_expression_list()
        output_operands = None
        input_operands = None
        clobbered_regs = None
        if self._accept("COLON"):
            output_operands = self._parse_asm_argument_expression_list()
            if self._accept("COLON"):
                input_operands = self._parse_asm_argument_expression_list()
                if self._accept("COLON"):
                    clobbered_regs = self._parse_asm_argument_expression_list()
        self._expect("RPAREN")
        return Asm(asm_kw, template, output_operands, input_operands,
                   clobbered_regs, coord=coord)

    def _parse_asm_opt(self):
        if not self._is_asm_keyword_token(self._peek_type()):
            return None
        return self._parse_asm_no_semi()

    def _parse_asm_label_opt(self):
        if not self._is_asm_keyword_token(self._peek_type()):
            return None
        coord = self._tok_coord(self._peek())
        asm_kw = self._parse_asm_keyword()
        self._expect("LPAREN")
        template = self._parse_unified_string_literal()
        self._expect("RPAREN")
        return Asm(asm_kw, template, None, None, None, coord=coord)

# }}}


# {{{ GNU + OpenCL extension mixin

_GNU_FUNCTION_SPECS = frozenset({"__INLINE__", "__INLINE"})
_GNU_TYPE_QUALIFIERS = frozenset({
    "__CONST", "__RESTRICT__", "__RESTRICT",
    "__EXTENSION__", "__VOLATILE", "__VOLATILE__",
})
_TYPEOF_TOKENS = frozenset({"__TYPEOF__", "TYPEOF", "__TYPEOF"})
_ATTRIBUTE_TOKENS = frozenset({"__ATTRIBUTE__", "__ATTRIBUTE"})


class _AsmAndAttributesMixin:
    """Provides asm/attribute parsing for pycparser 3.0 recursive descent."""

    def _scan_skip_paren_group(self):
        """In scan context: skip a balanced group starting at '('."""
        if self._peek_type() != "LPAREN":
            return
        self._advance()
        depth = 1
        while depth > 0:
            tok = self._peek()
            if tok is None:
                return
            if tok.type == "LPAREN":
                depth += 1
            elif tok.type == "RPAREN":
                depth -= 1
            self._advance()

    def _scan_declarator_name_info(self):
        """Override to skip GNU type qualifiers and __attribute__ in scan."""
        from pycparser.c_parser import _TYPE_QUALIFIER
        saw_paren = False
        while self._accept("TIMES"):
            # Skip standard and GNU type qualifiers after '*'
            while self._peek_type() in (_TYPE_QUALIFIER | _GNU_TYPE_QUALIFIERS):
                self._advance()
            # Skip __attribute__((...)) between '*' and declarator name
            while self._peek_type() in _ATTRIBUTE_TOKENS:
                self._advance()  # consume __ATTRIBUTE__ or __ATTRIBUTE
                self._scan_skip_paren_group()  # skip (
                self._scan_skip_paren_group()  # skip ((...))

        tok = self._peek()
        if tok is None:
            return None, saw_paren
        if tok.type in {"ID", "TYPEID"}:
            self._advance()
            return tok.type, saw_paren
        if tok.type == "LPAREN":
            saw_paren = True
            self._advance()
            tok_type, nested_paren = self._scan_declarator_name_info()
            if nested_paren:
                saw_paren = True
            depth = 1
            while True:
                tok = self._peek()
                if tok is None:
                    return None, saw_paren
                if tok.type == "LPAREN":
                    depth += 1
                elif tok.type == "RPAREN":
                    depth -= 1
                    self._advance()
                    if depth == 0:
                        break
                    continue
                self._advance()
            return tok_type, saw_paren
        return None, saw_paren

    def _parse_typeof_specifier(self, typeof_tok):
        coord = self._tok_coord(typeof_tok)
        self._expect("LPAREN")
        if self._starts_declaration():
            decl = self._parse_parameter_declaration()
            self._expect("RPAREN")
            return TypeOfDeclaration(typeof_tok.value, decl, coord)
        expr = self._parse_expression()
        self._expect("RPAREN")
        return TypeOfExpression(typeof_tok.value, expr, coord)

    def _parse_declarator_kind(self, kind, allow_paren):
        """Handle asm labels and attributes on declarators."""
        ptr = None
        if self._peek_type() == "TIMES":
            ptr = self._parse_pointer()

        # Attributes between pointer and direct declarator
        attrs_before_direct = None
        if ptr is not None and self._peek_type() in _ATTRIBUTE_TOKENS:
            attrs_before_direct = self._parse_attributes_opt()

        direct = self._parse_direct_declarator(kind, allow_paren=allow_paren)

        asm_label = self._parse_asm_label_opt()
        attrs_after_direct = self._parse_attributes_opt()

        # Merge attribute lists
        if attrs_before_direct is not None and attrs_before_direct.exprs:
            attrs = attrs_before_direct
            if attrs_after_direct.exprs:
                attrs.exprs.extend(attrs_after_direct.exprs)
        else:
            attrs = attrs_after_direct

        if asm_label or attrs.exprs:
            innermost_decl = direct
            while not isinstance(innermost_decl, c_ast.TypeDecl):
                try:
                    innermost_decl = innermost_decl.type
                except AttributeError:
                    break

            if isinstance(innermost_decl, c_ast.TypeDecl):
                decl_ext = to_decl_ext(innermost_decl)
                if asm_label:
                    decl_ext.asm = asm_label
                if attrs.exprs:
                    decl_ext.attributes = attrs

                if innermost_decl is direct:
                    direct = decl_ext
                else:
                    parent = direct
                    while parent.type is not innermost_decl:
                        parent = parent.type
                    parent.type = decl_ext

        if ptr is not None:
            return self._type_modify_decl(direct, ptr)
        return direct

    def _parse_function_decl(self, base_decl):
        """Handle asm/attributes after function declarations.

        Always creates FuncDeclExt (even without asm/attrs) to match the
        behavior of the PLY-based parser.
        """
        self._expect("LPAREN")
        if self._accept("RPAREN"):
            args = None
        else:
            args = (
                self._parse_parameter_type_list()
                if self._starts_declaration()
                else self._parse_identifier_list_opt()
            )
            self._expect("RPAREN")

        asm = self._parse_asm_opt()
        attrs = self._parse_attributes_opt()

        func = FuncDeclExt(
            args=args,
            type=None,
            attributes=attrs,
            asm=asm,
            coord=base_decl.coord,
        )

        if self._peek_type() == "LBRACE" and func.args is not None:
            for param in func.args.params:
                if isinstance(param, c_ast.EllipsisParam):
                    break
                name = getattr(param, "name", None)
                if name:
                    self._add_identifier(name, param.coord)

        return func

    def _parse_struct_or_union_specifier(self):
        """Handle __attribute__ on struct/union specifiers."""
        tok = self._advance()
        klass = self._select_struct_union_class(tok.value)

        attrs_before = self._parse_attributes_opt()

        if self._peek_type() in {"ID", "TYPEID"}:
            name_tok = self._advance()
            attrs_after_name = self._parse_attributes_opt()

            if self._peek_type() == "LBRACE":
                self._advance()
                if self._accept("RBRACE"):
                    st = klass(
                        name=name_tok.value, decls=[],
                        coord=self._tok_coord(name_tok)
                    )
                else:
                    decls = self._parse_struct_declaration_list()
                    self._expect("RBRACE")
                    st = klass(
                        name=name_tok.value, decls=decls,
                        coord=self._tok_coord(name_tok)
                    )

                all_exprs = attrs_before.exprs + attrs_after_name.exprs
                if all_exprs and isinstance(st, c_ast.Struct):
                    all_attrs = c_ast.ExprList(all_exprs, self._tok_coord(tok))
                    struct_ext = StructExt.from_pycparser(st)
                    struct_ext.attrib = AttributeSpecifier(all_attrs)
                    return struct_ext
                return st

            return klass(
                name=name_tok.value, decls=None, coord=self._tok_coord(name_tok)
            )

        if self._peek_type() == "LBRACE":
            brace_tok = self._advance()
            if self._accept("RBRACE"):
                st = klass(name=None, decls=[], coord=self._tok_coord(brace_tok))
            else:
                decls = self._parse_struct_declaration_list()
                self._expect("RBRACE")
                st = klass(name=None, decls=decls, coord=self._tok_coord(brace_tok))

            if attrs_before.exprs and isinstance(st, c_ast.Struct):
                struct_ext = StructExt.from_pycparser(st)
                struct_ext.attrib = AttributeSpecifier(attrs_before)
                return struct_ext
            return st

        self._parse_error("Invalid struct/union declaration", self._tok_coord(tok))

    def _parse_struct_declaration(self):
        """Handle __attribute__ in struct member declarations."""
        if self._peek_type() == "SEMI":
            self._advance()
            return None
        if self._peek_type() in {"PPPRAGMA", "_PRAGMA"}:
            return [self._parse_pppragma_directive()]

        leading_attrs = self._parse_attributes_opt()

        spec = self._parse_specifier_qualifier_list()

        if leading_attrs.exprs:
            spec = self._add_declaration_specifier(
                spec, AttributeSpecifier(leading_attrs), "function", append=True)

        assert "typedef" not in spec.get("storage", [])

        decls = None
        if self._starts_declarator() or self._peek_type() == "COLON":
            decls = self._parse_struct_declarator_list()

        trailing_attrs = self._parse_attributes_opt()

        if decls is not None:
            self._expect("SEMI")
            result = self._build_declarations(spec=spec, decls=decls)
            if trailing_attrs.exprs:
                for decl in result:
                    if isinstance(getattr(decl, "type", None), c_ast.Struct):
                        st = decl.type
                        if not isinstance(st, StructExt):
                            st = StructExt.from_pycparser(st)
                            decl.type = st
                        st.attrib = AttributeSpecifier(trailing_attrs)
            return result

        if len(spec["type"]) == 1:
            node = spec["type"][0]
            if isinstance(node, c_ast.Node):
                decl_type = node
                if trailing_attrs.exprs and isinstance(node, c_ast.Struct):
                    if not isinstance(node, StructExt):
                        node = StructExt.from_pycparser(node)
                        spec["type"][0] = node
                    node.attrib = AttributeSpecifier(trailing_attrs)
                    decl_type = node
            else:
                decl_type = c_ast.IdentifierType(node)
            self._expect("SEMI")
            return self._build_declarations(
                spec=spec, decls=[{"decl": decl_type, "init": None, "bitsize": None}]
            )

        self._expect("SEMI")
        return self._build_declarations(
            spec=spec, decls=[{"decl": None, "init": None, "bitsize": None}]
        )

# }}}


# {{{ GNU C parser

_GNU_DECL_START = (
    _DECL_START
    | _GNU_FUNCTION_SPECS
    | _GNU_TYPE_QUALIFIERS
    | _TYPEOF_TOKENS
    | _ATTRIBUTE_TOKENS
)


class GnuCParser(_AsmAndAttributesMixin, CParserBase):
    from pycparserext.ext_c_lexer import GnuCLexer as lexer_class  # noqa

    initial_type_symbols = frozenset({"__builtin_va_list"})

    def _starts_declaration(self, tok=None):
        tok = tok or self._peek()
        if tok is None:
            return False
        return tok.type in _GNU_DECL_START

    def _parse_declaration_specifiers(self, allow_no_type=False):
        spec = None
        saw_type = False
        first_coord = None

        while True:
            tok = self._peek()
            if tok is None:
                break
            tok_type = tok.type

            if tok_type == "_ALIGNAS":
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_alignment_specifier(), "alignment",
                    append=True)
                continue

            if tok_type == "_ATOMIC" and self._peek_type(2) == "LPAREN":
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_atomic_specifier(), "type", append=True)
                saw_type = True
                continue

            if tok_type in _TYPE_QUALIFIER:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "qual", append=True)
                continue

            if tok_type in _GNU_TYPE_QUALIFIERS:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "qual", append=True)
                continue

            if tok_type in _STORAGE_CLASS:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "storage", append=True)
                continue

            if tok_type in _FUNCTION_SPEC:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "function", append=True)
                continue

            if tok_type in _GNU_FUNCTION_SPECS:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "function", append=True)
                continue

            if tok_type in _TYPE_SPEC_SIMPLE:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                tok = self._advance()
                spec = self._add_declaration_specifier(
                    spec,
                    c_ast.IdentifierType([tok.value], coord=self._tok_coord(tok)),
                    "type", append=True)
                saw_type = True
                continue

            if tok_type == "TYPEID":
                if saw_type:
                    break
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                tok = self._advance()
                spec = self._add_declaration_specifier(
                    spec,
                    c_ast.IdentifierType([tok.value], coord=self._tok_coord(tok)),
                    "type", append=True)
                saw_type = True
                continue

            if tok_type in {"STRUCT", "UNION"}:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_struct_or_union_specifier(), "type",
                    append=True)
                saw_type = True
                continue

            if tok_type == "ENUM":
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_enum_specifier(), "type", append=True)
                saw_type = True
                continue

            if tok_type in _TYPEOF_TOKENS:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                typeof_tok = self._advance()
                spec = self._add_declaration_specifier(
                    spec, self._parse_typeof_specifier(typeof_tok), "type",
                    append=True)
                saw_type = True
                continue

            if tok_type in _ATTRIBUTE_TOKENS:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, AttributeSpecifier(self._parse_attribute_decl()),
                    "function", append=True)
                continue

            break

        if spec is None:
            self._parse_error("Invalid declaration", self.clex.filename)

        if not saw_type and not allow_no_type:
            self._parse_error("Missing type in declaration", first_coord)

        return spec, saw_type, first_coord

    def _parse_specifier_qualifier_list(self):
        spec = None
        saw_type = False
        saw_alignment = False
        first_coord = None

        while True:
            tok = self._peek()
            if tok is None:
                break
            tok_type = tok.type

            if tok_type == "_ALIGNAS":
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_alignment_specifier(), "alignment",
                    append=True)
                saw_alignment = True
                continue

            if tok_type == "_ATOMIC" and self._peek_type(2) == "LPAREN":
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_atomic_specifier(), "type", append=True)
                saw_type = True
                continue

            if tok_type in _TYPE_QUALIFIER:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "qual", append=True)
                continue

            if tok_type in _GNU_TYPE_QUALIFIERS:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "qual", append=True)
                continue

            if tok_type in _GNU_FUNCTION_SPECS:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "function", append=True)
                continue

            if tok_type in _TYPE_SPEC_SIMPLE:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                tok = self._advance()
                spec = self._add_declaration_specifier(
                    spec,
                    c_ast.IdentifierType([tok.value], coord=self._tok_coord(tok)),
                    "type", append=True)
                saw_type = True
                continue

            if tok_type == "TYPEID":
                if saw_type:
                    break
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                tok = self._advance()
                spec = self._add_declaration_specifier(
                    spec,
                    c_ast.IdentifierType([tok.value], coord=self._tok_coord(tok)),
                    "type", append=True)
                saw_type = True
                continue

            if tok_type in {"STRUCT", "UNION"}:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_struct_or_union_specifier(), "type",
                    append=True)
                saw_type = True
                continue

            if tok_type == "ENUM":
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_enum_specifier(), "type", append=True)
                saw_type = True
                continue

            if tok_type in _TYPEOF_TOKENS:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                typeof_tok = self._advance()
                spec = self._add_declaration_specifier(
                    spec, self._parse_typeof_specifier(typeof_tok), "type",
                    append=True)
                saw_type = True
                continue

            break

        if spec is None:
            self._parse_error("Invalid specifier list", self.clex.filename)

        if not saw_type and not saw_alignment:
            self._parse_error("Missing type in declaration", first_coord)

        if spec.get("storage") is None:
            spec["storage"] = []
        if spec.get("function") is None:
            spec["function"] = []

        return spec

    def _parse_type_qualifier_list(self):
        quals = []
        all_quals = _TYPE_QUALIFIER | _GNU_TYPE_QUALIFIERS
        while self._peek_type() in all_quals:
            quals.append(self._advance().value)
        return quals

    def _parse_array_decl_common(self, base_type, coord=None):
        """Override to handle GNU type qualifiers inside array dimensions."""
        from pycparser.c_parser import _TYPE_QUALIFIER
        all_quals = _TYPE_QUALIFIER | _GNU_TYPE_QUALIFIERS

        lbrack_tok = self._expect("LBRACKET")
        if coord is None:
            coord = self._tok_coord(lbrack_tok)

        def make_array_decl(dim, dim_quals):
            return c_ast.ArrayDecl(
                type=base_type, dim=dim, dim_quals=dim_quals, coord=coord
            )

        if self._accept("STATIC"):
            dim_quals = ["static"] + (self._parse_type_qualifier_list() or [])
            dim = self._parse_assignment_expression()
            self._expect("RBRACKET")
            return make_array_decl(dim, dim_quals)

        if self._peek_type() in all_quals:
            dim_quals = self._parse_type_qualifier_list() or []
            if self._accept("STATIC"):
                dim_quals = [*dim_quals, "static"]
                dim = self._parse_assignment_expression()
                self._expect("RBRACKET")
                return make_array_decl(dim, dim_quals)
            times_tok = self._accept("TIMES")
            if times_tok:
                self._expect("RBRACKET")
                dim = c_ast.ID(times_tok.value, self._tok_coord(times_tok))
                return make_array_decl(dim, dim_quals)
            dim = None
            if self._starts_expression():
                dim = self._parse_assignment_expression()
            self._expect("RBRACKET")
            return make_array_decl(dim, dim_quals)

        times_tok = self._accept("TIMES")
        if times_tok:
            self._expect("RBRACKET")
            dim = c_ast.ID(times_tok.value, self._tok_coord(times_tok))
            return make_array_decl(dim, [])

        dim = None
        if self._starts_expression():
            dim = self._parse_assignment_expression()
        self._expect("RBRACKET")
        return make_array_decl(dim, [])

    def _parse_unary_expression(self):
        tok_type = self._peek_type()
        if tok_type == "__ALIGNOF__":
            tok = self._advance()
            self._expect("LPAREN")
            typ = self._parse_type_name()
            self._expect("RPAREN")
            return c_ast.UnaryOp(tok.value, typ, self._tok_coord(tok))
        return super()._parse_unary_expression()

    def _parse_postfix_expression(self):
        tok_type = self._peek_type()
        if tok_type == "__BUILTIN_TYPES_COMPATIBLE_P":
            tok = self._advance()
            self._expect("LPAREN")
            decl1 = self._parse_parameter_declaration()
            self._expect("COMMA")
            decl2 = self._parse_parameter_declaration()
            self._expect("RPAREN")
            coord = self._tok_coord(tok)
            return c_ast.FuncCall(
                c_ast.ID(tok.value, coord),
                TypeList([decl1, decl2], coord),
                coord
            )
        return super()._parse_postfix_expression()

    def _parse_primary_expression(self):
        tok_type = self._peek_type()
        if tok_type == "LPAREN" and self._peek_type(2) == "LBRACE":
            self._advance()  # consume "("
            compound = self._parse_compound_statement()
            self._expect("RPAREN")
            return compound
        return super()._parse_primary_expression()

    def _parse_statement(self):
        tok_type = self._peek_type()
        if self._is_asm_keyword_token(tok_type):
            asm = self._parse_asm_no_semi()
            self._accept("SEMI")
            return asm
        return super()._parse_statement()

    def _parse_labeled_statement(self):
        tok_type = self._peek_type()
        if tok_type == "CASE":
            case_tok = self._advance()
            expr = self._parse_constant_expression()
            if self._accept("ELLIPSIS"):
                last = self._parse_constant_expression()
                expr = RangeExpression(expr, last, coord=self._tok_coord(case_tok))
            self._expect("COLON")
            if self._starts_statement():
                stmt = self._parse_pragmacomp_or_statement()
            else:
                stmt = c_ast.EmptyStatement(self._tok_coord(case_tok))
            return c_ast.Case(expr, [stmt], self._tok_coord(case_tok))
        return super()._parse_labeled_statement()

    def _parse_designator(self):
        if self._accept("LBRACKET"):
            expr = self._parse_constant_expression()
            if self._accept("ELLIPSIS"):
                last = self._parse_constant_expression()
                self._expect("RBRACKET")
                return RangeExpression(expr, last)
            self._expect("RBRACKET")
            return expr
        if self._accept("PERIOD"):
            return self._parse_identifier_or_typeid()
        self._parse_error("Invalid designator", self.clex.filename)

# }}}


# {{{ OpenCL C parser

_OCL_TYPE_QUALIFIERS = frozenset({
    "__GLOBAL__", "GLOBAL",
    "__LOCAL__", "LOCAL",
    "__CONSTANT__", "CONSTANT",
    "__PRIVATE__", "PRIVATE",
    "__READ_ONLY__", "READ_ONLY",
    "__WRITE_ONLY__", "WRITE_ONLY",
    "__READ_WRITE__", "READ_WRITE",
})

_OCL_FUNCTION_SPECS = frozenset({"__KERNEL", "KERNEL"})

_OCL_DECL_START = (
    _DECL_START
    | _ATTRIBUTE_TOKENS
    | _OCL_TYPE_QUALIFIERS
    | _OCL_FUNCTION_SPECS
)


class OpenCLCParser(_AsmAndAttributesMixin, CParserBase):
    from pycparserext.ext_c_lexer import OpenCLCLexer as lexer_class  # noqa

    INT_BIT_COUNTS = (8, 16, 32, 64)
    initial_type_symbols = (
            {
                "%s%d" % (base_name, count)
                for base_name in [
                    "char", "uchar", "short", "ushort", "int", "uint",
                    "long", "ulong", "float", "double", "half"]
                for count in [2, 3, 4, 8, 16]
                }
            | {
                "intptr_t", "uintptr_t",
                "intmax_t", "uintmax_t",
                "size_t", "ptrdiff_t",
                "uint", "ulong", "ushort", "uchar",
                "half", "bool"}
            | {"int%d_t" % bc for bc in INT_BIT_COUNTS}
            | {"uint%d_t" % bc for bc in INT_BIT_COUNTS}
            | {"int_least%d_t" % bc for bc in INT_BIT_COUNTS}
            | {"uint_least%d_t" % bc for bc in INT_BIT_COUNTS}
            | {"int_fast%d_t" % bc for bc in INT_BIT_COUNTS}
            | {"uint_fast%d_t" % bc for bc in INT_BIT_COUNTS}
            | {
                "image1d_t", "image1d_array_t", "image1d_buffer_t",
                "image2d_t", "image2d_array_t",
                "image3d_t",
                "sampler_t", "event_t"
                }
            | {"cfloat_t", "cdouble_t"}
            )

    def _starts_declaration(self, tok=None):
        tok = tok or self._peek()
        if tok is None:
            return False
        return tok.type in _OCL_DECL_START

    def _parse_declaration_specifiers(self, allow_no_type=False):
        spec = None
        saw_type = False
        first_coord = None

        while True:
            tok = self._peek()
            if tok is None:
                break
            tok_type = tok.type

            if tok_type == "_ALIGNAS":
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_alignment_specifier(), "alignment",
                    append=True)
                continue

            if tok_type == "_ATOMIC" and self._peek_type(2) == "LPAREN":
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_atomic_specifier(), "type", append=True)
                saw_type = True
                continue

            if tok_type in _TYPE_QUALIFIER:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "qual", append=True)
                continue

            if tok_type in _OCL_TYPE_QUALIFIERS:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "qual", append=True)
                continue

            if tok_type in _STORAGE_CLASS:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "storage", append=True)
                continue

            if tok_type in _FUNCTION_SPEC:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "function", append=True)
                continue

            if tok_type in _OCL_FUNCTION_SPECS:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "function", append=True)
                continue

            if tok_type in _TYPE_SPEC_SIMPLE:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                tok = self._advance()
                spec = self._add_declaration_specifier(
                    spec,
                    c_ast.IdentifierType([tok.value], coord=self._tok_coord(tok)),
                    "type", append=True)
                saw_type = True
                continue

            if tok_type == "TYPEID":
                if saw_type:
                    break
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                tok = self._advance()
                spec = self._add_declaration_specifier(
                    spec,
                    c_ast.IdentifierType([tok.value], coord=self._tok_coord(tok)),
                    "type", append=True)
                saw_type = True
                continue

            if tok_type in {"STRUCT", "UNION"}:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_struct_or_union_specifier(), "type",
                    append=True)
                saw_type = True
                continue

            if tok_type == "ENUM":
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_enum_specifier(), "type", append=True)
                saw_type = True
                continue

            if tok_type in _ATTRIBUTE_TOKENS:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, AttributeSpecifier(self._parse_attribute_decl()),
                    "function", append=True)
                continue

            break

        if spec is None:
            self._parse_error("Invalid declaration", self.clex.filename)

        if not saw_type and not allow_no_type:
            self._parse_error("Missing type in declaration", first_coord)

        return spec, saw_type, first_coord

    def _parse_specifier_qualifier_list(self):
        spec = None
        saw_type = False
        saw_alignment = False
        first_coord = None

        while True:
            tok = self._peek()
            if tok is None:
                break
            tok_type = tok.type

            if tok_type == "_ALIGNAS":
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_alignment_specifier(), "alignment",
                    append=True)
                saw_alignment = True
                continue

            if tok_type == "_ATOMIC" and self._peek_type(2) == "LPAREN":
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_atomic_specifier(), "type", append=True)
                saw_type = True
                continue

            if tok_type in _TYPE_QUALIFIER:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "qual", append=True)
                continue

            if tok_type in _OCL_TYPE_QUALIFIERS:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._advance().value, "qual", append=True)
                continue

            if tok_type in _TYPE_SPEC_SIMPLE:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                tok = self._advance()
                spec = self._add_declaration_specifier(
                    spec,
                    c_ast.IdentifierType([tok.value], coord=self._tok_coord(tok)),
                    "type", append=True)
                saw_type = True
                continue

            if tok_type == "TYPEID":
                if saw_type:
                    break
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                tok = self._advance()
                spec = self._add_declaration_specifier(
                    spec,
                    c_ast.IdentifierType([tok.value], coord=self._tok_coord(tok)),
                    "type", append=True)
                saw_type = True
                continue

            if tok_type in {"STRUCT", "UNION"}:
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_struct_or_union_specifier(), "type",
                    append=True)
                saw_type = True
                continue

            if tok_type == "ENUM":
                if first_coord is None:
                    first_coord = self._tok_coord(tok)
                spec = self._add_declaration_specifier(
                    spec, self._parse_enum_specifier(), "type", append=True)
                saw_type = True
                continue

            break

        if spec is None:
            self._parse_error("Invalid specifier list", self.clex.filename)

        if not saw_type and not saw_alignment:
            self._parse_error("Missing type in declaration", first_coord)

        if spec.get("storage") is None:
            spec["storage"] = []
        if spec.get("function") is None:
            spec["function"] = []

        return spec

    def _parse_type_qualifier_list(self):
        quals = []
        all_quals = _TYPE_QUALIFIER | _OCL_TYPE_QUALIFIERS
        while self._peek_type() in all_quals:
            quals.append(self._advance().value)
        return quals

    def _parse_statement(self):
        tok_type = self._peek_type()
        if self._is_asm_keyword_token(tok_type):
            asm = self._parse_asm_no_semi()
            self._accept("SEMI")
            return asm
        return super()._parse_statement()

# }}}


# vim: fdm=marker
