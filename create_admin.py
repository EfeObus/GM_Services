#!/usr/bin/env python3
"""
Create admin user with hardcoded credentials:
Email: admin@gmservices.ng
Password: admin123
"""
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from app import create_app
from database import db
from models.user import User
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Create admin user with hardcoded credentials"""
    
    app = create_app()
    
    with app.app_context():
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='admin@gmservices.ng').first()
        
        if admin_user:
            print("❌ Admin user already exists!")
            print(f"   Email: {admin_user.email}")
            print(f"   Role: {admin_user.role}")
            return
        
        # Create admin user
        admin = User(
            first_name='Admin',
            last_name='User',
            email='admin@gmservices.ng',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            is_active=True,
            is_verified=True
        )
        
        try:
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Admin user created successfully!")
            print("   Email: admin@gmservices.ng")
            print("   Password: admin123")
            print("   Role: admin")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating admin user: {str(e)}")

if __name__ == '__main__':
    create_admin_user()
