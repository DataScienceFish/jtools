# setup.py
from setuptools import setup, find_packages
from jtools import __name__, __version__

setup(
    name=__name__,
    version=__version__,
    author='DSFish',
    author_email='liumingshuo1017@gmail.com',
    description='A simple tools module',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/jtools',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9.12',
)