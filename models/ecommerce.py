"""
E-commerce Models for Gadgets and Accessories
Handles technology products, inventory, orders, and e-commerce functionality
"""
from database import db
from datetime import datetime
from decimal import Decimal
import uuid

class ProductCategory(db.Model):
    """Product Categories for organizing gadgets and accessories"""
    
    __tablename__ = 'product_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    slug = db.Column(db.String(150), unique=True, index=True)
    
    # Category Hierarchy
    parent_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    level = db.Column(db.Integer, default=0)  # 0=top-level, 1=subcategory, etc.
    
    # Display Settings
    icon = db.Column(db.String(100))  # CSS class or icon name
    image_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    
    # SEO
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.String(500))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('ProductCategory', remote_side=[id], backref='children')
    products = db.relationship('Product', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<ProductCategory {self.name}>'
    
    @property
    def full_path(self):
        """Get full category path"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name

class ProductBrand(db.Model):
    """Product Brands/Manufacturers"""
    
    __tablename__ = 'product_brands'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(255))
    website = db.Column(db.String(255))
    country = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='brand', lazy='dynamic')
    
    def __repr__(self):
        return f'<ProductBrand {self.name}>'

class Product(db.Model):
    """Product Model for Gadgets and Accessories"""
    
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    short_description = db.Column(db.String(500))
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(255), unique=True, index=True)
    
    # Category and Brand
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('product_brands.id'))
    
    # Pricing
    price = db.Column(db.Numeric(10, 2), nullable=False)
    compare_price = db.Column(db.Numeric(10, 2))  # Original/strike-through price
    cost_price = db.Column(db.Numeric(10, 2))  # Cost to the business
    currency = db.Column(db.String(3), default='NGN')
    
    # Inventory
    stock_quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=2)
    track_inventory = db.Column(db.Boolean, default=True)
    allow_backorder = db.Column(db.Boolean, default=False)
    
    # Physical Attributes
    weight = db.Column(db.Float)  # in kg
    dimensions = db.Column(db.JSON)  # {length, width, height} in cm
    color = db.Column(db.String(50))
    model_number = db.Column(db.String(100))
    
    # Product Specifications
    specifications = db.Column(db.JSON)  # Key-value pairs of specs
    features = db.Column(db.JSON)  # Array of features
    whats_in_box = db.Column(db.JSON)  # Array of included items
    
    # Media
    images = db.Column(db.JSON)  # Array of image URLs
    videos = db.Column(db.JSON)  # Array of video URLs
    documents = db.Column(db.JSON)  # Array of document URLs (manuals, etc.)
    
    # Product Status
    status = db.Column(db.String(20), default='active')  # active, inactive, discontinued
    is_featured = db.Column(db.Boolean, default=False)
    is_digital = db.Column(db.Boolean, default=False)
    requires_shipping = db.Column(db.Boolean, default=True)
    
    # SEO and Marketing
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.String(500))
    tags = db.Column(db.JSON)  # Array of tags
    
    # Warranty and Support
    warranty_period = db.Column(db.String(50))  # e.g., "1 year", "6 months"
    warranty_description = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    reviews = db.relationship('ProductReview', backref='product', lazy='dynamic')
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0 or not self.track_inventory
    
    @property
    def is_low_stock(self):
        return self.track_inventory and self.stock_quantity <= self.low_stock_threshold
    
    @property
    def average_rating(self):
        ratings = [r.rating for r in self.reviews.filter(ProductReview.rating.isnot(None)).all()]
        return sum(ratings) / len(ratings) if ratings else 0
    
    @property
    def review_count(self):
        return self.reviews.count()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'short_description': self.short_description,
            'sku': self.sku,
            'slug': self.slug,
            'price': float(self.price),
            'compare_price': float(self.compare_price) if self.compare_price else None,
            'currency': self.currency,
            'stock_quantity': self.stock_quantity,
            'is_in_stock': self.is_in_stock,
            'is_low_stock': self.is_low_stock,
            'category': self.category.name,
            'brand': self.brand.name if self.brand else None,
            'specifications': self.specifications,
            'features': self.features,
            'images': self.images,
            'status': self.status,
            'is_featured': self.is_featured,
            'average_rating': self.average_rating,
            'review_count': self.review_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Order(db.Model):
    """Customer Orders"""
    
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Customer Information
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Order Status
    status = db.Column(db.String(30), default='pending')  # pending, confirmed, processing, shipped, delivered, cancelled
    payment_status = db.Column(db.String(30), default='pending')  # pending, paid, failed, refunded
    
    # Financial Details
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(8, 2), default=0)
    shipping_amount = db.Column(db.Numeric(8, 2), default=0)
    discount_amount = db.Column(db.Numeric(8, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='NGN')
    
    # Shipping Information
    shipping_address = db.Column(db.JSON)  # Full address object
    shipping_method = db.Column(db.String(50))
    tracking_number = db.Column(db.String(100))
    
    # Payment Information
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(100))
    
    # Notes and Comments
    customer_notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # Relationships
    customer = db.relationship('User', backref='orders')
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if not self.order_number:
            self.order_number = self.generate_order_number()
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number"""
        prefix = "GM"
        timestamp = datetime.now().strftime("%y%m")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    """Individual items within an order"""
    
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Item Details
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Product Snapshot (in case product details change)
    product_name = db.Column(db.String(200), nullable=False)
    product_sku = db.Column(db.String(50), nullable=False)
    product_image = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'

class ProductReview(db.Model):
    """Product Reviews and Ratings"""
    
    __tablename__ = 'product_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Review Content
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200))
    review_text = db.Column(db.Text)
    
    # Review Status
    is_verified_purchase = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)
    
    # Helpful Votes
    helpful_votes = db.Column(db.Integer, default=0)
    total_votes = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('User', backref='product_reviews')
    
    def __repr__(self):
        return f'<ProductReview {self.product.name} - {self.rating} stars>'
    
    @property
    def helpfulness_ratio(self):
        if self.total_votes == 0:
            return 0
        return (self.helpful_votes / self.total_votes) * 100

class ShoppingCart(db.Model):
    """Shopping Cart for logged-in users"""
    
    __tablename__ = 'shopping_carts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100))  # For anonymous users
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='shopping_cart', uselist=False)
    items = db.relationship('CartItem', backref='cart', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items)
    
    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items)
    
    def __repr__(self):
        return f'<ShoppingCart {self.user.email if self.user else self.session_id}>'

class CartItem(db.Model):
    """Items in shopping cart"""
    
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('shopping_carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Item Details
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product')
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price
    
    def __repr__(self):
        return f'<CartItem {self.product.name} x{self.quantity}>'