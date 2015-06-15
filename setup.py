#! /usr/bin/env python

import os
import re
from setuptools import setup, find_packages

version = ''
with open('codalib/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

readme = ''
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as fd:
    readme = fd.read()

install_requires = [
    'lxml',
]

setup(
    name='codalib',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    description='A helper library for Coda.',
    long_description=readme,
    keywords='library anvl coda',
    author='University of North Texas Libraries',
    author_email='mark.phillips@unt.edu',
    url='https://github.com/unt-libraries/codalib',
    zip_safe=False,
    install_requires=install_requires,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ]
)
