"""
Security Key Management System
Handles automatic rotation of secret keys every 28 days
"""
import os
import secrets
import string
from datetime import datetime, timedelta
from database import db
from datetime import datetime

class SecurityKey(db.Model):
    """Model to track security keys and their rotation"""
    
    __tablename__ = 'security_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key_type = db.Column(db.String(50), nullable=False)  # 'SECRET_KEY', 'JWT_SECRET_KEY', etc.
    key_value = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f'<SecurityKey {self.key_type}>'
    
    @staticmethod
    def generate_secure_key(length=64):
        """Generate a cryptographically secure random key"""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        # Remove potentially problematic characters
        safe_alphabet = alphabet.replace('"', '').replace("'", '').replace('\\', '')
        return ''.join(secrets.choice(safe_alphabet) for _ in range(length))
    
    @staticmethod
    def create_or_rotate_key(key_type, force_rotation=False):
        """Create a new key or rotate existing one if needed"""
        try:
            current_key = SecurityKey.query.filter_by(
                key_type=key_type, 
                is_active=True
            ).first()
            
            now = datetime.utcnow()
            should_rotate = False
            
            if current_key:
                # Check if key needs rotation
                if force_rotation or now >= current_key.expires_at:
                    current_key.is_active = False
                    should_rotate = True
                else:
                    return current_key.key_value
            else:
                should_rotate = True
            
            if should_rotate:
                # Generate new key
                new_key_value = SecurityKey.generate_secure_key()
                expires_at = now + timedelta(days=28)  # 28 days from now
                
                new_key = SecurityKey(
                    key_type=key_type,
                    key_value=new_key_value,
                    expires_at=expires_at,
                    is_active=True
                )
                
                db.session.add(new_key)
                db.session.commit()
                
                # Update environment variable (for current session)
                os.environ[key_type] = new_key_value
                
                print(f"🔄 Rotated {key_type} - expires: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                return new_key_value
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error rotating key {key_type}: {str(e)}")
            # Fallback to generating a temporary key
            return SecurityKey.generate_secure_key()
    
    @staticmethod
    def get_active_key(key_type):
        """Get the current active key for a type"""
        current_key = SecurityKey.query.filter_by(
            key_type=key_type, 
            is_active=True
        ).first()
        
        if current_key:
            # Check if expired
            if datetime.utcnow() >= current_key.expires_at:
                return SecurityKey.create_or_rotate_key(key_type)
            return current_key.key_value
        else:
            return SecurityKey.create_or_rotate_key(key_type)
    
    @staticmethod
    def initialize_keys():
        """Initialize all required security keys"""
        key_types = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'CSRF_SECRET_KEY'
        ]
        
        for key_type in key_types:
            SecurityKey.create_or_rotate_key(key_type)
    
    @staticmethod
    def rotate_all_keys():
        """Force rotation of all keys (for scheduled tasks)"""
        key_types = [
            'SECRET_KEY',
            'JWT_SECRET_KEY', 
            'CSRF_SECRET_KEY'
        ]
        
        rotated_keys = []
        for key_type in key_types:
            new_key = SecurityKey.create_or_rotate_key(key_type, force_rotation=True)
            rotated_keys.append((key_type, new_key))
        
        return rotated_keys
    
    @staticmethod
    def check_key_expiry():
        """Check which keys are expiring soon (within 7 days)"""
        warning_date = datetime.utcnow() + timedelta(days=7)
        
        expiring_keys = SecurityKey.query.filter(
            SecurityKey.is_active == True,
            SecurityKey.expires_at <= warning_date
        ).all()
        
        return expiring_keys