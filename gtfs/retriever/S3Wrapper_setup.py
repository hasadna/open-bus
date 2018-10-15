#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import io

from setuptools import setup, find_packages

requirements = ['boto3']

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
]

setup(
    name='S3Wrapper',
    version='0.0.1',
    description='S3wrapper is python library for working with S3 interface',
    author='Aviv & Omer',
    author_email='',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.5, <4',
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
