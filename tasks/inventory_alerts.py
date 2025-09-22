"""
Inventory Alert System
Automated background tasks for inventory monitoring and low stock alerts
"""
from models.inventory import InventoryItem, LowStockAlert, InventoryLocation, StaffLocationAssignment
from models.ecommerce import Product
from models.jewelry import JewelryItem
from models.user import User
from database import db
from datetime import datetime, timedelta
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class InventoryAlertService:
    """Service for managing inventory alerts and notifications"""
    
    @staticmethod
    def check_low_stock_items():
        """Check all inventory items for low stock and create alerts"""
        try:
            # Get all active inventory items that are low on stock
            low_stock_items = InventoryItem.query.filter(
                InventoryItem.status == 'active',
                InventoryItem.current_stock <= InventoryItem.reorder_point
            ).all()
            
            alerts_created = 0
            alerts_updated = 0
            
            for item in low_stock_items:
                # Check if there's already an active alert for this item
                existing_alert = LowStockAlert.query.filter_by(
                    inventory_item_id=item.id,
                    status='active'
                ).first()
                
                if existing_alert:
                    # Update existing alert if stock level has changed
                    if existing_alert.current_stock != item.current_stock:
                        existing_alert.current_stock = item.current_stock
                        existing_alert.alert_level = 'critical' if item.current_stock < 2 else 'low'
                        existing_alert.updated_at = datetime.utcnow()
                        alerts_updated += 1
                else:
                    # Create new alert
                    alert = LowStockAlert(
                        inventory_item_id=item.id,
                        alert_level='critical' if item.current_stock < 2 else 'low',
                        current_stock=item.current_stock,
                        reorder_point=item.reorder_point
                    )
                    db.session.add(alert)
                    alerts_created += 1
            
            # Resolve alerts for items that are no longer low stock
            resolved_alerts = LowStockAlert.query.join(InventoryItem).filter(
                LowStockAlert.status == 'active',
                InventoryItem.current_stock > InventoryItem.reorder_point
            ).all()
            
            alerts_resolved = 0
            for alert in resolved_alerts:
                alert.status = 'resolved'
                alert.resolved_at = datetime.utcnow()
                alerts_resolved += 1
            
            db.session.commit()
            
            logger.info(f"Inventory alert check completed: {alerts_created} created, "
                       f"{alerts_updated} updated, {alerts_resolved} resolved")
            
            return {
                'alerts_created': alerts_created,
                'alerts_updated': alerts_updated,
                'alerts_resolved': alerts_resolved
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error checking low stock items: {str(e)}")
            raise e
    
    @staticmethod
    def get_critical_alerts(location_id=None):
        """Get critical alerts (2 or fewer items remaining)"""
        query = LowStockAlert.query.filter_by(
            status='active',
            alert_level='critical'
        )
        
        if location_id:
            query = query.join(InventoryItem).filter(
                InventoryItem.location_id == location_id
            )
        
        return query.order_by(LowStockAlert.created_at.desc()).all()
    
    @staticmethod
    def get_location_alerts(location_id):
        """Get all active alerts for a specific location"""
        return LowStockAlert.query.join(InventoryItem).filter(
            InventoryItem.location_id == location_id,
            LowStockAlert.status == 'active'
        ).order_by(LowStockAlert.created_at.desc()).all()
    
    @staticmethod
    def get_staff_alerts(staff_user_id):
        """Get alerts for all locations assigned to a staff member"""
        # Get assigned locations for staff
        assigned_locations = StaffLocationAssignment.query.filter_by(
            staff_id=staff_user_id,
            is_active=True
        ).all()
        
        if not assigned_locations:
            return []
        
        location_ids = [assignment.location_id for assignment in assigned_locations]
        
        return LowStockAlert.query.join(InventoryItem).filter(
            InventoryItem.location_id.in_(location_ids),
            LowStockAlert.status == 'active'
        ).order_by(LowStockAlert.created_at.desc()).all()
    
    @staticmethod
    def send_alert_notifications():
        """Send notifications for critical alerts"""
        try:
            # Get all critical alerts created in the last hour
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            critical_alerts = LowStockAlert.query.filter(
                LowStockAlert.alert_level == 'critical',
                LowStockAlert.status == 'active',
                LowStockAlert.created_at >= one_hour_ago
            ).all()
            
            if not critical_alerts:
                return {'notifications_sent': 0}
            
            # Group alerts by location
            location_alerts = {}
            for alert in critical_alerts:
                location_id = alert.inventory_item.location_id
                if location_id not in location_alerts:
                    location_alerts[location_id] = []
                location_alerts[location_id].append(alert)
            
            notifications_sent = 0
            
            # Send notifications to location managers and assigned staff
            for location_id, alerts in location_alerts.items():
                location = InventoryLocation.query.get(location_id)
                if not location:
                    continue
                
                # Prepare notification data
                alert_data = {
                    'location': location.name,
                    'alerts': [
                        {
                            'item_name': alert.inventory_item.get_item_name(),
                            'current_stock': alert.current_stock,
                            'reorder_point': alert.reorder_point
                        }
                        for alert in alerts
                    ]
                }
                
                # Get users to notify
                users_to_notify = set()
                
                # Add location manager
                if location.manager_id:
                    users_to_notify.add(location.manager_id)
                
                # Add assigned staff
                staff_assignments = StaffLocationAssignment.query.filter_by(
                    location_id=location_id,
                    is_active=True
                ).all()
                
                for assignment in staff_assignments:
                    users_to_notify.add(assignment.staff_id)
                
                # Add all admin users
                admin_users = User.query.filter_by(role='admin', is_active=True).all()
                for admin in admin_users:
                    users_to_notify.add(admin.id)
                
                # Send notifications (placeholder for email/SMS service)
                for user_id in users_to_notify:
                    user = User.query.get(user_id)
                    if user and user.email:
                        # This would integrate with your email service
                        logger.info(f"Would send critical stock alert to {user.email} for location {location.name}")
                        notifications_sent += 1
            
            return {'notifications_sent': notifications_sent}
            
        except Exception as e:
            logger.error(f"Error sending alert notifications: {str(e)}")
            raise e
    
    @staticmethod
    def cleanup_old_alerts(days_old=30):
        """Clean up old resolved alerts"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            old_alerts = LowStockAlert.query.filter(
                LowStockAlert.status.in_(['resolved', 'acknowledged']),
                LowStockAlert.updated_at < cutoff_date
            ).all()
            
            count = len(old_alerts)
            for alert in old_alerts:
                db.session.delete(alert)
            
            db.session.commit()
            
            logger.info(f"Cleaned up {count} old alerts")
            return {'alerts_cleaned': count}
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cleaning up old alerts: {str(e)}")
            raise e

def schedule_inventory_alerts():
    """Schedule inventory alert checks (call this from your task scheduler)"""
    try:
        # Check for low stock items
        result = InventoryAlertService.check_low_stock_items()
        
        # Send notifications if there are critical alerts
        if result.get('alerts_created', 0) > 0:
            InventoryAlertService.send_alert_notifications()
        
        # Cleanup old alerts weekly (you can adjust the frequency)
        import random
        if random.randint(1, 100) <= 1:  # 1% chance to run cleanup
            InventoryAlertService.cleanup_old_alerts()
        
        return result
        
    except Exception as e:
        logger.error(f"Error in scheduled inventory alert check: {str(e)}")
        return {'error': str(e)}

# Context processor for templates to show alert counts
def inventory_context_processor():
    """Template context processor to show inventory alerts in navigation"""
    if not hasattr(current_app, 'blueprints'):
        return {}
    
    try:
        from flask_login import current_user
        
        if not current_user.is_authenticated:
            return {}
        
        alert_count = 0
        critical_count = 0
        
        if current_user.is_admin():
            # Admin sees all alerts
            alert_count = LowStockAlert.query.filter_by(status='active').count()
            critical_count = LowStockAlert.query.filter_by(
                status='active',
                alert_level='critical'
            ).count()
            
        elif current_user.is_staff():
            # Staff sees alerts for assigned locations
            alerts = InventoryAlertService.get_staff_alerts(current_user.id)
            alert_count = len(alerts)
            critical_count = len([a for a in alerts if a.alert_level == 'critical'])
        
        return {
            'inventory_alert_count': alert_count,
            'inventory_critical_count': critical_count
        }
        
    except Exception as e:
        logger.error(f"Error in inventory context processor: {str(e)}")
        return {}