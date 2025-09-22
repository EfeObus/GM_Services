"""
Background Tasks for GM Services
Handles scheduled tasks like key rotation, notifications, etc.
"""
import threading
import time
from datetime import datetime, timedelta
from database import db
from models.security import SecurityKey

class BackgroundTaskManager:
    """Manages background tasks for the application"""
    
    def __init__(self):
        self.running = False
        self.tasks = []
        self.thread = None
    
    def start(self):
        """Start the background task manager"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_tasks, daemon=True)
            self.thread.start()
            print("🚀 Background task manager started")
    
    def stop(self):
        """Stop the background task manager"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("⏹️ Background task manager stopped")
    
    def _run_tasks(self):
        """Main task loop"""
        # Import create_app here to avoid circular imports
        from app import create_app
        app = create_app()
        
        with app.app_context():
            while self.running:
                try:
                    # Check for key rotation every hour
                    self._check_key_rotation()
                    
                    # Check for other scheduled tasks
                    self._run_scheduled_tasks()
                    
                    # Sleep for 1 hour
                    time.sleep(3600)  # 3600 seconds = 1 hour
                    
                except Exception as e:
                    print(f"❌ Background task error: {str(e)}")
                    time.sleep(300)  # Sleep for 5 minutes on error
    
    def _check_key_rotation(self):
        """Check if any keys need rotation"""
        try:
            expiring_keys = SecurityKey.check_key_expiry()
            
            if expiring_keys:
                print(f"⚠️ Found {len(expiring_keys)} keys expiring soon")
                
                for key in expiring_keys:
                    if datetime.utcnow() >= key.expires_at:
                        # Key has expired, rotate immediately
                        SecurityKey.create_or_rotate_key(key.key_type, force_rotation=True)
                        print(f"🔄 Rotated expired key: {key.key_type}")
                    else:
                        print(f"⏰ Key {key.key_type} expires in {(key.expires_at - datetime.utcnow()).days} days")
        
        except Exception as e:
            print(f"❌ Error checking key rotation: {str(e)}")
    
    def _run_scheduled_tasks(self):
        """Run other scheduled tasks"""
        try:
            # Add other scheduled tasks here
            # Example: cleanup old logs, send notifications, etc.
            pass
        except Exception as e:
            print(f"❌ Error running scheduled tasks: {str(e)}")
    
    def schedule_task(self, task_func, interval_minutes=60):
        """Schedule a custom task"""
        self.tasks.append({
            'function': task_func,
            'interval': interval_minutes,
            'last_run': datetime.utcnow()
        })

# Global task manager instance
task_manager = BackgroundTaskManager()

def init_background_tasks():
    """Initialize background tasks"""
    try:
        # Import create_app here to avoid circular imports
        from app import create_app
        # Initialize security keys
        with create_app().app_context():
            db.create_all()
            SecurityKey.initialize_keys()
        
        # Start background task manager
        task_manager.start()
        
    except Exception as e:
        print(f"❌ Error initializing background tasks: {str(e)}")

def stop_background_tasks():
    """Stop background tasks"""
    task_manager.stop()

# CLI command for manual key rotation
import click
from flask.cli import with_appcontext

@click.command()
@with_appcontext
def rotate_keys():
    """Manually rotate all security keys"""
    try:
        rotated_keys = SecurityKey.rotate_all_keys()
        print("🔄 Manual key rotation completed:")
        for key_type, key_value in rotated_keys:
            print(f"   {key_type}: {key_value[:20]}...")
        
        # Update .env file (optional)
        print("\n⚠️  Remember to update your .env file with the new keys:")
        for key_type, key_value in rotated_keys:
            print(f"{key_type}={key_value}")
            
    except Exception as e:
        print(f"❌ Error rotating keys: {str(e)}")

@click.command()
@with_appcontext
def check_keys():
    """Check status of security keys"""
    try:
        from models.security import SecurityKey
        
        active_keys = SecurityKey.query.filter_by(is_active=True).all()
        
        print("🔐 Current Security Keys Status:")
        print("-" * 50)
        
        for key in active_keys:
            days_until_expiry = (key.expires_at - datetime.utcnow()).days
            status = "🟢 OK" if days_until_expiry > 7 else "🟡 EXPIRING SOON" if days_until_expiry > 0 else "🔴 EXPIRED"
            
            print(f"{key.key_type:<20} | {status:<15} | Expires: {key.expires_at.strftime('%Y-%m-%d')} ({days_until_expiry} days)")
        
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error checking keys: {str(e)}")

def register_security_commands(app):
    """Register security CLI commands"""
    app.cli.add_command(rotate_keys)
    app.cli.add_command(check_keys)