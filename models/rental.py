"""
Rental Services Platform Models
Handles vehicle rentals, equipment rentals, and other rental services
"""
from database import db
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

class RentalCategory(db.Model):
    """Categories for rental items"""
    
    __tablename__ = 'rental_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))  # CSS icon class
    
    # Category Hierarchy
    parent_id = db.Column(db.Integer, db.ForeignKey('rental_categories.id'))
    
    # Display Settings
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('RentalCategory', remote_side=[id], backref='children')
    rental_items = db.relationship('RentalItem', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<RentalCategory {self.name}>'

class RentalItem(db.Model):
    """Items available for rental"""
    
    __tablename__ = 'rental_items'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    item_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('rental_categories.id'), nullable=False)
    
    # Item Type
    item_type = db.Column(db.String(50), nullable=False)  # vehicle, equipment, furniture, electronics
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.Integer)
    
    # Specifications
    specifications = db.Column(db.JSON)  # Key-value pairs of specs
    features = db.Column(db.JSON)  # Array of features
    capacity = db.Column(db.String(100))  # Seating capacity, weight capacity, etc.
    
    # Condition and Status
    condition = db.Column(db.String(30), default='excellent')  # excellent, good, fair
    status = db.Column(db.String(30), default='available')  # available, rented, maintenance, retired
    
    # Location
    location = db.Column(db.String(200))  # Where item is located
    pickup_location = db.Column(db.JSON)  # Pickup address
    delivery_available = db.Column(db.Boolean, default=True)
    delivery_radius = db.Column(db.Float)  # Delivery radius in km
    
    # Pricing
    hourly_rate = db.Column(db.Numeric(8, 2))
    daily_rate = db.Column(db.Numeric(8, 2), nullable=False)
    weekly_rate = db.Column(db.Numeric(8, 2))
    monthly_rate = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='NGN')
    
    # Security Deposit
    security_deposit = db.Column(db.Numeric(10, 2))
    damage_waiver_fee = db.Column(db.Numeric(6, 2))
    
    # Rental Terms
    min_rental_period = db.Column(db.String(20), default='1 day')  # 1 hour, 1 day, 1 week
    max_rental_period = db.Column(db.String(20))  # Maximum rental duration
    advance_booking_days = db.Column(db.Integer, default=0)  # Days in advance required
    
    # Requirements
    age_requirement = db.Column(db.Integer, default=18)
    license_required = db.Column(db.Boolean, default=False)
    license_type = db.Column(db.String(50))  # driving_license, equipment_cert, etc.
    insurance_required = db.Column(db.Boolean, default=False)
    
    # Media
    images = db.Column(db.JSON)  # Array of image URLs
    videos = db.Column(db.JSON)  # Array of video URLs
    documents = db.Column(db.JSON)  # Manuals, specifications, etc.
    
    # Maintenance
    last_service_date = db.Column(db.Date)
    next_service_date = db.Column(db.Date)
    service_interval_days = db.Column(db.Integer, default=30)
    maintenance_notes = db.Column(db.Text)
    
    # Usage Tracking
    total_rental_hours = db.Column(db.Integer, default=0)
    total_rental_days = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Numeric(12, 2), default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rentals = db.relationship('RentalBooking', backref='rental_item', lazy='dynamic')
    availability_calendar = db.relationship('RentalAvailability', backref='rental_item', lazy='dynamic')
    
    def __repr__(self):
        return f'<RentalItem {self.name} ({self.item_code})>'
    
    @property
    def is_available_today(self):
        """Check if item is available today"""
        return self.is_available_on_date(date.today())
    
    def is_available_on_date(self, check_date):
        """Check if item is available on specific date"""
        if self.status != 'available':
            return False
        
        # Check for overlapping rentals
        overlapping = self.rentals.filter(
            RentalBooking.status.in_(['confirmed', 'active']),
            RentalBooking.start_date <= check_date,
            RentalBooking.end_date > check_date
        ).first()
        
        return overlapping is None
    
    def is_available_for_period(self, start_date, end_date):
        """Check if item is available for entire period"""
        if self.status != 'available':
            return False
        
        # Check for any overlapping rentals
        overlapping = self.rentals.filter(
            RentalBooking.status.in_(['confirmed', 'active']),
            RentalBooking.start_date < end_date,
            RentalBooking.end_date > start_date
        ).first()
        
        return overlapping is None
    
    def calculate_rental_cost(self, start_date, end_date, rental_type='daily'):
        """Calculate rental cost for period"""
        delta = end_date - start_date
        
        if rental_type == 'hourly' and self.hourly_rate:
            hours = delta.total_seconds() / 3600
            return float(self.hourly_rate) * hours
        elif rental_type == 'weekly' and self.weekly_rate:
            weeks = delta.days / 7
            return float(self.weekly_rate) * weeks
        elif rental_type == 'monthly' and self.monthly_rate:
            months = delta.days / 30
            return float(self.monthly_rate) * months
        else:
            # Default to daily rate
            days = max(1, delta.days)
            return float(self.daily_rate) * days

