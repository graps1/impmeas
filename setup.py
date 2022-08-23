from setuptools import setup, find_packages

setup(
        name="impmeas",
        version="1.0",
        packages=find_packages(
            include=[
                "impmeas",
                "impmeas.bdds",
                "impmeas.mc"
            ],
            exclude=[
                "impmeas.tests",
                "impmeas.notebooks"
            ]
        )
)
