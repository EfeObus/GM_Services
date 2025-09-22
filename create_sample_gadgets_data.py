"""
Sample Data for Gadgets and Accessories
Creates initial product categories, brands, and sample products for testing
"""
from models.ecommerce import ProductCategory, ProductBrand, Product
from models.gadgets import Smartphone, Laptop, Accessory
from database import db
from decimal import Decimal

def create_sample_gadgets_data():
    """Create sample gadgets data for testing"""
    
    # Create product categories
    categories_data = [
        {
            'name': 'Smartphones',
            'slug': 'smartphones',
            'description': 'Latest smartphones with cutting-edge technology',
            'icon': 'fas fa-mobile-alt'
        },
        {
            'name': 'Laptops & PCs',
            'slug': 'laptops',
            'description': 'High-performance computers for work and gaming',
            'icon': 'fas fa-laptop'
        },
        {
            'name': 'Accessories',
            'slug': 'accessories',
            'description': 'Premium tech accessories',
            'icon': 'fas fa-headphones'
        }
    ]
    
    categories = {}
    for cat_data in categories_data:
        category = ProductCategory.query.filter_by(slug=cat_data['slug']).first()
        if not category:
            category = ProductCategory(**cat_data)
            db.session.add(category)
            db.session.flush()
        categories[cat_data['slug']] = category
    
    # Create product brands
    brands_data = [
        {'name': 'Apple', 'description': 'Premium technology products'},
        {'name': 'Samsung', 'description': 'Innovative mobile and computing solutions'},
        {'name': 'Dell', 'description': 'Professional computing solutions'},
        {'name': 'HP', 'description': 'Reliable computing and printing solutions'},
        {'name': 'Sony', 'description': 'Premium audio and electronics'},
        {'name': 'JBL', 'description': 'Professional audio equipment'},
        {'name': 'Anker', 'description': 'Reliable charging and power solutions'},
        {'name': 'Google', 'description': 'Smart technology products'},
        {'name': 'OnePlus', 'description': 'Never settle for less'},
        {'name': 'Lenovo', 'description': 'Smarter technology for all'}
    ]
    
    brands = {}
    for brand_data in brands_data:
        brand = ProductBrand.query.filter_by(name=brand_data['name']).first()
        if not brand:
            brand = ProductBrand(**brand_data)
            db.session.add(brand)
            db.session.flush()
        brands[brand_data['name']] = brand
    
    # Sample smartphones
    smartphones_data = [
        {
            'product': {
                'name': 'iPhone 15 Pro Max',
                'description': 'The ultimate iPhone with titanium design and advanced camera system',
                'short_description': 'Premium smartphone with titanium design and Pro camera system',
                'sku': 'IPH15PM256',
                'slug': 'iphone-15-pro-max',
                'price': Decimal('1299999'),
                'compare_price': Decimal('1399999'),
                'category_id': categories['smartphones'].id,
                'brand_id': brands['Apple'].id,
                'stock_quantity': 15,
                'is_featured': True,
                'features': [
                    'A17 Pro chip with 6-core GPU',
                    'Pro camera system with 5x Telephoto',
                    'Action button for quick controls',
                    'USB-C connector',
                    'Up to 29 hours video playback'
                ],
                'specifications': {
                    'Chip': 'A17 Pro',
                    'Display': '6.7-inch Super Retina XDR',
                    'Material': 'Titanium',
                    'Weight': '221 grams'
                },
                'whats_in_box': [
                    'iPhone 15 Pro Max',
                    'USB-C to USB-C Cable',
                    'Documentation'
                ],
                'images': [
                    'https://picsum.photos/600/400?random=101',
                    'https://picsum.photos/600/400?random=102',
                    'https://picsum.photos/600/400?random=103'
                ]
            },
            'smartphone': {
                'operating_system': 'iOS',
                'os_version': '17',
                'storage_options': [256, 512, 1024],
                'ram': '8GB',
                'rear_camera': '48MP Main + 12MP Ultra Wide + 12MP Telephoto',
                'front_camera': '12MP TrueDepth',
                'battery_capacity': '4441mAh',
                'screen_size': '6.7 inches',
                'display_type': 'Super Retina XDR OLED',
                'resolution': '2796 x 1290',
                'processor': 'A17 Pro',
                'network_support': ['5G', '4G LTE'],
                'water_resistance': 'IP68',
                'wireless_charging': True,
                'fast_charging': 'USB-C PD',
                'biometric_features': ['Face ID'],
                'warranty_status': 'original',
                'included_accessories': ['USB-C Cable', 'Documentation'],
                'trade_in_eligible': True
            }
        },
        {
            'product': {
                'name': 'Samsung Galaxy S24 Ultra',
                'description': 'Ultimate productivity and creativity with S Pen and AI features',
                'short_description': 'Premium Android smartphone with S Pen and AI capabilities',
                'sku': 'SGS24U512',
                'slug': 'samsung-galaxy-s24-ultra',
                'price': Decimal('999999'),
                'compare_price': Decimal('1099999'),
                'category_id': categories['smartphones'].id,
                'brand_id': brands['Samsung'].id,
                'stock_quantity': 25,
                'is_featured': True,
                'features': [
                    'Snapdragon 8 Gen 3 processor',
                    '200MP main camera with AI',
                    'Built-in S Pen',
                    '6.8-inch Dynamic AMOLED 2X',
                    '5000mAh battery with 45W charging'
                ],
                'specifications': {
                    'Processor': 'Snapdragon 8 Gen 3',
                    'Display': '6.8-inch Dynamic AMOLED 2X',
                    'S Pen': 'Built-in',
                    'Build': 'Titanium frame'
                },
                'whats_in_box': [
                    'Galaxy S24 Ultra',
                    'S Pen',
                    'USB-C Cable',
                    'SIM Ejector Tool',
                    'Quick Start Guide'
                ],
                'images': [
                    'https://picsum.photos/600/400?random=201',
                    'https://picsum.photos/600/400?random=202'
                ]
            },
            'smartphone': {
                'operating_system': 'Android',
                'os_version': '14',
                'storage_options': [256, 512, 1024],
                'ram': '12GB',
                'rear_camera': '200MP + 50MP + 12MP + 10MP',
                'front_camera': '12MP',
                'battery_capacity': '5000mAh',
                'screen_size': '6.8 inches',
                'display_type': 'Dynamic AMOLED 2X',
                'resolution': '3120 x 1440',
                'refresh_rate': '120Hz',
                'processor': 'Snapdragon 8 Gen 3',
                'network_support': ['5G', '4G LTE'],
                'water_resistance': 'IP68',
                'wireless_charging': True,
                'fast_charging': '45W Super Fast Charging',
                'biometric_features': ['Fingerprint', 'Face Recognition'],
                'warranty_status': 'original',
                'included_accessories': ['S Pen', 'USB-C Cable', 'SIM Tool'],
                'trade_in_eligible': True
            }
        }
    ]
    
    # Sample laptops
    laptops_data = [
        {
            'product': {
                'name': 'MacBook Pro 16-inch M3 Max',
                'description': 'Most powerful MacBook Pro ever with M3 Max chip',
                'short_description': 'Professional laptop with M3 Max chip for demanding workflows',
                'sku': 'MBP16M3MAX',
                'slug': 'macbook-pro-16-m3-max',
                'price': Decimal('2899999'),
                'compare_price': Decimal('3199999'),
                'category_id': categories['laptops'].id,
                'brand_id': brands['Apple'].id,
                'stock_quantity': 8,
                'is_featured': True,
                'features': [
                    'M3 Max chip with 16-core CPU',
                    '40-core GPU for extreme performance',
                    '128GB unified memory',
                    '16.2-inch Liquid Retina XDR display',
                    'Up to 22 hours battery life'
                ],
                'specifications': {
                    'Chip': 'Apple M3 Max',
                    'Memory': '128GB unified',
                    'Storage': '2TB SSD',
                    'Display': '16.2-inch Liquid Retina XDR'
                },
                'whats_in_box': [
                    'MacBook Pro',
                    'USB-C to MagSafe 3 Cable',
                    '140W USB-C Power Adapter'
                ],
                'images': [
                    'https://picsum.photos/600/400?random=301',
                    'https://picsum.photos/600/400?random=302'
                ]
            },
            'laptop': {
                'device_type': 'laptop',
                'form_factor': 'professional',
                'processor_brand': 'Apple',
                'processor_model': 'M3 Max',
                'cores': '16-core CPU',
                'ram_size': '128GB',
                'ram_type': 'Unified Memory',
                'storage_type': 'SSD',
                'storage_capacity': '2TB SSD',
                'graphics_type': 'Integrated',
                'graphics_card': '40-core GPU',
                'screen_size': '16.2 inches',
                'resolution': '3456 x 2234',
                'display_type': 'Liquid Retina XDR',
                'operating_system': 'macOS',
                'os_edition': 'Sonoma',
                'wifi_standard': 'Wi-Fi 6E',
                'bluetooth_version': '5.3',
                'usb_ports': {'USB-C': 4, 'Thunderbolt': 4},
                'hdmi_ports': 1,
                'audio_jack': True,
                'sd_card_slot': True,
                'battery_life': 'Up to 22 hours',
                'webcam_resolution': '1080p',
                'primary_use_case': 'Creative',
                'target_audience': ['Professionals', 'Creators'],
                'technical_support_included': True,
                'support_duration': '1 year AppleCare'
            }
        },
        {
            'product': {
                'name': 'Dell XPS 15 OLED',
                'description': 'Premium ultrabook with stunning OLED display',
                'short_description': 'High-performance ultrabook with OLED display and RTX graphics',
                'sku': 'DELLXPS15OLED',
                'slug': 'dell-xps-15-oled',
                'price': Decimal('1899999'),
                'compare_price': Decimal('2099999'),
                'category_id': categories['laptops'].id,
                'brand_id': brands['Dell'].id,
                'stock_quantity': 12,
                'features': [
                    'Intel 13th Gen Core i7 processor',
                    'NVIDIA RTX 4060 graphics',
                    '32GB DDR5 RAM',
                    '15.6-inch 4K OLED display',
                    'Premium aluminum build'
                ],
                'specifications': {
                    'Processor': 'Intel Core i7-13700H',
                    'Graphics': 'NVIDIA RTX 4060',
                    'Memory': '32GB DDR5',
                    'Storage': '1TB PCIe SSD'
                },
                'whats_in_box': [
                    'Dell XPS 15',
                    '130W USB-C Adapter',
                    'USB-C to USB-A Adapter'
                ],
                'images': [
                    'https://picsum.photos/600/400?random=401',
                    'https://picsum.photos/600/400?random=402'
                ]
            },
            'laptop': {
                'device_type': 'laptop',
                'form_factor': 'ultrabook',
                'processor_brand': 'Intel',
                'processor_model': 'Core i7-13700H',
                'processor_generation': '13th Gen',
                'cores': '14 cores, 20 threads',
                'base_clock': '2.4 GHz',
                'boost_clock': '5.0 GHz',
                'ram_size': '32GB',
                'ram_type': 'DDR5',
                'ram_speed': '4800MHz',
                'storage_type': 'SSD',
                'storage_capacity': '1TB PCIe SSD',
                'graphics_type': 'Dedicated',
                'graphics_card': 'NVIDIA RTX 4060',
                'graphics_memory': '8GB GDDR6',
                'screen_size': '15.6 inches',
                'resolution': '3840 x 2400',
                'display_type': 'OLED',
                'color_gamut': '100% DCI-P3',
                'touchscreen': True,
                'operating_system': 'Windows 11',
                'os_edition': 'Pro',
                'wifi_standard': 'Wi-Fi 6E',
                'bluetooth_version': '5.2',
                'usb_ports': {'USB-C': 2, 'Thunderbolt': 2},
                'audio_jack': True,
                'sd_card_slot': True,
                'battery_capacity': '86Wh',
                'battery_life': 'Up to 13 hours',
                'webcam_resolution': '720p',
                'primary_use_case': 'Creative',
                'target_audience': ['Professionals', 'Creators'],
                'technical_support_included': True
            }
        }
    ]
    
    # Sample accessories
    accessories_data = [
        {
            'product': {
                'name': 'AirPods Pro (2nd generation)',
                'description': 'Adaptive Audio automatically tunes the noise control',
                'short_description': 'Premium wireless earbuds with adaptive audio and noise cancellation',
                'sku': 'AIRPODSPRO2',
                'slug': 'airpods-pro-2nd-generation',
                'price': Decimal('289999'),
                'compare_price': Decimal('319999'),
                'category_id': categories['accessories'].id,
                'brand_id': brands['Apple'].id,
                'stock_quantity': 30,
                'is_featured': True,
                'features': [
                    'Adaptive Audio and Transparency',
                    'Active Noise Cancellation',
                    'Spatial Audio',
                    'Touch control',
                    'Up to 6 hours listening time'
                ],
                'specifications': {
                    'Driver': 'Custom high-excursion driver',
                    'Microphones': 'Dual beamforming',
                    'Connectivity': 'Bluetooth 5.3',
                    'Water Resistance': 'IPX4'
                },
                'whats_in_box': [
                    'AirPods Pro',
                    'MagSafe Charging Case',
                    'Silicone ear tips (4 sizes)',
                    'Lightning to USB-C Cable',
                    'Documentation'
                ],
                'images': [
                    'https://picsum.photos/600/400?random=501',
                    'https://picsum.photos/600/400?random=502'
                ]
            },
            'accessory': {
                'accessory_type': 'headphones',
                'sub_category': 'wireless_earbuds',
                'compatible_devices': ['iPhone', 'iPad', 'Mac', 'Apple Watch'],
                'compatibility_type': 'Universal',
                'device_categories': ['Smartphones', 'Tablets', 'Laptops'],
                'material': 'Premium plastic with silicone tips',
                'special_features': [
                    'Adaptive Audio',
                    'Active Noise Cancellation',
                    'Transparency mode',
                    'Spatial Audio',
                    'Hey Siri'
                ],
                'audio_features': [
                    'Active Noise Cancellation',
                    'Transparency Mode',
                    'Adaptive Audio',
                    'Spatial Audio'
                ],
                'connectivity_type': ['Bluetooth 5.3', 'Lightning'],
                'wireless_range': '10 meters',
                'waterproof': False,
                'protection_level': 'IPX4 sweat and water resistant'
            }
        },
        {
            'product': {
                'name': 'Anker PowerCore 26800mAh',
                'description': 'Ultra-high capacity portable charger for multiple devices',
                'short_description': 'High-capacity power bank with fast charging for all devices',
                'sku': 'ANKER26800',
                'slug': 'anker-powercore-26800mah',
                'price': Decimal('45999'),
                'compare_price': Decimal('55999'),
                'category_id': categories['accessories'].id,
                'brand_id': brands['Anker'].id,
                'stock_quantity': 50,
                'features': [
                    'Massive 26800mAh capacity',
                    'Charge 3 devices simultaneously',
                    'PowerIQ and VoltageBoost technology',
                    'MultiProtect safety system',
                    '6+ phone charges'
                ],
                'specifications': {
                    'Capacity': '26800mAh / 96.48Wh',
                    'Input': 'Micro USB (5V/2A)',
                    'Output': '3 USB ports',
                    'Technology': 'PowerIQ + VoltageBoost'
                },
                'whats_in_box': [
                    'PowerCore 26800',
                    'Micro USB Cable',
                    'Travel Pouch',
                    'User Manual'
                ],
                'images': [
                    'https://picsum.photos/600/400?random=601',
                    'https://picsum.photos/600/400?random=602'
                ]
            },
            'accessory': {
                'accessory_type': 'power_bank',
                'sub_category': 'portable_charger',
                'compatible_devices': ['All smartphones', 'Tablets', 'Small laptops'],
                'compatibility_type': 'Universal',
                'device_categories': ['Smartphones', 'Tablets'],
                'material': 'Premium matte finish',
                'battery_capacity': '26800mAh',
                'charging_speed': 'PowerIQ fast charging',
                'special_features': [
                    'PowerIQ Technology',
                    'VoltageBoost',
                    'MultiProtect Safety',
                    'Trickle-Charging Mode',
                    'LED Power Indicator'
                ],
                'connectivity_type': ['USB-A', 'Micro USB'],
                'protection_level': 'Surge protection, short circuit prevention'
            }
        }
    ]
    
    # Create smartphones
    for item_data in smartphones_data:
        product = Product(**item_data['product'])
        db.session.add(product)
        db.session.flush()
        
        smartphone = Smartphone(product_id=product.id, **item_data['smartphone'])
        db.session.add(smartphone)
    
    # Create laptops
    for item_data in laptops_data:
        product = Product(**item_data['product'])
        db.session.add(product)
        db.session.flush()
        
        laptop = Laptop(product_id=product.id, **item_data['laptop'])
        db.session.add(laptop)
    
    # Create accessories
    for item_data in accessories_data:
        product = Product(**item_data['product'])
        db.session.add(product)
        db.session.flush()
        
        accessory = Accessory(product_id=product.id, **item_data['accessory'])
        db.session.add(accessory)
    
    db.session.commit()
    print("Sample gadgets data created successfully!")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        create_sample_gadgets_data()