from setuptools import setup, find_packages

setup(
    name="privatevault-sdk",
    version="0.1.0-alpha",
    packages=find_packages(where=".."),  # relative to sdk/python
    package_dir={"": ".."},
    install_requires=["requests", "pydantic"],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "pvctl=cli.pv:main",  # points to updated cli/pv.py (now pvctl)
        ],
    },
)
