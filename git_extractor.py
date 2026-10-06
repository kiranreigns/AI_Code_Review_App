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

    # TODO: Add an author_filter parameter with a default value of None
    def extract_commits(self, repo_path, max_commits=50, author_filter=None):
        print(f"Extracting git history: {repo_path}")
        repo = Repo(repo_path)

        for commit in repo.iter_commits(max_count=max_commits):
            author_name = commit.author.name

            # TODO: Add a condition to check if the commit's author name contains the filter string (case-insensitive)
            if author_filter is not None and author_filter.lower() not in author_name.lower():

            # TODO: Skip commits that don't match the author filter
                continue

            git_commit = GitCommit(
                hash=commit.hexsha,
                message=commit.message.strip(),
                author=f"{author_name} <{commit.author.email}>",
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
        # Extract all commits first
        commits = extractor.extract_commits(repo_path, max_commits=10)

        # Display first few commits
        print("\nAll recent commits:")
        for i, commit in enumerate(commits[:3]):
            print(f"{i+1}. {commit.hash[:8]} - {commit.message[:50]}...")
            print(f"   Author: {commit.author}")
            print(f"   Date: {commit.date}")
            print()

        # TODO: Reset the extractor and create a new instance
        extractor = GitHistoryExtractor()
        # TODO: Define an author name to filter by (e.g., "Alice")
        author_filter = "Kiran"
        # TODO: Call extract_commits with the author_filter parameter
        filtered_commits = extractor.extract_commits(repo_path, max_commits=10, author_filter=author_filter)
        # TODO: Display filtered commits with appropriate header
        print(f"\nCommits by {author_filter}: \n")
        for i, commit in enumerate(filtered_commits):
            print(f"{i+1}. {commit.hash[:8]} - {commit.message[:50]}...")
            print(f"   Author: {commit.author}")
            print(f"   Date: {commit.date}")
            print()
        # TODO: Add logic to handle the case when no commits match the filter
        if len(extractor.commits) == 0:
            print("No commits found for this author.")

    except Exception as e:
        print(f"Error extracting git history: {e}")


if __name__ == "__main__":
    main()