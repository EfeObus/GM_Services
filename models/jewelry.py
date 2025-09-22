"""
Luxury Jewelry Store Models
Handles jewelry catalog, product management, and luxury sales transactions
"""
from database import db
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

class JewelryCategory(db.Model):
    """Jewelry product categories"""
    
    __tablename__ = 'jewelry_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    
    # Category Hierarchy
    parent_category_id = db.Column(db.Integer, db.ForeignKey('jewelry_categories.id'))
    
    # Display
    display_order = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(255))  # Category icon URL
    banner_image = db.Column(db.String(255))  # Category banner image
    
    # SEO
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.Text)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('JewelryCategory', remote_side=[id], backref='subcategories')
    jewelry_items = db.relationship('JewelryItem', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<JewelryCategory {self.name}>'

class JewelryMaterial(db.Model):
    """Materials used in jewelry (gold, silver, platinum, etc.)"""
    
    __tablename__ = 'jewelry_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    material_type = db.Column(db.String(50))  # metal, gemstone, organic
    
    # Properties
    purity_levels = db.Column(db.JSON)  # Available purity levels (e.g., 14k, 18k, 24k)
    color_variants = db.Column(db.JSON)  # Available colors
    
    # Pricing
    current_price_per_gram = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='NGN')
    price_volatility = db.Column(db.String(20))  # stable, moderate, high
    
    # Physical Properties
    density = db.Column(db.Float)
    hardness_scale = db.Column(db.String(20))  # Mohs scale for gemstones
    
    # Care Instructions
    care_instructions = db.Column(db.Text)
    cleaning_methods = db.Column(db.JSON)
    
    # Certification
    requires_certification = db.Column(db.Boolean, default=False)
    certification_authorities = db.Column(db.JSON)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<JewelryMaterial {self.name}>'

class JewelryBrand(db.Model):
    """Jewelry brands and designers"""
    
    __tablename__ = 'jewelry_brands'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    brand_story = db.Column(db.Text)
    
    # Brand Details
    country_of_origin = db.Column(db.String(100))
    founded_year = db.Column(db.Integer)
    founder_name = db.Column(db.String(200))
    
    # Contact Information
    website = db.Column(db.String(255))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    
    # Visual Identity
    logo_url = db.Column(db.String(255))
    brand_colors = db.Column(db.JSON)
    signature_style = db.Column(db.Text)
    
    # Certifications and Awards
    certifications = db.Column(db.JSON)
    awards = db.Column(db.JSON)
    
    # Business Details
    is_luxury_brand = db.Column(db.Boolean, default=False)
    price_range = db.Column(db.String(50))  # budget, mid-range, luxury, ultra-luxury
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jewelry_items = db.relationship('JewelryItem', backref='brand', lazy='dynamic')
    
    def __repr__(self):
        return f'<JewelryBrand {self.name}>'

