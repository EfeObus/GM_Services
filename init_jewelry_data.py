#!/usr/bin/env python3
"""
Initialize sample jewelry data for GM Services
Run this script to populate the database with sample jewelry collections and items
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db
from models.jewelry import JewelryCategory, JewelryMaterial, JewelryBrand, JewelryItem, JewelryCollection
from datetime import datetime
import uuid

def create_sample_jewelry_data():
    """Create sample jewelry data for testing"""
    
    with app.app_context():
        try:
            # Create Categories
            categories = [
                {
                    'name': 'Rings',
                    'slug': 'rings',
                    'description': 'Beautiful rings for all occasions',
                    'icon': 'fas fa-ring'
                },
                {
                    'name': 'Necklaces',
                    'slug': 'necklaces', 
                    'description': 'Elegant necklaces and pendants',
                    'icon': 'fas fa-gem'
                },
                {
                    'name': 'Earrings',
                    'slug': 'earrings',
                    'description': 'Stunning earrings for every style',
                    'icon': 'fas fa-circle'
                },
                {
                    'name': 'Bracelets',
                    'slug': 'bracelets',
                    'description': 'Beautiful bracelets and bangles',
                    'icon': 'fas fa-circle-notch'
                }
            ]
            
            category_objects = {}
            for cat_data in categories:
                category = JewelryCategory.query.filter_by(slug=cat_data['slug']).first()
                if not category:
                    category = JewelryCategory(**cat_data)
                    db.session.add(category)
                    db.session.flush()
                category_objects[cat_data['slug']] = category
            
            # Create Materials
            materials = [
                {
                    'name': '18K Gold',
                    'material_type': 'metal',
                    'purity_levels': ['18k'],
                    'color_variants': ['yellow', 'white', 'rose'],
                    'current_price_per_gram': 45000.00,
                    'care_instructions': 'Clean with soft cloth, avoid harsh chemicals'
                },
                {
                    'name': '24K Gold',
                    'material_type': 'metal', 
                    'purity_levels': ['24k'],
                    'color_variants': ['yellow'],
                    'current_price_per_gram': 65000.00,
                    'care_instructions': 'Pure gold, handle with care, avoid scratching'
                },
                {
                    'name': 'Diamond',
                    'material_type': 'gemstone',
                    'requires_certification': True,
                    'certification_authorities': ['GIA', 'AGS', 'GSI'],
                    'care_instructions': 'Clean with diamond cleaner or mild soap solution'
                },
                {
                    'name': 'Sterling Silver',
                    'material_type': 'metal',
                    'purity_levels': ['925'],
                    'current_price_per_gram': 800.00,
                    'care_instructions': 'Polish regularly to prevent tarnishing'
                }
            ]
            
            material_objects = {}
            for mat_data in materials:
                material = JewelryMaterial.query.filter_by(name=mat_data['name']).first()
                if not material:
                    material = JewelryMaterial(**mat_data)
                    db.session.add(material)
                    db.session.flush()
                material_objects[mat_data['name']] = material
            
            # Create Brand
            brand_data = {
                'name': 'GM Luxury',
                'description': 'Exquisite Nigerian jewelry craftsmanship',
                'country_of_origin': 'Nigeria',
                'founded_year': 2020,
                'is_luxury_brand': True,
                'price_range': 'luxury'
            }
            
            brand = JewelryBrand.query.filter_by(name=brand_data['name']).first()
            if not brand:
                brand = JewelryBrand(**brand_data)
                db.session.add(brand)
                db.session.flush()
            
            # Create Collections
            collections = [
                {
                    'name': 'Gold Heritage Collection',
                    'slug': 'gold-heritage',
                    'description': 'Traditional Nigerian gold jewelry with contemporary touches',
                    'collection_type': 'gold',
                    'price_range_min': 85000,
                    'price_range_max': 500000,
                    'key_features': ['Traditional Nigerian designs', '18k & 24k gold', 'Handcrafted', 'Cultural significance'],
                    'materials_used': ['18K Gold', '24K Gold'],
                    'occasions': ['Wedding', 'Traditional ceremonies', 'Special occasions'],
                    'is_featured': True,
                    'is_active': True
                },
                {
                    'name': 'Diamond Elegance Collection',
                    'slug': 'diamond-elegance',
                    'description': 'Certified diamonds in elegant settings for life\'s special moments',
                    'collection_type': 'diamond',
                    'price_range_min': 250000,
                    'price_range_max': 2000000,
                    'key_features': ['Certified diamonds', 'Elegant settings', 'Premium quality', 'Lifetime warranty'],
                    'materials_used': ['Diamond', '18K Gold', 'Platinum'],
                    'occasions': ['Engagement', 'Anniversary', 'Birthday', 'Achievement'],
                    'is_featured': True,
                    'is_active': True
                },
                {
                    'name': 'Custom Design Studio',
                    'slug': 'custom-design',
                    'description': 'Bespoke jewelry designed specifically for you',
                    'collection_type': 'custom',
                    'key_features': ['Personal consultation', '3D modeling', 'Unique designs', 'Handcrafted'],
                    'materials_used': ['Various metals', 'Precious gemstones', 'Semi-precious stones'],
                    'occasions': ['Personal', 'Gift', 'Special request'],
                    'requires_appointment': True,
                    'is_featured': True,
                    'is_active': True
                }
            ]
            
            collection_objects = {}
            for coll_data in collections:
                collection = JewelryCollection.query.filter_by(slug=coll_data['slug']).first()
                if not collection:
                    collection = JewelryCollection(**coll_data)
                    db.session.add(collection)
                    db.session.flush()
                collection_objects[coll_data['slug']] = collection
            
            # Create Sample Jewelry Items
            items = [
                {
                    'sku': 'GM-GOLD-001',
                    'name': 'Traditional Coral Bead Necklace',
                    'description': 'Authentic coral beads with 18k gold accents in traditional Nigerian style',
                    'category_id': category_objects['necklaces'].id,
                    'brand_id': brand.id,
                    'jewelry_type': 'necklace',
                    'sub_type': 'traditional',
                    'primary_material_id': material_objects['18K Gold'].id,
                    'design_style': 'traditional',
                    'occasion': ['wedding', 'traditional'],
                    'gender_target': 'women',
                    'base_price': 125000.00,
                    'weight': 45.5,
                    'dimensions': {'length': '18 inches', 'width': '12mm'},
                    'stock_quantity': 5,
                    'is_featured': True,
                    'status': 'active'
                },
                {
                    'sku': 'GM-DIAMOND-001', 
                    'name': 'Classic Solitaire Engagement Ring',
                    'description': 'Stunning 1-carat diamond solitaire in 18k white gold setting',
                    'category_id': category_objects['rings'].id,
                    'brand_id': brand.id,
                    'jewelry_type': 'ring',
                    'sub_type': 'engagement_ring',
                    'primary_material_id': material_objects['18K Gold'].id,
                    'primary_gemstone': 'Diamond',
                    'gemstone_details': {'carat': 1.0, 'cut': 'Round', 'color': 'F', 'clarity': 'VS1'},
                    'design_style': 'classic',
                    'occasion': ['engagement'],
                    'gender_target': 'women',
                    'base_price': 450000.00,
                    'weight': 3.2,
                    'dimensions': {'diameter': '6-7mm'},
                    'size_options': ['5', '5.5', '6', '6.5', '7', '7.5', '8'],
                    'stock_quantity': 3,
                    'is_featured': True,
                    'status': 'active'
                },
                {
                    'sku': 'GM-GOLD-002',
                    'name': 'Gele Gold Earrings',
                    'description': 'Intricate 24k gold earrings inspired by traditional Nigerian gele headwrap',
                    'category_id': category_objects['earrings'].id,
                    'brand_id': brand.id,
                    'jewelry_type': 'earrings',
                    'sub_type': 'drop_earrings',
                    'primary_material_id': material_objects['24K Gold'].id,
                    'design_style': 'traditional',
                    'occasion': ['traditional', 'formal'],
                    'gender_target': 'women',
                    'base_price': 185000.00,
                    'weight': 8.7,
                    'dimensions': {'length': '2.5 inches', 'width': '1 inch'},
                    'stock_quantity': 8,
                    'is_featured': True,
                    'status': 'active'
                },
                {
                    'sku': 'GM-DIAMOND-002',
                    'name': 'Diamond Tennis Bracelet',
                    'description': 'Elegant tennis bracelet featuring 2 carats of round diamonds',
                    'category_id': category_objects['bracelets'].id,
                    'brand_id': brand.id,
                    'jewelry_type': 'bracelet',
                    'sub_type': 'tennis_bracelet',
                    'primary_material_id': material_objects['18K Gold'].id,
                    'primary_gemstone': 'Diamond',
                    'gemstone_details': {'total_carat': 2.0, 'cut': 'Round', 'color': 'G-H', 'clarity': 'SI1'},
                    'design_style': 'classic',
                    'occasion': ['anniversary', 'formal'],
                    'gender_target': 'women',
                    'base_price': 680000.00,
                    'weight': 12.3,
                    'dimensions': {'length': '7 inches', 'width': '4mm'},
                    'stock_quantity': 2,
                    'is_featured': True,
                    'status': 'active'
                },
                {
                    'sku': 'GM-GOLD-003',
                    'name': 'Traditional Wedding Band Set',
                    'description': 'Matching 18k gold wedding bands with traditional Nigerian engraving',
                    'category_id': category_objects['rings'].id,
                    'brand_id': brand.id,
                    'jewelry_type': 'ring',
                    'sub_type': 'wedding_band',
                    'primary_material_id': material_objects['18K Gold'].id,
                    'design_style': 'traditional',
                    'occasion': ['wedding'],
                    'gender_target': 'unisex',
                    'base_price': 95000.00,
                    'weight': 6.8,
                    'dimensions': {'width': '4mm'},
                    'size_options': ['5', '5.5', '6', '6.5', '7', '7.5', '8', '8.5', '9', '9.5', '10'],
                    'stock_quantity': 15,
                    'is_customizable': True,
                    'customization_options': ['Engraving', 'Size adjustment'],
                    'is_featured': True,
                    'status': 'active'
                },
                {
                    'sku': 'GM-DIAMOND-003',
                    'name': 'Diamond Stud Earrings',
                    'description': 'Classic diamond stud earrings with 0.5 carat total weight',
                    'category_id': category_objects['earrings'].id,
                    'brand_id': brand.id,
                    'jewelry_type': 'earrings',
                    'sub_type': 'stud_earrings',
                    'primary_material_id': material_objects['18K Gold'].id,
                    'primary_gemstone': 'Diamond',
                    'gemstone_details': {'total_carat': 0.5, 'cut': 'Round', 'color': 'F-G', 'clarity': 'VS2'},
                    'design_style': 'classic',
                    'occasion': ['casual', 'formal'],
                    'gender_target': 'women',
                    'base_price': 275000.00,
                    'weight': 1.2,
                    'dimensions': {'diameter': '4mm'},
                    'stock_quantity': 10,
                    'is_featured': True,
                    'status': 'active'
                }
            ]
            
            for item_data in items:
                item = JewelryItem.query.filter_by(sku=item_data['sku']).first()
                if not item:
                    item = JewelryItem(**item_data)
                    db.session.add(item)
            
            # Commit all changes
            db.session.commit()
            print("✅ Sample jewelry data created successfully!")
            print(f"✅ Created {len(categories)} categories")
            print(f"✅ Created {len(materials)} materials")
            print(f"✅ Created 1 brand")
            print(f"✅ Created {len(collections)} collections")
            print(f"✅ Created {len(items)} jewelry items")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sample data: {str(e)}")
            raise

if __name__ == '__main__':
    create_sample_jewelry_data()