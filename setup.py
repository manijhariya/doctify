from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name="doctify",
    version="0.0.1",
    author="Manish Kumar",
    author_email="mannjhariya@gmail.com",
    license="MIT License",
    description="Build a CLI powered docstring generator for python code and repos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.github.com/manijhariya/doctify",
    py_modules=["doctify", "src"],
    packages=find_packages(),
    install_requires=[requirements],
    python_requires=">=3.11",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts" : 
        ['doctify=src.__main__:main']
    },
)
