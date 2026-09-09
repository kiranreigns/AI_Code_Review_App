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



if __name__ == '__main__':
  # TODO: Create a CodeFile instance with a realistic file path, content, language, and datetime.now() for last_updated
  example_file = CodeFile(
      file_path="src/main.py",
      content="print('Hello, world!')",
      language="python",
      last_updated=datetime.now()
  )
  
  # TODO: Print the CodeFile instance
  print(example_file)
  
  # TODO: Create a GitCommit instance with a sample hash, commit message, author name, and datetime.now() for date
  commit = GitCommit(
      hash="a1b2c3d4",
      message="Initial commit",
      author="Jane Doe",
      date=datetime.now()
  )
  print(commit)
  
  # TODO: Print the GitCommit instance
  print(commit)
  
  # TODO: Create a FileChange instance with a file path, commit hash, and sample diff content
  change = FileChange(
      file_path="src/main.py",
      commit_hash="a1b2c3d4",
      diff_content="+ print('Hello, world!')"
  )   
  print(change)
  # TODO: Print the FileChange instance
  
  print("Project setup complete. Ready to build components!")