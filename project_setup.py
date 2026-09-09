from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

@dataclass
class CodeFile:
    file_path: str
    content: str
    language: str
    last_updated: datetime
    file_size: int

# TODO: Create a list of at least 5 CodeFile instances with different languages
# Example: Python, JavaScript, Java, CSS, etc.
code_files = code_files = [
    # Add at least 5 CodeFile instances here
    CodeFile(
        file_path="src/main.py",
        content="print('Hello, world!')",
        language="Python",
        last_updated=datetime.now(),
        file_size=25
    ),

    CodeFile(
        file_path="src/app.js",
        content="console.log('Hello, world!');",
        language="JavaScript",
        last_updated=datetime.now(),
        file_size=30
    ),

    CodeFile(
        file_path="src/app.java",
        content='System.out.println("Hello, world!");',
        language="Java",
        last_updated=datetime.now(),
        file_size=15
    ),

    CodeFile(
        file_path="src/main.go",
        content='package main\nimport "fmt"\nfunc main() {\n    fmt.Println("Hello, world!")\n}',
        language="Go",
        last_updated=datetime.now(),
        file_size=60
    ),

    CodeFile(
        file_path="src/styles.css",
        content='body { margin: 0; padding: 0; }',
        language="CSS",
        last_updated=datetime.now(),
        file_size=35
    )
]

# TODO: Create a dictionary to store the count of files per language
language_counts = {}

# TODO: Write a loop to count files by language
# The loop should iterate through code_files and update language_counts
for code_file in code_files:
    language = code_file.language
    language_counts[language] = language_counts.get(language, 0) + 1

# TODO: Display the counts in a readable format
# Print a summary showing how many files belong to each language
print("=" * 40)
print("Code Files Summary by Language")
print("=" * 40)
for language, count in language_counts.items():
    print(f"{language}: {count} file(s)")
print("=" * 40)
print(f"Total files: {len(code_files)}")
if __name__ == "__main__":
    # The code above will run when this file is executed directly
    pass