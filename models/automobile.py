"""
Automobile Dealership Models
Handles vehicles, inventory, sales, and dealership operations
"""
from database import db
from datetime import datetime
from decimal import Decimal

class VehicleMake(db.Model):
    """Vehicle Make/Brand Model"""
    
    __tablename__ = 'vehicle_makes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # Toyota, Honda, Mercedes, etc.
    country = db.Column(db.String(100))  # Country of origin
    logo_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    models = db.relationship('VehicleModel', backref='make', lazy='dynamic')
    
    def __repr__(self):
        return f'<VehicleMake {self.name}>'

class VehicleModel(db.Model):
    """Vehicle Model under a Make"""
    
    __tablename__ = 'vehicle_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Camry, Accord, C-Class, etc.
    make_id = db.Column(db.Integer, db.ForeignKey('vehicle_makes.id'), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)  # sedan, suv, truck, motorcycle, etc.
    body_style = db.Column(db.String(50))  # sedan, coupe, hatchback, pickup, etc.
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicles = db.relationship('Vehicle', backref='model', lazy='dynamic')
    
    def __repr__(self):
        return f'<VehicleModel {self.make.name} {self.name}>'
    
    @property
    def full_name(self):
        return f"{self.make.name} {self.name}"

class Vehicle(db.Model):
    """Individual Vehicle/Inventory Item"""
    
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Vehicle Identification
    vin = db.Column(db.String(17), unique=True, index=True)  # Vehicle Identification Number
    stock_number = db.Column(db.String(50), unique=True, index=True)
    
    # Basic Information
    model_id = db.Column(db.Integer, db.ForeignKey('vehicle_models.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    trim = db.Column(db.String(100))  # LX, EX, Limited, etc.
    
    # Specifications
    engine = db.Column(db.String(100))  # 2.4L 4-Cylinder
    transmission = db.Column(db.String(50))  # Manual, Automatic, CVT
    drivetrain = db.Column(db.String(50))  # FWD, RWD, AWD, 4WD
    fuel_type = db.Column(db.String(30))  # Gasoline, Diesel, Electric, Hybrid
    fuel_economy_city = db.Column(db.Float)  # MPG in city
    fuel_economy_highway = db.Column(db.Float)  # MPG on highway
    
    # Physical Attributes
    exterior_color = db.Column(db.String(50))
    interior_color = db.Column(db.String(50))
    mileage = db.Column(db.Integer, default=0)  # Odometer reading
    
    # Pricing
    msrp = db.Column(db.Numeric(12, 2))  # Manufacturer's Suggested Retail Price
    selling_price = db.Column(db.Numeric(12, 2), nullable=False)
    cost_price = db.Column(db.Numeric(12, 2))  # What dealership paid
    currency = db.Column(db.String(3), default='NGN')
    
    # Condition and Status
    condition = db.Column(db.String(20), nullable=False)  # new, used, certified
    status = db.Column(db.String(20), default='available')  # available, sold, reserved, service
    
    # Features and Options
    features = db.Column(db.JSON)  # List of features/options
    description = db.Column(db.Text)
    
    # Media
    images = db.Column(db.JSON)  # Array of image URLs
    videos = db.Column(db.JSON)  # Array of video URLs
    
    # Location
    location = db.Column(db.String(100))  # Dealership location
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sold_at = db.Column(db.DateTime)
    
    # Relationships
    sales = db.relationship('VehicleSale', backref='vehicle', lazy='dynamic')
    inspections = db.relationship('VehicleInspection', backref='vehicle', lazy='dynamic')
    
    def __repr__(self):
        return f'<Vehicle {self.year} {self.model.full_name}>'
    
    @property
    def full_name(self):
        return f"{self.year} {self.model.full_name} {self.trim or ''}".strip()
    
    @property
    def is_available(self):
        return self.status == 'available'
    
    def to_dict(self):
        return {
            'id': self.id,
            'vin': self.vin,
            'stock_number': self.stock_number,
            'full_name': self.full_name,
            'year': self.year,
            'make': self.model.make.name,
            'model': self.model.name,
            'trim': self.trim,
            'condition': self.condition,
            'status': self.status,
            'selling_price': float(self.selling_price) if self.selling_price else None,
            'currency': self.currency,
            'mileage': self.mileage,
            'exterior_color': self.exterior_color,
            'interior_color': self.interior_color,
            'features': self.features,
            'images': self.images,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class VehicleSale(db.Model):
    """Vehicle Sales Records"""
    
    __tablename__ = 'vehicle_sales'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Sale Information
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    salesperson_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Financial Details
    sale_price = db.Column(db.Numeric(12, 2), nullable=False)
    trade_in_value = db.Column(db.Numeric(12, 2), default=0)
    down_payment = db.Column(db.Numeric(12, 2), default=0)
    financing_amount = db.Column(db.Numeric(12, 2), default=0)
    tax_amount = db.Column(db.Numeric(12, 2), default=0)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), default='NGN')
    
    # Payment and Financing
    payment_method = db.Column(db.String(50))  # cash, financing, lease
    financing_term_months = db.Column(db.Integer)
    interest_rate = db.Column(db.Float)
    monthly_payment = db.Column(db.Numeric(10, 2))
    
    # Sale Status
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    contract_signed = db.Column(db.Boolean, default=False)
    
    # Documents
    contract_url = db.Column(db.String(255))
    title_url = db.Column(db.String(255))
    registration_url = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='vehicle_purchases')
    salesperson = db.relationship('User', foreign_keys=[salesperson_id], backref='vehicle_sales')
    
    def __repr__(self):
        return f'<VehicleSale {self.vehicle.full_name} - {self.customer.full_name}>'

