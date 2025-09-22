"""
Car Maintenance Services Models
Handles car service bookings, maintenance scheduling, repair tracking, and mechanic management
"""
from database import db
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

class ServiceCenter(db.Model):
    """Service Centers/Garages"""
    
    __tablename__ = 'service_centers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    center_code = db.Column(db.String(10), unique=True, nullable=False)
    
    # Location
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), default='Nigeria')
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Contact Information
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    website = db.Column(db.String(255))
    
    # Operating Details
    operating_hours = db.Column(db.JSON)  # Daily operating hours
    services_offered = db.Column(db.JSON)  # List of services
    specializations = db.Column(db.JSON)  # Vehicle brands/types specialized in
    
    # Capacity
    total_bays = db.Column(db.Integer, default=1)
    available_bays = db.Column(db.Integer, default=1)
    
    # Certifications
    certifications = db.Column(db.JSON)  # List of certifications
    
    # Manager
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manager = db.relationship('User', backref='managed_service_centers')
    mechanics = db.relationship('Mechanic', backref='service_center', lazy='dynamic')
    service_bookings = db.relationship('ServiceBooking', backref='service_center', lazy='dynamic')
    
    def __repr__(self):
        return f'<ServiceCenter {self.name}>'
    
    @property
    def average_rating(self):
        """Calculate average rating from service bookings"""
        ratings = [booking.rating for booking in self.service_bookings.filter(
            ServiceBooking.rating.isnot(None)
        ).all()]
        return sum(ratings) / len(ratings) if ratings else 0

class Mechanic(db.Model):
    """Certified Mechanics"""
    
    __tablename__ = 'mechanics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_center_id = db.Column(db.Integer, db.ForeignKey('service_centers.id'), nullable=False)
    
    # Professional Details
    employee_id = db.Column(db.String(50), unique=True)
    specializations = db.Column(db.JSON)  # Engine, transmission, electronics, etc.
    experience_years = db.Column(db.Integer)
    
    # Certifications
    certifications = db.Column(db.JSON)  # List of certifications
    license_number = db.Column(db.String(100))
    
    # Availability
    availability_schedule = db.Column(db.JSON)  # Weekly schedule
    hourly_rate = db.Column(db.Numeric(6, 2))
    
    # Performance Metrics
    total_services_completed = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0.0)
    total_revenue_generated = db.Column(db.Numeric(12, 2), default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    employment_status = db.Column(db.String(30), default='active')  # active, on_leave, terminated
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='mechanic_profile')
    service_bookings = db.relationship('ServiceBooking', backref='assigned_mechanic', lazy='dynamic')
    
    def __repr__(self):
        return f'<Mechanic {self.user.full_name}>'
    
    @property
    def is_available_today(self):
        """Check if mechanic is available today"""
        return self.is_available_on_date(date.today())
    
    def is_available_on_date(self, check_date):
        """Check if mechanic is available on specific date"""
        if not self.is_active or self.employment_status != 'active':
            return False
        
        # Check for existing bookings
        day_name = check_date.strftime('%A').lower()
        schedule = self.availability_schedule or {}
        
        if day_name not in schedule:
            return False
        
        # Check for overlapping bookings
        overlapping = self.service_bookings.filter(
            ServiceBooking.status.in_(['confirmed', 'in_progress']),
            ServiceBooking.scheduled_date == check_date
        ).count()
        
        # Assume mechanic can handle multiple services per day
        max_services_per_day = 8
        return overlapping < max_services_per_day

class CarServiceType(db.Model):
    """Types of car services offered"""
    
    __tablename__ = 'car_service_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # maintenance, repair, diagnostic, cosmetic
    
    # Service Details
    estimated_duration = db.Column(db.Integer)  # Duration in minutes
    base_price = db.Column(db.Numeric(8, 2), nullable=False)
    currency = db.Column(db.String(3), default='NGN')
    
    # Requirements
    required_skills = db.Column(db.JSON)  # Required mechanic skills
    required_tools = db.Column(db.JSON)   # Required tools/equipment
    
    # Service Intervals
    recommended_interval_km = db.Column(db.Integer)  # Recommended mileage interval
    recommended_interval_months = db.Column(db.Integer)  # Recommended time interval
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_bookings = db.relationship('ServiceBooking', backref='service_type', lazy='dynamic')
    
    def __repr__(self):
        return f'<CarServiceType {self.name}>'

class CustomerVehicle(db.Model):
    """Customer-owned vehicles"""
    
    __tablename__ = 'customer_vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Vehicle Information
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    
    # Identification
    registration_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    vin = db.Column(db.String(17), unique=True, index=True)
    engine_number = db.Column(db.String(50))
    
    # Vehicle Details
    color = db.Column(db.String(30))
    transmission = db.Column(db.String(30))  # manual, automatic
    fuel_type = db.Column(db.String(30))  # petrol, diesel, electric, hybrid
    engine_capacity = db.Column(db.String(20))  # e.g., "2.0L"
    
    # Current Status
    current_mileage = db.Column(db.Integer, default=0)
    
    # Insurance and Registration
    insurance_company = db.Column(db.String(100))
    insurance_policy_number = db.Column(db.String(100))
    insurance_expiry = db.Column(db.Date)
    registration_expiry = db.Column(db.Date)
    
    # Service History Summary
    last_service_date = db.Column(db.Date)
    last_service_mileage = db.Column(db.Integer)
    next_service_due_date = db.Column(db.Date)
    next_service_due_mileage = db.Column(db.Integer)
    
    # Preferences
    preferred_service_center_id = db.Column(db.Integer, db.ForeignKey('service_centers.id'))
    preferred_mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = db.relationship('User', backref='owned_vehicles')
    preferred_service_center = db.relationship('ServiceCenter')
    preferred_mechanic = db.relationship('Mechanic')
    service_bookings = db.relationship('ServiceBooking', backref='vehicle', lazy='dynamic')
    
    def __repr__(self):
        return f'<CustomerVehicle {self.make} {self.model} ({self.registration_number})>'
    
    @property
    def full_name(self):
        return f"{self.year} {self.make} {self.model}"
    
    @property
    def service_due_soon(self):
        """Check if service is due soon (within 30 days or 1000 km)"""
        if self.next_service_due_date and self.next_service_due_date <= date.today() + timedelta(days=30):
            return True
        if self.next_service_due_mileage and self.current_mileage >= (self.next_service_due_mileage - 1000):
            return True
        return False

class ServiceBooking(db.Model):
    """Car Service Bookings"""
    
    __tablename__ = 'service_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Booking Details
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('customer_vehicles.id'), nullable=False)
    service_center_id = db.Column(db.Integer, db.ForeignKey('service_centers.id'), nullable=False)
    service_type_id = db.Column(db.Integer, db.ForeignKey('car_service_types.id'), nullable=False)
    
    # Scheduling
    scheduled_date = db.Column(db.Date, nullable=False)
    scheduled_time = db.Column(db.Time, nullable=False)
    estimated_completion = db.Column(db.DateTime)
    
    # Assignment
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'))
    bay_number = db.Column(db.String(10))
    
    # Service Details
    requested_services = db.Column(db.JSON)  # List of service IDs
    customer_complaints = db.Column(db.Text)
    special_instructions = db.Column(db.Text)
    
    # Vehicle Condition at Arrival
    arrival_mileage = db.Column(db.Integer)
    fuel_level = db.Column(db.String(20))  # full, 3/4, half, 1/4, empty
    exterior_condition_notes = db.Column(db.Text)
    personal_items_noted = db.Column(db.Text)
    
    # Service Status
    status = db.Column(db.String(30), default='scheduled')  # scheduled, confirmed, in_progress, completed, cancelled
    
    # Actual Service Execution
    actual_start_time = db.Column(db.DateTime)
    actual_completion_time = db.Column(db.DateTime)
    work_performed = db.Column(db.Text)
    
    # Parts and Materials
    parts_used = db.Column(db.JSON)  # List of parts with quantities and costs
    labor_hours = db.Column(db.Float)
    
    # Pricing
    labor_cost = db.Column(db.Numeric(8, 2))
    parts_cost = db.Column(db.Numeric(8, 2))
    additional_charges = db.Column(db.Numeric(6, 2), default=0)
    discount_amount = db.Column(db.Numeric(6, 2), default=0)
    tax_amount = db.Column(db.Numeric(6, 2), default=0)
    total_cost = db.Column(db.Numeric(8, 2))
    currency = db.Column(db.String(3), default='NGN')
    
    # Payment
    payment_status = db.Column(db.String(30), default='pending')  # pending, paid, partial, overdue
    payment_method = db.Column(db.String(50))
    
    # Quality Assurance
    quality_check_performed = db.Column(db.Boolean, default=False)
    quality_check_notes = db.Column(db.Text)
    
    # Customer Feedback
    rating = db.Column(db.Integer)  # 1-5 stars
    feedback = db.Column(db.Text)
    would_recommend = db.Column(db.Boolean)
    
    # Follow-up
    next_service_recommendation = db.Column(db.Text)
    next_service_due_date = db.Column(db.Date)
    next_service_due_mileage = db.Column(db.Integer)
    
    # Documents
    service_report_url = db.Column(db.String(255))
    invoice_url = db.Column(db.String(255))
    photos_before = db.Column(db.JSON)  # Photos before service
    photos_after = db.Column(db.JSON)   # Photos after service
    
    # Notes
    mechanic_notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('User', backref='service_bookings')
    
    def __init__(self, **kwargs):
        super(ServiceBooking, self).__init__(**kwargs)
        if not self.booking_number:
            self.booking_number = self.generate_booking_number()
    
    @staticmethod
    def generate_booking_number():
        """Generate unique booking number"""
        prefix = "SVC"
        timestamp = datetime.now().strftime("%y%m")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<ServiceBooking {self.booking_number}>'
    
    @property
    def is_overdue(self):
        """Check if service is overdue"""
        if self.status in ['completed', 'cancelled']:
            return False
        return datetime.now().date() > self.scheduled_date

