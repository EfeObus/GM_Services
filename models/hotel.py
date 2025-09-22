"""
Hotel Management System Models
Handles hotel operations, room management, reservations, and guest services
"""
from database import db
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

class Hotel(db.Model):
    """Hotel Properties"""
    
    __tablename__ = 'hotels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Location
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), default='Nigeria')
    postal_code = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Contact Information
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(255))
    
    # Hotel Details
    star_rating = db.Column(db.Integer)  # 1-5 stars
    total_rooms = db.Column(db.Integer, nullable=False)
    check_in_time = db.Column(db.Time, default=datetime.strptime('14:00', '%H:%M').time())
    check_out_time = db.Column(db.Time, default=datetime.strptime('11:00', '%H:%M').time())
    
    # Amenities and Services
    amenities = db.Column(db.JSON)  # List of hotel amenities
    services = db.Column(db.JSON)   # List of services offered
    
    # Policy and Rules
    cancellation_policy = db.Column(db.Text)
    house_rules = db.Column(db.Text)
    pet_policy = db.Column(db.String(100))  # allowed, not_allowed, additional_fee
    
    # Media
    images = db.Column(db.JSON)  # Array of image URLs
    virtual_tour_url = db.Column(db.String(255))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    room_types = db.relationship('RoomType', backref='hotel', lazy='dynamic')
    rooms = db.relationship('Room', backref='hotel', lazy='dynamic')
    reservations = db.relationship('Reservation', backref='hotel', lazy='dynamic')
    
    def __repr__(self):
        return f'<Hotel {self.name}>'
    
    @property
    def available_rooms_today(self):
        """Get count of available rooms for today"""
        today = date.today()
        return self.get_available_rooms_count(today, today + timedelta(days=1))
    
    def get_available_rooms_count(self, check_in_date, check_out_date):
        """Get count of available rooms for date range"""
        # This would implement complex availability logic
        total_rooms = self.rooms.filter_by(is_active=True).count()
        occupied_rooms = self.reservations.filter(
            Reservation.status == 'confirmed',
            Reservation.check_in_date < check_out_date,
            Reservation.check_out_date > check_in_date
        ).count()
        return total_rooms - occupied_rooms

class RoomType(db.Model):
    """Room Types/Categories"""
    
    __tablename__ = 'room_types'
    
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    
    # Basic Information
    name = db.Column(db.String(100), nullable=False)  # Standard, Deluxe, Suite, etc.
    description = db.Column(db.Text)
    short_description = db.Column(db.String(500))
    
    # Room Details
    max_occupancy = db.Column(db.Integer, nullable=False)
    bed_type = db.Column(db.String(50))  # single, double, queen, king, twin
    bed_count = db.Column(db.Integer, default=1)
    room_size = db.Column(db.Float)  # in square meters
    
    # Pricing
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='NGN')
    
    # Amenities and Features
    amenities = db.Column(db.JSON)  # List of room amenities
    features = db.Column(db.JSON)   # List of room features
    
    # Media
    images = db.Column(db.JSON)  # Array of image URLs
    floor_plan_url = db.Column(db.String(255))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rooms = db.relationship('Room', backref='room_type', lazy='dynamic')
    
    def __repr__(self):
        return f'<RoomType {self.hotel.name} - {self.name}>'

class Room(db.Model):
    """Individual Hotel Rooms"""
    
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_types.id'), nullable=False)
    
    # Room Identification
    room_number = db.Column(db.String(20), nullable=False)
    floor = db.Column(db.Integer)
    building = db.Column(db.String(50))  # For multi-building hotels
    
    # Room Status
    status = db.Column(db.String(30), default='available')  # available, occupied, maintenance, out_of_order
    is_active = db.Column(db.Boolean, default=True)
    
    # Room Condition
    last_cleaned = db.Column(db.DateTime)
    last_maintenance = db.Column(db.DateTime)
    
    # Special Features (room-specific)
    special_features = db.Column(db.JSON)  # Room-specific features
    accessibility_features = db.Column(db.JSON)  # Wheelchair accessible, etc.
    
    # Notes
    maintenance_notes = db.Column(db.Text)
    housekeeping_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='room', lazy='dynamic')
    
    def __repr__(self):
        return f'<Room {self.hotel.name} - {self.room_number}>'
    
    @property
    def is_available_today(self):
        """Check if room is available today"""
        today = date.today()
        return self.is_available_on_date(today)
    
    def is_available_on_date(self, check_date):
        """Check if room is available on specific date"""
        if not self.is_active or self.status in ['maintenance', 'out_of_order']:
            return False
        
        # Check for overlapping reservations
        overlapping = self.reservations.filter(
            Reservation.status == 'confirmed',
            Reservation.check_in_date <= check_date,
            Reservation.check_out_date > check_date
        ).first()
        
        return overlapping is None

