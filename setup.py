import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="polytropos",
    version="0.1.2",
    license='agpl-3.0',
    url='https://github.com/borenstein/polytropos',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        'scipy',
        'numpy',
        'pytest',
        'glom',
        'pytest-repeat',
        'pyyaml',
        'cachetools',
        'tblib',
        'click',
        'asciitree',
        'tqdm',
        'typing-extensions'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points='''
    [console_scripts]
    polytropos=polytropos.cli:cli
    '''
)
