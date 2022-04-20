"""Setup script.

Install package:
    $ pip install -e .

Requirements can be updated using `pip-compile`:
    $ pip install pip-tools
    $ pip-compile
"""

from setuptools import setup, find_packages

setup(
    name="ea_coverage",
    version="0.5.1",
    description='Python package for investigating coverage of Eval AI dataset',
    url="https://github.com/BlakeJC94/eval-ai-coverage",
    author="BlakeJC94",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        'fire',
        'mne',
        'numpy',
        'pandas',
        'tqdm',
    ],
    entry_points={
        'console_scripts': ['ea-coverage=ea_coverage.__main__:main'],
    },
)
