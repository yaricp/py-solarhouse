import os
import setuptools

from src.solarhouse.version import version

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setuptools.setup(
    name="solarhouse",  # Replace with your own username
    version=version,
    author="Yaric Pisarev",
    author_email="yaricp@gmail.com",
    description="package for calculate solar power what you can get\
                on surfaces of building by solar heat collectors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yaricp/py-solarhouse",
    package_dir={'solarhouse': 'src/solarhouse'},
    packages=['solarhouse'],
    install_requires=[
        'numpy',
        'scipy',
        'trimesh',
        'pvlib',
        'pandas',
        'matplotlib',
        'mpld3',
        'shapely',
        'jinja2',
        'netCDF4',
        'siphon',
        'tables',
    ],
    dependency_links=['https://github.com/Unidata/netcdf4-python'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
