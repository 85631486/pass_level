"""Add role column to users table."""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "app.db"


def migrate():
    """Add role column to users table."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check if role column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'role' in columns:
            print("Role column already exists")
            return
        
        # Add role column with default value 'student'
        print("Adding role column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(32) DEFAULT 'student' NOT NULL")
        
        # Update existing users to have 'student' role
        cursor.execute("UPDATE users SET role = 'student' WHERE role IS NULL")
        
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























