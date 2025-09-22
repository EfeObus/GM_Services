"""
Activity Logging Models
Tracks user registration, staff onboarding, user activities, and system usage
"""
from database import db
from datetime import datetime
from sqlalchemy import Index

class ActivityLog(db.Model):
    """
    Comprehensive activity logging for all user actions
    """
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # User and activity information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for system activities
    performed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Who performed the action
    
    # Activity details
    activity_type = db.Column(db.String(50), nullable=False)  # registration, login, logout, staff_onboarding, etc.
    action = db.Column(db.String(100), nullable=False)  # specific action taken
    description = db.Column(db.Text)  # detailed description
    category = db.Column(db.String(50), nullable=False)  # auth, user_management, system, etc.
    
    # Request information
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.Text)
    request_method = db.Column(db.String(10))  # GET, POST, etc.
    request_url = db.Column(db.Text)
    
    # Additional context
    additional_data = db.Column(db.JSON)  # Additional context as JSON
    success = db.Column(db.Boolean, default=True)  # Whether action was successful
    error_message = db.Column(db.Text)  # Error details if failed
    
    # Timing
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    duration_ms = db.Column(db.Integer)  # How long the action took
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='activity_logs')
    performed_by = db.relationship('User', foreign_keys=[performed_by_id], backref='performed_activities')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_activity_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_activity_type_timestamp', 'activity_type', 'timestamp'),
        Index('idx_activity_category_timestamp', 'category', 'timestamp'),
        Index('idx_activity_performed_by', 'performed_by_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<ActivityLog {self.activity_type}: {self.action}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'performed_by_id': self.performed_by_id,
            'activity_type': self.activity_type,
            'action': self.action,
            'description': self.description,
            'category': self.category,
            'ip_address': self.ip_address,
            'success': self.success,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'additional_data': self.additional_data
        }

class UserRegistration(db.Model):
    """
    Track all user registrations with detailed information
    """
    __tablename__ = 'user_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Registration method
    registration_method = db.Column(db.String(50), nullable=False)  # email, google, apple
    registration_source = db.Column(db.String(100))  # web, mobile, api
    
    # Registration details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    referrer_url = db.Column(db.Text)
    
    # Verification status
    email_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)
    verification_date = db.Column(db.DateTime)
    
    # Timestamps
    registration_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    first_login_date = db.Column(db.DateTime)
    
    # OAuth details (if applicable)
    oauth_provider = db.Column(db.String(50))  # google, apple
    oauth_id = db.Column(db.String(100))
    
    # Additional metadata
    registration_data = db.Column(db.JSON)  # Additional registration context
    
    # Relationships
    user = db.relationship('User', backref='registration_record')
    
    def __repr__(self):
        return f'<UserRegistration {self.user_id}: {self.registration_method}>'

class StaffOnboarding(db.Model):
    """
    Track staff onboarding process and activities
    """
    __tablename__ = 'staff_onboardings'
    
    id = db.Column(db.Integer, primary_key=True)
    staff_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    onboarded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Onboarding details
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    employee_id = db.Column(db.String(50))
    
    # Onboarding status
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, cancelled
    onboarding_stage = db.Column(db.String(50))  # account_created, permissions_set, training_assigned, etc.
    
    # Dates
    onboarding_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completion_date = db.Column(db.DateTime)
    first_login_date = db.Column(db.DateTime)
    
    # Training and setup
    training_completed = db.Column(db.Boolean, default=False)
    permissions_assigned = db.Column(db.JSON)  # List of permissions/roles assigned
    
    # Notes and comments
    onboarding_notes = db.Column(db.Text)
    admin_comments = db.Column(db.Text)
    
    # Relationships
    staff_user = db.relationship('User', foreign_keys=[staff_user_id], backref='onboarding_record')
    onboarded_by = db.relationship('User', foreign_keys=[onboarded_by_id], backref='onboarded_staff')
    
    def __repr__(self):
        return f'<StaffOnboarding {self.staff_user_id}: {self.status}>'

class UsageStatistics(db.Model):
    """
    Daily/hourly usage statistics for monitoring system usage
    """
    __tablename__ = 'usage_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Time period
    date = db.Column(db.Date, nullable=False)
    hour = db.Column(db.Integer)  # 0-23, null for daily stats
    
    # User statistics
    active_users = db.Column(db.Integer, default=0)
    new_registrations = db.Column(db.Integer, default=0)
    total_logins = db.Column(db.Integer, default=0)
    unique_visitors = db.Column(db.Integer, default=0)
    
    # Activity statistics
    total_activities = db.Column(db.Integer, default=0)
    failed_logins = db.Column(db.Integer, default=0)
    service_requests = db.Column(db.Integer, default=0)
    
    # Staff statistics
    active_staff = db.Column(db.Integer, default=0)
    staff_actions = db.Column(db.Integer, default=0)
    
    # System performance
    avg_response_time_ms = db.Column(db.Float)
    error_count = db.Column(db.Integer, default=0)
    
    # Detailed metrics
    metrics_data = db.Column(db.JSON)  # Additional metrics as JSON
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_usage_date_hour', 'date', 'hour'),
        Index('idx_usage_date', 'date'),
    )
    
    def __repr__(self):
        period = f"{self.date} {self.hour}:00" if self.hour is not None else str(self.date)
        return f'<UsageStatistics {period}>'

class LoginSession(db.Model):
    """
    Track user login sessions for detailed monitoring
    """
    __tablename__ = 'login_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    
    # Session details
    login_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    logout_time = db.Column(db.DateTime)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Login information
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    login_method = db.Column(db.String(50))  # password, google, apple
    
    # Session status
    is_active = db.Column(db.Boolean, default=True)
    logout_reason = db.Column(db.String(50))  # manual, timeout, forced, etc.
    
    # Location and device info
    location_data = db.Column(db.JSON)  # Country, city, etc.
    device_info = db.Column(db.JSON)  # Browser, OS, device type
    
    # Activity tracking
    page_views = db.Column(db.Integer, default=0)
    actions_performed = db.Column(db.Integer, default=0)
    
    # Relationships
    user = db.relationship('User', backref='login_sessions')
    
    def __repr__(self):
        return f'<LoginSession {self.user_id}: {self.login_time}>'
    
    @property
    def duration(self):
        """Calculate session duration"""
        end_time = self.logout_time or datetime.utcnow()
        return end_time - self.login_time
    
    @property
    def is_current_session(self):
        """Check if this is an active session"""
        return self.is_active and self.logout_time is None