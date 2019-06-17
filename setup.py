from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    """Command to run unit tests after in-place build."""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '-sv',
            '--flake8',
            '--cov', 'openapi_spec_validator',
            '--cov-report', 'term-missing',
        ]
        self.test_suite = True

    def run_tests(self):
        # Importing here, `cause outside the eggs aren't loaded.
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name="galaxy-swift",
    version="0.1.0",
    description="GOG Galaxy swift",
    author='Artur Maciag',
    author_email='maciag.artur@gmail.com',
    packages=find_packages("src"),
    package_dir={'': 'src'},
    install_requires=[
        "galaxy.plugin.api"
    ],
    entry_points={
        'console_scripts': [
            'galaxy = galaxy_swift.__main__:main'
        ]
    },
)
