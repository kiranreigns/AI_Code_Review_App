import os
import tempfile
import unittest
from datetime import datetime
from repository_scanner import RepositoryScanner, CodeFile

class TestRepositoryScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = RepositoryScanner()
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

        # Create some test files
        self.create_test_file("test.py", "print('Hello, world!')")
        self.create_test_file("test.js", "console.log('Hello, world!');")
        self.create_test_file("unknown.txt", "This is a text file")

        # Create an excluded directory with a file
        os.mkdir(os.path.join(self.test_dir, "node_modules"))
        self.create_test_file("node_modules/package.js", "// This should be excluded")

    def create_test_file(self, filename, content):
        path = os.path.join(self.test_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def test_language_detection(self):
        self.assertEqual(self.scanner.detect_language("test.py"), "Python")
        self.assertEqual(self.scanner.detect_language("test.js"), "JavaScript")
        self.assertEqual(self.scanner.detect_language("test.unknown"), "Unknown")

    def test_directory_exclusion(self):
        files = self.scanner.scan_repository(self.test_dir)

        # Check that files from excluded directories are not included
        excluded_files = [f for f in files if "node_modules" in f.file_path]
        self.assertEqual(len(excluded_files), 0, "Files from excluded directories should not be included")

    def test_multiple_scans(self):
        # First scan
        files1 = self.scanner.scan_repository(self.test_dir)

        # Create a new file
        self.create_test_file("new_file.py", "# New file")

        # Second scan
        files2 = self.scanner.scan_repository(self.test_dir)

        # The second scan should have one more file than the first
        self.assertEqual(len(files2), len(files1) + 1,
                         "Multiple scans should not accumulate files")

    def test_relative_paths(self):
        files = self.scanner.scan_repository(self.test_dir)

        # Check that paths are relative
        for file in files:
            self.assertFalse(os.path.isabs(file.file_path),
                            f"Path should be relative: {file.file_path}")
            self.assertFalse(self.test_dir in file.file_path,
                            f"Path should not contain the base directory: {file.file_path}")

    def tearDown(self):
        # Clean up the temporary directory
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.test_dir)

if __name__ == "__main__":
    unittest.main()