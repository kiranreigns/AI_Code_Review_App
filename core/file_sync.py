from datetime import datetime

from core.scanner import RepositoryScanner
from db.database import get_session
from db.models import CodeFile


def sync_repository_files(repo_path, session):
  """
   Synchronize files from the repository with the database.

    This function:
    1. Scans the repository for current files
    2. Updates existing files in the database if their content has changed
    3. Adds new files that don't exist in the database
    4. Optionally handles files that have been deleted from the repository

    Args:
        repo_path: Path to the repository
        session: SQLAlchemy database session

    Returns:
        dict: Statistics about files added, updated, and deleted
  """

  stats = {
    'added': 0,
    'updated': 0,
    'deleted': 0
  }

  scanner = RepositoryScanner()
  current_files = scanner.scan_repository(repo_path)

  # Query all existing files, keyed by path for O(1) lookup
  existing_files = session.query(CodeFile).all()
  existing_by_path = {f.file_path: f for f in existing_files}

  # Track which paths we've seen in this scan
  processed_paths = set()

  for file_data in current_files:
    processed_paths.add(file_data.file_path)

    existing_path = existing_by_path.get(file_data.file_path)
    # File exists — check if content actually changed
    if existing_path:
      if existing_path.content != file_data.content:
        existing_path.content = file_data.content
        existing_path.language = file_data.language
        existing_path.last_updated = datetime.now()
        stats['updated'] += 1
    else:
      # New file - create a record
      new_file = CodeFile(
        file_path = file_data.file_path,
        content = file_data.content,
        language = file_data.language,
        last_updated = file_data.last_updated
      )

      session.add(new_file)
      stats['added'] += 1

  # Anything in the DB but not in this scan has been deleted from the repo
  deleted_paths = set(existing_by_path.keys()) - processed_paths
  for path in deleted_paths:
    session.delete(existing_by_path[path])
    stats['deleted'] += 1

  session.commit()
  return stats

if __name__ == '__main__':
  from db.db_setup import setup_database
  setup_database()
  session = get_session()
  try:
    stats = sync_repository_files('.', session)
    print(f"Files added: {stats['added']}")
    print(f"Files updated: {stats['updated']}")
    print(f"Files deleted: {stats['deleted']}")
    print(f"Total files processed: {stats['added'] + stats['updated'] + stats['deleted']}")
  finally:
    session.close()
