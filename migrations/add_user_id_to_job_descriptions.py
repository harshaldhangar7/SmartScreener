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

def check_if_column_exists():
    with app.app_context():
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*)
                FROM information_schema.columns 
                WHERE table_name = 'job_descriptions'
                AND column_name = 'user_id'
            """))
            return result.scalar() > 0

def upgrade():
    with app.app_context():
        try:
            # Check if column already exists
            if not check_if_column_exists():
                # Add user_id column to job_descriptions table
                with db.engine.connect() as conn:
                    # Drop foreign key if it exists
                    try:
                        conn.execute(text('ALTER TABLE job_descriptions DROP FOREIGN KEY fk_user_id'))
                    except:
                        pass
                    
                    # Add the column and foreign key
                    conn.execute(text('ALTER TABLE job_descriptions ADD COLUMN fk_user_id INTEGER'))
                    conn.execute(text('ALTER TABLE job_descriptions ADD CONSTRAINT fk_user_id FOREIGN KEY (fk_user_id) REFERENCES users(id)'))
                    conn.commit()
                print("Column user_id added successfully!")
            else:
                print("Column user_id already exists!")
        except Exception as e:
            print(f"Error during migration: {str(e)}")
            raise

if __name__ == '__main__':
    upgrade() 