from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class CodeFile:
    file_path: str
    content: str
    language: str
    last_updated: datetime


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


def link_commit_to_files(
    commit: GitCommit, changes: List[FileChange]
) -> List[FileChange]:
    """
    Find all file changes that belong to a specific commit.

    Args:
        commit: A GitCommit instance
        changes: A list of FileChange instances

    Returns:
        A list of FileChange instances that match the commit's hash
    """
    # TODO: Create an empty list to store matching changes
    matching_changes = []
    # TODO: Loop through each change in the changes list
    for file_change in changes:
    # TODO: Check if the change's commit_hash matches the commit's hash
    # and add matching changes to your list
        if file_change.commit_hash == commit.hash:
            matching_changes.append(file_change)

        # TODO: Return the list of matching changes
        return matching_changes


if __name__ == "__main__":
    # Create a sample commit
    sample_commit = GitCommit(
        hash="a7f3d28c",
        message="Add login functionality",
        author="Jane Smith",
        date=datetime.now(),
    )

    # Create sample file changes (some matching the commit, some not)
    file_changes = [
        FileChange(
            file_path="src/auth.py",
            commit_hash="a7f3d28c",  # Matches our commit
            diff_content="+ def login(username, password):\n+     return check_credentials(username, password)",
        ),
        FileChange(
            file_path="src/utils.py",
            commit_hash="b8e4f19d",  # Different commit
            diff_content="+ def format_date(date):\n+     return date.strftime('%Y-%m-%d')",
        ),
        FileChange(
            file_path="src/models.py",
            commit_hash="a7f3d28c",  # Matches our commit
            diff_content="+ class User:\n+     def __init__(self, username, email):\n+         self.username = username\n+         self.email = email",
        ),
        FileChange(
            file_path="tests/test_auth.py",
            commit_hash="a7f3d28c",  # Matches our commit
            diff_content="+ def test_login():\n+     assert login('admin', 'password') == True",
        ),
        FileChange(
            file_path="README.md",
            commit_hash="c9d2e35a",  # Different commit
            diff_content="+ ## Authentication\n+ The system now supports user authentication.",
        ),
    ]

    # Find changes for our commit
    matching_changes = link_commit_to_files(sample_commit, file_changes)

    # Display the results
    print(f"Commit: {sample_commit.hash} - {sample_commit.message}")
    print(f"Found {len(matching_changes)} matching file changes:")

    # TODO: Add code to display each matching change
    # If there are matching changes, loop through them and print details
    if matching_changes:
        for file_change in matching_changes:
           print(f"\n  File: {file_change.file_path}")
        print(f"  Diff:\n{file_change.diff_content}")
    # If there are no matching changes, print a message saying so
    else:
        print("No matching changes found.")
