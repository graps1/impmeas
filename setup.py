from setuptools import setup, find_packages

setup(
        name="importance_measures",
        version="1.0",
        packages=find_packages(
            include=["importance_measures"],
            exclude=[
                "importance_measures.tests",
                "importance_measures.notebooks"
            ]
        )
)
