"""
Logistics and Delivery Service Models
Handles package tracking, delivery routes, fleet management, and logistics solutions
"""
from database import db
from datetime import datetime, date
from decimal import Decimal
import uuid

class LogisticsHub(db.Model):
    """Logistics Hubs/Warehouses"""
    
    __tablename__ = 'logistics_hubs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)  # LAG001, ABJ002, etc.
    hub_type = db.Column(db.String(50))  # main_hub, distribution_center, pickup_point
    
    # Location
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), default='Nigeria')
    postal_code = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Hub Details
    capacity = db.Column(db.Integer)  # Maximum packages
    operating_hours = db.Column(db.JSON)  # Daily operating hours
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    
    # Manager
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manager = db.relationship('User', backref='managed_hubs')
    shipments = db.relationship('Shipment', backref='origin_hub', foreign_keys='Shipment.origin_hub_id')
    deliveries = db.relationship('Shipment', backref='destination_hub', foreign_keys='Shipment.destination_hub_id')
    vehicles = db.relationship('DeliveryVehicle', backref='hub', lazy='dynamic')
    
    def __repr__(self):
        return f'<LogisticsHub {self.name} ({self.code})>'

class DeliveryVehicle(db.Model):
    """Delivery Fleet Vehicles"""
    
    __tablename__ = 'delivery_vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Vehicle Information
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)  # motorcycle, van, truck, bicycle
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)
    
    # Capacity
    max_weight = db.Column(db.Float)  # in kg
    max_volume = db.Column(db.Float)  # in cubic meters
    max_packages = db.Column(db.Integer)
    
    # Assignment
    hub_id = db.Column(db.Integer, db.ForeignKey('logistics_hubs.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Vehicle Status
    status = db.Column(db.String(30), default='available')  # available, in_use, maintenance, retired
    fuel_level = db.Column(db.Float)  # Percentage
    mileage = db.Column(db.Integer)
    
    # Maintenance
    last_service_date = db.Column(db.Date)
    next_service_date = db.Column(db.Date)
    maintenance_notes = db.Column(db.Text)
    
    # Insurance and Documents
    insurance_expiry = db.Column(db.Date)
    license_expiry = db.Column(db.Date)
    
    # Location Tracking
    current_latitude = db.Column(db.Float)
    current_longitude = db.Column(db.Float)
    last_location_update = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    driver = db.relationship('User', backref='assigned_vehicles')
    delivery_routes = db.relationship('DeliveryRoute', backref='vehicle', lazy='dynamic')
    
    def __repr__(self):
        return f'<DeliveryVehicle {self.registration_number}>'
    
    @property
    def is_available(self):
        return self.status == 'available' and self.driver_id is not None

class Shipment(db.Model):
    """Shipments/Packages"""
    
    __tablename__ = 'shipments'
    
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Sender Information
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sender_name = db.Column(db.String(200), nullable=False)
    sender_phone = db.Column(db.String(20), nullable=False)
    sender_email = db.Column(db.String(120))
    sender_address = db.Column(db.JSON, nullable=False)  # Full address object
    
    # Recipient Information
    recipient_name = db.Column(db.String(200), nullable=False)
    recipient_phone = db.Column(db.String(20), nullable=False)
    recipient_email = db.Column(db.String(120))
    recipient_address = db.Column(db.JSON, nullable=False)  # Full address object
    
    # Package Details
    package_type = db.Column(db.String(50))  # document, parcel, fragile, electronics
    weight = db.Column(db.Float, nullable=False)  # in kg
    dimensions = db.Column(db.JSON)  # {length, width, height} in cm
    declared_value = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='NGN')
    
    # Package Contents
    description = db.Column(db.Text, nullable=False)
    contents = db.Column(db.JSON)  # List of items
    special_instructions = db.Column(db.Text)
    
    # Service Type
    service_type = db.Column(db.String(50), nullable=False)  # standard, express, overnight, same_day
    delivery_option = db.Column(db.String(50))  # door_to_door, pickup_point, hub_collection
    
    # Routing
    origin_hub_id = db.Column(db.Integer, db.ForeignKey('logistics_hubs.id'))
    destination_hub_id = db.Column(db.Integer, db.ForeignKey('logistics_hubs.id'))
    
    # Pricing
    shipping_cost = db.Column(db.Numeric(8, 2), nullable=False)
    insurance_cost = db.Column(db.Numeric(6, 2), default=0)
    total_cost = db.Column(db.Numeric(8, 2), nullable=False)
    
    # Payment
    payment_status = db.Column(db.String(30), default='pending')  # pending, paid, cod
    payment_method = db.Column(db.String(50))
    paid_by = db.Column(db.String(20))  # sender, recipient
    
    # Status and Tracking
    status = db.Column(db.String(30), default='created')  # created, collected, in_transit, out_for_delivery, delivered, returned
    current_location = db.Column(db.String(200))
    
    # Important Dates
    pickup_date = db.Column(db.DateTime)
    expected_delivery = db.Column(db.DateTime)
    delivered_date = db.Column(db.DateTime)
    
    # Delivery Details
    delivered_to = db.Column(db.String(200))  # Who received the package
    delivery_signature = db.Column(db.String(255))  # Signature image URL
    delivery_photo = db.Column(db.String(255))  # Delivery proof photo
    
    # Notes
    internal_notes = db.Column(db.Text)
    delivery_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', backref='sent_shipments')
    tracking_events = db.relationship('TrackingEvent', backref='shipment', lazy='dynamic', order_by='TrackingEvent.created_at')
    
    def __init__(self, **kwargs):
        super(Shipment, self).__init__(**kwargs)
        if not self.tracking_number:
            self.tracking_number = self.generate_tracking_number()
    
    @staticmethod
    def generate_tracking_number():
        """Generate unique tracking number"""
        prefix = "GM"
        timestamp = datetime.now().strftime("%y%m%d")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<Shipment {self.tracking_number}>'
    
    def add_tracking_event(self, event_type, description, location=None, user_id=None):
        """Add a tracking event"""
        event = TrackingEvent(
            shipment_id=self.id,
            event_type=event_type,
            description=description,
            location=location or self.current_location,
            user_id=user_id
        )
        db.session.add(event)
        
        # Update shipment status if needed
        if event_type == 'delivered':
            self.status = 'delivered'
            self.delivered_date = datetime.utcnow()
        elif event_type == 'out_for_delivery':
            self.status = 'out_for_delivery'
        elif event_type == 'in_transit':
            self.status = 'in_transit'
        
        return event

class TrackingEvent(db.Model):
    """Shipment Tracking Events"""
    
    __tablename__ = 'tracking_events'
    
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), nullable=False)
    
    # Event Details
    event_type = db.Column(db.String(50), nullable=False)  # created, collected, in_transit, delivered, etc.
    description = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(200))
    
    # User who created the event (driver, staff, system)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Additional Data
    event_data = db.Column(db.JSON)  # Additional event-specific data
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='tracking_events')
    
    def __repr__(self):
        return f'<TrackingEvent {self.shipment.tracking_number} - {self.event_type}>'

