from scanner import RepositoryScanner

def test_language_detection():
    scanner = RepositoryScanner()

    test_files = [
        "app.py",
        "index.js",
        "Main.java",
        "utils.cpp",
        "component.ts",
        "index.html",
        "styles.css",
        "functions.php",
        "server.rb",
        "main.go",
        "unknown.xyz"
    ]

    print("Testing language detection:")
    print("--------------------------")

    for file in test_files:
        language = scanner.detect_language(file)
        print(f"{file}: {language}")

    print("--------------------------")

    # Check if all expected languages are detected correctly
    expected_results = {
        "app.py": "Python",
        "index.js": "JavaScript",
        "Main.java": "Java",
        "utils.cpp": "C++",
        "component.ts": "TypeScript",
        "index.html": "HTML",
        "styles.css": "CSS",
        "functions.php": "PHP",
        "server.rb": "Ruby",
        "main.go": "Go",
        "unknown.xyz": "Unknown"
    }

    all_correct = True
    for file, expected in expected_results.items():
        actual = scanner.detect_language(file)
        if actual != expected:
            print(f"❌ Error: {file} detected as {actual}, expected {expected}")
            all_correct = False

    if all_correct:
        print("✅ All languages detected correctly!")
    else:
        print("❌ Some languages were not detected correctly.")

if __name__ == "__main__":
    test_language_detection()
