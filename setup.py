from setuptools import setup, find_packages

setup(
    name="code_review_assistant",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "openai>=1.12.0",
        "python-dotenv>=1.0.0",
        "sqlalchemy>=2.0.23",
        "sqlalchemy-utils>=0.41.1",
        "redis>=5.0.1",
        "psycopg2-binary>=2.9.9"
    ]
) 