import os

from setuptools import find_packages, setup

readme = open("README.rst").read()
history = open("CHANGES.rst").read()

dependency_links = [
    "git://github.com/caltech/datacite@rest-api#egg=datacite",
]

tests_require = [
    "check-manifest>=0.42",
    "coverage>=5.3,<6",
    "pytest-cov>=2.10.1",
    "pytest-isort>=1.2.0",
    "pytest-pycodestyle>=2.2.0",
    "pytest-pydocstyle>=2.2.0",
    "pytest>=6,<7",
    "flake8>=3.8.3",
    "flake8-bugbear>=20.1.4",
]

docs_require = [
    "Sphinx>=3",
]

extras_require = {
    "docs": docs_require,
    "tests": tests_require,
}

extras_require["all"] = []
for reqs in extras_require.values():
    extras_require["all"].extend(reqs)

install_requires = [
    "click>=7.1.2",
]

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("medra_to_datacite", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]


setup(
    name="medra-to-datacite",
    license="MIT",
    version=version,
    description=__doc__,
    long_description=readme + "\n\n" + history,
    author="TU Graz Library",
    author_email="zeitschriften.bibliothek@tugraz.at",
    url="https://github.com/tu-graz-library/medra-to-datacite",
    include_package_data=True,
    packages=packages,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "medraToDatacite = medra_to_datacite.cli:cli",
        ]
    },
    dependency_links=dependency_links,
    extras_require=extras_require,
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
)
