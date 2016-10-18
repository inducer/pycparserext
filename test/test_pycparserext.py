from __future__ import print_function
import pytest


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


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        exec(sys.argv[1])
    else:
        from py.test.cmdline import main
        main([__file__])
