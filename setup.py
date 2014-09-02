from setuptools import setup, find_packages


_locals = {}
with open('pyvirtualfs/_version.py') as fp:
    exec(fp.read(), None, _locals)
version = _locals['__version__']


setup(
    name='pyvirtualfs',
    version=version,
    author='Silvan Wegmann',
    author_email='swegmann@narf.ch',
    packages=find_packages(),
    url='https://github.com/Jokymon/pyvirtualfs',
    license='LICENSE.txt',
    description='Pure Python tool for creating and populating image files.',
    long_description=open('README.txt').read(),
    entry_points="""
    [console_scripts]
    pyvfs = pyvirtualfs.pyvfs:main
    """,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
)
