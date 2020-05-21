import setuptools

setuptools.setup(
    name="solarhouse",  # Replace with your own username
    version="0.0.1",
    author="Yaric Pisarev",
    author_email="yaricp@gmail.com",
    description="package for calculate solar power what you can get\
                on surfaces of building by solar heat collectors",
    long_description="""This package allow you to calculate solar power on all faces of mesh of a house.
                     Also you can get plots of temperature of elements in a house. """,
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
