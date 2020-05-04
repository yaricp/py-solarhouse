import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="solarhouse",  # Replace with your own username
    version="0.0.1",
    author="Yaric Pisarev",
    author_email="yaricp@gmail.com",
    description="package for calculate solar power what you can get\
                on surfaces of building by solar heat collectors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
