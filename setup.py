import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

with open("requirements-pinned.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="wampproto",
    version="0.0.1",
    description="Sans-IO WAMP protocol implementation in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xconnio/wampproto.py",
    author="XConnIO",
    author_email="omer@xconn.io",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.10",
    install_requires=requirements,
    project_urls={
        "Source": "https://github.com/xconnio/wampproto.py",
    },
)
