from __future__ import print_function
import pytest


# Inspired from pycparser's compare_asts test function
def _compare_asts(first, second):
    if type(first) is not type(second):
        return False

    if isinstance(first, tuple):
        if first[0] != second[0]:
            return False

        return _compare_asts(first[1], second[1])

    for attr in first.attr_names:
        if getattr(first, attr) != getattr(second, attr):
            return False

    for i, c1 in enumerate(first.children()):
        if not _compare_asts(c1, second.children()[i]):
            return False
    return True


def _round_trip_matches(src):
    from pycparserext.ext_c_parser import GnuCParser
    from pycparserext.ext_c_generator import GnuCGenerator

    p = GnuCParser()

    first_ast = p.parse(src)

    gen = GnuCGenerator().visit(first_ast)

    second_ast = p.parse(gen)

    if not _compare_asts(first_ast, second_ast):
        print('First AST:')
        first_ast.show()

        print('Generated code:')
        print(gen)

        print('Second AST:')
        second_ast.show()

        return False
    return True


def test_asm_volatile_1():
    src = """
    void read_tsc(void) {
        long val;
        asm("rdtsc" : "=A" (val));
    }    """
    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_asm_volatile_2():
    src = """
    void read_tsc(void) {
        long val;
        asm volatile("rdtsc" : "=A" (val));
    }    """
    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_asm_volatile_3():
    src = """
    void read_tsc(void) {
        long fpenv;
        asm("mtfsf 255,%0" :: "f" (fpenv));
    }    """
    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_asm_volatile_4():
    src = """
    void barrier(void) {
        __asm__ __volatile__("": : :"memory");
    }    """
    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_asm_label():
    src = """
    int foo asm("renamed_foo");

    unsigned long bar asm("renamed_bar") __attribute__ ((aligned (16)));

    unsigned long bar2 asm("renamed_bar2");

    unsigned int * bar3 asm("renamed_bar3");

    void func() {
        static int var asm("renamed_var") = 5;
    }
    """
    assert _round_trip_matches(src)


def test_funky_header_code():
    src = """
        extern __inline int __attribute__ ((__nothrow__)) __signbitf (float __x)
         {
           int __m;
           __asm ("pmovmskb %1, %0" : "=r" (__m) : "x" (__x));
           return __m & 0x8;
         }
        """

    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_funky_header_code_2():
    src = """
        extern __inline int __attribute__ ((__nothrow__)) __signbitf (float __x)
         {
           int __m;
           if (__x == 0)
              __asm ("pmovmskb %1, %0" : "=r" (__m) : "x" (__x));
           else
              __asm ("pmovmskb %1, %0" : "=r" (__m) : "x" (__x));
           return __m & 0x8;
         }
        """

    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_funky_header_code_3():
    src = """
        extern __inline int __attribute__ ((__nothrow__)) __signbitf (float __x)
         {
           int __m;
           if (__x == 0)
              __asm ("pmovmskb %1, %0" : "=r" (__m) : "x" (__x));
           return __m & 0x8;
         }
        """

    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_funky_header_code_4():
    src = """
        extern __inline int __attribute__ ((__nothrow__)) __signbitf (float __x)
         {
           int __m;
           if (__x == 0) {
              __asm ("pmovmskb %1, %0" : "=r" (__m) : "x" (__x));
           } else {
              __asm ("pmovmskb %1, %0" : "=r" (__m) : "x" (__x));
           }
           return __m & 0x8;
         }
        """

    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_funky_header_code_5():
    src = """ void  do_foo(void) __asm(__STRING(do_foo));"""

    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


@pytest.mark.parametrize("typename", ["int", "uint"])
def test_opencl(typename):
    from pycparserext.ext_c_parser import OpenCLCParser
    src = """
            __kernel void zeroMatrix(__global float *A, int n,  __global float * B)
            {
                %s i = get_global_id(0);
                for (int k=0; k<n; k++)
                    A[i*n+k] = 0;
            }
            """ % typename

    p = OpenCLCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import OpenCLCGenerator
    print(OpenCLCGenerator().visit(ast))


