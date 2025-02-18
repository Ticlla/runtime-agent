from setuptools import setup, find_packages

setup(
    name="ai-agent-framework",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "redis>=5.0.1",
        "asyncpg>=0.28.0",
        "httpx>=0.25.0",
        "openai>=1.3.0",
        "python-dotenv>=1.0.0",
        "numpy>=1.26.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
        ],
    },
    python_requires=">=3.12",
) 