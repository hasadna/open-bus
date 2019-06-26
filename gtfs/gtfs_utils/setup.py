#!/usr/bin/env python
import io
from setuptools import setup, find_packages
from os.path import join, curdir

# About dict to store version and package info
about = dict()
with io.open(join(curdir, 'gtfs_utils', '__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), about)

requirements = [
    'partridge<1.0.0,>=0.11.0',
    'gtfstk==9.6.3',
    'numpy',
    'pandas<0.25,>=0.24',
    'boto3',
    'tqdm',
]

setup_requirements = [
    'pytest-runner',
    'sphinx==1.7.9',
    'sphinx_rtd_theme==0.4.2',
]

test_requirements = [
    'pytest',
]

setup(
    name='gtfs_utils',
    version=about['__version__'],
    description='gtfs_utils is python library for working with archives of'
                'GTFS feeds using pandas DataFrames.',
    author='Dan Bareket',
    author_email='dbareket@gmail.com',
    packages=find_packages(include=['.']),
    include_package_data=True,
    install_requires=requirements,
    license='MIT license',
    zip_safe=False,
    keywords='gtfs_utils',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.7, <4',
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
