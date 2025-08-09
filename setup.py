#!/usr/bin/env python3

import pathlib
import os
import sys

from glob import glob
from distutils import ccompiler
from setuptools import find_packages, setup


sources = glob('icer_compression/lib_icer/src/*.c')
cc = ccompiler.new_compiler(compiler='mingw32' if os.name == 'nt' else None)
cc.compile(
    sources=sources,
    output_dir='build',
    include_dirs=['icer_compression/lib_icer/inc'],
    extra_preargs=['-O2', '-fPIC', '-Wall', '-Wextra', '-std=c11'],
)
cc.link_shared_lib(
    objects=cc.object_filenames(sources, output_dir='build'),
    output_libname='icer',
    output_dir='build/lib'
)


MINIMAL_PY_VERSION = (3, 7)
if sys.version_info < MINIMAL_PY_VERSION:
    raise RuntimeError('This app works only with Python %s+' % '.'.join(map(str, MINIMAL_PY_VERSION)))


def get_file(rel_path):
    return (pathlib.Path(__file__).parent / rel_path).read_text('utf-8')


def get_version():
    for line in get_file('pyicer/__init__.py').splitlines():
        if line.startswith('__version__'):
            return line.split()[2][1:-1]


setup(
    name='pyicer',
    version=get_version(),
    url='https://github.com/baskiton/pyicer',
    project_urls={
        'Source': 'https://github.com/baskiton/pyicer',
        'Bug Tracker': 'https://github.com/baskiton/pyicer/issues',
    },
    license='MIT',
    author='Alexander Baskikh',
    author_email='baskiton@gmail.com',
    description='Python wrapper for libicer',
    long_description=get_file('README.md'),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    keywords='icer',
    python_requires='>=3.7',
)