class DeliveryRoute(db.Model):
    """Delivery Routes for Vehicles"""
    
    __tablename__ = 'delivery_routes'
    
    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(100), nullable=False)
    
    # Route Details
    vehicle_id = db.Column(db.Integer, db.ForeignKey('delivery_vehicles.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Route Planning
    planned_date = db.Column(db.Date, nullable=False)
    estimated_start_time = db.Column(db.Time)
    estimated_end_time = db.Column(db.Time)
    estimated_distance = db.Column(db.Float)  # in km
    
    # Actual Execution
    actual_start_time = db.Column(db.DateTime)
    actual_end_time = db.Column(db.DateTime)
    actual_distance = db.Column(db.Float)  # in km
    
    # Route Status
    status = db.Column(db.String(30), default='planned')  # planned, in_progress, completed, cancelled
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    driver = db.relationship('User', backref='delivery_routes')
    stops = db.relationship('DeliveryStop', backref='route', lazy='dynamic', order_by='DeliveryStop.sequence_number')
    
    def __repr__(self):
        return f'<DeliveryRoute {self.route_name}>'
    
    @property
    def total_shipments(self):
        return self.stops.count()
    
    @property
    def completed_deliveries(self):
        return self.stops.filter(DeliveryStop.status == 'delivered').count()

class DeliveryStop(db.Model):
    """Individual Stops in a Delivery Route"""
    
    __tablename__ = 'delivery_stops'
    
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('delivery_routes.id'), nullable=False)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), nullable=False)
    
    # Stop Details
    sequence_number = db.Column(db.Integer, nullable=False)  # Order in route
    stop_type = db.Column(db.String(30), default='delivery')  # pickup, delivery
    
    # Address
    address = db.Column(db.JSON, nullable=False)  # Full address object
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Timing
    estimated_arrival = db.Column(db.Time)
    actual_arrival = db.Column(db.DateTime)
    actual_departure = db.Column(db.DateTime)
    
    # Delivery Details
    status = db.Column(db.String(30), default='pending')  # pending, attempted, delivered, failed
    delivery_attempts = db.Column(db.Integer, default=0)
    
    # Recipient Information
    contact_name = db.Column(db.String(200))
    contact_phone = db.Column(db.String(20))
    
    # Delivery Proof
    signature_image = db.Column(db.String(255))
    delivery_photo = db.Column(db.String(255))
    recipient_id_verified = db.Column(db.Boolean, default=False)
    
    # Notes
    delivery_notes = db.Column(db.Text)
    failure_reason = db.Column(db.String(200))  # If delivery failed
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    shipment = db.relationship('Shipment', backref='delivery_stops')
    
    def __repr__(self):
        return f'<DeliveryStop {self.shipment.tracking_number}>'

