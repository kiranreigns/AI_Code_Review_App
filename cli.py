import argparse
import os
import sys
from pathlib import Path
from collections import Counter
from repository_scanner import RepositoryScanner
from git_extractor import GitHistoryExtractor
from git import Repo

try:
    from git.exc import InvalidGitRepositoryError, NoSuchPathError
except ImportError:
    class InvalidGitRepositoryError(Exception):
        pass

    class NoSuchPathError(Exception):
        pass


class CodebaseAnalyzer:
    def __init__(self):
        self.scanner = RepositoryScanner()
        self.git_extractor = GitHistoryExtractor()

    def analyze_repository(self, repo_path, output_format="simple"):
        print("Starting analysis...")

        # --- Path validation ---
        if not os.path.exists(repo_path):
            print(f"Error: path does not exist: {repo_path}")
            return False

        if not os.path.isdir(repo_path):
            print(f"Error: path is not a directory: {repo_path}")
            return False

        if not os.access(repo_path, os.R_OK):
            print(f"Error: no read permission for: {repo_path}")
            return False

        # --- File scanning ---
        try:
            files = self.scanner.scan_repository(repo_path)
        except PermissionError as e:
            print(f"Error scanning files (permission denied): {e}")
            return False
        except Exception as e:
            print(f"Error scanning files: {e}")
            return False

        # --- Git extraction ---
        try:
            commits = self.git_extractor.extract_commits(repo_path)
            file_changes = len(self.git_extractor.file_changes)
        except (InvalidGitRepositoryError, NoSuchPathError) as e:
            print(f"Warning: no git history available: {e}")
            commits = []
            file_changes = 0
        except Exception as e:
            print(f"Warning: git extraction failed: {e}")
            commits = []
            file_changes = 0

        # --- Derived stats ---
        total_lines = 0
        file_extensions = []
        for file in files:
            total_lines += len(file.content.splitlines())
            file_extensions.append(Path(file.file_path).suffix)

        avg_lines_per_file = total_lines // len(files) if files else 0
        counter = Counter(file_extensions)
        most_common_ext = counter.most_common(1)[0][0] if file_extensions else None

        languages = {}
        for file in files:
            languages[file.language] = languages.get(file.language, 0) + 1

        # --- Output ---
        print(f"\nResults:")
        print(f"Files: {len(files)}")
        print(f"Commits: {len(commits)}")
        if output_format == "detailed":
            print(f"File changes: {file_changes}")
            print(f"Languages: {languages}")
        print(f"Average lines per file: {avg_lines_per_file}")
        print(f"Most common extension: {most_common_ext}")

        return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', default='.', help='Repository path')
    parser.add_argument('--output-format', choices=['simple', 'detailed'], default='simple',
                         help='Output detail level')
    parser.add_argument('--scan-only', action='store_true',
                         help='Run only file scanning (skip git extraction)')
    args = parser.parse_args()

    analyzer = CodebaseAnalyzer()

    if args.scan_only:
        analyzer.scan_only_mode(args.repo)
        sys.exit(0)

    success = analyzer.analyze_repository(args.repo, args.output_format)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


'''
# Basic usage
python git_extractor.py ../chatbot

# With flags
python git_extractor.py ../chatbot --max-commits 20
python git_extractor.py ../chatbot --author Kiran
python git_extractor.py ../chatbot --extensions .py .js
python git_extractor.py ../chatbot --author Kiran --extensions .py --max-commits 5

# Help
python git_extractor.py --help
'''