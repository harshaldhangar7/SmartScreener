from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from sqlalchemy import inspect
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
# Ensure DATABASE_URL is set
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is required")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True  # Enable SQL query logging

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define all models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)

class Candidate(db.Model):
    __tablename__ = 'candidates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    skills = db.Column(db.JSON)  # List of skills
    experience_years = db.Column(db.Float, default=0)
    education = db.Column(db.JSON)  # List of education objects
    experience_entries = db.Column(db.JSON)  # List of experience objects
    resume_filename = db.Column(db.String(255))
    parsed_date = db.Column(db.DateTime)

class JobDescription(db.Model):
    __tablename__ = 'job_descriptions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    required_skills = db.Column(db.JSON)  # List of required skills
    min_experience = db.Column(db.Float, default=0)
    required_education = db.Column(db.JSON)  # List of required education levels
    created_date = db.Column(db.DateTime)
    fk_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

def inspect_table(table_name):
    """Inspect a table's structure using SQLAlchemy's inspect."""
    inspector = inspect(db.engine)
    columns = inspector.get_columns(table_name)
    foreign_keys = inspector.get_foreign_keys(table_name)
    
    print(f"\n{table_name} Table Structure:")
    print("Column Name | Type | Nullable | Key")
    print("--------------------------------------------------")
    for column in columns:
        print(f"{column['name']} | {column['type']} | {'NO' if not column['nullable'] else 'YES'} | {'PRI' if column.get('primary_key') else ''}")
    
    if foreign_keys:
        print("\nForeign Keys:")
        for fk in foreign_keys:
            print(f"Column: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

def reset_database():
    try:
        with app.app_context():
            logger.info("Starting database reset...")
            
            # Drop all tables
            logger.info("Dropping all tables...")
            db.drop_all()
            print("Dropped all tables")
            
            # Create all tables
            logger.info("Creating all tables...")
            db.create_all()
            print("Created all tables")
            
            # Verify table structures
            logger.info("Verifying table structures...")
            inspect_table('users')
            inspect_table('candidates')
            inspect_table('job_descriptions')
            
            print("\nDatabase reset completed successfully!")
            
    except Exception as e:
        logger.error(f"Error during database reset: {str(e)}")
        raise

if __name__ == '__main__':
    reset_database() 