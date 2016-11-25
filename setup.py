import io
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from pip.req import parse_requirements
from uberlogs import __version__

# parse_requirements() returns generator of pip.req.InstallRequirement objects
requirements = parse_requirements("requirements.txt", session=False)
test_requirements = parse_requirements("requirements-test.txt", session=False)


class PyTest(TestCommand):

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='uberlogs',
    version=__version__,
    url='http://github.com/odedlaz/uberlogs',
    license='MIT License',
    author='Oded Lazar',
    tests_require=[str(ir.req) for ir in test_requirements if ir.req],
    install_requires=[str(ir.req) for ir in requirements if ir.req],
    dependency_links=[str(ir.link) for ir in requirements if ir.link],
    cmdclass={'test': PyTest},
    author_email='odedlaz@gmail.com',
    description='UberLogs',
    packages=find_packages(),
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    extras_require={
        'testing': ['pytest'],
    }
)
