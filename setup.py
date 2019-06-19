#!/usr/bin/env python
from codecs import open
from os import path

from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='platon',
    version='0.1',
    license=license,
    long_description=long_description,
    description='Platon Python SDK',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='platon payment',
    packages=find_packages(),
    install_requires=['requests'],
)
