from setuptools import setup, find_packages

setup(
    name="gemini-parser",
    version="0.1.0",
    description="A Python library for processing documents with the Gemini API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Thimira Nirmal",
    author_email="timnirla@gamail.com",  # Replace with your email
    url="https://github.com/timnirla/gemini-parser",  # Replace with your GitHub URL
    packages=find_packages(include=["gemini_parser", "gemini_parser.*"]),
    install_requires=[
        "tqdm",
        "PyPDF2",
        "google-genai",
        "python-dotenv",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "gemini-parser=gemini_parser.document_processor:main",  # Optional CLI
        ],
    },
)
