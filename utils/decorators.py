"""
Role-based Access Control Decorators
Provides decorators for protecting routes based on user roles
"""
from functools import wraps
from flask import abort, redirect, url_for, flash, request
from flask_login import current_user, login_required

def admin_required(f):
    """
    Decorator to require admin role
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    """
    Decorator to require staff role (staff or admin)
    Also checks if password change is required for first-time staff login
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.can_access_staff():
            flash('Access denied. Staff privileges required.', 'error')
            abort(403)
        
        # Check if password change is required (but allow access to change_password route)
        if (current_user.password_change_required and 
            request.endpoint != 'staff.change_password'):
            flash('You must change your password before continuing.', 'warning')
            return redirect(url_for('staff.change_password'))
        
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    """
    Decorator to require customer role (any authenticated user)
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """
    Decorator to require specific roles
    Usage: @role_required('admin', 'staff')
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                flash(f'Access denied. Required roles: {", ".join(roles)}', 'error')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def active_user_required(f):
    """
    Decorator to ensure user account is active
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_active:
            flash('Your account is inactive. Please contact support.', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def verified_user_required(f):
    """
    Decorator to ensure user is verified
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_verified:
            flash('Please verify your account to access this feature.', 'error')
            return redirect(url_for('auth.verify_email'))
        return f(*args, **kwargs)
    return decorated_function