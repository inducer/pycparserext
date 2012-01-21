#!/usr/bin/env python
# -*- coding: latin1 -*-

import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    # 2.x
    from distutils.command.build_py import build_py

setup(name="pycparserext",
      version="2012.1",
      description="Extensions for pycparser",
      long_description="""
      Extended functionality for Eli Bendersky's 
      `pycparser <http://pypi.python.org/pypi/pycparser>`_,
      in particular support for parsing GNU extensions and
      OpenCL.

      See also the `github code repository <http://github.com/inducer/pycparserext>`_.
      """,
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],

      install_requires=[
          "pycparser>=2.05"
          ],

      author="Andreas Kloeckner",
      url="http://pypi.python.org/pypi/pycparserext",
      author_email="inform@tiker.net",
      license = "MIT",
      packages=["pycparserext"],

      # 2to3 invocation
      cmdclass={'build_py': build_py})
