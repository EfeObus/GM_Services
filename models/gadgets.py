"""
Gadgets and Accessories Models
Extended product models for specific gadget categories (smartphones, laptops, accessories)
"""
from database import db
from datetime import datetime
from decimal import Decimal
from models.ecommerce import Product


class Smartphone(db.Model):
    """Smartphone specific model extending Product"""
    
    __tablename__ = 'smartphones'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, unique=True)
    
    # Operating System
    operating_system = db.Column(db.String(50))  # Android, iOS
    os_version = db.Column(db.String(50))
    
    # Storage & Memory
    storage_options = db.Column(db.JSON)  # [64, 128, 256, 512] GB
    ram = db.Column(db.String(20))  # 4GB, 6GB, 8GB, 12GB
    expandable_storage = db.Column(db.Boolean, default=False)
    max_storage_expansion = db.Column(db.String(20))  # 1TB
    
    # Camera Specifications
    rear_camera = db.Column(db.String(100))  # "48MP + 12MP + 5MP"
    front_camera = db.Column(db.String(50))  # "16MP"
    camera_features = db.Column(db.JSON)  # ["Night mode", "Portrait", "4K video"]
    
    # Battery & Performance
    battery_capacity = db.Column(db.String(20))  # "4000mAh"
    fast_charging = db.Column(db.String(50))  # "65W fast charging"
    wireless_charging = db.Column(db.Boolean, default=False)
    processor = db.Column(db.String(100))  # "Snapdragon 888"
    
    # Display
    screen_size = db.Column(db.String(20))  # "6.7 inches"
    display_type = db.Column(db.String(50))  # "AMOLED"
    resolution = db.Column(db.String(50))  # "2400 x 1080"
    refresh_rate = db.Column(db.String(20))  # "120Hz"
    
    # Connectivity
    network_support = db.Column(db.JSON)  # ["5G", "4G LTE", "3G"]
    dual_sim = db.Column(db.Boolean, default=False)
    bluetooth_version = db.Column(db.String(20))  # "5.2"
    wifi_standards = db.Column(db.JSON)  # ["Wi-Fi 6", "Wi-Fi 5"]
    
    # Physical Features
    water_resistance = db.Column(db.String(20))  # "IP68"
    biometric_features = db.Column(db.JSON)  # ["Fingerprint", "Face unlock"]
    build_material = db.Column(db.String(100))  # "Aluminum frame, glass back"
    
    # Warranty & Support
    warranty_status = db.Column(db.String(20), default='original')  # original, refurbished
    included_accessories = db.Column(db.JSON)  # ["Charger", "USB Cable", "Earphones"]
    trade_in_eligible = db.Column(db.Boolean, default=True)
    
    # Relationships
    product = db.relationship('Product', backref=db.backref('smartphone_details', uselist=False))
    
    def __repr__(self):
        return f'<Smartphone {self.product.name}>'


class Laptop(db.Model):
    """Laptop and PC specific model extending Product"""
    
    __tablename__ = 'laptops'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, unique=True)
    
    # Type
    device_type = db.Column(db.String(50))  # laptop, desktop, all-in-one
    form_factor = db.Column(db.String(50))  # ultrabook, gaming, business, 2-in-1
    
    # Processor
    processor_brand = db.Column(db.String(50))  # Intel, AMD, Apple
    processor_model = db.Column(db.String(100))  # "Intel Core i7-12700H"
    processor_generation = db.Column(db.String(20))  # "12th Gen"
    cores = db.Column(db.String(20))  # "8 cores, 16 threads"
    base_clock = db.Column(db.String(20))  # "2.3 GHz"
    boost_clock = db.Column(db.String(20))  # "4.7 GHz"
    
    # Memory & Storage
    ram_size = db.Column(db.String(20))  # "16GB"
    ram_type = db.Column(db.String(20))  # "DDR4", "DDR5"
    ram_speed = db.Column(db.String(20))  # "3200MHz"
    max_ram_capacity = db.Column(db.String(20))  # "64GB"
    storage_type = db.Column(db.String(50))  # "SSD", "HDD", "SSD + HDD"
    storage_capacity = db.Column(db.String(50))  # "512GB SSD"
    additional_storage_slots = db.Column(db.Boolean, default=False)
    
    # Graphics
    graphics_type = db.Column(db.String(20))  # "Dedicated", "Integrated"
    graphics_card = db.Column(db.String(100))  # "NVIDIA RTX 4060"
    graphics_memory = db.Column(db.String(20))  # "8GB GDDR6"
    
    # Display
    screen_size = db.Column(db.String(20))  # "15.6 inches"
    resolution = db.Column(db.String(50))  # "1920 x 1080"
    display_type = db.Column(db.String(50))  # "IPS", "OLED"
    refresh_rate = db.Column(db.String(20))  # "144Hz"
    color_gamut = db.Column(db.String(50))  # "100% sRGB"
    touchscreen = db.Column(db.Boolean, default=False)
    
    # Operating System
    operating_system = db.Column(db.String(50))  # "Windows 11", "macOS", "Linux"
    os_edition = db.Column(db.String(50))  # "Home", "Pro"
    pre_installed_software = db.Column(db.JSON)  # ["Microsoft Office", "Adobe Creative Suite"]
    
    # Connectivity & Ports
    wifi_standard = db.Column(db.String(20))  # "Wi-Fi 6E"
    bluetooth_version = db.Column(db.String(20))  # "5.3"
    ethernet_port = db.Column(db.Boolean, default=True)
    usb_ports = db.Column(db.JSON)  # {"USB-A": 2, "USB-C": 2, "Thunderbolt": 1}
    hdmi_ports = db.Column(db.Integer, default=1)
    audio_jack = db.Column(db.Boolean, default=True)
    sd_card_slot = db.Column(db.Boolean, default=False)
    
    # Battery & Power
    battery_capacity = db.Column(db.String(20))  # "80Wh"
    battery_life = db.Column(db.String(50))  # "Up to 10 hours"
    power_adapter = db.Column(db.String(50))  # "65W USB-C"
    
    # Physical Attributes
    keyboard_type = db.Column(db.String(50))  # "Backlit", "RGB", "Mechanical"
    trackpad_features = db.Column(db.JSON)  # ["Precision trackpad", "Windows Hello"]
    biometric_features = db.Column(db.JSON)  # ["Fingerprint reader", "IR camera"]
    webcam_resolution = db.Column(db.String(20))  # "1080p"
    
    # Use Cases
    primary_use_case = db.Column(db.String(50))  # "Gaming", "Business", "Creative", "Student"
    target_audience = db.Column(db.JSON)  # ["Professionals", "Gamers", "Students"]
    
    # Support & Warranty
    technical_support_included = db.Column(db.Boolean, default=True)
    support_duration = db.Column(db.String(50))  # "1 year premium support"
    
    # Relationships
    product = db.relationship('Product', backref=db.backref('laptop_details', uselist=False))
    
    def __repr__(self):
        return f'<Laptop {self.product.name}>'


