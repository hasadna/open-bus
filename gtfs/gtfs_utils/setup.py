#!/usr/bin/env python
import io
from setuptools import setup, find_packages
from os.path import join, abspath, dirname

# About dict to store version and package info
about = dict()
with io.open(join(dirname(abspath(__file__)),
                  'gtfs_utils',
                  '__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), about)

requirements = [
    'python-dateutil<2.8.1,>=2.1',
    'boto3==1.10.13',
    'partridge==0.11.0',
    'gtfstk==9.6.3',
    'numpy==1.17.3',
    'pandas<0.25,>=0.24',
    'tqdm==4.37.0',
    'jsonschema==3.2.0',
    'sphinx-jsonschema==1.11',
    'sphinx==1.7.9',
    'sphinx_rtd_theme==0.4.2',
]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest==4.0.2',
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
    install_requires=requirements + test_requirements + setup_requirements,
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
    setup_requirements=setup_requirements,
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'run_gtfs_stats=gtfs_utils.gtfs_stats:main',
            'download_daily_ftp_files=gtfs_utils.download_daily_ftp_files:main',
        ],
    },
)
