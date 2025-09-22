"""
Database initialization commands for GM Services Nigeria
"""
import click
from flask.cli import with_appcontext
from database import db
from models.location import NigerianState, LocalGovernment
from data.nigeria_data import NIGERIAN_STATES, LOCAL_GOVERNMENTS

@click.command()
@with_appcontext
def init_nigeria_data():
    """Initialize Nigerian states and local government data"""
    try:
        # Create states
        print("Creating Nigerian states...")
        for state_data in NIGERIAN_STATES:
            existing_state = NigerianState.query.filter_by(name=state_data['name']).first()
            if not existing_state:
                state = NigerianState(
                    name=state_data['name'],
                    code=state_data['code'],
                    capital=state_data['capital'],
                    zone=state_data['zone']
                )
                db.session.add(state)
                print(f"Added state: {state_data['name']}")
        
        db.session.commit()
        
        # Create local governments
        print("\nCreating Local Government Areas...")
        for state_name, lgas in LOCAL_GOVERNMENTS.items():
            state = NigerianState.query.filter_by(name=state_name).first()
            if state:
                for lga_data in lgas:
                    existing_lga = LocalGovernment.query.filter_by(
                        name=lga_data['name'], 
                        state_id=state.id
                    ).first()
                    if not existing_lga:
                        lga = LocalGovernment(
                            name=lga_data['name'],
                            state_id=state.id,
                            headquarters=lga_data.get('headquarters', lga_data['name'])
                        )
                        db.session.add(lga)
                        print(f"Added LGA: {lga_data['name']} ({state_name})")
        
        db.session.commit()
        
        # Print summary
        states_count = NigerianState.query.count()
        lgas_count = LocalGovernment.query.count()
        
        print(f"\n✅ Nigeria data initialization completed!")
        print(f"📍 States created: {states_count}")
        print(f"🏛️ Local Governments created: {lgas_count}")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error initializing Nigeria data: {str(e)}")
        raise e

@click.command()
@with_appcontext
def create_sample_data():
    """Create sample data for testing"""
    try:
        # This would create sample users, services, etc.
        print("Creating sample data...")
        
        # Add sample admin user
        from models.user import User
        admin_email = "admin@gmservices.ng"
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if not existing_admin:
            admin = User.create_admin_user(
                email=admin_email,
                password="admin123",
                first_name="GM Services",
                last_name="Administrator"
            )
            admin.country = "Nigeria"
            admin.state = "Lagos"
            admin.city = "Ikeja"
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Admin user created: {admin_email}")
        else:
            print(f"ℹ️ Admin user already exists: {admin_email}")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating sample data: {str(e)}")
        raise e

def register_cli_commands(app):
    """Register CLI commands with Flask app"""
    app.cli.add_command(init_nigeria_data)
    app.cli.add_command(create_sample_data)
    app.cli.add_command(check_inventory_alerts)
    app.cli.add_command(init_inventory_sample_data)
    
    # Import and register security commands
    from tasks.background_tasks import register_security_commands
    register_security_commands(app)

@click.command()
@with_appcontext
def check_inventory_alerts():
    """Check for low stock items and create alerts"""
    try:
        from tasks.inventory_alerts import InventoryAlertService
        
        print("Checking inventory for low stock items...")
        result = InventoryAlertService.check_low_stock_items()
        
        print(f"✅ Inventory check completed:")
        print(f"   - Alerts created: {result.get('alerts_created', 0)}")
        print(f"   - Alerts updated: {result.get('alerts_updated', 0)}")
        print(f"   - Alerts resolved: {result.get('alerts_resolved', 0)}")
        
        # Send notifications if there are new critical alerts
        if result.get('alerts_created', 0) > 0:
            notification_result = InventoryAlertService.send_alert_notifications()
            print(f"   - Notifications sent: {notification_result.get('notifications_sent', 0)}")
        
    except Exception as e:
        print(f"❌ Error checking inventory alerts: {str(e)}")
        raise e

@click.command()
@with_appcontext
def init_inventory_sample_data():
    """Initialize sample inventory data"""
    try:
        from init_inventory_data import init_inventory_data
        init_inventory_data()
    except Exception as e:
        print(f"❌ Error initializing inventory data: {str(e)}")
        raise e