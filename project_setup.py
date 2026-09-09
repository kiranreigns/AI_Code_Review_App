from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class CodeFile:
    file_path: str
    content: str
    language: str
    last_updated: datetime
    # TODO: Add a new field called file_size with type int
    file_size: int

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
    # Create a CodeFile instance
    sample_file = CodeFile(
        file_path="src/main.py",
        content="def hello():\n    print('Hello, world!')",
        language="python",
        last_updated=datetime.now(),
        # TODO: Add the file_size parameter with an integer value
        file_size=5
    )
    print(sample_file)

    # Create a GitCommit instance
    sample_commit = GitCommit(
        hash="a7f3d28c",
        message="Add hello function",
        author="Jane Smith",
        date=datetime.now()
    )
    print(sample_commit)

    # Create a FileChange instance
    sample_change = FileChange(
        file_path="src/main.py",
        commit_hash="a7f3d28c",
        diff_content="+ def hello():\n+     print('Hello, world!')"
    )
    print(sample_change)

    print("Project setup complete. Ready to build components!")