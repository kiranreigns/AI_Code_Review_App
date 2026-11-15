from core.scanner import RepositoryScanner
from db.database import get_session, init_db
from db.models import CodeFile, Commit
from git_extractor import GitHistoryExtractor


def populate_database(repo_path, session):
  """
    Populate the database with code files and commits from a repository.

    Args:
        repo_path: Path to the repository
        session: SQLAlchemy database session
  """
  scanner = RepositoryScanner()
  git_extractor = GitHistoryExtractor()

  # store files
  print("scanning repository for code files...")
  files = scanner.scan_repository(repo_path)
  for file in files:
    existing_file = session.query(CodeFile).filter_by(file_path=file.file_path).first()
    if existing_file:
      existing_file.content = file.content
      existing_file.last_updated = file.last_updated
    else:
      db_file = CodeFile(
        file_path=file.file_path,
        content=file.content,
        language=file.language,
        last_updated=file.last_updated
      )
      session.add(db_file)
  session.commit()

  print(f"Stored {len(files)} code files in the database.")

  # store commits
  print("extracting commit history")
  commits = git_extractor.extract_commits(repo_path)
  for commit in commits:
    existing_commit = session.query(Commit).filter_by(hash=commit.hash).first()
    if not existing_commit:
      session.add(Commit(
        hash=commit.hash,
        message=commit.message,
        author=commit.author,
        date=commit.date
      ))
  session.commit()


if __name__ == "__main__":
  init_db()
  session = get_session()
  populate_database('.', session)
