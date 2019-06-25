import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="polytropos",
    version="0.0.5",
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
        'dacite',
        'pyyaml',
        'cachetools',
        'tblib'
    ],
    download_url='https://github.com/borenstein/polytropos/archive/0.0.4.tar.gz',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.7',
    ]
)
