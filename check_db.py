from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import text

# Initialize Flask app
app = Flask(__name__)
# Ensure DATABASE_URL is set
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is required")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

def check_table_structure():
    with app.app_context():
        with db.engine.connect() as conn:
            # Get table structure
            result = conn.execute(text("""
                SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY
                FROM information_schema.columns 
                WHERE table_name = 'job_descriptions'
                ORDER BY ORDINAL_POSITION;
            """))
            print("\nTable Structure:")
            print("Column Name | Type | Nullable | Key")
            print("-" * 50)
            for row in result:
                print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")
            
            # Get foreign keys
            result = conn.execute(text("""
                SELECT
                    CONSTRAINT_NAME,
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_NAME = 'job_descriptions'
                AND REFERENCED_TABLE_NAME IS NOT NULL;
            """))
            print("\nForeign Keys:")
            print("Constraint | Column | Referenced Table | Referenced Column")
            print("-" * 70)
            for row in result:
                print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")

if __name__ == '__main__':
    check_table_structure() 