from setuptools import setup, find_packages
import re


version = re.search(
    '^__version__\s*=\s*["\'](.*)["\']',
    open('trakt_tools/version.py').read(),
    re.M
).group(1)

with open("README.rst", "rb") as f:
    long_description = f.read().decode("utf-8")

setup(
    name="trakt-tools",
    version=version,

    description='Command-line tools for Trakt.tv',
    long_description=long_description,

    author='Dean Gardiner',
    author_email='me@dgardiner.net',

    packages=find_packages(include=[
        'trakt_tools',
        'trakt_tools.*'
    ]),

    entry_points={
        'console_scripts': [
            'trakt_tools = trakt_tools.runner.main:main'
        ]
    }
)
