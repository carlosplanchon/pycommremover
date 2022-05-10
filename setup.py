#!/usr/bin/env python3

from setuptools import setup

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="pycommremover",
    packages=["pycommremover"],
    version="0.1",
    license="MIT",
    description="Library to remove block and line comments.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Carlos A. Planchón and Agustín Céspedes",
    author_email="carlosandresplanchonprestes@gmail.com, "
            "agustinces17@gmail.com",
    url="https://github.com/carlosplanchon/pycommremover",
    download_url="https://github.com/carlosplanchon/"
        "pycommremover/archive/v0.1.tar.gz",
    keywords=["comment", "remover"],
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
)
