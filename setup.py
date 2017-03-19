import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
requirements = list(parse_requirements("requirements.txt",
                                       session=False))

test_requirements = list(parse_requirements("requirements-test.txt",
                                            session=False))


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
    version='0.0.13',
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
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ],
    extras_require={
        'testing': ['pytest'],
    }
)
