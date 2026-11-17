from datetime import datetime

from db.database import get_session, init_db
from db.models import CodeFile


def setup_database():
    """
    Initialize the database and populate it with initial test data.
    """
    # Initialize the database
    init_db()

    # Get a database session
    session = get_session()

    # Clear any existing data
    session.query(CodeFile).delete()
    session.commit()

    # Create initial test files
    initial_files = [
        CodeFile(
            file_path='main.py',
            content='print("Hello, World!")',  # This will be updated in the sync
            language='Python',
            last_updated=datetime(2023, 1, 1)
        ),
        CodeFile(
            file_path='utils.py',
            content='def add(a, b): return a + b',  # This will remain unchanged
            language='Python',
            last_updated=datetime(2023, 1, 1)
        ),
        CodeFile(
            file_path='deleted.py',  # This will be deleted in the sync
            content='# This file will be deleted',
            language='Python',
            last_updated=datetime(2023, 1, 1)
        )
    ]

    # Add files to the database
    for file in initial_files:
        session.add(file)

    # Commit changes
    session.commit()

    print("Database initialized with test data.")

if __name__ == "__main__":
    setup_database()