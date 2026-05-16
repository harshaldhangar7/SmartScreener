from app import db
from sqlalchemy import text

def _column_exists(connection, table_name: str, column_name: str) -> bool:
    result = connection.execute(text(
        """
        SELECT COUNT(*)
        FROM information_schema.columns 
        WHERE table_schema = DATABASE()
          AND table_name = :table
          AND column_name = :column
        """
    ), {"table": table_name, "column": column_name})
    return bool(result.scalar())

def upgrade():
    with db.engine.connect() as connection:
        # Add embedding columns as TEXT to store base64-encoded vectors (portable across MySQL variants)
        if not _column_exists(connection, 'candidates', 'embedding'):
            connection.execute(text("""
                ALTER TABLE candidates 
                ADD COLUMN embedding TEXT NULL
            """))
        if not _column_exists(connection, 'job_descriptions', 'embedding'):
            connection.execute(text("""
                ALTER TABLE job_descriptions 
                ADD COLUMN embedding TEXT NULL
            """))
        connection.commit()

def downgrade():
    with db.engine.connect() as connection:
        if _column_exists(connection, 'candidates', 'embedding'):
            connection.execute(text("""
                ALTER TABLE candidates 
                DROP COLUMN embedding
            """))
        if _column_exists(connection, 'job_descriptions', 'embedding'):
            connection.execute(text("""
                ALTER TABLE job_descriptions 
                DROP COLUMN embedding
            """))
        connection.commit()