class ServiceReminder(db.Model):
    """Service Reminders for customers"""
    
    __tablename__ = 'service_reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('customer_vehicles.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Reminder Details
    reminder_type = db.Column(db.String(50), nullable=False)  # maintenance, inspection, insurance, registration
    reminder_date = db.Column(db.Date, nullable=False)
    reminder_message = db.Column(db.Text, nullable=False)
    
    # Trigger Conditions
    mileage_trigger = db.Column(db.Integer)  # Remind when vehicle reaches this mileage
    date_trigger = db.Column(db.Date)        # Remind on this date
    
    # Notification Settings
    notify_email = db.Column(db.Boolean, default=True)
    notify_sms = db.Column(db.Boolean, default=False)
    notify_push = db.Column(db.Boolean, default=True)
    
    # Status
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    is_acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    vehicle = db.relationship('CustomerVehicle', backref='service_reminders')
    customer = db.relationship('User', backref='service_reminders')
    
    def __repr__(self):
        return f'<ServiceReminder {self.vehicle.registration_number} - {self.reminder_type}>'

class ServicePackage(db.Model):
    """Service Packages (bundled services)"""
    
    __tablename__ = 'service_packages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    package_type = db.Column(db.String(50))  # basic, premium, comprehensive
    
    # Package Details
    included_services = db.Column(db.JSON)  # List of service type IDs
    estimated_duration = db.Column(db.Integer)  # Total duration in minutes
    
    # Pricing
    package_price = db.Column(db.Numeric(8, 2), nullable=False)
    individual_price_total = db.Column(db.Numeric(8, 2))  # Total if bought separately
    savings_amount = db.Column(db.Numeric(6, 2))  # Amount saved
    currency = db.Column(db.String(3), default='NGN')
    
    # Validity
    valid_for_vehicle_types = db.Column(db.JSON)  # Car types this package applies to
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ServicePackage {self.name}>'

class CarServiceBookingRequest(db.Model):
    """Car Service Booking Requests - simplified model for easy booking"""
    
    __tablename__ = 'car_service_booking_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Customer Information
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    
    # Vehicle Information
    vehicle_make = db.Column(db.String(50), nullable=False)
    vehicle_model = db.Column(db.String(50), nullable=False)
    vehicle_year = db.Column(db.Integer, nullable=False)
    registration_number = db.Column(db.String(20), nullable=False)
    current_mileage = db.Column(db.Integer)
    
    # Service Type and Details
    service_type = db.Column(db.String(50), nullable=False)  # oil_maintenance, brake_suspension, ac_electrical
    service_category = db.Column(db.String(50), nullable=False)  # For admin categorization
    
    # Booking Preferences
    preferred_date = db.Column(db.Date, nullable=False)
    preferred_time = db.Column(db.String(10), nullable=False)
    service_location = db.Column(db.String(100), nullable=False)
    
    # Service Specifications (JSON for flexibility)
    service_specifications = db.Column(db.JSON)  # Stores form-specific fields
    additional_services = db.Column(db.JSON)     # Selected additional services
    
    # Customer Input
    customer_complaints = db.Column(db.Text)
    special_instructions = db.Column(db.Text)
    budget_range = db.Column(db.String(50))
    
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    
    # Request Status
    status = db.Column(db.String(30), default='pending')  # pending, confirmed, in_progress, completed, cancelled
    priority = db.Column(db.String(20), default='normal')  # urgent, high, normal, low
    
    # Admin Assignment
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_center = db.Column(db.String(100))
    assigned_mechanic = db.Column(db.String(100))
    
    # Estimated Details
    estimated_cost = db.Column(db.Numeric(8, 2))
    estimated_duration = db.Column(db.String(50))
    
    # Admin Response
    admin_notes = db.Column(db.Text)
    confirmation_sent = db.Column(db.Boolean, default=False)
    
    # Terms Acceptance
    terms_accepted = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_admin = db.relationship('User', backref='assigned_car_service_requests')
    
    def __init__(self, **kwargs):
        super(CarServiceBookingRequest, self).__init__(**kwargs)
        if not self.request_number:
            self.request_number = self.generate_request_number()
    
    @staticmethod
    def generate_request_number():
        """Generate unique request number"""
        prefix = "CSR"  # Car Service Request
        timestamp = datetime.now().strftime("%y%m%d")
        random_part = str(uuid.uuid4().hex)[:4].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'request_number': self.request_number,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'vehicle_info': f"{self.vehicle_year} {self.vehicle_make} {self.vehicle_model}",
            'registration_number': self.registration_number,
            'service_type': self.service_type,
            'preferred_date': self.preferred_date.isoformat() if self.preferred_date else None,
            'preferred_time': self.preferred_time,
            'service_location': self.service_location,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<CarServiceBookingRequest {self.request_number}>'