from pycparser.c_generator import CGenerator as CGeneratorBaseBuggy
from pycparserext.ext_c_parser import FuncDeclExt, TypeDeclExt
import pycparser.c_ast as c_ast


class CGeneratorBase(CGeneratorBaseBuggy):
    # bug fix
    def visit_UnaryOp(self, n):
        operand = self._parenthesize_unless_simple(n.expr)
        if n.op == 'p++':
            return '%s++' % operand
        elif n.op == 'p--':
            return '%s--' % operand
        elif n.op == 'sizeof':
            # Always parenthesize the argument of sizeof since it can be
            # a name.
            return 'sizeof(%s)' % self.visit(n.expr)
        else:
            # avoid merging of "- - x" or "__real__varname"
            return '%s %s' % (n.op, operand)


class AsmAndAttributesMixin(object):
    def visit_Asm(self, n):
        components = [
                n.template,
                ]
        if (n.output_operands is not None
                or n.input_operands is not None
                or n.clobbered_regs is not None):
            components.extend([
                n.output_operands,
                n.input_operands,
                n.clobbered_regs,
                ])

        return " %s(%s)" % (
                n.asm_keyword,
                " : ".join(
                    self.visit(c) for c in components))

    def _generate_type(self, n, modifiers=[]):
        """ Recursive generation from a type node. n is the type node.
            modifiers collects the PtrDecl, ArrayDecl and FuncDecl modifiers
            encountered on the way down to a TypeDecl, to allow proper
            generation from it.
        """
        typ = type(n)
        #~ print(n, modifiers)

        if typ in (c_ast.TypeDecl, TypeDeclExt):
            s = ''
            if n.quals:
                s += ' '.join(n.quals) + ' '
            s += self.visit(n.type)

            nstr = n.declname if n.declname else ''
            # Resolve modifiers.
            # Wrap in parens to distinguish pointer to array and pointer to
            # function syntax.
            #
            for i, modifier in enumerate(modifiers):
                if isinstance(modifier, c_ast.ArrayDecl):
                    if (i != 0 and isinstance(modifiers[i - 1], c_ast.PtrDecl)):
                        nstr = '(' + nstr + ')'
                    nstr += '[' + self.visit(modifier.dim) + ']'
                elif isinstance(modifier, c_ast.FuncDecl):
                    if (i != 0 and isinstance(modifiers[i - 1], c_ast.PtrDecl)):
                        nstr = '(' + nstr + ')'
                    nstr += '(' + self.visit(modifier.args) + ')'
                elif isinstance(modifier, FuncDeclExt):
                    if (i != 0 and isinstance(modifiers[i - 1], c_ast.PtrDecl)):
                        nstr = '(' + nstr + ')'
                    nstr += '(' + self.visit(modifier.args) + ')'

                    if modifier.asm is not None:
                        nstr += " " + self.visit(modifier.asm)

                    if modifier.attributes.exprs:
                        nstr += (
                                ' __attribute__(('
                                + self.visit(modifier.attributes)
                                + '))')

                elif isinstance(modifier, c_ast.PtrDecl):
                    # BUG FIX: pycparser ignores quals
                    quals = ' '.join(modifier.quals)
                    if quals:
                        quals = quals + ' '
                    nstr = '*' + quals + nstr

            if hasattr(n, "attributes") and n.attributes.exprs:
                nstr += ' __attribute__((' + self.visit(n.attributes) + '))'

            if nstr:
                s += ' ' + nstr
            return s
        elif typ == c_ast.Decl:
            return self._generate_decl(n.type)
        elif typ == c_ast.Typename:
            return self._generate_type(n.type)
        elif typ == c_ast.IdentifierType:
            return ' '.join(n.names) + ' '
        elif typ in (c_ast.ArrayDecl, c_ast.PtrDecl, c_ast.FuncDecl, FuncDeclExt):
            return self._generate_type(n.type, modifiers + [n])
        else:
            return self.visit(n)

    def _generate_decl(self, n):
        """ Generation from a Decl node.
        """
        s = ''

        def funcspec_to_str(i):
            if isinstance(i, c_ast.Node):
                return self.visit(i)
            else:
                return i

        if n.funcspec:
            s = ' '.join(funcspec_to_str(i) for i in n.funcspec) + ' '
        if n.storage:
            s += ' '.join(n.storage) + ' '
        s += self._generate_type(n.type)
        return s

    def visit_AttributeSpecifier(self, n):
        return ' __attribute__((' + self.visit(n.exprlist) + '))'


class GnuCGenerator(AsmAndAttributesMixin, CGeneratorBase):
    def visit_TypeOfDeclaration(self, n):
        return "__typeof__(%s)" % self.visit(n.declaration)

    def visit_TypeOfExpression(self, n):
        return "__typeof__(%s)" % self.visit(n.expr)

    def visit_TypeList(self, n):
        return ', '.join(self.visit(ch) for ch in n.types)


class GNUCGenerator(GnuCGenerator):
    def __init__(self):
        from warnings import warn
        warn("GNUCGenerator is now called GnuCGenerator",
                DeprecationWarning, stacklevel=2)


class OpenCLCGenerator(AsmAndAttributesMixin, CGeneratorBase):
    def visit_FileAST(self, n):
        s = ''
        from pycparserext.ext_c_parser import PreprocessorLine
        for ext in n.ext:
            if isinstance(ext, (c_ast.FuncDef, PreprocessorLine)):
                s += self.visit(ext)
            else:
                s += self.visit(ext) + ';\n'
        return s

    def visit_PreprocessorLine(self, n):
        return n.contents

# vim: fdm=marker
