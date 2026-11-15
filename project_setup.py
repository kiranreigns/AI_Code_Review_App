# TODO: You might need to import additional modules for file path handling
import os
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CodeFile:
    file_path: str
    content: str
    language: str
    last_updated: datetime

    # TODO: Add a get_file_extension method that extracts and returns the file extension from file_path
    # The method should handle cases where there is no extension and return an appropriate default value
    def get_file_extension(self):
        extension = os.path.splitext(self.file_path)[-1]
        return extension

@dataclass
class GitCommit:
    hash: str
    message: str
    author: str
    date: datetime


@dataclass
class FileChange:
    file_path: str
    commit_hash: str
    diff_content: str


if __name__ == "__main__":
    # Create sample CodeFile instances with different file paths
    python_file = CodeFile(
        file_path="src/main.py",
        content="print('Hello, world!')",
        language="python",
        last_updated=datetime.now(),
    )

    javascript_file = CodeFile(
        file_path="web/script.js",
        content="console.log('Hello, world!');",
        language="javascript",
        last_updated=datetime.now(),
    )

    readme_file = CodeFile(
        file_path="README",
        content="# Project Documentation",
        language="markdown",
        last_updated=datetime.now(),
    )

    dockerfile = CodeFile(
        file_path="Dockerfile",
        content="FROM python:3.9-slim",
        language="dockerfile",
        last_updated=datetime.now(),
    )

    code_files = [python_file, javascript_file, readme_file, dockerfile]

    # TODO: Call the get_file_extension method on each CodeFile instance and print the results
    # Make sure to display both the file path and its extension
    for code_file in code_files:
        print(f"{code_file.language} : {code_file.get_file_extension()}")

    print("Project setup complete. Ready to build components!")
