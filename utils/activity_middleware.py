"""
Activity Tracking Middleware
Automatically tracks user activities and page views
"""
from flask import request, g, current_app
from flask_login import current_user
from utils.activity_logger import ActivityLogger
from datetime import datetime
import time

class ActivityTrackingMiddleware:
    """
    Middleware to automatically track user activities
    """
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_request)
    
    def before_request(self):
        """Track request start time and user activity"""
        g.start_time = time.time()
        g.should_log_activity = True
        
        # Skip logging for certain routes
        skip_routes = [
            'static',
            'favicon.ico',
            '_debug_toolbar',
            'debug-toolbar'
        ]
        
        if request.endpoint in skip_routes or request.path.startswith('/static/'):
            g.should_log_activity = False
            return
        
        # Log page view for authenticated users
        if current_user and current_user.is_authenticated:
            self._log_page_view()
    
    def after_request(self, response):
        """Track response and log activity if needed"""
        if not getattr(g, 'should_log_activity', False):
            return response
        
        # Calculate request duration
        duration_ms = None
        if hasattr(g, 'start_time'):
            duration_ms = int((time.time() - g.start_time) * 1000)
        
        # Log significant activities
        if current_user and current_user.is_authenticated:
            self._log_request_activity(response, duration_ms)
        
        return response
    
    def teardown_request(self, exception):
        """Handle any cleanup after request"""
        if exception:
            # Log error if authenticated user encountered an exception
            if current_user and current_user.is_authenticated:
                ActivityLogger.log_activity(
                    user_id=current_user.id,
                    activity_type='system_error',
                    action='request_error',
                    description=f'Error during request: {str(exception)}',
                    category='system',
                    success=False,
                    error_message=str(exception)
                )
    
    def _log_page_view(self):
        """Log page views for monitoring"""
        try:
            # Don't log API calls or AJAX requests
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return
            
            # Only log GET requests for page views
            if request.method != 'GET':
                return
            
            activity_type = 'page_view'
            action = f'viewed_{request.endpoint or "unknown"}'
            description = f'User viewed {request.path}'
            
            ActivityLogger.log_activity(
                user_id=current_user.id,
                activity_type=activity_type,
                action=action,
                description=description,
                category='navigation',
                metadata={
                    'endpoint': request.endpoint,
                    'path': request.path,
                    'args': dict(request.args) if request.args else None
                }
            )
            
        except Exception as e:
            current_app.logger.error(f"Failed to log page view: {str(e)}")
    
    def _log_request_activity(self, response, duration_ms):
        """Log significant user activities"""
        try:
            # Skip if already logged by specific routes
            if getattr(g, 'activity_logged', False):
                return
            
            # Define activities worth logging
            significant_activities = {
                'POST': 'form_submission',
                'PUT': 'data_update',
                'DELETE': 'data_deletion',
                'PATCH': 'data_modification'
            }
            
            if request.method in significant_activities:
                activity_type = significant_activities[request.method]
                action = f'{request.method.lower()}_{request.endpoint or "unknown"}'
                description = f'User performed {request.method} on {request.path}'
                
                # Determine success based on response status
                success = 200 <= response.status_code < 400
                error_message = None if success else f'HTTP {response.status_code}'
                
                ActivityLogger.log_activity(
                    user_id=current_user.id,
                    activity_type=activity_type,
                    action=action,
                    description=description,
                    category='user_action',
                    success=success,
                    error_message=error_message,
                    duration_ms=duration_ms,
                    metadata={
                        'endpoint': request.endpoint,
                        'status_code': response.status_code,
                        'form_data': self._safe_form_data() if request.form else None
                    }
                )
                
        except Exception as e:
            current_app.logger.error(f"Failed to log request activity: {str(e)}")
    
    def _safe_form_data(self):
        """Extract safe form data (excluding passwords and sensitive info)"""
        try:
            sensitive_fields = ['password', 'confirm_password', 'token', 'csrf_token', 'api_key']
            safe_data = {}
            
            for key, value in request.form.items():
                if key.lower() not in sensitive_fields:
                    safe_data[key] = value
            
            return safe_data if safe_data else None
            
        except Exception:
            return None

# Decorator for manual activity logging
def log_activity(activity_type, action, description=None, category='user_action', metadata=None):
    """
    Decorator to manually log specific activities
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)
                
                if current_user and current_user.is_authenticated:
                    ActivityLogger.log_activity(
                        user_id=current_user.id,
                        activity_type=activity_type,
                        action=action,
                        description=description or f'User performed {action}',
                        category=category,
                        success=True,
                        duration_ms=duration_ms,
                        metadata=metadata
                    )
                    # Mark as logged to avoid duplicate logging
                    g.activity_logged = True
                
                return result
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                
                if current_user and current_user.is_authenticated:
                    ActivityLogger.log_activity(
                        user_id=current_user.id,
                        activity_type=activity_type,
                        action=action,
                        description=description or f'Failed to perform {action}',
                        category=category,
                        success=False,
                        error_message=str(e),
                        duration_ms=duration_ms,
                        metadata=metadata
                    )
                
                raise
        
        return wrapper
    return decorator