class JewelryItem(db.Model):
    """Individual jewelry items/products"""
    
    __tablename__ = 'jewelry_items'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    detailed_description = db.Column(db.Text)
    
    # Categorization
    category_id = db.Column(db.Integer, db.ForeignKey('jewelry_categories.id'), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('jewelry_brands.id'))
    
    # Product Type
    jewelry_type = db.Column(db.String(50))  # ring, necklace, earrings, bracelet, watch
    sub_type = db.Column(db.String(50))  # engagement_ring, pendant, stud_earrings
    
    # Materials and Specifications
    primary_material_id = db.Column(db.Integer, db.ForeignKey('jewelry_materials.id'))
    secondary_materials = db.Column(db.JSON)  # Additional materials with quantities
    
    # Gemstones
    primary_gemstone = db.Column(db.String(100))
    gemstone_details = db.Column(db.JSON)  # Cut, color, clarity, carat weight
    accent_gemstones = db.Column(db.JSON)  # Additional gemstones
    
    # Physical Specifications
    weight = db.Column(db.Float)  # Weight in grams
    dimensions = db.Column(db.JSON)  # Length, width, height
    size_options = db.Column(db.JSON)  # Available sizes
    
    # Design Details
    design_style = db.Column(db.String(100))  # vintage, modern, classic, contemporary
    occasion = db.Column(db.JSON)  # wedding, engagement, casual, formal
    gender_target = db.Column(db.String(20))  # men, women, unisex, children
    
    # Pricing
    base_price = db.Column(db.Numeric(12, 2), nullable=False)
    sale_price = db.Column(db.Numeric(12, 2))
    cost_price = db.Column(db.Numeric(12, 2))
    currency = db.Column(db.String(3), default='NGN')
    
    # Pricing Factors
    material_cost = db.Column(db.Numeric(10, 2))
    labor_cost = db.Column(db.Numeric(8, 2))
    design_cost = db.Column(db.Numeric(6, 2))
    markup_percentage = db.Column(db.Float)
    
    # Inventory
    stock_quantity = db.Column(db.Integer, default=0)
    reserved_quantity = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=2)
    low_stock_threshold = db.Column(db.Integer, default=2)
    max_stock_level = db.Column(db.Integer)
    
    # Product Images
    primary_image = db.Column(db.String(255))
    additional_images = db.Column(db.JSON)  # Array of image URLs
    video_url = db.Column(db.String(255))
    view_360_images = db.Column(db.JSON)  # 360-degree view images
    
    # Certifications
    authenticity_certificate = db.Column(db.String(255))
    appraisal_certificate = db.Column(db.String(255))
    gemstone_certificates = db.Column(db.JSON)
    
    # Care and Maintenance
    care_instructions = db.Column(db.Text)
    warranty_period_months = db.Column(db.Integer, default=12)
    warranty_terms = db.Column(db.Text)
    
    # Customization
    is_customizable = db.Column(db.Boolean, default=False)
    customization_options = db.Column(db.JSON)
    custom_order_lead_time = db.Column(db.Integer)  # Days
    
    # SEO and Marketing
    slug = db.Column(db.String(200), unique=True)
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.Text)
    tags = db.Column(db.JSON)  # Search tags
    
    # Status and Visibility
    status = db.Column(db.String(30), default='active')  # active, inactive, discontinued
    is_featured = db.Column(db.Boolean, default=False)
    is_bestseller = db.Column(db.Boolean, default=False)
    is_new_arrival = db.Column(db.Boolean, default=False)
    
    # Analytics
    view_count = db.Column(db.Integer, default=0)
    wishlist_count = db.Column(db.Integer, default=0)
    total_sales = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    primary_material = db.relationship('JewelryMaterial', backref='primary_jewelry_items')
    order_items = db.relationship('JewelryOrderItem', backref='jewelry_item', lazy='dynamic')
    reviews = db.relationship('JewelryReview', backref='jewelry_item', lazy='dynamic')
    
    def __repr__(self):
        return f'<JewelryItem {self.sku} - {self.name}>'
    
    @property
    def current_price(self):
        """Get current selling price (sale price if available, otherwise base price)"""
        return self.sale_price if self.sale_price else self.base_price
    
    @property
    def is_on_sale(self):
        """Check if item is currently on sale"""
        return self.sale_price is not None and self.sale_price < self.base_price
    
    @property
    def available_stock(self):
        """Get available stock (total - reserved)"""
        return max(0, self.stock_quantity - self.reserved_quantity)
    
    @property
    def is_in_stock(self):
        """Check if item is in stock"""
        return self.available_stock > 0
    
    @property
    def is_low_stock(self):
        """Check if item is at or below low stock threshold"""
        return self.available_stock <= self.low_stock_threshold
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.filter(JewelryReview.rating.isnot(None)).all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)

