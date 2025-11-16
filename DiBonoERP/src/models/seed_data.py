"""
DiBono ERP - Database Seeding
Initial data population for admin and employee accounts only
All other data (inventory, menu items, suppliers) should be added through the UI
"""

from datetime import datetime

from utils.passlib_compat import ensure_bcrypt_about

ensure_bcrypt_about()
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from models.database import User, get_session, init_db


def seed_database():
    """Seed database with initial user accounts only"""
    session = get_session()
    
    try:
        # Check if already seeded
        if session.query(User).filter_by(username='admin').first():
            print("✓ Database already seeded")
            return
        
        print("Seeding database with user accounts...")
        
        # Create Admin Account
        admin = User(
            username='admin',
            password_hash=bcrypt.hash('CatchTheWave!'),
            full_name='Administrator',
            role='admin',
            salary=0,
            shift='Any'
        )
        
        # Create Employee Accounts
        employee1 = User(
            username='ahmed',
            password_hash=bcrypt.hash('123456'),
            full_name='Ahmed Hassan',
            role='employee',
            salary=500000,  # 500 LYD in fils
            shift='Morning 8AM-4PM'
        )
        
        employee2 = User(
            username='fatima',
            password_hash=bcrypt.hash('123456'),
            full_name='Fatima Ali',
            role='employee',
            salary=500000,
            shift='Evening 4PM-12AM'
        )
        
        session.add_all([admin, employee1, employee2])
        session.commit()
        
        print("✓ Database seeded successfully!")
        print("\n📋 User Accounts Created:")
        print("  👤 Admin account: admin / CatchTheWave!")
        print("  👤 Employee 1: ahmed / 123456")
        print("  👤 Employee 2: fatima / 123456")
        print("\n📝 Note: All inventory, menu items, and other data should be added through the application UI")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == '__main__':
    init_db()
    seed_database()
