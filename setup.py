import setuptools

setuptools.setup(
    name="eval_ai_coverage",
    version="0.0.1",
    description='Python package for investigating coverage of Eval AI dataset',
    url="https://github.com/BlakeJC94/eval-ai-coverage",
    author="Blake Cook",
    classifiers=[
        'Development Status :: Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    python_requires=">=3.8",
    packages=setuptools.find_packages(),
    package_data={'seeralgo': ['../output/*']},
    install_requires=[
        'numpy',
        'pandas',
        'mne',
        'tqdm',
    ],
)