def test_array_attributes():
    src = """
        int x[10] __attribute__((unused));
        int y[20] __attribute((aligned(10)));
        """

    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_func_decl_attribute():
    src = """
    extern void int happy(void) __attribute__((unused));
    int main()
    {
    }
    """

    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_func_ret_ptr_decl_attribute():
    src = """
    extern void* memcpy(const void* src, const void *dst, int len)
    __attribute__((unused));
    """
    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_array_ptr_decl_attribute():
    src = """
    int* __attribute__((weak)) array[256];
    """
    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_gnu_statement_expression():
    src = """
      int func(int a) {
        return (int)({; ; *(int*)&a;});
     }
    """
    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()


def test_empty_gnu_statement_expression():
    # Incase, ASSERTS turn out to be empty statements
    src = """
      int func(int a) {
              ({
                    ; ;
                         });
                }
    """

    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_lvalue_gnu_statement_expression():
    src = """
      int func(int a) {
        int ret=(int)({; ; *(int*)&a;});
        return ret;
     }
    """

    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_empty_struct_declaration():
    src = """
        typedef struct Foo {
        } Foo_t;
    """

    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    print(GnuCGenerator().visit(ast))


def test_nesty_c_declarator():
    src = """
    struct a {
        int *b[1][1];
    };
    """

    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()


def test_const_ptr_func_arg():
    src = """
    const int *bar;
    void foo(const int *bar, int * const baz);
    """

    from pycparserext.ext_c_parser import GnuCParser
    p = GnuCParser()
    ast = p.parse(src)
    ast.show()

    from pycparserext.ext_c_generator import GnuCGenerator
    src_str = GnuCGenerator().visit(ast)

    assert src_str.count("*") == 3
    print(src_str)


def test_pointer_reproduction():
    src = """
    struct foo {
        const char                      *bar;
        const char                      *baz;
    };

    int main () {
        return 0;
    }
    """
    import pycparserext.ext_c_parser as ext_c_parser
    import pycparserext.ext_c_generator as ext_c_generator

    parser = ext_c_parser.GnuCParser()
    ast = parser.parse(src)
    gen = ext_c_generator.GnuCGenerator()
    print(gen.visit(ast))


def test_no_added_attr():
    src = """
    char* foo() {
        return "";
    }

    int main() {
        return 0;
    }
    """
    import pycparserext.ext_c_parser as ext_c_parser
    import pycparserext.ext_c_generator as ext_c_generator

    parser = ext_c_parser.GnuCParser()
    ast = parser.parse(src)
    gen = ext_c_generator.GnuCGenerator()
    print(gen.visit(ast))
    assert "attr" not in gen.visit(ast)


def test_double_pointer():
    src = """
    typedef struct Error {
        int dummy;
    } Error;

    void func_with_p2pp(const char *, Error **);
    """
    import pycparserext.ext_c_parser as ext_c_parser
    import pycparserext.ext_c_generator as ext_c_generator

    parser = ext_c_parser.GnuCParser()
    ast = parser.parse(src)
    gen = ext_c_generator.GnuCGenerator()
    ast.show()
    assert gen.visit(ast).find("func_with_p2pp(const char *, Error **)") != -1


def test_designated_initializers():
    src = """
    int a[6] = { [4] = 29, [2] = 15 };

    int widths[] = { [0 ... 9] = 1, [10 ... 99] = 2, [100] = 3 };

    int v1 = 5, v2 = 6;
    int b[] = { [1] = v1, v2, [4] = v4 };

    struct foo { int x; int y; };
    struct foo bar[10] = { [1].y = 5, [2].x = 1, [0].x = 3 };

    char char_map[256] = { [0 ... 255] = '?', ['0' ... '9'] = 'X' };
    """
    assert _round_trip_matches(src)


def test_case_ranges():
    src = """
    void f() {
        switch (1) {
            case 3:
                break;
            case 0 ... 5:
                break;
            case 'A' ... 'Z':
                break;
        }
    }
    """
    assert _round_trip_matches(src)


@pytest.mark.parametrize("restrict_kw", ["restrict", "__restrict__", "__restrict"])
def test_restrict(restrict_kw):
    src = """
    void f(int n, int * {0} p, int * {0} q)
    {{
    }}
    typedef int *array_t[10];
    {0} array_t a;
    void f(int m, int n, float a[{0} m][n], float b[{0} m][n]);
    """ .format(restrict_kw)
    assert _round_trip_matches(src)


