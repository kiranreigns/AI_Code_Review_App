from git import Repo
from datetime import datetime
import os

# Minimal dataclasses for continuity with the outline
from dataclasses import dataclass

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

class GitHistoryExtractor:
    def __init__(self):
        self.commits = []
        self.file_changes = []

    def extract_commits(self, repo_path, max_commits=50):
        print(f"Extracting git history: {repo_path}")
        repo = Repo(repo_path)

        for commit in repo.iter_commits(max_count=max_commits):
            git_commit = GitCommit(
                hash=commit.hexsha,
                message=commit.message.strip(),
                author=f"{commit.author.name} <{commit.author.email}>",
                date=commit.committed_datetime
            )
            self.commits.append(git_commit)

            # Extract file changes
            if commit.parents:
                parent = commit.parents[0]
                for diff in parent.diff(commit, create_patch=True):
                    if diff.b_path:
                        file_change = FileChange(
                            file_path=diff.b_path,
                            commit_hash=commit.hexsha,
                            diff_content=diff.diff.decode('utf-8', errors='ignore')
                        )
                        self.file_changes.append(file_change)

        print(f"Found {len(self.commits)} commits, {len(self.file_changes)} changes")
        return self.commits


def main():
    extractor = GitHistoryExtractor()

    # Use current directory as the git repository
    repo_path = "../chatbot"

    # Check if we're in a git repository
    if not os.path.exists(os.path.join(repo_path, ".git")):
        print("Not a git repository. Initializing a sample repo...")
        # For demo purposes, we'll just show the class structure
        print("GitHistoryExtractor initialized successfully!")
        return

    try:
        commits = extractor.extract_commits(repo_path, max_commits=10)

        # Display first few commits
        print("\nRecent commits:")
        for i, commit in enumerate(commits[:3]):
            # TODO: Change the commit hash display to show only the first 6 characters (instead of 8)
            # TODO: Change the commit message display to show only the first 30 characters (instead of 50)
            print(f"{i+1}. {commit.hash[:6]} - {commit.message[:30]}...")
            print(f"   Author: {commit.author}")
            print(f"   Date: {commit.date}")
            print()

    except Exception as e:
        print(f"Error extracting git history: {e}")


if __name__ == "__main__":
    main()