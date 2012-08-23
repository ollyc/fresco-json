#!/usr/bin/env python
# Copyright (c) 2012 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

import os
import re
from setuptools import setup, find_packages

VERSIONFILE = "src/fresco_json.py"


def get_version():
    with open(VERSIONFILE, 'r') as f:
        return re.search(b"^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                           f.read(), re.M).group(1)


def read(*path):
    """
    Read and return content from ``path``
    """
    f = open(os.path.join(os.path.dirname(__file__), *path), 'r')
    try:
        return f.read().decode('UTF-8')
    finally:
        f.close()

setup(
    name='fresco-json',
    version=get_version(),
    url='',

    license='BSD',
    author='Oliver Cope',
    author_email='oliver@redgecko.org',

    description='',
    long_description=read('README.txt') + "\n\n" + read("CHANGELOG.txt"),

    py_modules=['fresco_json'],
    packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
    package_dir={'': 'src'},

    install_requires=['fresco', 'zope.component'],
    zip_safe=False,
    classifiers=[],
)