class JewelryOrder(db.Model):
    """Jewelry orders"""
    
    __tablename__ = 'jewelry_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Customer Information
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Order Details
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    order_type = db.Column(db.String(30), default='standard')  # standard, custom, rush
    
    # Shipping Information
    shipping_address = db.Column(db.JSON)
    billing_address = db.Column(db.JSON)
    shipping_method = db.Column(db.String(50))
    
    # Order Totals
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(8, 2), default=0)
    shipping_cost = db.Column(db.Numeric(6, 2), default=0)
    insurance_cost = db.Column(db.Numeric(6, 2), default=0)
    discount_amount = db.Column(db.Numeric(8, 2), default=0)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), default='NGN')
    
    # Payment Information
    payment_status = db.Column(db.String(30), default='pending')  # pending, paid, partial, refunded
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(100))
    payment_date = db.Column(db.DateTime)
    
    # Order Status
    status = db.Column(db.String(30), default='pending')  # pending, confirmed, processing, shipped, delivered, cancelled
    
    # Processing Timeline
    confirmed_date = db.Column(db.DateTime)
    processing_started_date = db.Column(db.DateTime)
    shipped_date = db.Column(db.DateTime)
    delivered_date = db.Column(db.DateTime)
    estimated_delivery_date = db.Column(db.Date)
    
    # Special Instructions
    customer_notes = db.Column(db.Text)
    gift_message = db.Column(db.Text)
    special_instructions = db.Column(db.Text)
    
    # Gift Options
    is_gift = db.Column(db.Boolean, default=False)
    gift_wrap = db.Column(db.Boolean, default=False)
    gift_receipt = db.Column(db.Boolean, default=False)
    
    # Tracking
    tracking_number = db.Column(db.String(100))
    carrier = db.Column(db.String(100))
    
    # Insurance and Security
    is_insured = db.Column(db.Boolean, default=False)
    insurance_value = db.Column(db.Numeric(12, 2))
    requires_signature = db.Column(db.Boolean, default=True)
    
    # Customer Service
    customer_service_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('User', backref='jewelry_orders')
    order_items = db.relationship('JewelryOrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(JewelryOrder, self).__init__(**kwargs)
        if not self.order_number:
            self.order_number = self.generate_order_number()
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number"""
        prefix = "JWL"
        timestamp = datetime.now().strftime("%y%m")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<JewelryOrder {self.order_number}>'

class JewelryOrderItem(db.Model):
    """Individual items in a jewelry order"""
    
    __tablename__ = 'jewelry_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('jewelry_orders.id'), nullable=False)
    jewelry_item_id = db.Column(db.Integer, db.ForeignKey('jewelry_items.id'), nullable=False)
    
    # Order Item Details
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    total_price = db.Column(db.Numeric(12, 2), nullable=False)
    
    # Customization
    customizations = db.Column(db.JSON)  # Applied customizations
    engraving_text = db.Column(db.String(200))
    special_requests = db.Column(db.Text)
    
    # Size and Specifications
    selected_size = db.Column(db.String(20))
    selected_material = db.Column(db.String(100))
    selected_gemstone = db.Column(db.String(100))
    
    # Status
    item_status = db.Column(db.String(30), default='pending')  # pending, confirmed, processing, ready, shipped
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<JewelryOrderItem {self.order.order_number} - {self.jewelry_item.name}>'

class JewelryReview(db.Model):
    """Customer reviews for jewelry items"""
    
    __tablename__ = 'jewelry_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    jewelry_item_id = db.Column(db.Integer, db.ForeignKey('jewelry_items.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('jewelry_orders.id'))
    
    # Review Content
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200))
    review_text = db.Column(db.Text)
    
    # Detailed Ratings
    quality_rating = db.Column(db.Integer)  # 1-5
    design_rating = db.Column(db.Integer)   # 1-5
    value_rating = db.Column(db.Integer)    # 1-5
    service_rating = db.Column(db.Integer)  # 1-5
    
    # Review Details
    would_recommend = db.Column(db.Boolean)
    verified_purchase = db.Column(db.Boolean, default=False)
    
    # Media
    review_images = db.Column(db.JSON)  # Customer photos
    review_videos = db.Column(db.JSON)  # Customer videos
    
    # Moderation
    is_approved = db.Column(db.Boolean, default=False)
    moderated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    moderation_notes = db.Column(db.Text)
    
    # Helpfulness
    helpful_votes = db.Column(db.Integer, default=0)
    total_votes = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='jewelry_reviews')
    moderator = db.relationship('User', foreign_keys=[moderated_by_id], backref='moderated_jewelry_reviews')
    order = db.relationship('JewelryOrder', backref='reviews')
    
    def __repr__(self):
        return f'<JewelryReview {self.jewelry_item.name} - {self.rating} stars>'
    
    @property
    def helpfulness_percentage(self):
        """Calculate helpfulness percentage"""
        if self.total_votes == 0:
            return 0
        return (self.helpful_votes / self.total_votes) * 100

class JewelryWishlist(db.Model):
    """Customer wishlists for jewelry items"""
    
    __tablename__ = 'jewelry_wishlists'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    jewelry_item_id = db.Column(db.Integer, db.ForeignKey('jewelry_items.id'), nullable=False)
    
    # Wishlist Details
    notes = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    
    # Notifications
    notify_on_sale = db.Column(db.Boolean, default=True)
    notify_on_restock = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('User', backref='jewelry_wishlist')
    jewelry_item = db.relationship('JewelryItem', backref='wishlist_entries')
    
    # Unique constraint to prevent duplicate wishlist entries
    __table_args__ = (db.UniqueConstraint('customer_id', 'jewelry_item_id', name='unique_customer_jewelry_wishlist'),)
    
    def __repr__(self):
        return f'<JewelryWishlist {self.customer.full_name} - {self.jewelry_item.name}>'

class JewelryPromotion(db.Model):
    """Promotions and discounts for jewelry items"""
    
    __tablename__ = 'jewelry_promotions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    promotion_code = db.Column(db.String(50), unique=True)
    
    # Promotion Type
    promotion_type = db.Column(db.String(50), nullable=False)  # percentage, fixed_amount, buy_one_get_one
    
    # Discount Details
    discount_percentage = db.Column(db.Float)
    discount_amount = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='NGN')
    
    # Validity
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    
    # Usage Limits
    max_uses = db.Column(db.Integer)
    max_uses_per_customer = db.Column(db.Integer, default=1)
    current_uses = db.Column(db.Integer, default=0)
    
    # Conditions
    minimum_order_amount = db.Column(db.Numeric(10, 2))
    applicable_categories = db.Column(db.JSON)  # Category IDs
    applicable_brands = db.Column(db.JSON)      # Brand IDs
    applicable_items = db.Column(db.JSON)       # Specific item IDs
    
    # Customer Eligibility
    customer_groups = db.Column(db.JSON)  # Eligible customer groups
    first_time_customers_only = db.Column(db.Boolean, default=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<JewelryPromotion {self.name}>'
    
    @property
    def is_valid(self):
        """Check if promotion is currently valid"""
        now = datetime.utcnow()
        return (self.is_active and 
                self.start_date <= now <= self.end_date and
                (self.max_uses is None or self.current_uses < self.max_uses))

class JewelryServiceRequest(db.Model):
    """Jewelry service requests for consultations, quotes, and collections"""
    
    __tablename__ = 'jewelry_service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Customer Information
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for guest requests
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    
    # Request Type
    request_type = db.Column(db.String(50), nullable=False)  # consultation, collection_view, quote_request
    
    # Consultation Details (for consultation requests)
    consultation_type = db.Column(db.String(50))  # custom_design, repair, appraisal, etc.
    jewelry_type = db.Column(db.String(50))  # ring, necklace, etc.
    preferred_metal = db.Column(db.String(50))
    preferred_gemstone = db.Column(db.String(50))
    budget_range = db.Column(db.String(50))
    occasion = db.Column(db.String(50))
    design_style = db.Column(db.String(50))
    timeline = db.Column(db.String(50))
    
    # Collection Viewing Details (for collection requests)
    collection_type = db.Column(db.String(50))  # gold, diamond, custom, all
    jewelry_types_interest = db.Column(db.String(100))
    viewing_preference = db.Column(db.String(50))  # catalog, appointment, virtual, photos
    preferred_date = db.Column(db.Date)
    preferred_time = db.Column(db.String(50))
    
    # Quote Details (for quote requests)
    quote_type = db.Column(db.String(50))  # purchase, custom_design, repair, appraisal
    item_description = db.Column(db.Text)
    metal_type = db.Column(db.String(50))
    gemstone_details = db.Column(db.Text)
    weight_grams = db.Column(db.Numeric(8, 2))
    dimensions = db.Column(db.String(100))
    
    # Description and Requirements
    description = db.Column(db.Text)
    additional_notes = db.Column(db.Text)
    special_requirements = db.Column(db.Text)
    
    # Engraving Details
    engraving_required = db.Column(db.Boolean, default=False)
    engraving_text = db.Column(db.String(100))
    size_known = db.Column(db.Boolean, default=False)
    ring_size = db.Column(db.String(10))
    
    # Contact Preferences
    preferred_contact_method = db.Column(db.String(20), default='email')
    preferred_contact_time = db.Column(db.String(50))
    
    # File Attachments
    reference_images = db.Column(db.JSON)  # List of uploaded image URLs
    item_images = db.Column(db.JSON)  # List of item image URLs
    
    # Request Status and Assignment
    status = db.Column(db.String(30), default='submitted')  # submitted, assigned, in_progress, quoted, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Assigned staff member
    assigned_department = db.Column(db.String(50), default='jewelry')
    
    # Response Details
    estimated_quote = db.Column(db.Numeric(12, 2))
    estimated_timeline = db.Column(db.String(100))
    response_notes = db.Column(db.Text)
    response_date = db.Column(db.DateTime)
    
    # Follow-up
    follow_up_required = db.Column(db.Boolean, default=True)
    follow_up_date = db.Column(db.DateTime)
    customer_satisfaction = db.Column(db.Integer)  # 1-5 rating
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='jewelry_requests')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_jewelry_requests')
    
    def __repr__(self):
        return f'<JewelryServiceRequest {self.request_number}>'
    
    @property
    def is_overdue(self):
        """Check if request is overdue for response"""
        if self.status in ['completed', 'cancelled']:
            return False
        
        # Different SLA based on request type
        sla_hours = {
            'quote_request': 24,
            'consultation': 48,
            'collection_view': 24
        }
        
        hours = sla_hours.get(self.request_type, 48)
        deadline = self.created_at + timedelta(hours=hours)
        return datetime.utcnow() > deadline
    
    def generate_request_number(self):
        """Generate unique request number"""
        if not self.request_number:
            prefix = {
                'consultation': 'JC',
                'collection_view': 'JV',
                'quote_request': 'JQ'
            }.get(self.request_type, 'JS')
            
            timestamp = datetime.utcnow().strftime('%Y%m%d')
            # Get count of requests today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            count = JewelryServiceRequest.query.filter(
                JewelryServiceRequest.created_at >= today_start,
                JewelryServiceRequest.request_type == self.request_type
            ).count() + 1
            
            self.request_number = f"{prefix}{timestamp}{count:03d}"

class JewelryCollection(db.Model):
    """Predefined jewelry collections (Gold, Diamond, Custom, etc.)"""
    
    __tablename__ = 'jewelry_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    detailed_description = db.Column(db.Text)
    
    # Collection Type
    collection_type = db.Column(db.String(50), nullable=False)  # gold, diamond, custom, mixed
    
    # Visual Elements
    banner_image = db.Column(db.String(255))
    gallery_images = db.Column(db.JSON)  # List of image URLs
    video_url = db.Column(db.String(255))
    
    # Collection Details
    featured_items = db.Column(db.JSON)  # List of featured item IDs
    price_range_min = db.Column(db.Numeric(12, 2))
    price_range_max = db.Column(db.Numeric(12, 2))
    currency = db.Column(db.String(3), default='NGN')
    
    # Features and Highlights
    key_features = db.Column(db.JSON)  # List of key features
    materials_used = db.Column(db.JSON)  # List of materials
    occasions = db.Column(db.JSON)  # Suitable occasions
    target_audience = db.Column(db.JSON)  # Target customer groups
    
    # SEO and Marketing
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.Text)
    tags = db.Column(db.JSON)
    
    # Display Settings
    display_order = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Availability
    available_for_viewing = db.Column(db.Boolean, default=True)
    requires_appointment = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<JewelryCollection {self.name}>'
    
    @property
    def formatted_price_range(self):
        """Get formatted price range string"""
        if self.price_range_min and self.price_range_max:
            return f"₦{self.price_range_min:,.0f} - ₦{self.price_range_max:,.0f}"
        elif self.price_range_min:
            return f"From ₦{self.price_range_min:,.0f}"
        else:
            return "Contact for Pricing"