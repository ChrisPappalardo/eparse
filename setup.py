#!/usr/bin/env python

'''
setup script for eparse
'''

from setuptools import setup, find_packages


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'click>=8.0.0',
    'openpyxl>=3.0.0',
    'pandas>=2.0.0',
    'peewee>=3.16.0',
]

test_requirements = [
    'black',
    'coverage',
    'flake8',
    'ipython',
    'pytest',
    'tox',
]

setup(
    author='Chris Pappalardo',
    author_email='cpappala@gmail.com',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    description='''
    Excel spreadsheet crawler and table parser for data discovery, extraction, and querying
    ''',
    entry_points={
        'console_scripts': [
            'eparse=eparse.cli:entry_point',
        ],
    },
    install_requires=requirements,
    license='MIT license',
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='eparse',
    name='eparse',
    packages=find_packages(include=['eparse', 'eparse.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ChrisPappalardo/eparse',
    version='0.7.0',
    zip_safe=False,
)
