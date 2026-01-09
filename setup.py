import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name="ci_cd_test_project",
    version="1.0",
    packages=find_packages(),
    options={
        'sdist': {
            'dist_dir': os.path.join(here, 'dist')
        }
    }
)
