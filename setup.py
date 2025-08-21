"""
Setup script for requests-ai-validator package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Читаем версию из __init__.py
def get_version():
    init_file = Path("requests_ai_validator") / "__init__.py"
    with open(init_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return "0.1.0"

# Читаем README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="requests-ai-validator",
    version=get_version(),
    author="Aleksei Koledachkin",
    author_email="akoledachkin@gmail.com",
    description="AI-powered validation wrapper for Python requests library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/manikosto/requests-ai-validator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.25.0"],
        "pydantic": ["pydantic>=2.0.0"],
        "jsonschema": ["jsonschema>=4.0.0"],
        "yaml": ["PyYAML>=6.0"],
        "allure": ["allure-pytest>=2.12.0"],
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.25.0",
            "pydantic>=2.0.0",
            "jsonschema>=4.0.0",
            "PyYAML>=6.0",
            "allure-pytest>=2.12.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
        ]
    },
    keywords="requests api testing validation ai http automation",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/requests-ai-validator/issues",
        "Source": "https://github.com/yourusername/requests-ai-validator",
        "Documentation": "https://github.com/yourusername/requests-ai-validator#readme",
    },
    include_package_data=True,
    package_data={
        "requests_ai_validator": ["*.json", "*.yaml"],
    },
)
