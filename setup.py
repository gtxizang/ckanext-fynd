from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).parent
long_description = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="ckanext-fynd",
    version="0.1.0",
    description=(
        "CKAN extension providing an MCP server for AI assistant "
        "access to datasets, DataStore, and portal metadata"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gtxizang/ckanext-fynd",
    license="AGPL-3.0",
    python_requires=">=3.10",
    packages=find_packages(include=["ckanext", "ckanext.*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "ckan>=2.10",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: CKAN",
    ],
    entry_points={
        "ckan.plugins": [
            "fynd = ckanext.fynd.plugin:FyndPlugin",
        ],
    },
)
