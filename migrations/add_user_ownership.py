import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from flask_migrate import Migrate, upgrade

def run_migration():
    with app.app_context():
        try:
            # Add user_id columns
            db.engine.execute('ALTER TABLE candidates ADD COLUMN user_id INTEGER REFERENCES users(id)')
            db.engine.execute('ALTER TABLE job_descriptions ADD COLUMN user_id INTEGER REFERENCES users(id)')
            
            # Set default user_id for existing records (if any)
            db.engine.execute('UPDATE candidates SET user_id = 1 WHERE user_id IS NULL')
            db.engine.execute('UPDATE job_descriptions SET user_id = 1 WHERE user_id IS NULL')
            
            # Make user_id columns NOT NULL
            db.engine.execute('ALTER TABLE candidates ALTER COLUMN user_id SET NOT NULL')
            db.engine.execute('ALTER TABLE job_descriptions ALTER COLUMN user_id SET NOT NULL')
            print("Migration completed successfully!")
        except Exception as e:
            print(f"Error during migration: {str(e)}")

if __name__ == '__main__':
    run_migration() 