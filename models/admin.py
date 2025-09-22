"""
Admin Dashboard Models
Handles comprehensive admin dashboard for managing all GM Services
"""
from database import db
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

class AdminRole(db.Model):
    """Admin roles and permissions"""
    
    __tablename__ = 'admin_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # Permissions
    permissions = db.Column(db.JSON, nullable=False)  # List of permission codes
    
    # Role Hierarchy
    level = db.Column(db.Integer, default=1)  # 1=basic, 5=super_admin
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    admin_users = db.relationship('AdminUser', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<AdminRole {self.name}>'

class AdminUser(db.Model):
    """Admin users with dashboard access"""
    
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('admin_roles.id'), nullable=False)
    
    # Admin Details
    admin_id = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100))
    supervisor_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    
    # Access Control
    allowed_services = db.Column(db.JSON)  # List of services they can manage
    ip_restrictions = db.Column(db.JSON)   # IP addresses allowed
    
    # Session Management
    last_login = db.Column(db.DateTime)
    last_activity = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    
    # Two-Factor Authentication
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32))
    backup_codes = db.Column(db.JSON)
    
    # Preferences
    dashboard_preferences = db.Column(db.JSON)  # UI preferences
    notification_preferences = db.Column(db.JSON)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    employment_status = db.Column(db.String(30), default='active')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='admin_profile')
    supervisor = db.relationship('AdminUser', remote_side=[id], backref='supervised_users')
    activity_logs = db.relationship('AdminActivityLog', backref='admin_user', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(AdminUser, self).__init__(**kwargs)
        if not self.admin_id:
            self.admin_id = self.generate_admin_id()
    
    @staticmethod
    def generate_admin_id():
        """Generate unique admin ID"""
        prefix = "ADM"
        timestamp = datetime.now().strftime("%y%m")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<AdminUser {self.admin_id} - {self.user.full_name}>'
    
    @property
    def is_locked(self):
        """Check if admin account is locked"""
        if self.account_locked_until:
            return datetime.utcnow() < self.account_locked_until
        return False

class AdminActivityLog(db.Model):
    """Log of admin activities"""
    
    __tablename__ = 'admin_activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    
    # Activity Details
    action = db.Column(db.String(100), nullable=False)  # login, create_user, update_service, etc.
    description = db.Column(db.Text)
    
    # Target Information
    target_type = db.Column(db.String(50))  # user, service, transaction, etc.
    target_id = db.Column(db.Integer)
    
    # Request Details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    request_url = db.Column(db.String(500))
    http_method = db.Column(db.String(10))
    
    # Data Changes
    old_values = db.Column(db.JSON)  # Previous values
    new_values = db.Column(db.JSON)  # New values
    
    # Result
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    
    # Session Information
    session_id = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdminActivityLog {self.action} by {self.admin_user.admin_id}>'

class DashboardWidget(db.Model):
    """Dashboard widgets and metrics"""
    
    __tablename__ = 'dashboard_widgets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Widget Configuration
    widget_type = db.Column(db.String(50), nullable=False)  # chart, metric, table, list
    data_source = db.Column(db.String(100))  # SQL query or API endpoint
    refresh_interval_minutes = db.Column(db.Integer, default=15)
    
    # Display Settings
    chart_type = db.Column(db.String(50))  # line, bar, pie, donut
    color_scheme = db.Column(db.JSON)      # Colors for charts
    size = db.Column(db.String(20), default='medium')  # small, medium, large
    
    # Permissions
    required_permissions = db.Column(db.JSON)  # Who can see this widget
    services_filter = db.Column(db.JSON)       # Which services this applies to
    
    # Position
    dashboard_section = db.Column(db.String(50))  # overview, financial, operations
    display_order = db.Column(db.Integer, default=0)
    
    # Cache Settings
    cache_duration_minutes = db.Column(db.Integer, default=5)
    last_cached = db.Column(db.DateTime)
    cached_data = db.Column(db.JSON)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DashboardWidget {self.name}>'

class BusinessMetric(db.Model):
    """Business metrics and KPIs"""
    
    __tablename__ = 'business_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Metric Information
    metric_name = db.Column(db.String(100), nullable=False)
    metric_category = db.Column(db.String(50))  # financial, operational, customer
    
    # Time Period
    date = db.Column(db.Date, nullable=False, index=True)
    period_type = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly
    
    # Service Breakdown
    service_type = db.Column(db.String(50))  # automobile, hotel, etc., or 'total'
    
    # Metric Values
    value = db.Column(db.Numeric(15, 2))
    previous_period_value = db.Column(db.Numeric(15, 2))
    target_value = db.Column(db.Numeric(15, 2))
    
    # Additional Data
    metric_metadata = db.Column(db.JSON)  # Additional metric data
    
    # Calculation Details
    calculation_method = db.Column(db.String(100))
    data_sources = db.Column(db.JSON)  # Tables/sources used
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BusinessMetric {self.metric_name} - {self.date}>'
    
    @property
    def percentage_change(self):
        """Calculate percentage change from previous period"""
        if not self.previous_period_value or self.previous_period_value == 0:
            return None
        return ((self.value - self.previous_period_value) / self.previous_period_value) * 100
    
    @property
    def target_achievement(self):
        """Calculate percentage of target achieved"""
        if not self.target_value or self.target_value == 0:
            return None
        return (self.value / self.target_value) * 100

class SystemAlert(db.Model):
    """System alerts and notifications"""
    
    __tablename__ = 'system_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Alert Details
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # info, warning, error, critical
    
    # Source
    source_system = db.Column(db.String(100))  # payment, user_management, etc.
    source_reference = db.Column(db.String(100))  # Related record ID
    
    # Priority and Urgency
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    requires_action = db.Column(db.Boolean, default=False)
    auto_resolve = db.Column(db.Boolean, default=False)
    
    # Assignment
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    assigned_at = db.Column(db.DateTime)
    
    # Resolution
    status = db.Column(db.String(30), default='open')  # open, assigned, resolved, closed
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    
    # Escalation
    escalation_level = db.Column(db.Integer, default=0)
    escalated_at = db.Column(db.DateTime)
    escalated_to_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    
    # Notification
    notification_sent = db.Column(db.Boolean, default=False)
    notification_channels = db.Column(db.JSON)  # email, sms, slack
    
    # Metadata
    alert_data = db.Column(db.JSON)  # Additional alert data
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_to = db.relationship('AdminUser', foreign_keys=[assigned_to_id], backref='assigned_alerts')
    resolved_by = db.relationship('AdminUser', foreign_keys=[resolved_by_id], backref='resolved_alerts')
    escalated_to = db.relationship('AdminUser', foreign_keys=[escalated_to_id], backref='escalated_alerts')
    
    def __init__(self, **kwargs):
        super(SystemAlert, self).__init__(**kwargs)
        if not self.alert_id:
            self.alert_id = self.generate_alert_id()
    
    @staticmethod
    def generate_alert_id():
        """Generate unique alert ID"""
        prefix = "ALT"
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<SystemAlert {self.alert_id} - {self.alert_type}>'

class SystemConfiguration(db.Model):
    """System configuration settings"""
    
    __tablename__ = 'system_configurations'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False, unique=True, index=True)
    value = db.Column(db.Text)
    
    # Configuration Details
    category = db.Column(db.String(50))  # system, payment, email, sms
    description = db.Column(db.Text)
    data_type = db.Column(db.String(20), default='string')  # string, integer, boolean, json
    
    # Validation
    validation_rules = db.Column(db.JSON)  # Validation rules for the value
    default_value = db.Column(db.Text)
    
    # Access Control
    is_sensitive = db.Column(db.Boolean, default=False)  # Encrypted storage
    requires_restart = db.Column(db.Boolean, default=False)  # Requires system restart
    
    # Environment
    environment = db.Column(db.String(20), default='production')  # development, staging, production
    
    # Metadata
    last_modified_by_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    modification_reason = db.Column(db.Text)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    last_modified_by = db.relationship('AdminUser', backref='configuration_changes')
    
    def __repr__(self):
        return f'<SystemConfiguration {self.key}>'

