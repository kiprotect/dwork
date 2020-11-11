from distutils.core import setup
from setuptools import find_packages
from req import reqs

setup(
    name="dwork",
    python_requires=">=3.6",
    version="0.0.4",
    author="KIProtect GmbH",
    author_email="dwork@kiprotect.com",
    license="BSD-3",
    url="https://github.com/kiprotect/dwork",
    packages=find_packages(),
    package_data={"": ["*.ini"], "dwork" : ['py.typed']},
    install_requires=reqs,
    zip_safe=False,
    # no console script so far
    #entry_points={"console_scripts": ["dwork = dwork.cli.main:dwork"]},
    description="A Python toolkit for differentially private data science & analytics.",
)