def test_node_visitor():
    from pycparser.c_ast import NodeVisitor

    # key is type of visit, value is [actual #, expected #]
    visits = {
        'TypeList': [0, 1],
        # AttributeSpecifier is part of exprlist, not nodelist
        'AttributeSpecifier': [0, 0],
        'Asm': [0, 1],
        # PreprocessorLine is OpenCL, not GNU
        'PreprocessorLine': [0, 0],
        'TypeOfDeclaration': [0, 4],
        'TypeOfExpression': [0, 1],
        'FuncDeclExt': [0, 1],
    }

    class TestVisitor(NodeVisitor):
        def visit_TypeList(self, node):
            visits['TypeList'][0] += 1
            NodeVisitor.generic_visit(self, node)

        def visit_AttributeSpecifier(self, node):
            visits['AttributeSpecifier'][0] += 1
            NodeVisitor.generic_visit(self, node)

        def visit_Asm(self, node):
            visits['Asm'][0] += 1
            NodeVisitor.generic_visit(self, node)

        def visit_PreprocessorLine(self, node):
            visits['PreprocessorLine'][0] += 1
            NodeVisitor.generic_visit(self, node)

        def visit_TypeOfDeclaration(self, node):
            visits['TypeOfDeclaration'][0] += 1
            NodeVisitor.generic_visit(self, node)

        def visit_TypeOfExpression(self, node):
            visits['TypeOfExpression'][0] += 1
            NodeVisitor.generic_visit(self, node)

        def visit_FuncDeclExt(self, node):
            visits['FuncDeclExt'][0] += 1
            NodeVisitor.generic_visit(self, node)

    src_gnu = """
    int func1(int a, int b) {
        __typeof__(a) _a = __builtin_types_compatible_p(long char, short int);
        __typeof__ (__typeof__ (char *)[4]) y;
        typeof (typeof (char *)[4]) z;
        asm("rdtsc" : "=A" (val));
        __attribute__((unused)) static int c;
    }
    """
    import pycparserext.ext_c_parser as ext_c_parser

    parser = ext_c_parser.GnuCParser()
    ast = parser.parse(src_gnu)
    ast.show()
    TestVisitor().visit(ast)
    for visit_type, visit_num in visits.items():
        assert_msg = '{}: Should have visited {}, got {}'.format(
            visit_type, visit_num[1], visit_num[0])
        assert visit_num[0] == visit_num[1], assert_msg


def test_typeof_reproduction():
    src = """
    int func(int a, int b) {
        __typeof__(a) _a = a;
        typeof(b) _b = b;

        __typeof__ (__typeof__ (char *)[4]) y;
        typeof (typeof (char *)[4]) z;
    }
    """
    assert _round_trip_matches(src)

    import pycparserext.ext_c_parser as ext_c_parser
    from pycparser.c_ast import NodeVisitor

    # key is type of visit, value is
    # [actual # __typeof__, expected # __typeof__,
    #   actual # typeof, expected # typeof]
    visits = {
        'TypeOfDeclaration': [0, 2, 0, 2],
        'TypeOfExpression': [0, 1, 0, 1],
    }

    class TestVisitor(NodeVisitor):
        def visit_TypeOfDeclaration(self, node):
            idx = 0 if node.typeof_keyword == '__typeof__' else 2
            visits['TypeOfDeclaration'][idx] += 1
            NodeVisitor.generic_visit(self, node)

        def visit_TypeOfExpression(self, node):
            idx = 0 if node.typeof_keyword == '__typeof__' else 2
            visits['TypeOfExpression'][idx] += 1
            NodeVisitor.generic_visit(self, node)

    parser = ext_c_parser.GnuCParser()
    ast = parser.parse(src)
    ast.show()
    TestVisitor().visit(ast)
    for visit_type, visit_num in visits.items():
        assert_msg = '{}: Should have visited ({}, {}), got ({}, {})'.format(
            visit_type,
            visit_num[1], visit_num[3],
            visit_num[0], visit_num[2])
        assert visit_num[0] == visit_num[1] and \
               visit_num[2] == visit_num[3], assert_msg


def test_typedef():
    from pycparser import c_ast
    from pycparserext.ext_c_parser import GnuCParser
    from pycparserext.ext_c_generator import GnuCGenerator

    p = GnuCParser()

    first_ast = p.parse('typedef int foo;').ext[0]
    assert isinstance(first_ast, c_ast.Typedef)

    gen = GnuCGenerator().visit(first_ast.type)

    assert gen == 'int'


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        exec(sys.argv[1])
    else:
        from py.test.cmdline import main
        main([__file__])