class Reservation(db.Model):
    """Hotel Reservations/Bookings"""
    
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    reservation_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Hotel and Room
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_types.id'), nullable=False)
    
    # Guest Information
    guest_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    guest_name = db.Column(db.String(200), nullable=False)
    guest_email = db.Column(db.String(120), nullable=False)
    guest_phone = db.Column(db.String(20))
    
    # Additional Guests
    additional_guests = db.Column(db.JSON)  # List of additional guest details
    total_guests = db.Column(db.Integer, default=1)
    adults = db.Column(db.Integer, default=1)
    children = db.Column(db.Integer, default=0)
    
    # Reservation Dates
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    nights = db.Column(db.Integer, nullable=False)
    
    # Actual Check-in/out
    actual_check_in = db.Column(db.DateTime)
    actual_check_out = db.Column(db.DateTime)
    
    # Pricing
    room_rate = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    taxes = db.Column(db.Numeric(8, 2), default=0)
    fees = db.Column(db.Numeric(8, 2), default=0)
    discounts = db.Column(db.Numeric(8, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='NGN')
    
    # Payment
    payment_status = db.Column(db.String(30), default='pending')  # pending, partial, paid, refunded
    amount_paid = db.Column(db.Numeric(10, 2), default=0)
    payment_method = db.Column(db.String(50))
    
    # Reservation Status
    status = db.Column(db.String(30), default='pending')  # pending, confirmed, checked_in, checked_out, cancelled, no_show
    
    # Special Requests
    special_requests = db.Column(db.Text)
    arrival_time = db.Column(db.String(50))  # Expected arrival time
    
    # Booking Source
    booking_source = db.Column(db.String(50), default='direct')  # direct, online, phone, walk_in
    
    # Notes
    guest_notes = db.Column(db.Text)
    staff_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    # Relationships
    guest = db.relationship('User', backref='hotel_reservations')
    services = db.relationship('ReservationService', backref='reservation', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(Reservation, self).__init__(**kwargs)
        if not self.reservation_number:
            self.reservation_number = self.generate_reservation_number()
        if self.check_in_date and self.check_out_date:
            self.nights = (self.check_out_date - self.check_in_date).days
    
    @staticmethod
    def generate_reservation_number():
        """Generate unique reservation number"""
        prefix = "RES"
        timestamp = datetime.now().strftime("%y%m")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<Reservation {self.reservation_number}>'
    
    @property
    def is_current(self):
        """Check if guest is currently checked in"""
        return self.status == 'checked_in'
    
    @property
    def can_check_in(self):
        """Check if guest can check in today"""
        return (self.status == 'confirmed' and 
                self.check_in_date <= date.today())

class HotelService(db.Model):
    """Hotel Services and Amenities"""
    
    __tablename__ = 'hotel_services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # spa, restaurant, laundry, transport, etc.
    
    # Pricing
    price = db.Column(db.Numeric(8, 2))
    currency = db.Column(db.String(3), default='NGN')
    pricing_type = db.Column(db.String(30))  # fixed, per_hour, per_item, etc.
    
    # Availability
    is_active = db.Column(db.Boolean, default=True)
    available_hours = db.Column(db.JSON)  # Operating hours
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<HotelService {self.name}>'

class ReservationService(db.Model):
    """Services booked with reservations"""
    
    __tablename__ = 'reservation_services'
    
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('hotel_services.id'), nullable=False)
    
    # Service Details
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Numeric(8, 2), nullable=False)
    total_price = db.Column(db.Numeric(8, 2), nullable=False)
    
    # Scheduling
    service_date = db.Column(db.Date)
    service_time = db.Column(db.Time)
    
    # Status
    status = db.Column(db.String(30), default='booked')  # booked, confirmed, completed, cancelled
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    service = db.relationship('HotelService')
    
    def __repr__(self):
        return f'<ReservationService {self.service.name}>'

