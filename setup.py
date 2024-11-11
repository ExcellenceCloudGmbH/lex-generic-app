from setuptools import setup, find_packages

setup(
    name="generic_app",
    version="1.0.1",
    author="Melih Sünbül",
    author_email="m.sunbul@lund-it.com",
    description="A Python / Django library to create business applications easily with complex logic",
    long_description_content_type="text/markdown",
    url="https://github.com/LundIT/dpag-generic-app",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
