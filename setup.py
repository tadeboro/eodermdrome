# coding=utf-8

from setuptools import setup, find_packages
from os import path

setup(
    name = "eodermdrome",
    version = "0.1",
    description = "Simple eodermdrome interpreter",
    author = "Tadej Borovšak",
    author_email = "tadeboro@gmail.com",
    url = "https://github.com/tadeboro/eodermdrome",
    license = "MIT",

    classifiers = [
        "Development status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Interpreters",
    ],

    keywords = "Barebones eodermdrome interpreter",
    packages = find_packages(exclude=["samples"]),
    install_requires = ["graphviz", "pyparsing"],
    entry_points = {
        "console_scripts": [
            "runeo=eodermdrome:main",
        ],
    },
)
