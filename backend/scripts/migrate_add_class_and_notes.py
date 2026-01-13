"""Add class_name and notes columns to users table."""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "app.db"


def migrate():
    """Add class_name and notes columns to users table."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add class_name column if not exists
        if 'class_name' not in columns:
            print("Adding class_name column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN class_name VARCHAR(128) NULL")
        else:
            print("class_name column already exists")
        
        # Add notes column if not exists
        if 'notes' not in columns:
            print("Adding notes column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN notes VARCHAR(512) NULL")
        else:
            print("notes column already exists")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()























