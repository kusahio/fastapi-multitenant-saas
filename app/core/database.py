import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase # declarative_base
from core.settings import settings
from urllib.parse import quote_plus

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
  DATABASE_URL = f'postgresql://{settings.db_user}:{quote_plus(settings.db_password)}@{settings.db_host}:{settings.db_port}/{settings.db_name}'

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()
class Base(DeclarativeBase):
  pass

def get_db():
  db = SessionLocal()

  try:
    yield db
  finally:
    db.close()