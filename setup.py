"""
Setup script for MapLeads
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mapleads",
    version="1.0.0",
    author="MapLeads Contributors",
    description="Open-source B2B lead generation tool for Google Maps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/MapLeads",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=[
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0",
        "sqlalchemy>=2.0.0",
        "pandas>=2.0.0",
        "requests>=2.31.0",
        "tqdm>=4.66.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "schedule>=1.2.0",
        "pydantic>=2.0.0",
        "openpyxl>=3.1.0",
    ],
    extras_require={
        "email": ["yagmail>=0.15.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mapleads=mapleads:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/*.csv", "data/*.db"],
    },
)
