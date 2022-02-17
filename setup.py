# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

VERSION = "v0.3.1"

LONG_DESCRIPTION = """
This package contains a [Sphinx](http://www.sphinx-doc.org/) extension
for producing exercise and solution directives.

This project is maintained and supported by the Executable Books Project.
"""

SHORT_DESCRIPTION = "A Sphinx extension for producing exercises and solutions."

BASE_URL = "https://github.com/executablebooks/sphinx-exercise"
URL = f"{BASE_URL}/archive/{VERSION}.tar.gz"

# Define all extras
extras = {
    "code_style": ["flake8<3.8.0,>=3.7.0", "black", "pre-commit==1.17.0"],
    "testing": [
        "coverage",
        "pytest>=3.6,<4",
        "pytest-cov",
        "pytest-regressions",
        "beautifulsoup4",
        "myst-nb",
        "texsoup",
    ],
    "rtd": [
        "sphinx>=3.0",
        "sphinx-book-theme",
        "myst-nb",
    ],
}

extras["all"] = set(ii for jj in extras.values() for ii in jj)

setup(
    name="sphinx-exercise",
    version=VERSION,
    python_requires=">=3.6",
    author="QuantEcon",
    author_email="admin@quantecon.org",
    url=BASE_URL,
    download_url=URL,
    project_urls={
        "Source": BASE_URL,
        "Tracker": f"{BASE_URL}/issues",
    },
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license="BSD",
    packages=find_packages(),
    install_requires=["docutils>=0.15", "sphinx", "sphinx-book-theme"],
    extras_require=extras,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Environment :: Web Environment",
        "Framework :: Sphinx :: Extension",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python",
        "Topic :: Documentation :: Sphinx",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
)