class VehicleInspection(db.Model):
    """Vehicle Inspection Records"""
    
    __tablename__ = 'vehicle_inspections'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    inspector_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Inspection Details
    inspection_type = db.Column(db.String(50), nullable=False)  # pre-sale, trade-in, routine
    overall_condition = db.Column(db.String(20))  # excellent, good, fair, poor
    mileage_at_inspection = db.Column(db.Integer)
    
    # Inspection Results
    exterior_condition = db.Column(db.String(20))
    interior_condition = db.Column(db.String(20))
    engine_condition = db.Column(db.String(20))
    transmission_condition = db.Column(db.String(20))
    
    # Issues and Notes
    issues_found = db.Column(db.JSON)  # List of issues
    recommendations = db.Column(db.Text)
    repair_estimates = db.Column(db.JSON)  # Estimated repair costs
    
    # Media
    inspection_photos = db.Column(db.JSON)  # Array of photo URLs
    
    # Timestamps
    inspection_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    inspector = db.relationship('User', backref='vehicle_inspections')
    
    def __repr__(self):
        return f'<VehicleInspection {self.vehicle.full_name} - {self.inspection_date.strftime("%Y-%m-%d")}>'


class MaintenanceRequest(db.Model):
    """Vehicle Maintenance Service Requests"""
    
    __tablename__ = 'maintenance_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Customer Information
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Vehicle Information
    vehicle_make = db.Column(db.String(100), nullable=False)
    vehicle_model = db.Column(db.String(100), nullable=False)
    vehicle_year = db.Column(db.Integer, nullable=False)
    license_plate = db.Column(db.String(20))
    mileage = db.Column(db.Integer)
    
    # Service Details
    service_type = db.Column(db.String(100), nullable=False)  # oil_change, brake_service, engine_repair, etc.
    service_category = db.Column(db.String(50), nullable=False)  # routine, repair, emergency
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, emergency
    
    # Scheduling
    preferred_date = db.Column(db.Date)
    preferred_time = db.Column(db.String(20))
    estimated_duration = db.Column(db.Integer)  # in hours
    
    # Contact Information
    contact_phone = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(120))
    pickup_required = db.Column(db.Boolean, default=False)
    pickup_address = db.Column(db.Text)
    
    # Assignment
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    service_center_id = db.Column(db.Integer, db.ForeignKey('service_centers.id'))
    
    # Status and Progress
    status = db.Column(db.String(20), default='pending')  # pending, assigned, in_progress, completed, cancelled
    progress_notes = db.Column(db.JSON)  # Array of progress updates
    
    # Pricing
    estimated_cost = db.Column(db.Numeric(10, 2))
    final_cost = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='NGN')
    
    # Files and Images
    attachments = db.Column(db.JSON)  # Array of file URLs
    before_photos = db.Column(db.JSON)  # Photos before service
    after_photos = db.Column(db.JSON)  # Photos after service
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scheduled_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='maintenance_requests')
    assigned_staff = db.relationship('User', foreign_keys=[assigned_staff_id], backref='assigned_maintenance_requests')
    
    def __repr__(self):
        return f'<MaintenanceRequest {self.request_number} - {self.service_type}>'
    
    @property
    def vehicle_info(self):
        return f"{self.vehicle_year} {self.vehicle_make} {self.vehicle_model}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_number': self.request_number,
            'vehicle_info': self.vehicle_info,
            'service_type': self.service_type,
            'service_category': self.service_category,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'preferred_date': self.preferred_date.isoformat() if self.preferred_date else None,
            'estimated_cost': float(self.estimated_cost) if self.estimated_cost else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class InsuranceRequest(db.Model):
    """Vehicle Insurance Service Requests"""
    
    __tablename__ = 'insurance_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Customer Information
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Vehicle Information
    vehicle_make = db.Column(db.String(100), nullable=False)
    vehicle_model = db.Column(db.String(100), nullable=False)
    vehicle_year = db.Column(db.Integer, nullable=False)
    license_plate = db.Column(db.String(20))
    vin = db.Column(db.String(17))
    vehicle_value = db.Column(db.Numeric(12, 2))
    
    # Insurance Details
    insurance_type = db.Column(db.String(50), nullable=False)  # comprehensive, third_party, commercial
    coverage_type = db.Column(db.String(50), nullable=False)  # new_policy, renewal, claim
    current_insurer = db.Column(db.String(100))
    current_policy_number = db.Column(db.String(50))
    previous_claims = db.Column(db.Boolean, default=False)
    
    # Coverage Requirements
    coverage_amount = db.Column(db.Numeric(12, 2))
    deductible_preference = db.Column(db.Numeric(10, 2))
    additional_coverage = db.Column(db.JSON)  # Array of additional coverage types
    
    # Personal Information
    driver_license_number = db.Column(db.String(50))
    years_of_experience = db.Column(db.Integer)
    age = db.Column(db.Integer)
    previous_accidents = db.Column(db.Boolean, default=False)
    accident_details = db.Column(db.Text)
    
    # Contact Information
    contact_phone = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(120))
    preferred_contact_method = db.Column(db.String(20), default='phone')
    
    # Assignment
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    insurance_provider = db.Column(db.String(100))
    
    # Status and Progress
    status = db.Column(db.String(20), default='pending')  # pending, processing, quoted, approved, rejected, completed
    progress_notes = db.Column(db.JSON)  # Array of progress updates
    
    # Pricing
    quoted_premium = db.Column(db.Numeric(10, 2))
    final_premium = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='NGN')
    payment_frequency = db.Column(db.String(20))  # monthly, quarterly, annually
    
    # Files and Documents
    documents = db.Column(db.JSON)  # Array of document URLs
    vehicle_photos = db.Column(db.JSON)  # Vehicle photos for assessment
    
    # Policy Information
    policy_number = db.Column(db.String(50))
    policy_start_date = db.Column(db.Date)
    policy_end_date = db.Column(db.Date)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    quoted_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='insurance_requests')
    assigned_staff = db.relationship('User', foreign_keys=[assigned_staff_id], backref='assigned_insurance_requests')
    
    def __repr__(self):
        return f'<InsuranceRequest {self.request_number} - {self.insurance_type}>'
    
    @property
    def vehicle_info(self):
        return f"{self.vehicle_year} {self.vehicle_make} {self.vehicle_model}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_number': self.request_number,
            'vehicle_info': self.vehicle_info,
            'insurance_type': self.insurance_type,
            'coverage_type': self.coverage_type,
            'status': self.status,
            'quoted_premium': float(self.quoted_premium) if self.quoted_premium else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class VehicleRegistrationRequest(db.Model):
    """Vehicle Registration and License Plate Service Requests"""
    
    __tablename__ = 'vehicle_registration_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Customer Information
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Request Type
    registration_type = db.Column(db.String(50), nullable=False)  # 'new_registration', 'renewal'
    
    # Vehicle Information
    vehicle_make = db.Column(db.String(100), nullable=False)
    vehicle_model = db.Column(db.String(100), nullable=False)
    vehicle_year = db.Column(db.Integer, nullable=False)
    vehicle_color = db.Column(db.String(50), nullable=False)
    engine_number = db.Column(db.String(100))
    chassis_number = db.Column(db.String(100))
    
    # For Renewals
    current_registration_number = db.Column(db.String(20))  # For renewals
    expiry_date = db.Column(db.Date)  # Current registration expiry
    
    # Owner Information
    owner_name = db.Column(db.String(200), nullable=False)
    owner_address = db.Column(db.Text, nullable=False)
    owner_phone = db.Column(db.String(20), nullable=False)
    owner_email = db.Column(db.String(120))
    owner_state = db.Column(db.String(50), nullable=False)
    owner_lga = db.Column(db.String(100), nullable=False)
    
    # Vehicle Use
    vehicle_purpose = db.Column(db.String(50), nullable=False)  # 'private', 'commercial', 'government'
    
    # Documentation Status
    purchase_receipt = db.Column(db.Boolean, default=False)
    customs_papers = db.Column(db.Boolean, default=False)
    insurance_certificate = db.Column(db.Boolean, default=False)
    roadworthiness_certificate = db.Column(db.Boolean, default=False)
    driver_license = db.Column(db.Boolean, default=False)
    
    # Processing Information
    service_center = db.Column(db.String(100))
    processing_priority = db.Column(db.String(20), default='standard')  # 'standard', 'express', 'same_day'
    
    # Contact Information
    contact_phone = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(120))
    pickup_required = db.Column(db.Boolean, default=False)
    pickup_address = db.Column(db.Text)
    
    # Assignment
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Status and Progress
    status = db.Column(db.String(30), default='submitted')  # 'submitted', 'documents_review', 'processing', 'production', 'ready', 'completed', 'cancelled'
    progress_notes = db.Column(db.JSON)  # Array of progress updates
    
    # Processing Milestones
    documents_verified_at = db.Column(db.DateTime)
    frsc_approved_at = db.Column(db.DateTime)
    plate_produced_at = db.Column(db.DateTime)
    ready_for_pickup_at = db.Column(db.DateTime)
    
    # Pricing
    service_fee = db.Column(db.Numeric(10, 2))
    government_fee = db.Column(db.Numeric(10, 2))
    processing_fee = db.Column(db.Numeric(10, 2))
    total_amount = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='NGN')
    payment_status = db.Column(db.String(20), default='pending')  # 'pending', 'paid', 'partial', 'refunded'
    
    # Generated Information
    new_registration_number = db.Column(db.String(20))  # Generated registration number
    plate_number = db.Column(db.String(20))  # Generated plate number
    
    # Files and Documents
    uploaded_documents = db.Column(db.JSON)  # Array of uploaded document URLs
    generated_documents = db.Column(db.JSON)  # Generated certificates, receipts
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='vehicle_registration_requests')
    assigned_staff = db.relationship('User', foreign_keys=[assigned_staff_id], backref='assigned_registration_requests')
    
    def __init__(self, **kwargs):
        super(VehicleRegistrationRequest, self).__init__(**kwargs)
        if not self.request_number:
            self.request_number = self.generate_request_number()
    
    @staticmethod
    def generate_request_number():
        """Generate unique request number"""
        from datetime import datetime
        import uuid
        prefix = "VR"
        timestamp = datetime.now().strftime("%y%m%d")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<VehicleRegistrationRequest {self.request_number} - {self.registration_type}>'
    
    @property
    def vehicle_info(self):
        return f"{self.vehicle_year} {self.vehicle_make} {self.vehicle_model} ({self.vehicle_color})"
    
    @property
    def is_new_registration(self):
        return self.registration_type == 'new_registration'
    
    @property
    def is_renewal(self):
        return self.registration_type == 'renewal'
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_number': self.request_number,
            'registration_type': self.registration_type,
            'vehicle_info': self.vehicle_info,
            'owner_name': self.owner_name,
            'status': self.status,
            'processing_priority': self.processing_priority,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'payment_status': self.payment_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }