"""
License Plates and Paperwork Models
Handles vehicle registration, license plate processing, and government paperwork assistance
"""
from database import db
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

class DocumentType(db.Model):
    """Types of vehicle documents and paperwork"""
    
    __tablename__ = 'document_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # registration, license, permit, certificate
    
    # Document Details
    issuing_authority = db.Column(db.String(100))  # FRSC, VIO, etc.
    validity_period_months = db.Column(db.Integer)  # How long document is valid
    renewal_period_months = db.Column(db.Integer)   # How often to renew
    
    # Requirements
    required_documents = db.Column(db.JSON)  # List of required supporting documents
    eligibility_criteria = db.Column(db.JSON)  # Requirements for eligibility
    
    # Processing
    processing_time_days = db.Column(db.Integer)  # Estimated processing time
    fees = db.Column(db.JSON)  # Different fee structures
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('DocumentApplication', backref='document_type', lazy='dynamic')
    
    def __repr__(self):
        return f'<DocumentType {self.name}>'

class LicensePlateCategory(db.Model):
    """License plate categories and types"""
    
    __tablename__ = 'license_plate_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    category_code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Plate Specifications
    plate_format = db.Column(db.String(50))  # Format pattern (e.g., "AAA-000-AA")
    color_scheme = db.Column(db.String(100))  # Background and text colors
    special_features = db.Column(db.JSON)     # Reflective, holographic, etc.
    
    # Usage
    vehicle_types = db.Column(db.JSON)  # Types of vehicles this applies to
    usage_restrictions = db.Column(db.JSON)  # Any usage restrictions
    
    # Pricing
    base_fee = db.Column(db.Numeric(8, 2), nullable=False)
    renewal_fee = db.Column(db.Numeric(6, 2))
    replacement_fee = db.Column(db.Numeric(6, 2))
    currency = db.Column(db.String(3), default='NGN')
    
    # Validity
    validity_years = db.Column(db.Integer, default=5)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    license_plates = db.relationship('LicensePlate', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<LicensePlateCategory {self.category_code} - {self.name}>'

class LicensePlate(db.Model):
    """Individual license plates"""
    
    __tablename__ = 'license_plates'
    
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('license_plate_categories.id'), nullable=False)
    
    # Ownership
    current_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('customer_vehicles.id'))
    
    # Issue Details
    issued_date = db.Column(db.Date, nullable=False)
    issued_by = db.Column(db.String(100))  # Issuing office
    issued_state = db.Column(db.String(50))
    
    # Validity
    expiry_date = db.Column(db.Date, nullable=False)
    
    # Status
    status = db.Column(db.String(30), default='active')  # active, expired, suspended, revoked, lost, stolen
    
    # Physical Details
    manufacture_date = db.Column(db.Date)
    manufacturer = db.Column(db.String(100))
    serial_number = db.Column(db.String(50))
    
    # Security Features
    security_features = db.Column(db.JSON)  # RFID, hologram, etc.
    verification_code = db.Column(db.String(100))
    
    # Notes
    special_notes = db.Column(db.Text)
    restrictions = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    current_owner = db.relationship('User', backref='owned_license_plates')
    vehicle = db.relationship('CustomerVehicle', backref='license_plates')
    applications = db.relationship('DocumentApplication', backref='license_plate', lazy='dynamic')
    
    def __repr__(self):
        return f'<LicensePlate {self.plate_number}>'
    
    @property
    def is_expired(self):
        """Check if license plate is expired"""
        return date.today() > self.expiry_date
    
    @property
    def expires_soon(self):
        """Check if license plate expires within 30 days"""
        return date.today() + timedelta(days=30) >= self.expiry_date

class DocumentApplication(db.Model):
    """Applications for vehicle documents and license plates"""
    
    __tablename__ = 'document_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    application_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Application Details
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type_id = db.Column(db.Integer, db.ForeignKey('document_types.id'), nullable=False)
    application_type = db.Column(db.String(50), nullable=False)  # new, renewal, replacement, transfer
    
    # Related Records
    vehicle_id = db.Column(db.Integer, db.ForeignKey('customer_vehicles.id'))
    license_plate_id = db.Column(db.Integer, db.ForeignKey('license_plates.id'))
    
    # Application Data
    application_data = db.Column(db.JSON)  # Form data specific to document type
    requested_plate_number = db.Column(db.String(20))  # For custom plate requests
    
    # Supporting Documents
    submitted_documents = db.Column(db.JSON)  # List of uploaded document URLs
    document_verification_status = db.Column(db.JSON)  # Status of each document
    
    # Processing
    submitted_date = db.Column(db.DateTime, default=datetime.utcnow)
    processing_office = db.Column(db.String(100))
    assigned_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Status Tracking
    status = db.Column(db.String(30), default='submitted')  # submitted, under_review, approved, rejected, completed
    status_notes = db.Column(db.Text)
    
    # Review Process
    review_started_date = db.Column(db.DateTime)
    review_completed_date = db.Column(db.DateTime)
    reviewer_notes = db.Column(db.Text)
    
    # Approval/Rejection
    approved_date = db.Column(db.DateTime)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rejection_reason = db.Column(db.Text)
    rejection_date = db.Column(db.DateTime)
    
    # Collection/Delivery
    ready_for_collection_date = db.Column(db.DateTime)
    collection_method = db.Column(db.String(50))  # pickup, delivery, mail
    delivery_address = db.Column(db.Text)
    collected_date = db.Column(db.DateTime)
    collected_by = db.Column(db.String(200))
    
    # Payment
    application_fee = db.Column(db.Numeric(8, 2))
    processing_fee = db.Column(db.Numeric(6, 2))
    additional_fees = db.Column(db.Numeric(6, 2), default=0)
    total_fee = db.Column(db.Numeric(8, 2))
    currency = db.Column(db.String(3), default='NGN')
    payment_status = db.Column(db.String(30), default='pending')  # pending, paid, refunded
    payment_reference = db.Column(db.String(100))
    
    # Timeline Tracking
    estimated_completion_date = db.Column(db.Date)
    actual_completion_date = db.Column(db.Date)
    
    # Communication
    sms_notifications_sent = db.Column(db.JSON)  # Log of SMS notifications
    email_notifications_sent = db.Column(db.JSON)  # Log of email notifications
    
    # Quality Assurance
    qa_checked = db.Column(db.Boolean, default=False)
    qa_checked_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    qa_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applicant = db.relationship('User', foreign_keys=[applicant_id], backref='document_applications')
    assigned_officer = db.relationship('User', foreign_keys=[assigned_officer_id], backref='assigned_applications')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='approved_applications')
    qa_checked_by = db.relationship('User', foreign_keys=[qa_checked_by_id], backref='qa_checked_applications')
    vehicle = db.relationship('CustomerVehicle', backref='document_applications')
    
    def __init__(self, **kwargs):
        super(DocumentApplication, self).__init__(**kwargs)
        if not self.application_number:
            self.application_number = self.generate_application_number()
    
    @staticmethod
    def generate_application_number():
        """Generate unique application number"""
        prefix = "DOC"
        timestamp = datetime.now().strftime("%y%m")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<DocumentApplication {self.application_number}>'
    
    @property
    def is_overdue(self):
        """Check if application is overdue"""
        if self.status in ['completed', 'rejected']:
            return False
        if self.estimated_completion_date:
            return date.today() > self.estimated_completion_date
        return False

