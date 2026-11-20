# AI Code Review App

A code review assistant that scans a repository, extracts its git history, stores both in a database, and (in progress) uses an OpenAI model to review the code.

> **Status:** early development. The data pipeline (scan → git history → database) works. The AI review step and a unified CLI are not wired up yet.

## Features

- **Repository scanner**: walks a repo, reads source files (`.py`, `.js`, `.java`, `.cpp`, `.ts`) and detects their language. It skips `.git`, `node_modules`, `__pycache__` and `.venv`.
- **Git history extraction**: pulls recent commits (default 50) and per-file diffs with GitPython. You can filter by author or file extension.
- **Database storage**: SQLAlchemy models for files, commits and file/commit links. SQLite by default, and any SQLAlchemy URL works (for example Postgres via `psycopg2`).
- **File sync**: updates stored files when content changes, adds new files, and tracks deletions.
- **OpenAI client setup**: loads the API key from the environment and returns a client and model name.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (a `uv.lock` is used) or pip
- An OpenAI API key (only for the AI features)

## Setup

```bash
git clone <this-repo>
cd AI_Code_Review_App
uv sync            # or: pip install -e .
```

Create a `.env` file:

```env
OPENAI_API_KEY=sk-...
# Optional. Defaults to sqlite:///codebase.db
DATABASE_URL=sqlite:///codebase.db
```

## Usage

Run each module from the project root.

```bash
# Scan this repo, extract commits, and store everything in the database
python -m core.db_population

# Check the OpenAI client configuration
python -m services.openai_setup

# Seed the database with sample data (for testing file sync)
python -m db.db_setup
```

Note: `init_db()` drops and recreates all tables, so `core.db_population` resets existing data on each run.

## Project structure

```
.
├── core/
│   ├── scanner.py        # RepositoryScanner: finds and reads code files
│   ├── storage.py        # store_code_files: upsert scanned files
│   ├── file_sync.py      # sync_repository_files: add/update/delete sync
│   └── db_population.py  # populate_database: files + commits into the DB
├── db/
│   ├── models.py         # CodeFile, Commit, FileCommit
│   ├── database.py       # engine, sessions, init_db
│   └── db_setup.py       # sample test data
├── services/
│   └── openai_setup.py   # OpenAI client and model config
├── git_extractor.py      # GitHistoryExtractor
├── commit_file_linker.py # link commits to their file changes
├── project_setup.py      # standalone dataclass examples
├── cli.py                # CLI entry point (see known issues)
├── main.py               # placeholder entry point
└── test_scanner.py       # scanner test
```

## Data model

| Table          | Columns                                                |
| -------------- | ------------------------------------------------------ |
| `code_files`   | `id`, `file_path` (unique), `content`, `language`, `last_updated` |
| `commits`      | `id`, `hash` (unique), `message`, `author`, `date`     |
| `file_commits` | `id`, `file_id` → code_files, `commit_id` → commits, `diff_text` |

## Known issues and roadmap

- `cli.py` imports `repository_scanner`, which no longer exists. The scanner now lives at `core.scanner`, so the import needs updating.
- `commit_file_linker.link_commit_to_files` returns inside the loop, so it only checks the first change.
- `db_population` stores commits but doesn't yet populate `file_commits` with diffs.
- The model name in `services/openai_setup.py` is hard-coded. Check that it's valid for your account.
- Next steps: send diffs to the OpenAI model, generate review comments, and add a working CLI.
