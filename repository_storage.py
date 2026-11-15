from db.models import CodeFile
from db.database import get_session, init_db
from repository_scanner import RepositoryScanner

def store_code_files(files, session):
  """
  Store a list of code files in the database.

    Args:
        files: List of file objects with file_path, content, language, and last_updated attributes
        session: SQLAlchemy database session

    Returns:
        int: Number of files stored in the database
  """

  # 1. Iterate through the files
  for file in files:
      # 2. Check if file already exists by file_path
      existing = session.query(CodeFile).filter_by(file_path=file.file_path).first()
      if existing:
          # 3. Update existing file content and timestamp
          existing.content = file.content
          existing.last_updated = file.last_updated
      else:
          # 4. Create a new CodeFile object
          db_file = CodeFile(
              file_path=file.file_path,
              content=file.content,
              language=file.language,
              last_updated=file.last_updated
          )
          # 5. Add the file to the session
          session.add(db_file)
  # 6. Commit the session to save the files
  session.commit()

  return len(files)
