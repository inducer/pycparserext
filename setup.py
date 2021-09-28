#!/usr/bin/env python
# -*- coding: latin1 -*-

from setuptools import setup

setup(name="pycparserext",
      version="2021.1",
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

      python_requires="~=3.6",
      install_requires=[
          "ply>=3.4",
          "pycparser>=2.18,<=2.20",
          ],

      author="Andreas Kloeckner",
      url="http://pypi.python.org/pypi/pycparserext",
      author_email="inform@tiker.net",
      license="MIT",
      packages=["pycparserext"])
