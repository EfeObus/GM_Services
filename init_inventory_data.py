"""
Initialize Sample Inventory Data
Creates sample inventory locations, staff assignments, and inventory items
"""
from app import create_app
from database import db
from models.user import User
from models.inventory import InventoryLocation, StaffLocationAssignment, InventoryItem, LowStockAlert
from models.ecommerce import Product
from models.jewelry import JewelryItem
from datetime import datetime
import random

def init_inventory_data():
    """Initialize sample inventory data"""
    
    app = create_app()
    with app.app_context():
        try:
            print("Creating sample inventory locations...")
            
            # Create inventory locations
            locations_data = [
                {
                    'name': 'Lagos Main Warehouse',
                    'code': 'LGS-MAIN',
                    'description': 'Primary warehouse facility in Lagos',
                    'address': '23 Commercial Avenue, Ikoyi',
                    'city': 'Lagos',
                    'state': 'Lagos State',
                    'country': 'Nigeria'
                },
                {
                    'name': 'Abuja Distribution Center',
                    'code': 'ABJ-DIST',
                    'description': 'Northern region distribution center',
                    'address': '15 Independence Avenue, Maitama',
                    'city': 'Abuja',
                    'state': 'FCT',
                    'country': 'Nigeria'
                },
                {
                    'name': 'Port Harcourt Storage',
                    'code': 'PHC-STOR',
                    'description': 'Port Harcourt storage facility',
                    'address': '42 Aba Road, GRA',
                    'city': 'Port Harcourt',
                    'state': 'Rivers State',
                    'country': 'Nigeria'
                }
            ]
            
            locations = []
            for loc_data in locations_data:
                location = InventoryLocation.query.filter_by(code=loc_data['code']).first()
                if not location:
                    location = InventoryLocation(**loc_data)
                    db.session.add(location)
                    db.session.flush()
                locations.append(location)
            
            print(f"Created {len(locations)} inventory locations")
            
            # Create staff users if they don't exist
            staff_data = [
                {
                    'first_name': 'John',
                    'last_name': 'Inventory',
                    'email': 'john.inventory@gmservices.com',
                    'role': 'staff',
                    'department': 'Inventory Management',
                    'employee_id': 'INV001'
                },
                {
                    'first_name': 'Sarah',
                    'last_name': 'Stockkeeper',
                    'email': 'sarah.stock@gmservices.com',
                    'role': 'staff',
                    'department': 'Inventory Management',
                    'employee_id': 'INV002'
                },
                {
                    'first_name': 'Mike',
                    'last_name': 'Warehouse',
                    'email': 'mike.warehouse@gmservices.com',
                    'role': 'staff',
                    'department': 'Inventory Management',
                    'employee_id': 'INV003'
                }
            ]
            
            staff_users = []
            for staff_info in staff_data:
                user = User.query.filter_by(email=staff_info['email']).first()
                if not user:
                    user = User(**staff_info)
                    user.set_password('password123')  # Default password for demo
                    db.session.add(user)
                    db.session.flush()
                staff_users.append(user)
            
            print(f"Created {len(staff_users)} staff users")
            
            # Assign managers to locations
            if len(staff_users) >= len(locations):
                for i, location in enumerate(locations):
                    if not location.manager_id:
                        location.manager_id = staff_users[i].id
            
            # Create staff location assignments
            assignments_data = [
                {'staff_idx': 0, 'location_idx': 0, 'role': 'manager', 'permissions': ['view_inventory', 'adjust_stock', 'manage_alerts']},
                {'staff_idx': 1, 'location_idx': 1, 'role': 'supervisor', 'permissions': ['view_inventory', 'adjust_stock']},
                {'staff_idx': 2, 'location_idx': 2, 'role': 'clerk', 'permissions': ['view_inventory']},
                {'staff_idx': 0, 'location_idx': 1, 'role': 'supervisor', 'permissions': ['view_inventory', 'adjust_stock']},  # Cross-assignment
            ]
            
            for assignment_data in assignments_data:
                if assignment_data['staff_idx'] < len(staff_users) and assignment_data['location_idx'] < len(locations):
                    existing = StaffLocationAssignment.query.filter_by(
                        staff_id=staff_users[assignment_data['staff_idx']].id,
                        location_id=locations[assignment_data['location_idx']].id
                    ).first()
                    
                    if not existing:
                        assignment = StaffLocationAssignment(
                            staff_id=staff_users[assignment_data['staff_idx']].id,
                            location_id=locations[assignment_data['location_idx']].id,
                            role=assignment_data['role'],
                            permissions=assignment_data['permissions']
                        )
                        db.session.add(assignment)
            
            print("Created staff location assignments")
            
            # Create inventory items for existing products
            products = Product.query.filter_by(status='active').limit(20).all()
            jewelry_items = JewelryItem.query.filter_by(status='active').limit(10).all()
            
            inventory_items_created = 0
            
            # Create inventory for products
            for product in products:
                for location in locations:
                    # Check if inventory item already exists
                    existing = InventoryItem.query.filter_by(
                        product_id=product.id,
                        location_id=location.id
                    ).first()
                    
                    if not existing:
                        # Create random stock levels (some will be low stock for demo)
                        stock_level = random.choice([0, 1, 2, 5, 10, 15, 25, 50])
                        
                        # Calculate unit cost safely
                        if hasattr(product, 'cost_price') and product.cost_price:
                            unit_cost = float(product.cost_price)
                        elif product.price:
                            unit_cost = float(product.price) * 0.7
                        else:
                            unit_cost = 100.0  # Default cost
                        
                        inventory_item = InventoryItem(
                            product_id=product.id,
                            location_id=location.id,
                            current_stock=stock_level,
                            reserved_stock=0,
                            available_stock=stock_level,
                            reorder_point=2,  # Set to 2 as required
                            max_stock_level=100,
                            unit_cost=unit_cost,
                            total_value=stock_level * unit_cost,
                            status='active'
                        )
                        db.session.add(inventory_item)
                        inventory_items_created += 1
            
            # Create inventory for jewelry items
            for jewelry in jewelry_items:
                for location in locations[:2]:  # Only first 2 locations for jewelry
                    existing = InventoryItem.query.filter_by(
                        jewelry_item_id=jewelry.id,
                        location_id=location.id
                    ).first()
                    
                    if not existing:
                        stock_level = random.choice([0, 1, 2, 3, 5, 8])
                        
                        # Calculate unit cost safely for jewelry
                        if jewelry.base_price:
                            unit_cost = float(jewelry.base_price) * 0.6
                        else:
                            unit_cost = 500.0  # Default cost for jewelry
                        
                        inventory_item = InventoryItem(
                            jewelry_item_id=jewelry.id,
                            location_id=location.id,
                            current_stock=stock_level,
                            reserved_stock=0,
                            available_stock=stock_level,
                            reorder_point=2,
                            max_stock_level=20,
                            unit_cost=unit_cost,
                            total_value=stock_level * unit_cost,
                            status='active'
                        )
                        db.session.add(inventory_item)
                        inventory_items_created += 1
            
            print(f"Created {inventory_items_created} inventory items")
            
            db.session.commit()
            
            # Create low stock alerts for items with stock <= 2
            low_stock_items = InventoryItem.query.filter(
                InventoryItem.current_stock <= 2,
                InventoryItem.status == 'active'
            ).all()
            
            alerts_created = 0
            for item in low_stock_items:
                existing_alert = LowStockAlert.query.filter_by(
                    inventory_item_id=item.id,
                    status='active'
                ).first()
                
                if not existing_alert:
                    alert = LowStockAlert(
                        inventory_item_id=item.id,
                        alert_level='critical' if item.current_stock < 2 else 'low',
                        current_stock=item.current_stock,
                        reorder_point=item.reorder_point
                    )
                    db.session.add(alert)
                    alerts_created += 1
            
            db.session.commit()
            print(f"Created {alerts_created} low stock alerts")
            
            print("\n=== Inventory System Summary ===")
            print(f"Locations: {len(locations)}")
            print(f"Staff Users: {len(staff_users)}")
            print(f"Inventory Items: {inventory_items_created}")
            print(f"Low Stock Alerts: {alerts_created}")
            print("\nInventory system initialized successfully!")
            
            # Print access information
            print("\n=== Access Information ===")
            print("Staff Login Credentials (password: password123):")
            for user in staff_users:
                assignments = StaffLocationAssignment.query.filter_by(staff_id=user.id, is_active=True).all()
                locations_assigned = [assignment.location.name for assignment in assignments]
                print(f"- {user.email} ({user.full_name}) - Assigned to: {', '.join(locations_assigned)}")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing inventory data: {str(e)}")
            raise e

if __name__ == '__main__':
    init_inventory_data()