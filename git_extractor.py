import os
from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from git import InvalidGitRepositoryError, Repo
from git.exc import GitCommandError


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

    def extract_commits(self, repo_path, max_commits=50, author_filter=None, file_extensions=None):
        print(f"Extracting git history: {repo_path}")
        repo = Repo(repo_path)

        for commit in repo.iter_commits(max_count=max_commits):
            author_name = commit.author.name

            if author_filter is not None and author_filter.lower() not in author_name.lower():
                continue

            file_changes = []

            if commit.parents:
                parent = commit.parents[0]
                for diff in parent.diff(commit, create_patch=True):
                    if diff.b_path:
                        file_changes.append(FileChange(
                            file_path=diff.b_path,
                            commit_hash=commit.hexsha,
                            diff_content=diff.diff.decode('utf-8', errors='ignore')
                        ))

            if file_extensions is not None:
                matched = [fc for fc in file_changes if any(fc.file_path.endswith(ext) for ext in file_extensions)]
                if not matched:
                    continue
                file_changes = matched

            self.commits.append(GitCommit(
                hash=commit.hexsha,
                message=commit.message.strip(),
                author=f"{author_name} <{commit.author.email}>",
                date=commit.committed_datetime
            ))
            self.file_changes.extend(file_changes)

        print(f"Found {len(self.commits)} commits, {len(self.file_changes)} changes")
        return self.commits

    def get_file_change_count(self):
        """
        Count how many times each file has been changed across all commits.

        Returns:
            dict: A dictionary where keys are file paths (str) and values are the number of changes (int)
        """
        file_counts = {}
        if not self.file_changes:
            return None
        for file_change in self.file_changes:
            file_counts[file_change.file_path] = file_counts.get(file_change.file_path, 0) + 1
        return file_counts

    # Add a generate_commit_summary method that returns a dictionary with repository statistics
    # The method should include: total_commits, unique_authors, most_active_author, most_changed_file, and date_range
    def generate_commit_summary(self):
        if not self.commits:
            return None
        total_commits = len(self.commits)
        author_counts = Counter(commit.author for commit in self.commits)
        most_active_author = author_counts.most_common(1)[0][0]
        file_counts = self.get_file_change_count()
        most_changed_file = max(file_counts, key=file_counts.get) if file_counts else None
        dates = [c.date for c in self.commits]
        date_range = f"{min(dates).strftime('%d-%m-%Y')} to {max(dates).strftime('%d-%m-%Y')}"

        return {
            "total_commits": total_commits,
            "unique_authors": len(author_counts),
            "most_active_author": most_active_author,
            "most_changed_file": most_changed_file,
            "date_range": date_range
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract and analyze git history")
    parser.add_argument("repo_path", help="Path to the git repository")
    parser.add_argument("--max-commits", type=int, default=10, help="Max number of commits to extract (default: 10)")
    parser.add_argument("--author", help="Filter commits by author name")
    parser.add_argument("--extensions", nargs="+", help="Filter by file extensions e.g. .py .js")
    args = parser.parse_args()

    extractor = GitHistoryExtractor()
    repo_path = args.repo_path

    if not os.path.exists(os.path.join(repo_path, ".git")):
        print("Not a git repository.")
        return

    try:
        commits = extractor.extract_commits(repo_path, max_commits=args.max_commits, author_filter=args.author, file_extensions=args.extensions)

        print("\nCommits:")
        for i, commit in enumerate(commits):
            print(f"{i+1}. {commit.hash[:8]} - {commit.message[:50]}")
            print(f"   Author: {commit.author}")
            print(f"   Date: {commit.date}")
            print()

        if not extractor.commits:
            print("No commits found.")
            return

        result = extractor.get_file_change_count()
        if result:
            print("File change counts (most frequent first):")
            for file_change, count in sorted(result.items(), key=lambda x: x[1], reverse=True):
                label = "change" if count == 1 else "changes"
                print(f"{file_change}: {count} {label}")

        print()
        commit_summary = extractor.generate_commit_summary()
        if commit_summary:
            print("Commit Summary:")
            print(f"Total Commits: {commit_summary['total_commits']}")
            print(f"Unique Authors: {commit_summary['unique_authors']}")
            print(f"Most Active Author: {commit_summary['most_active_author']}")
            print(f"Most Changed File: {commit_summary['most_changed_file']}")
            print(f"Date Range: {commit_summary['date_range']}")

    except (GitCommandError, InvalidGitRepositoryError) as e:
        print(f"Error extracting git history: {e}")


if __name__ == "__main__":
    main()