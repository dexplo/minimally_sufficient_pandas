import setuptools
import re

with open('minimally_sufficient_pandas/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split("'")[1]

with open("README.md", "r") as fh:
    long_description = fh.read()

pat = r'!\[img\]\('
repl = r'![img](https://raw.githubusercontent.com/dexplo/minimally_sufficient_pandas/master/'
long_description = re.sub(pat, repl, long_description)

setuptools.setup(
    name="minimally_sufficient_pandas",
    version=version,
    author="Ted Petrou",
    author_email="petrou.theodore@gmail.com",
    description="A pandas DataFrame accessor limiting methods to a minimally sufficient subset",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="pandas DataFrame minimally sufficient",
    url="https://github.com/dexplo/bar_chart_race",
    packages=setuptools.find_packages(),
    license='BSD',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas>=0.24"],
    python_requires='>=3.6',
    include_package_data=True,
)