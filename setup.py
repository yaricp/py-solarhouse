import setuptools
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setuptools.setup(
    name="solarhouse",  # Replace with your own username
    version="0.0.1",
    author="Yaric Pisarev",
    author_email="yaricp@gmail.com",
    description="package for calculate solar power what you can get\
                on surfaces of building by solar heat collectors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yaricp/py-solarhouse",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