class Accessory(db.Model):
    """Tech Accessories model extending Product"""
    
    __tablename__ = 'accessories'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, unique=True)
    
    # Accessory Category
    accessory_type = db.Column(db.String(50))  # "headphones", "power_bank", "case", "smartwatch"
    sub_category = db.Column(db.String(50))  # "wireless_earbuds", "phone_case", "laptop_charger"
    
    # Compatibility
    compatible_devices = db.Column(db.JSON)  # ["iPhone 13", "Samsung Galaxy S23", "MacBook Pro"]
    compatibility_type = db.Column(db.String(50))  # "Universal", "Brand Specific", "Model Specific"
    device_categories = db.Column(db.JSON)  # ["Smartphones", "Laptops", "Tablets"]
    
    # Physical Properties
    material = db.Column(db.String(100))  # "Aluminum", "Silicone", "Leather"
    durability_rating = db.Column(db.String(20))  # "IP67", "Military Grade"
    color_options = db.Column(db.JSON)  # ["Black", "White", "Blue", "Red"]
    
    # Special Features (dynamic based on accessory type)
    special_features = db.Column(db.JSON)  # Tech-specific features
    
    # Power & Battery (for powered accessories)
    battery_capacity = db.Column(db.String(20))  # "10000mAh" for power banks
    charging_speed = db.Column(db.String(50))  # "18W fast charging"
    wireless_charging = db.Column(db.Boolean, default=False)
    
    # Audio Features (for audio accessories)
    audio_features = db.Column(db.JSON)  # ["Noise Cancellation", "Transparency Mode"]
    driver_size = db.Column(db.String(20))  # "40mm"
    frequency_response = db.Column(db.String(50))  # "20Hz - 20kHz"
    impedance = db.Column(db.String(20))  # "32 ohms"
    
    # Connectivity (for wireless accessories)
    connectivity_type = db.Column(db.JSON)  # ["Bluetooth 5.0", "USB-C", "Lightning"]
    wireless_range = db.Column(db.String(20))  # "10 meters"
    
    # Protection Features (for cases and protectors)
    protection_level = db.Column(db.String(50))  # "Drop protection up to 2m"
    screen_protection = db.Column(db.Boolean, default=False)
    waterproof = db.Column(db.Boolean, default=False)
    
    # Smart Features (for smartwatches and smart accessories)
    smart_features = db.Column(db.JSON)  # ["Heart rate monitor", "GPS", "Sleep tracking"]
    app_compatibility = db.Column(db.JSON)  # ["iOS", "Android"]
    
    # Relationships
    product = db.relationship('Product', backref=db.backref('accessory_details', uselist=False))
    
    def __repr__(self):
        return f'<Accessory {self.product.name}>'

    def get_type_specific_features(self):
        """Get features specific to accessory type"""
        type_features = {
            'headphones': ['audio_features', 'driver_size', 'frequency_response'],
            'power_bank': ['battery_capacity', 'charging_speed', 'wireless_charging'],
            'case': ['protection_level', 'material', 'waterproof'],
            'smartwatch': ['smart_features', 'battery_capacity', 'app_compatibility'],
            'charger': ['charging_speed', 'compatibility_type', 'connectivity_type']
        }
        return type_features.get(self.accessory_type, [])


class ProductImage(db.Model):
    """Product Images for detailed product media"""
    
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Image Details
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(255))
    
    # Image Properties
    image_type = db.Column(db.String(50))  # "front", "back", "side", "detail", "lifestyle"
    is_primary = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    
    # File Properties
    file_size = db.Column(db.Integer)  # in bytes
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    mime_type = db.Column(db.String(50))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref=db.backref('detailed_images', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ProductImage {self.filename}>'

    @property
    def image_url(self):
        """Get full URL for the image"""
        return f"/static/uploads/{self.filename}"