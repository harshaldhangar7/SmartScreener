from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

def check_if_column_exists():
    with app.app_context():
        with db.engine.connect() as conn:
            # For SQLite, use PRAGMA table_info
            result = conn.execute(text("PRAGMA table_info(job_descriptions)"))
            columns = result.fetchall()
            return any(col[1] == 'company_name' for col in columns)

def upgrade():
    with app.app_context():
        try:
            # Check if column already exists
            if not check_if_column_exists():
                # Add company_name column to job_descriptions table
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE job_descriptions ADD COLUMN company_name VARCHAR(100)'))
                    conn.commit()
                print("Column company_name added successfully!")
            else:
                print("Column company_name already exists!")
        except Exception as e:
            print(f"Error during migration: {str(e)}")
            raise

if __name__ == '__main__':
    upgrade()