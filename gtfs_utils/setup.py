#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import io

from setuptools import setup, find_packages

# About dict to store version and package info
about = dict()
with io.open('gtfs_utils/__version__.py', 'r', encoding='utf-8') as f:
    exec(f.read(), about)

requirements = [
    'partridge>=0.10.0',
    'gtfstk',
    'numpy',
    'pandas',
    'boto3',
]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest',
]

setup(
    name='gtfs_utils',
    version=about['__version__'],
    description='gtfs_utils is python library for working with archives of'
                'GTFS feeds using pandas DataFrames.',
    #    long_description=readme + '\n\n' + history,
    author='Dan Bareket',
    author_email='dbareket@gmail.com',
    #    url='https://github.com/remix/partridge',
    packages=find_packages(include=['gtfs_utils']),
    include_package_data=True,
    install_requires=requirements,
    license='MIT license',
    zip_safe=False,
    keywords='gtfs_utils',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.5, <4',
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
