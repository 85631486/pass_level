"""Add student_id column to users table."""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "app.db"


def migrate():
    """Add student_id column to users table."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check if student_id column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'student_id' in columns:
            print("student_id column already exists")
            return
        
        # Add student_id column
        print("Adding student_id column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN student_id VARCHAR(64) NULL")
        
        # Create index for student_id
        print("Creating index for student_id...")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_student_id ON users(student_id)")
        
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























