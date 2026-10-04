import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://volunteer:volunteer123@localhost:5432/volunteerconnect"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Base.metadata.create_all only creates tables that don't exist yet - it never
# adds new columns to a table that is already there. Since this project has no
# migration tool (Alembic, etc.), new columns added to the models below are
# applied here with plain, idempotent ALTER TABLE statements. This only runs
# against Postgres (production/local Postgres); a fresh SQLite test database
# already gets the new columns from create_all, so it's skipped there.
def run_light_migrations():
    if engine.dialect.name != "postgresql":
        return

    statements = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_document TEXT",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_status VARCHAR(30) DEFAULT 'unverified'",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP",
        "ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS status VARCHAR(30) DEFAULT 'active'",
        "ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS donation_link VARCHAR(500)",
    ]

    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))
