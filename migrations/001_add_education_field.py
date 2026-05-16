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
    # Add required_education column to job_descriptions table if missing
    with db.engine.connect() as connection:
        if not _column_exists(connection, 'job_descriptions', 'required_education'):
            connection.execute(text(
                """
                ALTER TABLE job_descriptions 
                ADD COLUMN required_education JSON DEFAULT ('[]')
                """
            ))
            connection.commit()

def downgrade():
    # Remove required_education column from job_descriptions table
    with db.engine.connect() as connection:
        if _column_exists(connection, 'job_descriptions', 'required_education'):
            connection.execute(text(
                """
                ALTER TABLE job_descriptions 
                DROP COLUMN required_education
                """
            ))
            connection.commit()