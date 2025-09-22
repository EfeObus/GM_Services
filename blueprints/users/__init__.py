"""
Users Blueprint
Customer portal with dashboard, service bookings, and account management
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models.user import User
from database import db
from datetime import datetime
from utils.decorators import customer_required

# Try to import Service and ServiceRequest models
try:
    from models.service import Service
except ImportError:
    Service = None

try:
    from models.service_request import ServiceRequest  
except ImportError:
    ServiceRequest = None

try:
    from models.loan import LoanApplication
except ImportError:
    LoanApplication = None

try:
    from models.enhanced_loan import EnhancedLoanApplication, LoanType
except ImportError:
    EnhancedLoanApplication = None
    LoanType = None

# Create blueprint
users_bp = Blueprint('users', __name__, template_folder='templates')

@users_bp.route('/dashboard')
@login_required
@customer_required
def dashboard():
    """Customer dashboard"""
    if not ServiceRequest:
        # If ServiceRequest model is not available, show basic dashboard
        return render_template('users/dashboard.html',
                             recent_requests=[],
                             loan_applications=[],
                             pending_count=0,
                             completed_count=0)
    
    # Get user's recent service requests
    recent_requests = ServiceRequest.query.filter_by(
        customer_id=current_user.id
    ).order_by(ServiceRequest.created_at.desc()).limit(5).all()
    
    # Get counts for dashboard stats
    pending_count = ServiceRequest.query.filter_by(
        customer_id=current_user.id,
        status='submitted'
    ).count()
    
    completed_count = ServiceRequest.query.filter_by(
        customer_id=current_user.id,
        status='resolved'
    ).count()
    
    # Get user's loan applications (check if LoanApplication exists)
    if LoanApplication:
        loan_applications = LoanApplication.query.filter_by(
            user_id=current_user.id
        ).order_by(LoanApplication.created_at.desc()).limit(3).all()
    else:
        loan_applications = []
    
    return render_template('users/dashboard.html', 
                         recent_requests=recent_requests,
                         loan_applications=loan_applications,
                         pending_count=pending_count,
                         completed_count=completed_count)

@users_bp.route('/profile')
@login_required
@customer_required
def profile():
    """User profile page"""
    return render_template('users/profile.html')

@users_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@customer_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')
        current_user.city = request.form.get('city')
        current_user.state = request.form.get('state')
        current_user.country = request.form.get('country')
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('users.profile'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')
    
    return render_template('users/edit_profile.html')

@users_bp.route('/services')
@login_required
@customer_required
def services():
    """Available services"""
    services = Service.query.filter_by(is_active=True).all()
    return render_template('users/services.html', services=services)

@users_bp.route('/services/<int:service_id>')
@login_required
@customer_required
def service_detail(service_id):
    """Service detail page"""
    service = Service.query.get_or_404(service_id)
    return render_template('users/service_detail.html', service=service)

@users_bp.route('/services/<int:service_id>/request', methods=['GET', 'POST'])
@login_required
@customer_required
def request_service(service_id):
    """Request a service"""
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'POST':
        description = request.form.get('description')
        preferred_date = request.form.get('preferred_date')
        
        if not description:
            flash('Please provide a description of your requirements.', 'error')
            return render_template('users/request_service.html', service=service)
        
        service_request = ServiceRequest(
            user_id=current_user.id,
            service_id=service_id,
            description=description,
            preferred_date=datetime.strptime(preferred_date, '%Y-%m-%d') if preferred_date else None,
            status='pending'
        )
        
        try:
            db.session.add(service_request)
            db.session.commit()
            flash('Service request submitted successfully!', 'success')
            return redirect(url_for('users.my_requests'))
        except Exception as e:
            db.session.rollback()
            flash('Error submitting request. Please try again.', 'error')
    
    return render_template('users/request_service.html', service=service)

@users_bp.route('/my-requests')
@login_required
@customer_required
def my_requests():
    """User's service requests"""
    requests = ServiceRequest.query.filter_by(
        user_id=current_user.id
    ).order_by(ServiceRequest.created_at.desc()).all()
    
    return render_template('users/my_requests.html', requests=requests)

@users_bp.route('/loans')
@login_required
@customer_required
def loan_applications():
    """User's loan applications"""
    # Try to get enhanced loan applications first
    if EnhancedLoanApplication:
        applications = EnhancedLoanApplication.query.filter_by(
            user_id=current_user.id
        ).order_by(EnhancedLoanApplication.created_at.desc()).all()
    elif LoanApplication:
        # Fallback to old loan applications
        applications = LoanApplication.query.filter_by(
            user_id=current_user.id
        ).order_by(LoanApplication.created_at.desc()).all()
    else:
        applications = []
    
    return render_template('users/loan_applications.html', applications=applications)

@users_bp.route('/loans/<int:application_id>')
@login_required
@customer_required
def view_loan_application(application_id):
    """View loan application details"""
    if EnhancedLoanApplication:
        application = EnhancedLoanApplication.query.filter_by(
            id=application_id, 
            user_id=current_user.id
        ).first_or_404()
    else:
        application = LoanApplication.query.filter_by(
            id=application_id, 
            user_id=current_user.id
        ).first_or_404()
    
    return render_template('users/loan_application_detail.html', application=application)

@users_bp.route('/loans/apply', methods=['GET', 'POST'])
@login_required
@customer_required
def apply_loan():
    """Apply for a loan"""
    if request.method == 'POST':
        loan_type = request.form.get('loan_type')
        amount = float(request.form.get('amount'))
        purpose = request.form.get('purpose')
        employment_status = request.form.get('employment_status')
        monthly_income = float(request.form.get('monthly_income'))
        
        loan_application = LoanApplication(
            user_id=current_user.id,
            loan_type=loan_type,
            amount=amount,
            purpose=purpose,
            employment_status=employment_status,
            monthly_income=monthly_income,
            status='pending'
        )
        
        try:
            db.session.add(loan_application)
            db.session.commit()
            flash('Loan application submitted successfully!', 'success')
            return redirect(url_for('users.my_loans'))
        except Exception as e:
            db.session.rollback()
            flash('Error submitting loan application. Please try again.', 'error')
    
    return render_template('users/apply_loan.html')

@users_bp.route('/my-loans')
@login_required
@customer_required
def my_loans():
    """User's loan applications"""
    loans = LoanApplication.query.filter_by(
        user_id=current_user.id
    ).order_by(LoanApplication.created_at.desc()).all()
    
    return render_template('users/my_loans.html', loans=loans)

@users_bp.route('/chat')
@login_required
@customer_required
def chat():
    """Live chat with support"""
    return render_template('users/chat.html')

@users_bp.route('/notifications')
@login_required
@customer_required
def notifications():
    """User notifications"""
    return render_template('users/notifications.html')

@users_bp.route('/billing')
@login_required
@customer_required
def billing():
    """Billing and payments"""
    return render_template('users/billing.html')