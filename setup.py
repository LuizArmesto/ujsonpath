# coding: utf-8
from __future__ import print_function

import sys
from os.path import dirname, join
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

_name = 'ujsonpath'
_description = 'A fast JSONPath implementation'

_install_requires = []
_tests_require = [
    'pytest',
    'pytest-cov',
    'tox',
    'virtualenv',
]


def _get_version():
    """Return the project version from VERSION file."""
    with open(join(dirname(__file__), _name, 'VERSION'), 'rb') as f:
        version = f.read().decode('ascii').strip()
    return version


class Tox(TestCommand):
    """Run the test cases using TOX command."""

    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        else:
            # Run all tests by default
            args = ['-c', join(dirname(__file__), 'tox.ini'), 'tests']
        errno = tox.cmdline(args=args)
        sys.exit(errno)


setup(
    name=_name,
    version=_get_version(),
    url='https://github.com/LuizArmesto/{name}'.format(name=_name),
    description=_description,
    long_description=open('README.md').read(),
    author='Luiz Armesto',
    maintainer='Luiz Armesto',
    maintainer_email='luiz.armesto@gmail.com',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=_install_requires,
    tests_require=_tests_require,
    cmdclass={
        'test': Tox,
    },
)
