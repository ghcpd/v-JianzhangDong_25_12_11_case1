import os
from setuptools import setup, find_packages

# Ensure setup runs with repository root as cwd so sdist creates dist/ where CD expects it
os.chdir(os.path.dirname(__file__))

setup(
    name="ci_cd_test_project",
    version="1.0",
    packages=find_packages(),
)
