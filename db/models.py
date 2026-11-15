from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CodeFile(Base):
  __tablename__ = 'code_files'
  id = Column(Integer, primary_key=True)
  file_path = Column(String, nullable=False, unique=True)
  content = Column(Text, nullable=False)
  language = Column(String)
  last_updated = Column(DateTime)


class Commit(Base):
  __tablename__ = 'commits'
  id = Column(Integer, primary_key=True)
  hash = Column(String, nullable=False, unique=True)
  message = Column(Text)
  author = Column(String)
  date = Column(DateTime)


class FileCommit(Base):
  __tablename__ = 'file_commits'
  id = Column(Integer, primary_key=True)
  file_id = Column(Integer, ForeignKey('code_files.id'))
  commit_id = Column(Integer, ForeignKey('commits.id'))
  diff_text = Column(Text)