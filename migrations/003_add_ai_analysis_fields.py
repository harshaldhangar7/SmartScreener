"""
Migration: Add AI analysis fields to candidates table
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Add AI analysis fields to the candidates table."""
    
    # Get database path from environment or use default
    db_path = os.environ.get("DATABASE_URL", "sqlite:///instance/smartscreener.db")
    if db_path.startswith("sqlite:///"):
        db_path = db_path[10:]  # Remove sqlite:/// prefix
    
    print(f"Running migration on database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(candidates)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations_needed = []
        
        if 'ai_analysis' not in columns:
            migrations_needed.append("ALTER TABLE candidates ADD COLUMN ai_analysis TEXT")
            
        if 'ai_summary' not in columns:
            migrations_needed.append("ALTER TABLE candidates ADD COLUMN ai_summary TEXT")
            
        if 'ai_quality_score' not in columns:
            migrations_needed.append("ALTER TABLE candidates ADD COLUMN ai_quality_score REAL DEFAULT 0")
            
        if 'ai_analysis_date' not in columns:
            migrations_needed.append("ALTER TABLE candidates ADD COLUMN ai_analysis_date DATETIME")
        
        if not migrations_needed:
            print("All AI analysis fields already exist. No migration needed.")
            return True
        
        # Execute migrations
        for migration in migrations_needed:
            print(f"Executing: {migration}")
            cursor.execute(migration)
        
        conn.commit()
        print(f"Successfully added {len(migrations_needed)} AI analysis fields to candidates table.")
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(candidates)")
        columns = [column[1] for column in cursor.fetchall()]
        
        required_fields = ['ai_analysis', 'ai_summary', 'ai_quality_score', 'ai_analysis_date']
        missing_fields = [field for field in required_fields if field not in columns]
        
        if missing_fields:
            print(f"Warning: Some fields are still missing: {missing_fields}")
            return False
        else:
            print("Migration completed successfully. All AI analysis fields are present.")
            return True
            
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        exit(1)