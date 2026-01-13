"""Add course_data_json and related fields to levels table."""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "app.db"


def migrate():
    """Add course_data_json, last_md_sync, last_json_edit, edit_mode columns to levels table."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(levels)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add course_data_json column
        if 'course_data_json' not in columns:
            print("Adding course_data_json column to levels table...")
            cursor.execute("ALTER TABLE levels ADD COLUMN course_data_json TEXT")
        
        # Add last_md_sync column
        if 'last_md_sync' not in columns:
            print("Adding last_md_sync column to levels table...")
            cursor.execute("ALTER TABLE levels ADD COLUMN last_md_sync DATETIME")
        
        # Add last_json_edit column
        if 'last_json_edit' not in columns:
            print("Adding last_json_edit column to levels table...")
            cursor.execute("ALTER TABLE levels ADD COLUMN last_json_edit DATETIME")
        
        # Add edit_mode column
        if 'edit_mode' not in columns:
            print("Adding edit_mode column to levels table...")
            cursor.execute("ALTER TABLE levels ADD COLUMN edit_mode VARCHAR(10)")
        
        conn.commit()
        print("Migration completed successfully!")
        print("Added columns: course_data_json, last_md_sync, last_json_edit, edit_mode")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()

