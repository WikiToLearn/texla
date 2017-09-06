from setuptools import setup
from setuptools import find_packages

setup(
    name="texla",
    version="0.1.2",
    author="Davide Valsecchi",
    author_email="valsecchi.davide94@gmail.com",
    url="https://github.com/WikiToLearn/texla",
    license="GPL",
    packages=find_packages(),
    install_requires=[
        "PyYaml", "requests"
    ],
    python_requires='>=3',
    include_package_data=True,
    entry_points={
        "console_scripts" : [
            "texla=texla.scripts.texla:main"
        ]
    }
)
