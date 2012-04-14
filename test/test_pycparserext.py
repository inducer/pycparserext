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

    from pycparserext.ext_c_generator import GnuCGenerator
    print GnuCGenerator().visit(ast)





if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        exec(sys.argv[1])
    else:
        from py.test.cmdline import main
        main([__file__])
