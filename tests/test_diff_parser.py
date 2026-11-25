import pytest

from core.diff_parser import ADD, CONTEXT, REMOVE, parse_diff

MODIFIED = """\
diff --git a/app.py b/app.py
index 1111111..2222222 100644
--- a/app.py
+++ b/app.py
@@ -1,4 +1,5 @@ def main():
 import os
-print("old")
+print("new")
+print("extra")
 x = 1
 y = 2
@@ -20,2 +21,2 @@
-a = 1
+a = 2
 b = 3
"""


def test_empty_input():
    assert parse_diff("") == []
    assert parse_diff("   \n") == []


def test_modified_file_with_two_hunks():
    (f,) = parse_diff(MODIFIED)
    assert f.path == "app.py" and f.status == "modified"
    assert len(f.hunks) == 2
    assert f.additions == 3 and f.deletions == 2
    h = f.hunks[0]
    assert (h.old_start, h.old_count, h.new_start, h.new_count) == (1, 4, 1, 5)
    assert h.section == "def main():"


def test_line_numbers():
    (f,) = parse_diff(MODIFIED)
    lines = f.hunks[0].lines
    assert [l.type for l in lines] == [CONTEXT, REMOVE, ADD, ADD, CONTEXT, CONTEXT]
    assert (lines[0].old_lineno, lines[0].new_lineno) == (1, 1)
    assert (lines[1].old_lineno, lines[1].new_lineno) == (2, None)
    assert (lines[2].old_lineno, lines[2].new_lineno) == (None, 2)
    assert (lines[3].old_lineno, lines[3].new_lineno) == (None, 3)
    assert (lines[4].old_lineno, lines[4].new_lineno) == (3, 4)
    assert f.added_lines()[:2] == [(2, 'print("new")'), (3, 'print("extra")')]


def test_hunks_only_input_like_gitpython():
    text = "@@ -1,2 +1,2 @@\n-a\n+b\n c\n"
    (f,) = parse_diff(text)
    assert f.path is None and f.additions == 1 and f.deletions == 1


def test_new_file():
    text = (
        "diff --git a/n.py b/n.py\nnew file mode 100644\nindex 000..111\n"
        "--- /dev/null\n+++ b/n.py\n@@ -0,0 +1,2 @@\n+one\n+two\n"
    )
    (f,) = parse_diff(text)
    assert f.status == "added" and f.old_path is None and f.path == "n.py"
    assert f.additions == 2


def test_deleted_file():
    text = (
        "diff --git a/d.py b/d.py\ndeleted file mode 100644\nindex 111..000\n"
        "--- a/d.py\n+++ /dev/null\n@@ -1,2 +0,0 @@\n-one\n-two\n"
    )
    (f,) = parse_diff(text)
    assert f.status == "deleted" and f.new_path is None and f.path == "d.py"
    assert f.deletions == 2


def test_rename_without_changes():
    text = (
        "diff --git a/old.py b/new.py\nsimilarity index 100%\n"
        "rename from old.py\nrename to new.py\n"
    )
    (f,) = parse_diff(text)
    assert f.status == "renamed" and (f.old_path, f.new_path) == ("old.py", "new.py")
    assert f.hunks == []


def test_binary_file():
    text = "diff --git a/i.png b/i.png\nindex 1..2\nBinary files a/i.png and b/i.png differ\n"
    (f,) = parse_diff(text)
    assert f.is_binary and f.hunks == []


def test_multiple_files():
    text = MODIFIED + (
        "diff --git a/b.py b/b.py\n--- a/b.py\n+++ b/b.py\n@@ -1 +1 @@\n-x\n+y\n"
    )
    files = parse_diff(text)
    assert [f.path for f in files] == ["app.py", "b.py"]
    assert files[1].hunks[0].old_count == 1  # implicit count


def test_no_newline_marker_ignored():
    text = "@@ -1 +1 @@\n-a\n\\ No newline at end of file\n+b\n\\ No newline at end of file\n"
    (f,) = parse_diff(text)
    assert [l.content for l in f.hunks[0].lines] == ["a", "b"]


def test_removed_line_that_looks_like_header():
    text = "diff --git a/s.sql b/s.sql\n--- a/s.sql\n+++ b/s.sql\n@@ -1,2 +1,1 @@\n--- comment\n keep\n"
    (f,) = parse_diff(text)
    assert f.hunks[0].removed[0].content == "-- comment"
    assert f.path == "s.sql"


def test_plain_unified_diff_multiple_files():
    text = "--- a/x\n+++ b/x\n@@ -1 +1 @@\n-1\n+2\n--- a/y\n+++ b/y\n@@ -1 +1 @@\n-3\n+4\n"
    assert [f.path for f in parse_diff(text)] == ["x", "y"]


def test_malformed_hunk_header():
    with pytest.raises(ValueError):
        parse_diff("@@ nonsense @@\n+a\n")
