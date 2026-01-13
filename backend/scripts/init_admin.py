"""Initialize admin account and first teacher account."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import SessionLocal, engine, init_db
from app.models.user import User


def init_admin():
    """Initialize admin account."""
    # Initialize database
    init_db()
    
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.role == "admin").first()
        if admin:
            print(f"Admin account already exists: {admin.email or admin.phone}")
            return
        
        # Create admin account
        admin = User(
            email="admin@ggzj.edu",
            nickname="系统管理员",
            hashed_password=get_password_hash("admin123456"),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print("Admin account created successfully!")
        print(f"  Email: admin@ggzj.edu")
        print(f"  Password: admin123456")
        print("  Please change the password after first login!")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating admin: {e}")
        raise
    finally:
        db.close()


def create_teacher(email: str, phone: str, nickname: str, password: str):
    """Create a teacher account."""
    db = SessionLocal()
    try:
        # Check if teacher already exists
        if email:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                print(f"User with email {email} already exists")
                return
        
        if phone:
            existing = db.query(User).filter(User.phone == phone).first()
            if existing:
                print(f"User with phone {phone} already exists")
                return
        
        # Create teacher account
        teacher = User(
            email=email,
            phone=phone,
            nickname=nickname,
            hashed_password=get_password_hash(password),
            role="teacher",
            is_active=True,
        )
        db.add(teacher)
        db.commit()
        print(f"Teacher account created successfully!")
        print(f"  Email: {email or 'N/A'}")
        print(f"  Phone: {phone or 'N/A'}")
        print(f"  Nickname: {nickname}")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating teacher: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize admin and teacher accounts")
    parser.add_argument("--admin-only", action="store_true", help="Only create admin account")
    parser.add_argument("--teacher-email", type=str, help="Teacher email")
    parser.add_argument("--teacher-phone", type=str, help="Teacher phone")
    parser.add_argument("--teacher-nickname", type=str, help="Teacher nickname")
    parser.add_argument("--teacher-password", type=str, default="teacher123456", help="Teacher password")
    
    args = parser.parse_args()
    
    # Always create admin
    init_admin()
    
    # Create teacher if provided
    if not args.admin_only and args.teacher_nickname:
        if not args.teacher_email and not args.teacher_phone:
            print("Error: Teacher email or phone is required")
            sys.exit(1)
        create_teacher(
            email=args.teacher_email,
            phone=args.teacher_phone,
            nickname=args.teacher_nickname,
            password=args.teacher_password,
        )
    elif not args.admin_only:
        print("\nTo create a teacher account, use:")
        print("  python scripts/init_admin.py --teacher-email teacher@example.com --teacher-nickname 'Teacher Name'")























