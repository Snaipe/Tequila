import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "tequila",
    version = "0.0.1",
    author = "Snaipe",
    author_email = "franklinmathieu@gmail.com",
    description = "A minecraft server manager",
    license = "BSD",
    keywords = "minecraft server manager",
    url = "http://github.com/Snaipe/tequila",
    packages=['tequila'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
        ],
    )
