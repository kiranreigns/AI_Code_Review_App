import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

@dataclass
class CodeFile:
    file_path: str
    content: str
    language: str
    last_updated: datetime

class RepositoryScanner:
    def __init__(self):
        self.language_map = {
            '.py': 'Python', '.js': 'JavaScript', '.java': 'Java',
            '.cpp': 'C++', '.ts': 'TypeScript'
        }
        self.exclude_dirs = {'.git', 'node_modules', '__pycache__'}
        self.files = []

    def detect_language(self, file_path):
        # TODO: Extract the file extension (suffix) from the file_path, convert it to lowercase,
        suffix = Path(file_path).suffix.lower()
        # and return the corresponding language from language_map or 'Unknown' if not found
        return self.language_map.get(suffix, 'Unknown')

    def scan_repository(self, repo_path):
        print(f"Scanning: {repo_path}")

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)

                if self.detect_language(file_path) == 'Unknown':
                    continue

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
                except Exception as e:
                    print(f"Error: {e}")

        print(f"Found {len(self.files)} files")
        return self.files


if __name__ == "__main__":
    scanner = RepositoryScanner()
    repo_path = "../chatbot"
    files = scanner.scan_repository(repo_path)
    print(f"Found {len(files)} code files in {repo_path}.")
    for code_file in files:
        print(f"{code_file.file_path}: {code_file.language}")