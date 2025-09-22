"""
User Model
Handles customers, staff, and admin users with role-based access
"""
from database import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """User model for customers, staff, and admin"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Address Information
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    
    # User Status and Role
    role = db.Column(db.String(20), default='customer', nullable=False)  # customer, staff, admin
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    password_change_required = db.Column(db.Boolean, default=False, nullable=False)  # For first-time staff login
    
    # Staff-specific fields
    department = db.Column(db.String(100))  # For staff members
    employee_id = db.Column(db.String(50))  # For staff members
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Profile Information
    profile_image = db.Column(db.String(255))
    bio = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    
    # OAuth Information
    google_id = db.Column(db.String(100))
    apple_id = db.Column(db.String(100))
    
    # Relationships
    # Specify foreign key explicitly for loan applications as applicant
    loan_applications = db.relationship('LoanApplication', 
                                      foreign_keys='LoanApplication.user_id',
                                      backref='applicant', lazy='dynamic')
    # The assigned_loans relationship is already defined in LoanApplication model
    chat_messages = db.relationship('ChatMessage', backref='sender', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}"
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return user ID for Flask-Login"""
        return str(self.id)
    
    def is_customer(self):
        """Check if user is a customer"""
        return self.role == 'customer'
    
    def is_staff(self):
        """Check if user is staff"""
        return self.role == 'staff'
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def can_access_admin(self):
        """Check if user can access admin features"""
        return self.role == 'admin'
    
    def can_access_staff(self):
        """Check if user can access staff features"""
        return self.role in ['staff', 'admin']
    
    def get_pending_requests_count(self):
        """Get count of pending service requests (for staff)"""
        if self.is_staff() or self.is_admin():
            return self.assigned_requests.filter_by(status='pending').count()
        return 0
    
    def get_completed_requests_count(self):
        """Get count of completed service requests (for staff)"""
        if self.is_staff() or self.is_admin():
            return self.assigned_requests.filter_by(status='completed').count()
        return 0
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'department': self.department,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @staticmethod
    def create_admin_user(email, password, first_name="Admin", last_name="User"):
        """Create admin user (for initial setup)"""
        admin = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=generate_password_hash(password),
            role='admin',
            is_active=True,
            is_verified=True
        )
        return admin