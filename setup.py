#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Edwin Steele",
    author_email='edwin@wordspeak.org',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Recommendation engine for NSW petrol purchases",
    entry_points={
        'console_scripts': [
            'nsw_petrol_pricing=nsw_petrol_pricing.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='nsw_petrol_pricing',
    name='nsw_petrol_pricing',
    packages=find_packages(include=['nsw_petrol_pricing', 'nsw_petrol_pricing.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/edwinsteele/nsw_petrol_pricing',
    version='0.1.0',
    zip_safe=False,
)