class GuestProfile(db.Model):
    """Extended guest profile for hotel preferences"""
    
    __tablename__ = 'guest_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Preferences
    room_preferences = db.Column(db.JSON)  # Floor preference, view, etc.
    dietary_preferences = db.Column(db.JSON)  # Vegetarian, allergies, etc.
    special_occasions = db.Column(db.JSON)  # Birthday, anniversary, etc.
    
    # Loyalty Information
    loyalty_level = db.Column(db.String(20), default='standard')  # standard, silver, gold, platinum
    total_stays = db.Column(db.Integer, default=0)
    total_nights = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Numeric(12, 2), default=0)
    
    # Communication Preferences
    preferred_communication = db.Column(db.String(30), default='email')  # email, sms, phone
    marketing_consent = db.Column(db.Boolean, default=False)
    
    # Notes
    staff_notes = db.Column(db.Text)  # Internal notes about guest
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='guest_profile', uselist=False)
    
    def __repr__(self):
        return f'<GuestProfile {self.user.full_name}>'

class HotelServiceRequest(db.Model):
    """Hotel Service Requests for Operations, Booking System, and Staff Training"""
    
    __tablename__ = 'hotel_service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Request Type
    service_type = db.Column(db.String(50), nullable=False)  # operations_management, booking_system, staff_training
    
    # Client Information
    client_name = db.Column(db.String(200), nullable=False)
    client_email = db.Column(db.String(120), nullable=False)
    client_phone = db.Column(db.String(20))
    company_name = db.Column(db.String(200))
    
    # Hotel Details
    hotel_name = db.Column(db.String(200))
    hotel_location = db.Column(db.String(200))
    hotel_size = db.Column(db.String(100))  # Small (1-50 rooms), Medium (51-200), Large (200+)
    current_management_system = db.Column(db.String(200))
    
    # Service Specific Details
    specific_requirements = db.Column(db.Text)
    budget_range = db.Column(db.String(100))
    timeline = db.Column(db.String(100))
    priority_level = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    
    # Staff Training Specific (if applicable)
    number_of_staff = db.Column(db.Integer)
    training_areas = db.Column(db.JSON)  # List of specific training areas needed
    current_skill_level = db.Column(db.String(50))  # beginner, intermediate, advanced
    
    # Booking System Specific (if applicable)
    current_booking_system = db.Column(db.String(200))
    integration_requirements = db.Column(db.Text)
    expected_monthly_bookings = db.Column(db.Integer)
    
    # Operations Management Specific (if applicable)
    current_operations_challenges = db.Column(db.Text)
    departments_to_manage = db.Column(db.JSON)  # List of departments
    quality_standards_required = db.Column(db.Text)
    
    # Request Status
    status = db.Column(db.String(30), default='pending')  # pending, reviewed, assigned, in_progress, completed, cancelled
    
    # Assignment
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Staff member assigned
    assigned_at = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)
    
    # Follow-up
    follow_up_date = db.Column(db.Date)
    last_contact_date = db.Column(db.Date)
    consultation_scheduled = db.Column(db.DateTime)
    
    # Pricing and Quote
    estimated_cost = db.Column(db.Numeric(12, 2))
    quote_provided = db.Column(db.Boolean, default=False)
    quote_accepted = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_to = db.relationship('User', backref='assigned_hotel_requests', foreign_keys=[assigned_to_id])
    
    def __init__(self, **kwargs):
        super(HotelServiceRequest, self).__init__(**kwargs)
        if not self.request_number:
            self.request_number = self.generate_request_number()
    
    def generate_request_number(self):
        """Generate unique request number"""
        prefix = {
            'operations_management': 'HOM',
            'booking_system': 'HBS', 
            'staff_training': 'HST'
        }.get(self.service_type, 'HSR')
        
        timestamp = datetime.now().strftime('%Y%m%d')
        sequence = str(uuid.uuid4())[:8].upper()
        return f"{prefix}-{timestamp}-{sequence}"
    
    def __repr__(self):
        return f'<HotelServiceRequest {self.request_number}>'
    
    @property
    def status_color(self):
        """Get status color for UI"""
        colors = {
            'pending': 'warning',
            'reviewed': 'info',
            'assigned': 'primary',
            'in_progress': 'secondary',
            'completed': 'success',
            'cancelled': 'danger'
        }
        return colors.get(self.status, 'secondary')
    
    @property
    def priority_color(self):
        """Get priority color for UI"""
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'urgent': 'dark'
        }
        return colors.get(self.priority_level, 'secondary')
    
    def get_service_type_display(self):
        """Get human readable service type"""
        types = {
            'operations_management': 'Operations Management',
            'booking_system': 'Booking System',
            'staff_training': 'Staff Training'
        }
        return types.get(self.service_type, self.service_type.title())