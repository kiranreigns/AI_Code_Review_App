"""Parse unified diffs into structured objects.

Handles both full ``git diff`` output (with ``diff --git`` headers) and the
hunks-only text that GitPython returns per file (it starts at ``@@``).
"""

import re
from dataclasses import dataclass, field
from typing import Optional

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@ ?(.*)$")
GIT_HEADER_RE = re.compile(r"^diff --git a/(.*?) b/(.*)$")

ADD, REMOVE, CONTEXT = "add", "remove", "context"


@dataclass
class DiffLine:
    type: str  # ADD, REMOVE or CONTEXT
    content: str  # line text without the +/-/space prefix
    old_lineno: Optional[int] = None  # None for added lines
    new_lineno: Optional[int] = None  # None for removed lines


@dataclass
class Hunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    section: str = ""  # text after the second @@ (usually the enclosing function)
    lines: list[DiffLine] = field(default_factory=list)

    @property
    def added(self) -> list[DiffLine]:
        return [line for line in self.lines if line.type == ADD]

    @property
    def removed(self) -> list[DiffLine]:
        return [line for line in self.lines if line.type == REMOVE]


@dataclass
class FileDiff:
    old_path: Optional[str] = None  # None when the file is new
    new_path: Optional[str] = None  # None when the file was deleted
    status: str = "modified"  # added, deleted, modified or renamed
    is_binary: bool = False
    hunks: list[Hunk] = field(default_factory=list)

    @property
    def path(self) -> Optional[str]:
        return self.new_path or self.old_path

    @property
    def additions(self) -> int:
        return sum(len(h.added) for h in self.hunks)

    @property
    def deletions(self) -> int:
        return sum(len(h.removed) for h in self.hunks)

    def added_lines(self) -> list[tuple[int, str]]:
        """(line number in the new file, content) for every added line."""
        return [(line.new_lineno, line.content) for h in self.hunks for line in h.added]


def parse_diff(text: str) -> list[FileDiff]:
    """
    Parse unified diff text into a list of FileDiff objects.

    Accepts multi-file ``git diff`` output, a single-file diff, or hunks-only
    text. Empty input returns an empty list. Raises ValueError on a malformed
    hunk header.
    """
    if not text or not text.strip():
        return []

    files: list[FileDiff] = []
    current: Optional[FileDiff] = None
    hunk: Optional[Hunk] = None
    old_remaining = new_remaining = 0
    old_no = new_no = 0

    for raw in text.splitlines():
        # Inside a hunk body the counts decide what a line is. This keeps a
        # removed line like "-- comment" from being read as a "---" header.
        if hunk is not None and (old_remaining > 0 or new_remaining > 0):
            if raw.startswith("+"):
                hunk.lines.append(DiffLine(ADD, raw[1:], None, new_no))
                new_no += 1
                new_remaining -= 1
                continue
            if raw.startswith("-"):
                hunk.lines.append(DiffLine(REMOVE, raw[1:], old_no, None))
                old_no += 1
                old_remaining -= 1
                continue
            if raw.startswith(" ") or raw == "":
                hunk.lines.append(DiffLine(CONTEXT, raw[1:], old_no, new_no))
                old_no += 1
                new_no += 1
                old_remaining -= 1
                new_remaining -= 1
                continue
        if raw.startswith("\\"):  # "\ No newline at end of file"
            continue

        match = GIT_HEADER_RE.match(raw)
        if match:
            current = FileDiff(old_path=match.group(1), new_path=match.group(2))
            files.append(current)
            hunk = None
            continue

        if raw.startswith("@@"):
            match = HUNK_RE.match(raw)
            if not match:
                raise ValueError(f"Malformed hunk header: {raw!r}")
            if current is None:  # hunks-only input
                current = FileDiff()
                files.append(current)
            old_start, old_count, new_start, new_count, section = match.groups()
            hunk = Hunk(
                old_start=int(old_start),
                old_count=1 if old_count is None else int(old_count),
                new_start=int(new_start),
                new_count=1 if new_count is None else int(new_count),
                section=section.strip(),
            )
            current.hunks.append(hunk)
            old_no, new_no = hunk.old_start, hunk.new_start
            old_remaining, new_remaining = hunk.old_count, hunk.new_count
            continue

        # Plain unified diffs (no "diff --git" line) start a new file at "---".
        if raw.startswith("--- ") and (current is None or current.hunks):
            current = FileDiff()
            files.append(current)
            hunk = None
        if current is not None:
            _apply_metadata(current, raw)

    return files


def _apply_metadata(file_diff: FileDiff, line: str) -> None:
    if line.startswith("new file mode"):
        file_diff.status = "added"
        file_diff.old_path = None
    elif line.startswith("deleted file mode"):
        file_diff.status = "deleted"
        file_diff.new_path = None
    elif line.startswith("rename from "):
        file_diff.status = "renamed"
        file_diff.old_path = line[len("rename from "):]
    elif line.startswith("rename to "):
        file_diff.status = "renamed"
        file_diff.new_path = line[len("rename to "):]
    elif line.startswith("Binary files") or line.startswith("GIT binary patch"):
        file_diff.is_binary = True
    elif line.startswith("--- "):
        path = _strip_prefix(line[4:], "a/")
        if path is None:
            file_diff.status = "added"
        file_diff.old_path = path
    elif line.startswith("+++ "):
        path = _strip_prefix(line[4:], "b/")
        if path is None:
            file_diff.status = "deleted"
        file_diff.new_path = path


def _strip_prefix(path: str, prefix: str) -> Optional[str]:
    path = path.split("\t")[0].strip()
    if path == "/dev/null":
        return None
    return path[len(prefix):] if path.startswith(prefix) else path
