import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()

setup(
    name = "tc-goggles",
    version = "0.0",
    author = "Darío Cutillas",
    description = ("Utility python API for executing TeamCity queries."),
    license = "MIT",
    keywords = "example documentation tutorial",
    url = "http://packages.python.org/an_example_pypi_project",
    packages=['tc_goggles', 'tc_goggles.cli'],
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    requires=['requests'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)