class LogisticsService(db.Model):
    """Available Logistics Services and Pricing"""
    
    __tablename__ = 'logistics_services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Service Type
    service_category = db.Column(db.String(50))  # delivery, warehousing, freight
    delivery_time = db.Column(db.String(50))  # same_day, next_day, 2-3_days, standard
    
    # Pricing Structure
    base_price = db.Column(db.Numeric(8, 2), nullable=False)
    price_per_kg = db.Column(db.Numeric(6, 2))
    price_per_km = db.Column(db.Numeric(4, 2))
    currency = db.Column(db.String(3), default='NGN')
    
    # Service Limits
    max_weight = db.Column(db.Float)  # Maximum weight in kg
    max_dimensions = db.Column(db.JSON)  # Maximum dimensions
    
    # Coverage
    coverage_areas = db.Column(db.JSON)  # List of covered states/cities
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<LogisticsService {self.name}>'
    
    def calculate_shipping_cost(self, weight, distance, origin_state, destination_state):
        """Calculate shipping cost based on weight and distance"""
        cost = float(self.base_price)
        
        if self.price_per_kg and weight:
            cost += float(self.price_per_kg) * weight
        
        if self.price_per_km and distance:
            cost += float(self.price_per_km) * distance
        
        # Apply state-specific multipliers if needed
        # This could be expanded with more complex pricing logic
        
        return round(cost, 2)


class LogisticsQuoteRequest(db.Model):
    """Logistics Quote Request Model for handling quotes for different logistics services"""
    
    __tablename__ = 'logistics_quote_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    quote_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Customer Information
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(200))
    
    # Service Type
    service_type = db.Column(db.String(50), nullable=False)  # freight_transport, express_delivery, supply_chain
    
    # Pickup Information
    pickup_address = db.Column(db.Text, nullable=False)
    pickup_city = db.Column(db.String(100), nullable=False)
    pickup_state = db.Column(db.String(100), nullable=False)
    pickup_date = db.Column(db.Date)
    pickup_time = db.Column(db.String(20))
    
    # Delivery Information
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_city = db.Column(db.String(100), nullable=False)
    delivery_state = db.Column(db.String(100), nullable=False)
    delivery_date = db.Column(db.Date)
    delivery_time = db.Column(db.String(20))
    
    # Package/Shipment Details
    package_description = db.Column(db.Text, nullable=False)
    package_weight = db.Column(db.Float)  # in kg
    package_dimensions = db.Column(db.JSON)  # {length, width, height} in cm
    package_value = db.Column(db.Numeric(10, 2))
    special_requirements = db.Column(db.Text)
    
    # Service-specific details
    freight_type = db.Column(db.String(50))  # full_load, partial_load, container
    vehicle_type = db.Column(db.String(50))  # truck, van, motorcycle
    insurance_required = db.Column(db.Boolean, default=False)
    urgency_level = db.Column(db.String(30))  # standard, urgent, emergency
    
    # Supply Chain specific
    supply_chain_type = db.Column(db.String(50))  # warehousing, distribution, inventory_management
    duration_months = db.Column(db.Integer)  # For supply chain contracts
    volume_per_month = db.Column(db.Integer)  # Expected monthly volume
    
    # Quote Details
    status = db.Column(db.String(30), default='pending')  # pending, processing, quoted, approved, rejected, completed
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Pricing
    quoted_price = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='NGN')
    quote_valid_until = db.Column(db.Date)
    quote_notes = db.Column(db.Text)
    
    # Assignment
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Important Dates
    quoted_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Additional Notes
    customer_notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='logistics_quote_requests')
    assigned_staff = db.relationship('User', foreign_keys=[assigned_staff_id], backref='assigned_logistics_quotes')
    
    def __init__(self, **kwargs):
        super(LogisticsQuoteRequest, self).__init__(**kwargs)
        if not self.quote_number:
            self.quote_number = self.generate_quote_number()
    
    @staticmethod
    def generate_quote_number():
        """Generate unique quote number"""
        prefix = "LQ"
        timestamp = datetime.now().strftime("%y%m%d")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<LogisticsQuoteRequest {self.quote_number} - {self.service_type}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'quote_number': self.quote_number,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'company_name': self.company_name,
            'service_type': self.service_type,
            'pickup_address': self.pickup_address,
            'pickup_city': self.pickup_city,
            'pickup_state': self.pickup_state,
            'delivery_address': self.delivery_address,
            'delivery_city': self.delivery_city,
            'delivery_state': self.delivery_state,
            'package_description': self.package_description,
            'package_weight': float(self.package_weight) if self.package_weight else None,
            'package_value': float(self.package_value) if self.package_value else None,
            'special_requirements': self.special_requirements,
            'status': self.status,
            'priority': self.priority,
            'quoted_price': float(self.quoted_price) if self.quoted_price else None,
            'currency': self.currency,
            'quote_notes': self.quote_notes,
            'customer_notes': self.customer_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'quoted_at': self.quoted_at.isoformat() if self.quoted_at else None
        }