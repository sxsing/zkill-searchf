import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zkill-searchf", # Replace with your own username
    version="0.0.1",
    author="Chang Liu",
    author_email="lcqwop@gmail.com",
    description="Search for EVE Killmails on Zkillboard by ship and equipments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sxsing/zkill-searchf",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "aiohttp",
        "PyYAML",
    ],
    entry_points={
        "console_scripts": ["zkill-searchf=zkill_searchf.search:cli_entry_point"]
    },
)