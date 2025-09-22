#!/usr/bin/env python3
"""
Database Migration Script for Automobile Service Updates
Creates new tables for MaintenanceRequest and InsuranceRequest models
"""
import sys
import os

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import db
from models.automobile import MaintenanceRequest, InsuranceRequest, VehicleMake, VehicleModel

def create_tables():
    """Create new tables for automobile services"""
    with app.app_context():
        try:
            print("Creating new automobile service tables...")
            
            # Create tables if they don't exist
            db.create_all()
            
            # Check if the new tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            # Verify new tables exist
            new_tables = ['maintenance_requests', 'insurance_requests']
            for table in new_tables:
                if table in tables:
                    print(f"✓ Table '{table}' created successfully")
                else:
                    print(f"✗ Table '{table}' not found")
            
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {str(e)}")
            sys.exit(1)

def create_sample_data():
    """Create sample vehicle makes and models if they don't exist"""
    with app.app_context():
        try:
            print("Creating sample vehicle data...")
            
            # Sample vehicle makes
            sample_makes = [
                {'name': 'Toyota', 'country': 'Japan'},
                {'name': 'Honda', 'country': 'Japan'},
                {'name': 'Mercedes-Benz', 'country': 'Germany'},
                {'name': 'BMW', 'country': 'Germany'},
                {'name': 'Ford', 'country': 'USA'},
                {'name': 'Hyundai', 'country': 'South Korea'},
                {'name': 'Kia', 'country': 'South Korea'},
                {'name': 'Volkswagen', 'country': 'Germany'},
                {'name': 'Nissan', 'country': 'Japan'},
                {'name': 'Audi', 'country': 'Germany'}
            ]
            
            # Sample models for each make
            sample_models = {
                'Toyota': ['Camry', 'Corolla', 'RAV4', 'Highlander', 'Prius', 'Hilux'],
                'Honda': ['Accord', 'Civic', 'CR-V', 'Pilot', 'Insight', 'HR-V'],
                'Mercedes-Benz': ['C-Class', 'E-Class', 'S-Class', 'GLC', 'GLE', 'A-Class'],
                'BMW': ['3 Series', '5 Series', '7 Series', 'X3', 'X5', 'X1'],
                'Ford': ['Focus', 'Escape', 'Explorer', 'F-150', 'Mustang', 'Edge'],
                'Hyundai': ['Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Accent', 'Creta'],
                'Kia': ['Forte', 'Optima', 'Sportage', 'Sorento', 'Rio', 'Seltos'],
                'Volkswagen': ['Jetta', 'Passat', 'Tiguan', 'Atlas', 'Golf', 'Arteon'],
                'Nissan': ['Altima', 'Sentra', 'Rogue', 'Pathfinder', 'Murano', 'Patrol'],
                'Audi': ['A3', 'A4', 'A6', 'Q3', 'Q5', 'Q7']
            }
            
            # Create makes
            for make_data in sample_makes:
                existing_make = VehicleMake.query.filter_by(name=make_data['name']).first()
                if not existing_make:
                    make = VehicleMake(
                        name=make_data['name'],
                        country=make_data['country'],
                        is_active=True
                    )
                    db.session.add(make)
                    print(f"✓ Added vehicle make: {make_data['name']}")
                else:
                    print(f"- Vehicle make already exists: {make_data['name']}")
            
            db.session.commit()
            
            # Create models
            for make_name, models in sample_models.items():
                make = VehicleMake.query.filter_by(name=make_name).first()
                if make:
                    for model_name in models:
                        existing_model = VehicleModel.query.filter_by(
                            name=model_name, make_id=make.id
                        ).first()
                        if not existing_model:
                            model = VehicleModel(
                                name=model_name,
                                make_id=make.id,
                                vehicle_type='sedan',  # Default type
                                is_active=True
                            )
                            db.session.add(model)
                            print(f"✓ Added vehicle model: {make_name} {model_name}")
                        else:
                            print(f"- Vehicle model already exists: {make_name} {model_name}")
            
            db.session.commit()
            print("Sample data created successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating sample data: {str(e)}")

if __name__ == '__main__':
    print("GM Services Automobile Migration Script")
    print("======================================")
    
    create_tables()
    create_sample_data()
    
    print("\nMigration completed!")
    print("You can now:")
    print("1. Access vehicle sales at: http://127.0.0.1:5040/services/automobile/vehicles")
    print("2. Submit maintenance requests at: http://127.0.0.1:5040/services/automobile/maintenance/request")
    print("3. Submit insurance requests at: http://127.0.0.1:5040/services/automobile/insurance/request")
    print("4. Admin can manage vehicles at: http://127.0.0.1:5040/services/admin/vehicles")
    print("5. Admin can view requests at: http://127.0.0.1:5040/services/admin/maintenance-requests")