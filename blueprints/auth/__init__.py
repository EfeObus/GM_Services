"""
Authentication Blueprint
Handles user registration, login, logout, and password management
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import User
from database import db
import re
import requests
import jwt
from datetime import datetime
from utils.activity_logger import ActivityLogger

# Create blueprint
auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = bool(request.form.get('remember_me'))
        
        if not email or not password:
            flash('Please provide both email and password.', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                # Log failed login attempt
                ActivityLogger.log_activity(
                    user_id=user.id,
                    activity_type='authentication',
                    action='login_failed',
                    description='Login failed - account inactive',
                    category='auth',
                    success=False,
                    error_message='Account is inactive'
                )
                flash('Your account is inactive. Please contact support.', 'error')
                return render_template('auth/login.html')
            
            # Update user's last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=remember_me)
            
            # Log successful login
            ActivityLogger.log_login(user.id, login_method='password')
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            # Redirect based on user role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'staff':
                return redirect(url_for('staff.dashboard'))
            else:
                return redirect(url_for('users.dashboard'))
        else:
            # Log failed login attempt
            ActivityLogger.log_activity(
                user_id=user.id if user else None,
                activity_type='authentication',
                action='login_failed',
                description='Login failed - invalid credentials',
                category='auth',
                success=False,
                error_message='Invalid email or password',
                metadata={'attempted_email': email}
            )
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        errors = []
        
        if not all([first_name, last_name, email, password, confirm_password]):
            errors.append('All fields are required.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append('Please enter a valid email address.')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email address already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(password),
            role='customer'
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Log user registration
            ActivityLogger.log_user_registration(
                user_id=user.id,
                registration_method='email',
                registration_source='web'
            )
            
            login_user(user)
            
            # Log initial login after registration
            ActivityLogger.log_login(user.id, login_method='password')
            
            flash('Registration successful! Welcome to GM Services.', 'success')
            return redirect(url_for('users.dashboard'))
        
        except Exception as e:
            db.session.rollback()
            # Log failed registration
            ActivityLogger.log_activity(
                activity_type='registration',
                action='registration_failed',
                description='User registration failed',
                category='auth',
                success=False,
                error_message=str(e),
                metadata={'attempted_email': email}
            )
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    user_id = current_user.id
    
    # Log logout
    ActivityLogger.log_logout(user_id, logout_reason='manual')
    
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password"""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # TODO: Implement email sending with reset token
            flash('If this email is registered, you will receive password reset instructions.', 'info')
        else:
            flash('If this email is registered, you will receive password reset instructions.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    # TODO: Implement token verification and password reset
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/reset_password.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/reset_password.html')
        
        # Update password logic here
        flash('Password reset successful! Please log in with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html')

# OAuth Routes
@auth_bp.route('/oauth/google')
def google_oauth():
    """Redirect to Google OAuth"""
    google_client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    redirect_uri = url_for('auth.google_callback', _external=True)
    
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={google_client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid email profile&"
        f"response_type=code&"
        f"access_type=offline"
    )
    
    return redirect(google_auth_url)

@auth_bp.route('/oauth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    code = request.args.get('code')
    
    if not code:
        flash('Google authentication failed.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Exchange code for token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'client_id': current_app.config.get('GOOGLE_CLIENT_ID'),
            'client_secret': current_app.config.get('GOOGLE_CLIENT_SECRET'),
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': url_for('auth.google_callback', _external=True)
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            raise Exception('Failed to get access token')
        
        # Get user info from Google
        user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={token_json['access_token']}"
        user_response = requests.get(user_info_url)
        user_info = user_response.json()
        
        # Check if user exists
        user = User.query.filter_by(google_id=user_info['id']).first()
        
        if not user:
            # Check if email already exists
            existing_user = User.query.filter_by(email=user_info['email']).first()
            if existing_user:
                # Link Google account to existing user
                existing_user.google_id = user_info['id']
                user = existing_user
                
                # Log account linking
                ActivityLogger.log_activity(
                    user_id=user.id,
                    activity_type='authentication',
                    action='oauth_account_linked',
                    description='Google account linked to existing user',
                    category='auth',
                    metadata={'oauth_provider': 'google', 'google_id': user_info['id']}
                )
            else:
                # Create new user
                user = User(
                    first_name=user_info.get('given_name', ''),
                    last_name=user_info.get('family_name', ''),
                    email=user_info['email'],
                    google_id=user_info['id'],
                    role='customer',
                    is_active=True,
                    is_verified=True,
                    password_hash=generate_password_hash('oauth_user')  # Generate random password
                )
                db.session.add(user)
                db.session.commit()
                
                # Log OAuth registration
                ActivityLogger.log_user_registration(
                    user_id=user.id,
                    registration_method='google',
                    registration_source='web',
                    oauth_provider='google',
                    oauth_id=user_info['id']
                )
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user)
        
        # Log OAuth login
        ActivityLogger.log_login(user.id, login_method='google')
        
        flash(f'Welcome, {user.first_name}!', 'success')
        
        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('users.dashboard'))
        
    except Exception as e:
        current_app.logger.error(f"Google OAuth error: {str(e)}")
        flash('Google authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/oauth/apple')
def apple_oauth():
    """Redirect to Apple OAuth"""
    apple_client_id = current_app.config.get('APPLE_CLIENT_ID')
    redirect_uri = url_for('auth.apple_callback', _external=True)
    
    apple_auth_url = (
        f"https://appleid.apple.com/auth/authorize?"
        f"client_id={apple_client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=name email&"
        f"response_type=code&"
        f"response_mode=form_post"
    )
    
    return redirect(apple_auth_url)

@auth_bp.route('/oauth/apple/callback', methods=['POST'])
def apple_callback():
    """Handle Apple OAuth callback"""
    code = request.form.get('code')
    id_token = request.form.get('id_token')
    
    if not code or not id_token:
        flash('Apple authentication failed.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Decode the ID token (without verification for simplicity - in production, verify the signature)
        decoded_token = jwt.decode(id_token, options={"verify_signature": False})
        
        apple_id = decoded_token.get('sub')
        email = decoded_token.get('email')
        
        if not apple_id or not email:
            raise Exception('Invalid Apple ID token')
        
        # Check if user exists
        user = User.query.filter_by(apple_id=apple_id).first()
        
        if not user:
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                # Link Apple account to existing user
                existing_user.apple_id = apple_id
                user = existing_user
            else:
                # Create new user
                # Apple doesn't always provide name, so use email prefix as fallback
                name_parts = email.split('@')[0].split('.')
                first_name = name_parts[0].capitalize() if len(name_parts) > 0 else 'User'
                last_name = name_parts[1].capitalize() if len(name_parts) > 1 else ''
                
                user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    apple_id=apple_id,
                    role='customer',
                    is_active=True,
                    is_verified=True,
                    password_hash=generate_password_hash('oauth_user')  # Generate random password
                )
                db.session.add(user)
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user)
        flash(f'Welcome, {user.first_name}!', 'success')
        
        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('users.dashboard'))
        
    except Exception as e:
        current_app.logger.error(f"Apple OAuth error: {str(e)}")
        flash('Apple authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))