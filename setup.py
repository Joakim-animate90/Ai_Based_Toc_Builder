from setuptools import setup, find_packages

setup(
    name="ai_based_toc_builder",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.110.0",
        "uvicorn>=0.27.0",
        "pydantic>=2.6.0",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
        "python-multipart>=0.0.9",
        "PyMuPDF>=1.23.5",
        "openai>=1.10.0",
    ],
)
