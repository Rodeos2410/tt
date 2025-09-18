from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)


def init_db():
    # create tables if missing
    SQLModel.metadata.create_all(engine)
    # simple migration: add 'balance' column to user table if it doesn't exist
    try:
        with engine.begin() as conn:
            res = conn.execute(text("PRAGMA table_info('user')")).mappings().all()
            cols = [r['name'] for r in res]
            if 'balance' not in cols:
                conn.execute(text("ALTER TABLE user ADD COLUMN balance REAL DEFAULT 0.0"))
    except Exception:
        # best-effort migration; do not crash startup if it fails
        pass


def get_session():
    with Session(engine) as session:
        yield session
