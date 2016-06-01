from os.path import abspath, dirname, join
from setuptools import setup, find_packages

INIT_FILE = join(dirname(abspath(__file__)), 'justified', '__init__.py')

def get_version():
    with open(INIT_FILE) as fd:
        for line in fd:
            if line.startswith('__version__'):
                version = line.split()[-1].strip('\'')
                return version
        raise AttributeError('Package does not have a __version__')

setup(
    name='justified',
    description="Python implementation of the Knuth-Plass algorithm for fixed-width type",
    #long_description=open('README.md').read(),
    url="http://github.com/benjamin9999/justified/",
    version=get_version(),
    author='Benjamin Yates',
    author_email='benjamin@rqdq.com',
    packages=['justified'],
    install_requires=[],
    license='MIT',
)

