"""
Script to create an initial admin user for the Musa LMS system.
Run this after migrating the database.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.models import AuthUser, AuthUserRole
from app.core.security import get_password_hash


def create_admin_user():
    """Create an admin user"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(AuthUser).filter(
            AuthUser.role == AuthUserRole.ADMIN
        ).first()
        
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.email}")
            return
        
        # Get admin details
        print("Creating Admin User")
        print("-" * 50)
        email = input("Enter admin email: ").strip()
        password = input("Enter admin password: ").strip()
        full_name = input("Enter admin full name: ").strip()
        
        # Validate inputs
        if not email or not password or not full_name:
            print("Error: All fields are required!")
            return
        
        # Check if email already exists
        existing_user = db.query(AuthUser).filter(AuthUser.email == email).first()
        if existing_user:
            print(f"Error: User with email {email} already exists!")
            return
        
        # Create admin user
        admin = AuthUser(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role=AuthUserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("\n" + "=" * 50)
        print("✅ Admin user created successfully!")
        print("=" * 50)
        print(f"Email: {admin.email}")
        print(f"Name: {admin.full_name}")
        print(f"Role: {admin.role.value}")
        print(f"ID: {admin.id}")
        print("\nYou can now login with these credentials.")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


def create_sample_users():
    """Create sample users for testing"""
    db = SessionLocal()
    
    try:
        print("\nCreating Sample Users for Testing")
        print("-" * 50)
        
        # Sample tutor
        tutor = AuthUser(
            email="tutor@example.com",
            hashed_password=get_password_hash("tutor123"),
            full_name="John Tutor",
            role=AuthUserRole.TUTOR,
            is_active=True
        )
        db.add(tutor)
        
        # Sample students
        student1 = AuthUser(
            email="student1@example.com",
            hashed_password=get_password_hash("student123"),
            full_name="Alice Student",
            role=AuthUserRole.STUDENT,
            is_active=True
        )
        db.add(student1)
        
        student2 = AuthUser(
            email="student2@example.com",
            hashed_password=get_password_hash("student123"),
            full_name="Bob Student",
            role=AuthUserRole.STUDENT,
            is_active=True
        )
        db.add(student2)
        
        db.commit()
        
        print("✅ Sample users created:")
        print("  - Tutor: tutor@example.com (password: tutor123)")
        print("  - Student 1: student1@example.com (password: student123)")
        print("  - Student 2: student2@example.com (password: student123)")
        
    except Exception as e:
        print(f"Error creating sample users: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Musa LMS - User Creation Script")
    print("=" * 50)
    
    create_admin_user()
    
    # Ask if user wants to create sample users
    create_samples = input("\nDo you want to create sample users for testing? (y/n): ").strip().lower()
    if create_samples == 'y':
        create_sample_users()
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)
