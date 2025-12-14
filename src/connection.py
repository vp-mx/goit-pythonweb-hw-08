from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from settings import settings


engine = create_engine(settings.database_url, echo=True)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """Database session dependency for FastAPI routes."""
    db = Session()
    try:
        yield db
    finally:
        db.close()
