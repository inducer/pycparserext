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
      version="2013.1",
      description="Extensions for pycparser",
      long_description=open("README.rst", "r").read(),
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
          "ply>=3.4",
          "pycparser>=2.09.1",
          ],

      author="Andreas Kloeckner",
      url="http://pypi.python.org/pypi/pycparserext",
      author_email="inform@tiker.net",
      license = "MIT",
      packages=["pycparserext"],

      # 2to3 invocation
      cmdclass={'build_py': build_py})
