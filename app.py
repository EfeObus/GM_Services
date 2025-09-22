"""
GM Services - Main Flask Application Entry Point
A professional multi-service web platform providing automobile dealerships,
loans, logistics, rentals, hotel management, luxury jewelry, and more.
"""
from flask import Flask, render_template, redirect, url_for
from database import db
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_cors import CORS
import os
from dotenv import load_dotenv
from utils.activity_middleware import ActivityTrackingMiddleware

# Load environment variables
load_dotenv()

# Initialize extensions
login_manager = LoginManager()
migrate = Migrate()
socketio = SocketIO()
cors = CORS()
activity_tracker = ActivityTrackingMiddleware()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")
    cors.init_app(app)
    activity_tracker.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from blueprints.auth import auth_bp
    from blueprints.users import users_bp
    from blueprints.staff import staff_bp
    from blueprints.admin import admin_bp
    from blueprints.services import services_bp
    from blueprints.gadgets import gadgets_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/user')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(services_bp, url_prefix='/services')
    app.register_blueprint(gadgets_bp, url_prefix='/shop')
    
    # Register chat events
    from chat.events import register_chat_events
    register_chat_events(socketio)
    
    # Register inventory context processor
    from tasks.inventory_alerts import inventory_context_processor
    app.context_processor(inventory_context_processor)
    
    # Register CLI commands
    from cli_commands import register_cli_commands
    register_cli_commands(app)
    
    # Main routes
    @app.route('/')
    def index():
        """Homepage with service overview"""
        return render_template('index.html')
    
    @app.route('/about')
    def about():
        """About GM Services"""
        return render_template('about.html')
    
    @app.route('/contact')
    def contact():
        """Contact information"""
        return render_template('contact.html')
    
    @app.route('/privacy')
    def privacy():
        """Privacy Policy"""
        return render_template('privacy.html')
    
    @app.route('/terms')
    def terms():
        """Terms of Service"""
        return render_template('terms.html')
    
    @app.route('/support')
    def support():
        """Support Center"""
        return render_template('support.html')
    
    @app.route('/faq')
    def faq():
        """Frequently Asked Questions"""
        return render_template('faq.html')
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    # Run the app
    socketio.run(app, debug=False, host='0.0.0.0', port=5040)