class RentalBooking(db.Model):
    """Rental Bookings/Reservations"""
    
    __tablename__ = 'rental_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Rental Details
    rental_item_id = db.Column(db.Integer, db.ForeignKey('rental_items.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Rental Period
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    rental_duration_days = db.Column(db.Integer, nullable=False)
    
    # Actual Rental Period
    actual_pickup_time = db.Column(db.DateTime)
    actual_return_time = db.Column(db.DateTime)
    
    # Pricing
    rental_type = db.Column(db.String(20), default='daily')  # hourly, daily, weekly, monthly
    unit_rate = db.Column(db.Numeric(8, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    delivery_fee = db.Column(db.Numeric(6, 2), default=0)
    security_deposit = db.Column(db.Numeric(10, 2), default=0)
    insurance_fee = db.Column(db.Numeric(6, 2), default=0)
    tax_amount = db.Column(db.Numeric(6, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='NGN')
    
    # Delivery/Pickup
    pickup_method = db.Column(db.String(30), default='pickup')  # pickup, delivery
    pickup_address = db.Column(db.JSON)  # If delivery is selected
    return_method = db.Column(db.String(30), default='return')  # return, pickup
    return_address = db.Column(db.JSON)  # If pickup is selected
    
    # Customer Information
    customer_name = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    
    # Driver Information (for vehicle rentals)
    primary_driver_name = db.Column(db.String(200))
    primary_driver_license = db.Column(db.String(50))
    additional_drivers = db.Column(db.JSON)  # List of additional drivers
    
    # Booking Status
    status = db.Column(db.String(30), default='pending')  # pending, confirmed, active, completed, cancelled
    
    # Payment
    payment_status = db.Column(db.String(30), default='pending')  # pending, partial, paid, refunded
    amount_paid = db.Column(db.Numeric(10, 2), default=0)
    deposit_paid = db.Column(db.Numeric(10, 2), default=0)
    
    # Special Requirements
    special_requests = db.Column(db.Text)
    usage_purpose = db.Column(db.String(200))  # Wedding, business, personal, etc.
    
    # Terms and Conditions
    terms_accepted = db.Column(db.Boolean, default=False)
    terms_accepted_at = db.Column(db.DateTime)
    
    # Documents
    rental_agreement_url = db.Column(db.String(255))
    inspection_checklist_url = db.Column(db.String(255))
    
    # Notes
    customer_notes = db.Column(db.Text)
    staff_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    customer = db.relationship('User', backref='rental_bookings')
    inspections = db.relationship('RentalInspection', backref='booking', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(RentalBooking, self).__init__(**kwargs)
        if not self.booking_number:
            self.booking_number = self.generate_booking_number()
        if self.start_date and self.end_date:
            self.rental_duration_days = (self.end_date - self.start_date).days
    
    @staticmethod
    def generate_booking_number():
        """Generate unique booking number"""
        prefix = "RNT"
        timestamp = datetime.now().strftime("%y%m")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<RentalBooking {self.booking_number}>'
    
    @property
    def is_active(self):
        """Check if rental is currently active"""
        return self.status == 'active'
    
    @property
    def is_overdue(self):
        """Check if rental is overdue for return"""
        if self.status != 'active':
            return False
        return date.today() > self.end_date

class RentalInspection(db.Model):
    """Rental Item Inspections (Pre and Post Rental)"""
    
    __tablename__ = 'rental_inspections'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('rental_bookings.id'), nullable=False)
    
    # Inspection Details
    inspection_type = db.Column(db.String(30), nullable=False)  # pre_rental, post_rental
    inspector_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Condition Assessment
    overall_condition = db.Column(db.String(30))  # excellent, good, fair, poor, damaged
    exterior_condition = db.Column(db.String(30))
    interior_condition = db.Column(db.String(30))
    mechanical_condition = db.Column(db.String(30))
    
    # Damage Assessment
    damages_found = db.Column(db.JSON)  # List of damages
    damage_photos = db.Column(db.JSON)  # Array of damage photo URLs
    
    # Fuel/Battery Level (for vehicles/equipment)
    fuel_level = db.Column(db.Float)  # Percentage
    mileage = db.Column(db.Integer)  # For vehicles
    operating_hours = db.Column(db.Float)  # For equipment
    
    # Inspection Results
    passed_inspection = db.Column(db.Boolean, default=True)
    issues_noted = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    
    # Financial Impact
    damage_charges = db.Column(db.Numeric(8, 2), default=0)
    cleaning_charges = db.Column(db.Numeric(6, 2), default=0)
    late_return_charges = db.Column(db.Numeric(6, 2), default=0)
    
    # Media
    inspection_photos = db.Column(db.JSON)  # General inspection photos
    inspection_video = db.Column(db.String(255))
    
    # Customer Acknowledgment
    customer_signature = db.Column(db.String(255))  # Signature image URL
    customer_acknowledged = db.Column(db.Boolean, default=False)
    
    # Timestamps
    inspection_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    inspector = db.relationship('User', backref='rental_inspections')
    
    def __repr__(self):
        return f'<RentalInspection {self.booking.booking_number} - {self.inspection_type}>'

class RentalAvailability(db.Model):
    """Rental Item Availability Calendar"""
    
    __tablename__ = 'rental_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    rental_item_id = db.Column(db.Integer, db.ForeignKey('rental_items.id'), nullable=False)
    
    # Date Range
    date = db.Column(db.Date, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    # Reason for unavailability
    unavailable_reason = db.Column(db.String(100))  # maintenance, booked, blocked
    
    # Special Pricing
    special_rate = db.Column(db.Numeric(8, 2))  # Special rate for this date
    rate_type = db.Column(db.String(20))  # daily, hourly, etc.
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<RentalAvailability {self.rental_item.name} - {self.date}>'

class RentalPackage(db.Model):
    """Rental Packages (Bundle of items)"""
    
    __tablename__ = 'rental_packages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    package_type = db.Column(db.String(50))  # wedding, event, business, vacation
    
    # Pricing
    daily_rate = db.Column(db.Numeric(10, 2), nullable=False)
    weekly_rate = db.Column(db.Numeric(10, 2))
    monthly_rate = db.Column(db.Numeric(12, 2))
    discount_percentage = db.Column(db.Float, default=0)  # Discount vs individual items
    
    # Package Details
    included_items = db.Column(db.JSON)  # List of rental item IDs and quantities
    package_duration = db.Column(db.String(50))  # Recommended duration
    
    # Requirements
    min_rental_days = db.Column(db.Integer, default=1)
    advance_booking_days = db.Column(db.Integer, default=7)
    
    # Media
    images = db.Column(db.JSON)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<RentalPackage {self.name}>'


class RentalBookingRequest(db.Model):
    """Rental Booking Requests submitted by customers for admin approval"""
    
    __tablename__ = 'rental_booking_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Customer Information
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_address = db.Column(db.Text)
    
    # Rental Type
    rental_type = db.Column(db.String(50), nullable=False)  # vehicle, equipment, property
    
    # Rental Details
    item_category = db.Column(db.String(100))  # Car, SUV, Generator, Apartment, etc.
    item_description = db.Column(db.Text, nullable=False)
    preferred_specifications = db.Column(db.JSON)  # Specific requirements
    
    # Rental Period
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    rental_duration_days = db.Column(db.Integer, nullable=False)
    flexible_dates = db.Column(db.Boolean, default=False)
    
    # Location Preferences
    pickup_location = db.Column(db.Text)
    delivery_required = db.Column(db.Boolean, default=False)
    delivery_address = db.Column(db.Text)
    
    # Additional Requirements
    driver_required = db.Column(db.Boolean, default=False)  # For vehicles
    installation_required = db.Column(db.Boolean, default=False)  # For equipment
    setup_required = db.Column(db.Boolean, default=False)  # For equipment/furniture
    insurance_required = db.Column(db.Boolean, default=False)
    
    # Budget and Preferences
    budget_range_min = db.Column(db.Numeric(10, 2))
    budget_range_max = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='NGN')
    
    # Usage Information
    usage_purpose = db.Column(db.String(200))  # Wedding, business, personal, etc.
    number_of_users = db.Column(db.Integer)
    special_requirements = db.Column(db.Text)
    
    # Request Status
    status = db.Column(db.String(30), default='pending')  # pending, processing, quoted, approved, rejected, completed
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Assignment
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Quote Information
    quoted_amount = db.Column(db.Numeric(10, 2))
    quote_breakdown = db.Column(db.JSON)  # Detailed pricing breakdown
    quote_notes = db.Column(db.Text)
    quote_valid_until = db.Column(db.Date)
    
    # Approval Information
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approval_notes = db.Column(db.Text)
    rejection_reason = db.Column(db.Text)
    
    # Terms and Conditions
    terms_accepted = db.Column(db.Boolean, default=False)
    terms_accepted_at = db.Column(db.DateTime)
    terms_version = db.Column(db.String(10))  # Version of T&C accepted
    
    # Linked Booking
    rental_booking_id = db.Column(db.Integer, db.ForeignKey('rental_bookings.id'))  # If approved and booked
    
    # Important Dates
    quoted_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    rejected_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Notes
    customer_notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='rental_requests')
    assigned_staff = db.relationship('User', foreign_keys=[assigned_staff_id], backref='assigned_rental_requests')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_rental_requests')
    linked_booking = db.relationship('RentalBooking', backref='original_request')
    
    def __init__(self, **kwargs):
        super(RentalBookingRequest, self).__init__(**kwargs)
        if not self.request_number:
            self.request_number = self.generate_request_number()
        if self.start_date and self.end_date:
            self.rental_duration_days = (self.end_date - self.start_date).days + 1
    
    @staticmethod
    def generate_request_number():
        """Generate unique request number"""
        prefix = "RRQ"
        timestamp = datetime.now().strftime("%y%m%d")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<RentalBookingRequest {self.request_number} - {self.rental_type}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'request_number': self.request_number,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'rental_type': self.rental_type,
            'item_category': self.item_category,
            'item_description': self.item_description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'rental_duration_days': self.rental_duration_days,
            'pickup_location': self.pickup_location,
            'delivery_required': self.delivery_required,
            'delivery_address': self.delivery_address,
            'usage_purpose': self.usage_purpose,
            'budget_range_min': float(self.budget_range_min) if self.budget_range_min else None,
            'budget_range_max': float(self.budget_range_max) if self.budget_range_max else None,
            'special_requirements': self.special_requirements,
            'status': self.status,
            'priority': self.priority,
            'quoted_amount': float(self.quoted_amount) if self.quoted_amount else None,
            'quote_notes': self.quote_notes,
            'customer_notes': self.customer_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }