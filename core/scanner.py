import os
from datetime import datetime
from pathlib import Path

from db.models import CodeFile


class RepositoryScanner:
    def __init__(self):
        self.language_map = {
            '.py': 'Python', '.js': 'JavaScript', '.java': 'Java',
            '.cpp': 'C++', '.ts': 'TypeScript'
        }
        self.exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv'}
        self.files = []

    def detect_language(self, file_path):
        suffix = Path(file_path).suffix.lower()
        return self.language_map.get(suffix, 'Unknown')

    def scan_repository(self, repo_path):
        self.files = []
        seen_paths = set()
        print(f"Scanning: {repo_path}")

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)

                if self.detect_language(file_path) == 'Unknown':
                    continue

                if relative_path in seen_paths:
                    continue
                seen_paths.add(relative_path)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    code_file = CodeFile(
                        file_path=relative_path,
                        content=content,
                        language=self.detect_language(file_path),
                        last_updated=datetime.now()
                    )
                    self.files.append(code_file)
                except (OSError, UnicodeDecodeError) as e:
                    print(f"Error: {e}")

        print(f"Found {len(self.files)} files")
        return self.files


if __name__ == "__main__":
    import sys
    scanner = RepositoryScanner()
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "../chatbot"
    files = scanner.scan_repository(repo_path)
    print(f"Found {len(files)} code files in {repo_path}.")
    for code_file in files:
        print(f"{code_file.file_path}: {code_file.language}")