class VehicleRegistration(db.Model):
    """Vehicle registration records"""
    
    __tablename__ = 'vehicle_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Vehicle Details
    vehicle_id = db.Column(db.Integer, db.ForeignKey('customer_vehicles.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Registration Details
    registration_date = db.Column(db.Date, nullable=False)
    registration_state = db.Column(db.String(50), nullable=False)
    registration_office = db.Column(db.String(100))
    
    # Validity
    expiry_date = db.Column(db.Date, nullable=False)
    
    # Previous Registrations
    previous_registration_number = db.Column(db.String(20))
    previous_state = db.Column(db.String(50))
    
    # Documentation
    certificate_number = db.Column(db.String(50))
    certificate_issued_date = db.Column(db.Date)
    
    # Status
    status = db.Column(db.String(30), default='active')  # active, expired, transferred, cancelled
    
    # Fees and Payments
    registration_fee = db.Column(db.Numeric(8, 2))
    other_fees = db.Column(db.Numeric(6, 2), default=0)
    total_paid = db.Column(db.Numeric(8, 2))
    currency = db.Column(db.String(3), default='NGN')
    
    # Notes
    special_conditions = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicle = db.relationship('CustomerVehicle', backref='registrations')
    owner = db.relationship('User', backref='vehicle_registrations')
    
    def __repr__(self):
        return f'<VehicleRegistration {self.registration_number}>'
    
    @property
    def is_expired(self):
        """Check if registration is expired"""
        return date.today() > self.expiry_date
    
    @property
    def expires_soon(self):
        """Check if registration expires within 30 days"""
        return date.today() + timedelta(days=30) >= self.expiry_date

class DocumentRenewalReminder(db.Model):
    """Automated reminders for document renewal"""
    
    __tablename__ = 'document_renewal_reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Target Details
    target_type = db.Column(db.String(50), nullable=False)  # license_plate, registration, permit
    target_id = db.Column(db.Integer, nullable=False)  # ID of the target record
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Reminder Details
    reminder_type = db.Column(db.String(50))  # renewal, expiry_warning
    reminder_date = db.Column(db.Date, nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Delivery Method
    notify_email = db.Column(db.Boolean, default=True)
    notify_sms = db.Column(db.Boolean, default=True)
    notify_push = db.Column(db.Boolean, default=True)
    
    # Status
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    delivery_status = db.Column(db.JSON)  # Status for each delivery method
    
    # Response Tracking
    is_acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_at = db.Column(db.DateTime)
    action_taken = db.Column(db.String(100))  # renewed, ignored, postponed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='document_reminders')
    
    def __repr__(self):
        return f'<DocumentRenewalReminder {self.target_type}:{self.target_id}>'

class GovernmentOffice(db.Model):
    """Government offices for document processing"""
    
    __tablename__ = 'government_offices'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    office_type = db.Column(db.String(50))  # VIO, FRSC, State_Motor_Registry
    office_code = db.Column(db.String(20), unique=True)
    
    # Location
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), default='Nigeria')
    
    # Contact Information
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(255))
    
    # Operating Details
    operating_hours = db.Column(db.JSON)  # Daily operating hours
    services_offered = db.Column(db.JSON)  # List of services
    
    # Capacity and Performance
    daily_capacity = db.Column(db.Integer)  # Applications processed per day
    average_processing_time = db.Column(db.Float)  # Average days to process
    
    # Officer in Charge
    head_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    head_officer = db.relationship('User', backref='headed_government_offices')
    
    def __repr__(self):
        return f'<GovernmentOffice {self.name}>'

class DocumentTemplate(db.Model):
    """Templates for different document types"""
    
    __tablename__ = 'document_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    document_type_id = db.Column(db.Integer, db.ForeignKey('document_types.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Template Content
    template_content = db.Column(db.Text)  # HTML template
    required_fields = db.Column(db.JSON)   # List of required form fields
    optional_fields = db.Column(db.JSON)   # List of optional form fields
    
    # Validation Rules
    validation_rules = db.Column(db.JSON)  # Validation rules for fields
    
    # Version Control
    version = db.Column(db.String(20), default='1.0')
    is_current_version = db.Column(db.Boolean, default=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document_type = db.relationship('DocumentType', backref='templates')
    
    def __repr__(self):
        return f'<DocumentTemplate {self.name} v{self.version}>'