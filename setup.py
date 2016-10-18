#!/usr/bin/env python
# -*- coding: latin1 -*-

from setuptools import setup

setup(name="pycparserext",
      version="2016.2",
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
          "pycparser>=2.14",
          ],

      author="Andreas Kloeckner",
      url="http://pypi.python.org/pypi/pycparserext",
      author_email="inform@tiker.net",
      license="MIT",
      packages=["pycparserext"])
