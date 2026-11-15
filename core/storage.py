from db.models import CodeFile
from db.database import get_session, init_db
from core.scanner import RepositoryScanner


def store_code_files(files, session):
    """
    Store a list of code files in the database.

    Args:
        files: List of file objects with file_path, content, language, and last_updated attributes
        session: SQLAlchemy database session

    Returns:
        int: Number of files stored in the database
    """

    for file in files:
        existing = session.query(CodeFile).filter_by(file_path=file.file_path).first()
        if existing:
            existing.content = file.content
            existing.last_updated = file.last_updated
        else:
            db_file = CodeFile(
                file_path=file.file_path,
                content=file.content,
                language=file.language,
                last_updated=file.last_updated
            )
            session.add(db_file)
    session.commit()

    return len(files)
