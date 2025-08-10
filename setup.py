#!/usr/bin/env python3

import pathlib
import sys

from glob import glob
from setuptools import find_packages, setup, Extension


MINIMAL_PY_VERSION = (3, 7)
if sys.version_info < MINIMAL_PY_VERSION:
    raise RuntimeError('This app works only with Python %s+' % '.'.join(map(str, MINIMAL_PY_VERSION)))


def get_file(rel_path):
    return (pathlib.Path(__file__).parent / rel_path).read_text('utf-8')


setup(
    name='pyicer',
    setuptools_git_versioning={
        'enabled': True,
        'template': '{tag}.{ccount}',
        'dev_template': '{tag}.{ccount}',
        'dirty_template': '{tag}.{ccount}',
    },
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
    setup_requires=[
        'setuptools-git-versioning',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.7',
    ext_modules=[
        Extension(
            '_pyicer',
            sources=glob('icer_compression/lib_icer/src/*.c') + ['src/_pyicer.c'],
            include_dirs=['icer_compression/lib_icer/inc'],
            extra_compile_args=['-std=c11', '-Wall', '-O2', '-fPIC'],
        )
    ],
)
