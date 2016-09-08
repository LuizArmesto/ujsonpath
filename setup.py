# coding: utf-8

from os.path import dirname, join
from setuptools import setup, find_packages

def _get_version():
    """Return the project version from VERSION file."""

    with open(join(dirname(__file__), 'jsonpath/VERSION'), 'rb') as f:
        version = f.read().decode('ascii').strip()
    return version

setup(
    name='jsonpath',
    version=_get_version(),
    url='',
    description='Blabs Web Console',
    long_description=open('README.md').read(),
    author='Blabs Team',
    maintainer='Blabs Team',
    maintainer_email='',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[]
)