class DataExport(db.Model):
    """Data export requests and files"""
    
    __tablename__ = 'data_exports'
    
    id = db.Column(db.Integer, primary_key=True)
    export_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Export Details
    requested_by_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    export_type = db.Column(db.String(50), nullable=False)  # users, transactions, services
    
    # Parameters
    date_range_start = db.Column(db.Date)
    date_range_end = db.Column(db.Date)
    filters = db.Column(db.JSON)  # Additional filters
    
    # Export Format
    file_format = db.Column(db.String(20), default='csv')  # csv, xlsx, pdf, json
    columns_included = db.Column(db.JSON)  # Which columns to export
    
    # Processing
    status = db.Column(db.String(30), default='pending')  # pending, processing, completed, failed
    total_records = db.Column(db.Integer)
    processed_records = db.Column(db.Integer, default=0)
    
    # File Information
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)  # File size in bytes
    download_count = db.Column(db.Integer, default=0)
    
    # Processing Details
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    # Access Control
    expires_at = db.Column(db.DateTime)  # File expiration
    is_encrypted = db.Column(db.Boolean, default=False)
    download_password = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    requested_by = db.relationship('AdminUser', backref='data_exports')
    
    def __init__(self, **kwargs):
        super(DataExport, self).__init__(**kwargs)
        if not self.export_id:
            self.export_id = self.generate_export_id()
    
    @staticmethod
    def generate_export_id():
        """Generate unique export ID"""
        prefix = "EXP"
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<DataExport {self.export_id} - {self.export_type}>'
    
    @property
    def is_expired(self):
        """Check if export file is expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

class AuditTrail(db.Model):
    """Comprehensive audit trail for all system changes"""
    
    __tablename__ = 'audit_trails'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Entity Information
    table_name = db.Column(db.String(100), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    
    # Action Details
    action = db.Column(db.String(20), nullable=False)  # CREATE, UPDATE, DELETE
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    admin_user_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    
    # Changes
    old_values = db.Column(db.JSON)  # Previous values
    new_values = db.Column(db.JSON)  # New values
    changed_fields = db.Column(db.JSON)  # List of changed field names
    
    # Context
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    session_id = db.Column(db.String(100))
    request_id = db.Column(db.String(100))
    
    # Business Context
    business_reason = db.Column(db.Text)  # Why the change was made
    approval_reference = db.Column(db.String(100))  # Approval ticket/reference
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='audit_trails')
    admin_user = db.relationship('AdminUser', backref='admin_audit_trails')
    
    def __init__(self, **kwargs):
        super(AuditTrail, self).__init__(**kwargs)
        if not self.audit_id:
            self.audit_id = self.generate_audit_id()
    
    @staticmethod
    def generate_audit_id():
        """Generate unique audit ID"""
        prefix = "AUD"
        timestamp = datetime.now().strftime("%y%m%d%H%M%S")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<AuditTrail {self.audit_id} - {self.action} on {self.table_name}>'

class SystemBackup(db.Model):
    """System backup records"""
    
    __tablename__ = 'system_backups'
    
    id = db.Column(db.Integer, primary_key=True)
    backup_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Backup Details
    backup_type = db.Column(db.String(30), nullable=False)  # full, incremental, differential
    backup_scope = db.Column(db.String(50))  # database, files, complete
    
    # File Information
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.BigInteger)  # Size in bytes
    compression_ratio = db.Column(db.Float)
    
    # Backup Content
    tables_included = db.Column(db.JSON)  # Which tables were backed up
    files_included = db.Column(db.JSON)   # Which file directories
    
    # Processing
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    
    # Status
    status = db.Column(db.String(30), default='in_progress')  # in_progress, completed, failed
    error_message = db.Column(db.Text)
    
    # Verification
    checksum = db.Column(db.String(64))  # File checksum for integrity
    verified = db.Column(db.Boolean, default=False)
    verification_date = db.Column(db.DateTime)
    
    # Storage
    storage_location = db.Column(db.String(200))  # local, s3, azure, etc.
    retention_until = db.Column(db.Date)  # When backup expires
    
    # Restoration
    can_restore = db.Column(db.Boolean, default=True)
    last_restore_test = db.Column(db.DateTime)
    restore_test_success = db.Column(db.Boolean)
    
    # Metadata
    created_by_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    backup_software = db.Column(db.String(100))
    backup_version = db.Column(db.String(50))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    created_by = db.relationship('AdminUser', backref='created_backups')
    
    def __init__(self, **kwargs):
        super(SystemBackup, self).__init__(**kwargs)
        if not self.backup_id:
            self.backup_id = self.generate_backup_id()
    
    @staticmethod
    def generate_backup_id():
        """Generate unique backup ID"""
        prefix = "BAK"
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<SystemBackup {self.backup_id} - {self.backup_type}>'
    
    @property
    def is_expired(self):
        """Check if backup has expired"""
        if self.retention_until:
            return date.today() > self.retention_until
        return False


class AdminNotification(db.Model):
    """Admin notifications for service requests and system events"""
    
    __tablename__ = 'admin_notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Recipient
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Notification Details
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # service_request, logistics_quote, etc.
    
    # Priority and Status
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    
    # Related Data
    related_model = db.Column(db.String(100))  # ServiceRequest, LogisticsQuoteRequest, etc.
    related_id = db.Column(db.Integer)
    
    # Action Buttons
    action_url = db.Column(db.String(255))  # URL for primary action
    action_text = db.Column(db.String(100))  # Text for action button
    
    # Delivery
    delivery_method = db.Column(db.String(50), default='dashboard')  # dashboard, email, sms
    email_sent = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime)
    
    # Expiry
    expires_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='admin_notifications')
    
    def __repr__(self):
        return f'<AdminNotification {self.title} for User {self.user_id}>'
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        db.session.commit()
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    @property
    def priority_class(self):
        """Get CSS class for priority"""
        priority_classes = {
            'low': 'info',
            'normal': 'primary',
            'high': 'warning',
            'urgent': 'danger'
        }
        return priority_classes.get(self.priority, 'primary')
    
    @property
    def priority_icon(self):
        """Get icon for priority"""
        priority_icons = {
            'low': 'fas fa-info-circle',
            'normal': 'fas fa-bell',
            'high': 'fas fa-exclamation-triangle',
            'urgent': 'fas fa-exclamation-circle'
        }
        return priority_icons.get(self.priority, 'fas fa-bell')