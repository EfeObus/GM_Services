"""
Admin Blueprint
Administrative portal for managing users, services, staff assignments, and analytics
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models.user import User
from models.loan import LoanApplication
from models.enhanced_loan import EnhancedLoanApplication, LoanType, LoanPolicy
from models.hotel import HotelServiceRequest
from models.activity_tracking import ActivityLog, UsageStatistics, UserRegistration, StaffOnboarding, LoginSession
from models.inventory import InventoryLocation, InventoryItem, StockMovement, LowStockAlert, StaffLocationAssignment
from models.ecommerce import Product, ProductCategory
from models.jewelry import JewelryItem
from models.automobile import Vehicle
from utils.activity_logger import ActivityLogger
from database import db
from datetime import datetime, timedelta
from utils.decorators import admin_required
from sqlalchemy import func, and_, or_
import pandas as pd
import csv
import io
import os
from werkzeug.utils import secure_filename

# Initialize activity logger
logger = ActivityLogger()

# Try to import Service and ServiceRequest models
try:
    from models.service import Service
except ImportError:
    Service = None

try:
    from models.service_request import ServiceRequest  
except ImportError:
    ServiceRequest = None

# Create blueprint
admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with overview statistics"""
    try:
        # Log admin dashboard access
        ActivityLogger.log_activity(
            user_id=current_user.id,
            activity_type='admin_dashboard_access',
            description=f'Admin {current_user.full_name} accessed dashboard',
            metadata={'admin_id': current_user.id}
        )
        
        # Get basic counts
        user_count = User.query.count()
        staff_count = User.query.filter_by(role='staff').count()
        customer_count = User.query.filter_by(role='customer').count()
        admin_count = User.query.filter_by(role='admin').count()
        
        # Safe model access
        service_count = Service.query.count() if Service else 0
        pending_requests = ServiceRequest.query.filter_by(status='pending').count() if ServiceRequest else 0
        
        # Get inventory statistics
        total_locations = InventoryLocation.query.filter_by(is_active=True).count()
        total_inventory_items = InventoryItem.query.filter_by(status='active').count()
        low_stock_count = InventoryItem.query.filter(
            InventoryItem.status == 'active',
            InventoryItem.current_stock <= InventoryItem.reorder_point
        ).count()
        out_of_stock_count = InventoryItem.query.filter(
            InventoryItem.status == 'active',
            InventoryItem.current_stock <= 0
        ).count()
        
        # Get total inventory value
        total_inventory_value = db.session.query(
            func.sum(InventoryItem.current_stock * InventoryItem.unit_cost)
        ).filter(InventoryItem.status == 'active').scalar() or 0
        
        # Get recent activities (last 10)
        recent_activities = ActivityLog.query.order_by(
            ActivityLog.timestamp.desc()
        ).limit(10).all()
        
        # Get today's statistics
        today = datetime.now().date()
        new_registrations_today = UserRegistration.query.filter(
            func.date(UserRegistration.registration_date) == today
        ).count()
        
        failed_logins = ActivityLog.query.filter(
            ActivityLog.activity_type == 'login',
            ActivityLog.success == False,
            func.date(ActivityLog.timestamp) == today
        ).count()
        
        # Get recent low stock alerts (last 5)
        recent_inventory_alerts = LowStockAlert.query.filter_by(status='active')\
            .order_by(LowStockAlert.created_at.desc()).limit(5).all()
        
        return render_template('admin/dashboard.html',
                             user_count=user_count,
                             staff_count=staff_count,
                             customer_count=customer_count,
                             admin_count=admin_count,
                             service_count=service_count,
                             pending_requests=pending_requests,
                             total_locations=total_locations,
                             total_inventory_items=total_inventory_items,
                             low_stock_count=low_stock_count,
                             out_of_stock_count=out_of_stock_count,
                             total_inventory_value=total_inventory_value,
                             recent_activities=recent_activities,
                             recent_inventory_alerts=recent_inventory_alerts,
                             new_registrations_today=new_registrations_today,
                             failed_logins=failed_logins,
                             last_backup=None,  # Could implement backup tracking
                             uptime=None,  # Could implement uptime tracking
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                             
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('admin/dashboard.html',
                             user_count=0,
                             staff_count=0,
                             service_count=0,
                             pending_requests=0,
                             recent_activities=[],
                             new_registrations_today=0,
                             failed_logins=0,
                             last_backup=None,
                             uptime=None,
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Redirect to dashboard"""
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Manage users"""
    try:
        role_filter = request.args.get('role', 'all')
        search = request.args.get('search', '')
        
        query = User.query
        
        if role_filter != 'all':
            query = query.filter_by(role=role_filter)
        
        if search:
            query = query.filter(
                db.or_(
                    User.first_name.contains(search),
                    User.last_name.contains(search),
                    User.email.contains(search)
                )
            )
        
        users = query.order_by(User.created_at.desc()).all()
        
        # Log admin accessing users list
        logger.log_activity(
            user_id=current_user.id,
            action='view_users_list',
            description=f'Admin viewed users list with filters - role: {role_filter}, search: {search}',
            metadata={'role_filter': role_filter, 'search_term': search, 'total_users': len(users)}
        )
        
        return render_template('admin/users.html', users=users, role_filter=role_filter, search=search)
        
    except Exception as e:
        flash(f'Error loading users: {str(e)}', 'error')
        return render_template('admin/users.html', users=[], role_filter='all', search='')

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """User detail page"""
    user = User.query.get_or_404(user_id)
    
    # Get user's service requests if customer
    service_requests = []
    loan_applications = []
    
    if user.role == 'customer':
        service_requests = ServiceRequest.query.filter_by(customer_id=user_id).order_by(ServiceRequest.created_at.desc()).all()
        loan_applications = LoanApplication.query.filter_by(user_id=user_id).order_by(LoanApplication.created_at.desc()).all()
    
    return render_template('admin/user_detail.html', 
                         user=user,
                         service_requests=service_requests,
                         loan_applications=loan_applications)

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    old_status = user.is_active
    user.is_active = not user.is_active
    
    try:
        db.session.commit()
        status = 'activated' if user.is_active else 'deactivated'
        flash(f'User {status} successfully!', 'success')
        
        # Log the activity
        logger.log_activity(
            user_id=current_user.id,
            action='user_status_changed',
            description=f'User {user.first_name} {user.last_name} (ID: {user.id}) {status} by admin',
            metadata={'target_user_id': user.id, 'previous_status': old_status, 'new_status': user.is_active}
        )
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating user status.', 'error')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/staff')
@login_required
@admin_required
def staff():
    """Manage staff"""
    try:
        staff_members = User.query.filter_by(role='staff').order_by(User.created_at.desc()).all()
        
        # Get staff performance metrics
        staff_stats = {}
        for staff_member in staff_members:
            try:
                if ServiceRequest:
                    assigned_tasks = ServiceRequest.query.filter_by(assigned_to_id=staff_member.id).count()
                    completed_tasks = ServiceRequest.query.filter_by(
                        assigned_to_id=staff_member.id,
                        status='completed'
                    ).count()
                else:
                    assigned_tasks = 0
                    completed_tasks = 0
                
                staff_stats[staff_member.id] = {
                    'assigned_tasks': assigned_tasks,
                    'completed_tasks': completed_tasks
                }
            except Exception as e:
                print(f"Error getting stats for staff {staff_member.id}: {e}")
                staff_stats[staff_member.id] = {
                    'assigned_tasks': 0,
                    'completed_tasks': 0
                }
        
        # Log admin accessing staff list
        logger.log_activity(
            user_id=current_user.id,
            action='view_staff_list',
            description=f'Admin viewed staff management page',
            metadata={'total_staff': len(staff_members)}
        )
        
        return render_template('admin/staff.html', staff_members=staff_members, staff_stats=staff_stats)
        
    except Exception as e:
        flash(f'Error loading staff management: {str(e)}', 'error')
        return render_template('admin/staff.html', staff_members=[], staff_stats={})

@admin_bp.route('/staff/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_staff():
    """Create new staff member"""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        department = request.form.get('department')
        
        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return render_template('admin/create_staff.html')
        
        # Create staff user
        from werkzeug.security import generate_password_hash
        import secrets
        
        temp_password = secrets.token_urlsafe(8)
        
        staff_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(temp_password),
            role='staff',
            department=department,
            password_change_required=True  # Force password change on first login
        )
        
        try:
            db.session.add(staff_user)
            db.session.commit()
            
            # Log staff onboarding
            ActivityLogger.log_staff_onboarding(
                staff_user_id=staff_user.id,
                onboarded_by_id=current_user.id,
                department=department,
                position=request.form.get('position', ''),
                employee_id=f"EMP{staff_user.id:04d}",
                notes=f"Staff member created by {current_user.full_name}"
            )
            
            # TODO: Send email with temporary password
            flash(f'Staff member created! Temporary password: {temp_password}', 'success')
            return redirect(url_for('admin.staff'))
        except Exception as e:
            db.session.rollback()
            # Log failed staff creation
            ActivityLogger.log_activity(
                performed_by_id=current_user.id,
                activity_type='staff_management',
                action='staff_creation_failed',
                description='Failed to create staff member',
                category='user_management',
                success=False,
                error_message=str(e),
                metadata={'attempted_email': email, 'department': department}
            )
            flash('Error creating staff member.', 'error')
    
    return render_template('admin/create_staff.html')

@admin_bp.route('/staff/<int:staff_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_staff(staff_id):
    """Delete a staff member"""
    try:
        staff_member = User.query.filter_by(id=staff_id, role='staff').first_or_404()
        
        # Prevent admin from deleting themselves
        if staff_member.id == current_user.id:
            flash('You cannot delete your own account', 'error')
            return redirect(url_for('admin.staff'))
        
        staff_name = f"{staff_member.first_name} {staff_member.last_name}"
        staff_email = staff_member.email
        
        # Soft delete by deactivating instead of actual deletion to preserve data integrity
        staff_member.is_active = False
        staff_member.email = f"deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{staff_member.email}"
        
        db.session.commit()
        
        # Log staff deletion
        ActivityLogger.log_activity(
            user_id=current_user.id,
            activity_type='staff_management',
            action='staff_deleted',
            description=f'Admin deleted staff member: {staff_name}',
            category='user_management',
            success=True,
            metadata={'deleted_staff_id': staff_id, 'deleted_staff_name': staff_name, 'deleted_staff_email': staff_email}
        )
        
        flash(f'Staff member {staff_name} has been deleted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting staff member: {str(e)}', 'error')
    
    return redirect(url_for('admin.staff'))

@admin_bp.route('/staff/<int:staff_id>/change-password', methods=['POST'])
@login_required
@admin_required
def change_staff_password(staff_id):
    """Change staff member password"""
    try:
        staff_member = User.query.filter_by(id=staff_id, role='staff').first_or_404()
        new_password = request.form.get('new_password')
        
        if not new_password or len(new_password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return redirect(url_for('admin.user_detail', user_id=staff_id))
        
        from werkzeug.security import generate_password_hash
        staff_member.password_hash = generate_password_hash(new_password)
        staff_member.password_change_required = True  # Force password change on next login
        staff_member.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log password change
        ActivityLogger.log_activity(
            user_id=current_user.id,
            activity_type='staff_management',
            action='password_changed',
            description=f'Admin changed password for staff: {staff_member.first_name} {staff_member.last_name}',
            category='user_management',
            success=True,
            metadata={'staff_id': staff_id, 'staff_email': staff_member.email}
        )
        
        flash(f'Password changed for {staff_member.first_name} {staff_member.last_name}. They will be required to change it on next login.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error changing password: {str(e)}', 'error')
    
    return redirect(url_for('admin.user_detail', user_id=staff_id))

@admin_bp.route('/staff/<int:staff_id>/change-role', methods=['POST'])
@login_required
@admin_required
def change_staff_role(staff_id):
    """Change staff member role"""
    try:
        staff_member = User.query.filter_by(id=staff_id).first_or_404()
        new_role = request.form.get('new_role')
        new_department = request.form.get('new_department')
        
        # Prevent admin from demoting themselves
        if staff_member.id == current_user.id and new_role != 'admin':
            flash('You cannot change your own role', 'error')
            return redirect(url_for('admin.user_detail', user_id=staff_id))
        
        if new_role not in ['admin', 'staff', 'customer']:
            flash('Invalid role specified', 'error')
            return redirect(url_for('admin.user_detail', user_id=staff_id))
        
        old_role = staff_member.role
        old_department = staff_member.department
        
        staff_member.role = new_role
        if new_department:
            staff_member.department = new_department
        staff_member.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log role change
        ActivityLogger.log_activity(
            user_id=current_user.id,
            activity_type='staff_management',
            action='role_changed',
            description=f'Admin changed role for {staff_member.first_name} {staff_member.last_name} from {old_role} to {new_role}',
            category='user_management',
            success=True,
            metadata={
                'staff_id': staff_id,
                'staff_email': staff_member.email,
                'old_role': old_role,
                'new_role': new_role,
                'old_department': old_department,
                'new_department': new_department
            }
        )
        
        flash(f'Role changed for {staff_member.first_name} {staff_member.last_name} from {old_role} to {new_role}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error changing role: {str(e)}', 'error')
    
    return redirect(url_for('admin.user_detail', user_id=staff_id))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user account"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent admin from deleting themselves
        if user.id == current_user.id:
            flash('You cannot delete your own account', 'error')
            return redirect(url_for('admin.users'))
        
        # Prevent deletion of other admins unless current user is super admin
        if user.role == 'admin' and current_user.role != 'super_admin':
            flash('You cannot delete admin accounts', 'error')
            return redirect(url_for('admin.users'))
        
        user_name = f"{user.first_name} {user.last_name}"
        user_email = user.email
        user_role = user.role
        
        # Soft delete by deactivating instead of actual deletion
        user.is_active = False
        user.email = f"deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user.email}"
        
        db.session.commit()
        
        # Log user deletion
        ActivityLogger.log_activity(
            user_id=current_user.id,
            activity_type='user_management',
            action='user_deleted',
            description=f'Admin deleted user: {user_name} ({user_role})',
            category='user_management',
            success=True,
            metadata={'deleted_user_id': user_id, 'deleted_user_name': user_name, 'deleted_user_email': user_email, 'deleted_user_role': user_role}
        )
        
        flash(f'User {user_name} has been deleted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/update', methods=['POST'])
@login_required
@admin_required
def update_user_details(user_id):
    """Update user details upon request"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        
        # Update user details
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if phone:
            user.phone = phone
        if address:
            user.address = address
        if city:
            user.city = city
        if state:
            user.state = state
        
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log user update
        ActivityLogger.log_activity(
            user_id=current_user.id,
            activity_type='user_management',
            action='user_details_updated',
            description=f'Admin updated details for user: {user.first_name} {user.last_name}',
            category='user_management',
            success=True,
            metadata={'updated_user_id': user_id, 'updated_user_email': user.email}
        )
        
        flash(f'User details updated successfully for {user.first_name} {user.last_name}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user details: {str(e)}', 'error')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/hotel-requests')
@login_required
@admin_required
def hotel_requests():
    """Manage hotel service requests"""
    status_filter = request.args.get('status', 'all')
    service_type_filter = request.args.get('service_type', 'all')
    priority_filter = request.args.get('priority', 'all')
    
    query = HotelServiceRequest.query
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter(HotelServiceRequest.status == status_filter)
    if service_type_filter != 'all':
        query = query.filter(HotelServiceRequest.service_type == service_type_filter)
    if priority_filter != 'all':
        query = query.filter(HotelServiceRequest.priority_level == priority_filter)
    
    # Get requests with pagination
    page = request.args.get('page', 1, type=int)
    requests = query.order_by(HotelServiceRequest.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get filter counts
    total_requests = HotelServiceRequest.query.count()
    pending_requests = HotelServiceRequest.query.filter_by(status='pending').count()
    in_progress_requests = HotelServiceRequest.query.filter_by(status='in_progress').count()
    completed_requests = HotelServiceRequest.query.filter_by(status='completed').count()
    
    # Get staff members for assignment
    staff_members = User.query.filter_by(role='staff').all()
    
    return render_template('admin/hotel_requests.html',
                         requests=requests,
                         status_filter=status_filter,
                         service_type_filter=service_type_filter,
                         priority_filter=priority_filter,
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         in_progress_requests=in_progress_requests,
                         completed_requests=completed_requests,
                         staff_members=staff_members)

@admin_bp.route('/hotel-requests/<int:request_id>')
@login_required
@admin_required
def hotel_request_detail(request_id):
    """View hotel request details"""
    hotel_request = HotelServiceRequest.query.get_or_404(request_id)
    staff_members = User.query.filter_by(role='staff').all()
    
    return render_template('admin/hotel_request_detail.html',
                         hotel_request=hotel_request,
                         staff_members=staff_members)

@admin_bp.route('/hotel-requests/<int:request_id>/assign', methods=['POST'])
@login_required
@admin_required
def assign_hotel_request(request_id):
    """Assign hotel request to staff"""
    hotel_request = HotelServiceRequest.query.get_or_404(request_id)
    staff_id = request.form.get('staff_id')
    
    try:
        if staff_id:
            staff_member = User.query.get(staff_id)
            if staff_member and staff_member.role == 'staff':
                hotel_request.assigned_to_id = staff_id
                hotel_request.assigned_at = datetime.utcnow()
                hotel_request.status = 'assigned'
                
                # Log activity
                ActivityLogger.log_activity(
                    user_id=current_user.id,
                    action='assign_hotel_request',
                    description=f'Assigned hotel request {hotel_request.request_number} to {staff_member.full_name}'
                )
                
                db.session.commit()
                flash(f'Hotel request assigned to {staff_member.full_name} successfully!', 'success')
            else:
                flash('Invalid staff member selected.', 'error')
        else:
            # Unassign
            hotel_request.assigned_to_id = None
            hotel_request.assigned_at = None
            hotel_request.status = 'pending'
            db.session.commit()
            flash('Hotel request unassigned successfully!', 'success')
            
    except Exception as e:
        db.session.rollback()
        flash('Error assigning hotel request.', 'error')
    
    return redirect(url_for('admin.hotel_request_detail', request_id=request_id))

@admin_bp.route('/hotel-requests/<int:request_id>/update-status', methods=['POST'])
@login_required
@admin_required 
def update_hotel_request_status(request_id):
    """Update hotel request status"""
    hotel_request = HotelServiceRequest.query.get_or_404(request_id)
    new_status = request.form.get('status')
    admin_notes = request.form.get('admin_notes', '')
    
    try:
        if new_status in ['pending', 'reviewed', 'assigned', 'in_progress', 'completed', 'cancelled']:
            old_status = hotel_request.status
            hotel_request.status = new_status
            
            if admin_notes:
                hotel_request.admin_notes = admin_notes
            
            # Log activity
            ActivityLogger.log_activity(
                user_id=current_user.id,
                action='update_hotel_request_status',
                description=f'Updated hotel request {hotel_request.request_number} status from {old_status} to {new_status}'
            )
            
            db.session.commit()
            flash(f'Hotel request status updated to {new_status.replace("_", " ").title()}!', 'success')
        else:
            flash('Invalid status selected.', 'error')
            
    except Exception as e:
        db.session.rollback()
        flash('Error updating hotel request status.', 'error')
    
    return redirect(url_for('admin.hotel_request_detail', request_id=request_id))

@admin_bp.route('/requests')
@login_required
@admin_required
def requests():
    """Manage service requests"""
    status_filter = request.args.get('status', 'all')
    
    query = ServiceRequest.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    requests = query.order_by(ServiceRequest.created_at.desc()).all()
    
    # Get staff for assignment
    staff_members = User.query.filter_by(role='staff', is_active=True).all()
    
    return render_template('admin/requests.html', 
                         requests=requests, 
                         status_filter=status_filter,
                         staff_members=staff_members)

@admin_bp.route('/requests/<int:request_id>/assign', methods=['POST'])
@login_required
@admin_required
def assign_request(request_id):
    """Assign service request to staff"""
    service_request = ServiceRequest.query.get_or_404(request_id)
    staff_id = request.form.get('staff_id')
    
    if staff_id:
        staff_member = User.query.get(staff_id)
        if staff_member and staff_member.role == 'staff':
            service_request.assigned_to_id = staff_id
            service_request.status = 'in_progress'
            service_request.updated_at = datetime.utcnow()
            
            try:
                db.session.commit()
                flash('Request assigned successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error assigning request.', 'error')
        else:
            flash('Invalid staff member.', 'error')
    else:
        flash('Please select a staff member.', 'error')
    
    return redirect(url_for('admin.requests'))

@admin_bp.route('/loans')
@login_required
@admin_required
def loans():
    """Manage enhanced loan applications"""
    status_filter = request.args.get('status', 'all')
    loan_type_filter = request.args.get('loan_type', 'all')
    
    query = EnhancedLoanApplication.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if loan_type_filter != 'all':
        query = query.filter_by(loan_type_id=loan_type_filter)
    
    loans = query.order_by(EnhancedLoanApplication.created_at.desc()).all()
    loan_types = LoanType.query.filter_by(is_active=True).all()
    staff_members = User.query.filter_by(role='staff', is_active=True).all()
    
    return render_template('admin/enhanced_loans.html', 
                         loans=loans, 
                         loan_types=loan_types,
                         staff_members=staff_members,
                         status_filter=status_filter,
                         loan_type_filter=loan_type_filter)

@admin_bp.route('/loans/<int:loan_id>')
@login_required
@admin_required
def view_loan(loan_id):
    """View detailed loan application"""
    loan = EnhancedLoanApplication.query.get_or_404(loan_id)
    staff_members = User.query.filter_by(role='staff', is_active=True).all()
    
    return render_template('admin/loan_detail.html', 
                         loan=loan, 
                         staff_members=staff_members)

@admin_bp.route('/loans/<int:loan_id>/assign', methods=['POST'])
@login_required
@admin_required
def assign_loan(loan_id):
    """Assign loan to staff member"""
    loan = EnhancedLoanApplication.query.get_or_404(loan_id)
    staff_id = request.form.get('staff_id')
    
    if staff_id:
        staff_member = User.query.filter_by(id=staff_id, role='staff', is_active=True).first()
        if staff_member:
            try:
                loan.assign_to_staff(staff_id, current_user.id)
                db.session.commit()
                
                # Log the assignment
                ActivityLogger.log_activity(
                    user_id=current_user.id,
                    action='loan_assigned',
                    description=f'Assigned loan {loan.application_number} to {staff_member.full_name}'
                )
                
                flash(f'Loan application assigned to {staff_member.full_name} successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error assigning loan: {str(e)}', 'error')
        else:
            flash('Invalid staff member selected.', 'error')
    else:
        flash('Please select a staff member.', 'error')
    
    return redirect(url_for('admin.view_loan', loan_id=loan_id))

@admin_bp.route('/loans/<int:loan_id>/update', methods=['POST'])
@login_required
@admin_required
def update_loan_status(loan_id):
    """Update loan application status"""
    loan = EnhancedLoanApplication.query.get_or_404(loan_id)
    new_status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    if new_status in ['approved', 'rejected']:
        try:
            if new_status == 'approved':
                approved_amount = request.form.get('approved_amount')
                interest_rate = request.form.get('interest_rate')
                
                loan.approve_loan(
                    approved_by_id=current_user.id,
                    approved_amount=float(approved_amount) if approved_amount else None,
                    interest_rate=float(interest_rate) if interest_rate else None
                )
                
                action_msg = f'Approved loan {loan.application_number}'
            else:
                rejection_reason = request.form.get('rejection_reason', notes)
                loan.reject_loan(current_user.id, rejection_reason)
                action_msg = f'Rejected loan {loan.application_number}'
            
            if notes:
                loan.review_notes = notes
            
            db.session.commit()
            
            # Log the action
            ActivityLogger.log_activity(
                user_id=current_user.id,
                action='loan_reviewed',
                description=action_msg
            )
            
            flash(f'Loan application {new_status} successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating loan status: {str(e)}', 'error')
    else:
        flash('Invalid status selected.', 'error')
    
    return redirect(url_for('admin.view_loan', loan_id=loan_id))

@admin_bp.route('/loans/setup', methods=['POST'])
@login_required
@admin_required
def setup_loan_system():
    """Initialize loan types and policies"""
    try:
        # Create default loan types
        LoanType.create_default_types()
        
        # Create default policies
        LoanPolicy.create_default_policies()
        
        db.session.commit()
        flash('Loan system setup completed successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error setting up loan system: {str(e)}', 'error')
    
    return redirect(url_for('admin.loans'))
    
    return redirect(url_for('admin.loans'))

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Analytics dashboard"""
    # Revenue and financial metrics
    # Service requests by status
    request_status_counts = db.session.query(
        ServiceRequest.status,
        func.count(ServiceRequest.id)
    ).group_by(ServiceRequest.status).all()
    
    # Users by month (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_users = db.session.query(
        func.date_trunc('month', User.created_at).label('month'),
        func.count(User.id)
    ).filter(
        User.created_at >= six_months_ago,
        User.role == 'customer'
    ).group_by('month').order_by('month').all()
    
    # Service popularity
    service_popularity = db.session.query(
        Service.name,
        func.count(ServiceRequest.id)
    ).join(ServiceRequest).group_by(Service.name).order_by(func.count(ServiceRequest.id).desc()).all()
    
    analytics_data = {
        'request_status_counts': dict(request_status_counts),
        'monthly_users': monthly_users,
        'service_popularity': service_popularity
    }
    
    return render_template('admin/analytics.html', analytics_data=analytics_data)

@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """System settings"""
    return render_template('admin/settings.html')

# ===== COMPREHENSIVE MONITORING AND ACTIVITY TRACKING =====

@admin_bp.route('/monitoring')
@login_required
@admin_required
def monitoring():
    """Comprehensive admin monitoring dashboard"""
    # Get date range (default to last 7 days)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = datetime.now() - timedelta(days=7)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    if not end_date:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Get comprehensive activity data
    all_activities = ActivityLogger.get_admin_monitoring_data(
        start_date=start_date,
        end_date=end_date
    )
    
    # Summary statistics
    total_activities = len(all_activities)
    unique_users = len(set(activity.user_id for activity in all_activities if activity.user_id))
    failed_activities = len([a for a in all_activities if not a.success])
    
    # Activity breakdown by type
    activity_types = {}
    category_breakdown = {}
    hourly_distribution = {}
    
    for activity in all_activities:
        # By type
        activity_types[activity.activity_type] = activity_types.get(activity.activity_type, 0) + 1
        
        # By category
        category_breakdown[activity.category] = category_breakdown.get(activity.category, 0) + 1
        
        # By hour
        hour = activity.timestamp.hour
        hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
    
    # Recent registrations
    recent_registrations = UserRegistration.query.filter(
        UserRegistration.registration_date >= start_date
    ).order_by(UserRegistration.registration_date.desc()).limit(10).all()
    
    # Recent staff onboardings
    recent_onboardings = StaffOnboarding.query.filter(
        StaffOnboarding.onboarding_date >= start_date
    ).order_by(StaffOnboarding.onboarding_date.desc()).limit(10).all()
    
    # Active sessions
    active_sessions = LoginSession.query.filter_by(is_active=True).count()
    
    return render_template('admin/monitoring.html',
                         activities=all_activities[:100],  # Limit to 100 most recent
                         total_activities=total_activities,
                         unique_users=unique_users,
                         failed_activities=failed_activities,
                         activity_types=activity_types,
                         category_breakdown=category_breakdown,
                         hourly_distribution=hourly_distribution,
                         recent_registrations=recent_registrations,
                         recent_onboardings=recent_onboardings,
                         active_sessions=active_sessions,
                         start_date=start_date.strftime('%Y-%m-%d'),
                         end_date=end_date.strftime('%Y-%m-%d'))

@admin_bp.route('/monitoring/user/<int:user_id>')
@login_required
@admin_required
def monitor_user_detailed(user_id):
    """Detailed user monitoring for admin"""
    user = User.query.get_or_404(user_id)
    
    # Get comprehensive user data
    activities = ActivityLogger.get_user_activities(user_id=user_id, limit=200)
    
    # User registration details
    registration = UserRegistration.query.filter_by(user_id=user_id).first()
    
    # Staff onboarding details (if applicable)
    onboarding = StaffOnboarding.query.filter_by(staff_user_id=user_id).first()
    
    # Login sessions
    login_sessions = LoginSession.query.filter_by(user_id=user_id).order_by(
        LoginSession.login_time.desc()
    ).limit(20).all()
    
    # Activity statistics
    activity_stats = {}
    for activity in activities:
        date_key = activity.timestamp.date()
        if date_key not in activity_stats:
            activity_stats[date_key] = {'total': 0, 'failed': 0}
        activity_stats[date_key]['total'] += 1
        if not activity.success:
            activity_stats[date_key]['failed'] += 1
    
    return render_template('admin/user_monitoring_detailed.html',
                         user=user,
                         activities=activities,
                         registration=registration,
                         onboarding=onboarding,
                         login_sessions=login_sessions,
                         activity_stats=activity_stats,
                         current_time=datetime.now())

@admin_bp.route('/monitoring/staff')
@login_required
@admin_required
def monitor_staff():
    """Monitor all staff activities"""
    # Get all staff members
    staff_members = User.query.filter_by(role='staff').all()
    
    # Get staff activities from last 7 days
    start_date = datetime.now() - timedelta(days=7)
    
    staff_activities = {}
    for staff in staff_members:
        activities = ActivityLog.query.filter(
            ActivityLog.performed_by_id == staff.id,
            ActivityLog.timestamp >= start_date
        ).order_by(ActivityLog.timestamp.desc()).limit(50).all()
        
        staff_activities[staff.id] = {
            'staff': staff,
            'activities': activities,
            'total_count': len(activities),
            'onboarding_record': StaffOnboarding.query.filter_by(staff_user_id=staff.id).first()
        }
    
    return render_template('admin/staff_monitoring.html',
                         staff_activities=staff_activities)

@admin_bp.route('/monitoring/statistics')
@login_required
@admin_required
def usage_statistics():
    """Usage statistics dashboard"""
    # Get date range
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now().date() - timedelta(days=days)
    
    # Get usage statistics
    daily_stats = UsageStatistics.query.filter(
        UsageStatistics.date >= start_date,
        UsageStatistics.hour.is_(None)  # Daily stats only
    ).order_by(UsageStatistics.date).all()
    
    # Calculate totals and trends
    total_stats = {
        'total_users': sum(stat.active_users or 0 for stat in daily_stats),
        'total_registrations': sum(stat.new_registrations or 0 for stat in daily_stats),
        'total_logins': sum(stat.total_logins or 0 for stat in daily_stats),
        'total_activities': sum(stat.total_activities or 0 for stat in daily_stats),
        'avg_response_time': sum(stat.avg_response_time_ms or 0 for stat in daily_stats) / len(daily_stats) if daily_stats else 0
    }
    
    # Registration methods breakdown
    registration_methods = db.session.query(
        UserRegistration.registration_method,
        func.count(UserRegistration.id)
    ).group_by(UserRegistration.registration_method).all()
    
    # Most active users
    most_active_users = db.session.query(
        User.id, User.first_name, User.last_name, User.email, User.role,
        func.count(ActivityLog.id).label('activity_count')
    ).join(ActivityLog, User.id == ActivityLog.user_id).filter(
        ActivityLog.timestamp >= datetime.now() - timedelta(days=days)
    ).group_by(User.id, User.first_name, User.last_name, User.email, User.role).order_by(
        func.count(ActivityLog.id).desc()
    ).limit(10).all()
    
    return render_template('admin/usage_statistics.html',
                         daily_stats=daily_stats,
                         total_stats=total_stats,
                         registration_methods=dict(registration_methods),
                         most_active_users=most_active_users,
                         days=days)

@admin_bp.route('/api/monitoring/activities')
@login_required
@admin_required
def api_admin_activities():
    """API endpoint for admin activity monitoring"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    activity_type = request.args.get('type')
    category = request.args.get('category')
    user_id = request.args.get('user_id', type=int)
    success_only = request.args.get('success_only', type=bool)
    
    # Build query
    query = ActivityLog.query
    
    if activity_type:
        query = query.filter_by(activity_type=activity_type)
    
    if category:
        query = query.filter_by(category=category)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if success_only is not None:
        query = query.filter_by(success=success_only)
    
    # Date filtering
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(ActivityLog.timestamp >= start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(ActivityLog.timestamp <= end_date)
    
    # Paginate results
    activities = query.order_by(ActivityLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'activities': [activity.to_dict() for activity in activities.items],
        'total': activities.total,
        'pages': activities.pages,
        'current_page': page,
        'has_next': activities.has_next,
        'has_prev': activities.has_prev
    })

@admin_bp.route('/api/monitoring/export')
@login_required
@admin_required
def export_activity_data():
    """Export activity data for admin analysis"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    format_type = request.args.get('format', 'json')  # json, csv
    
    query = ActivityLog.query
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(ActivityLog.timestamp >= start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(ActivityLog.timestamp <= end_date)
    
    activities = query.order_by(ActivityLog.timestamp.desc()).limit(10000).all()
    
    if format_type == 'csv':
        # Return CSV format
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'ID', 'User ID', 'Activity Type', 'Action', 'Category', 
            'Success', 'Timestamp', 'IP Address', 'Description'
        ])
        
        # Data
        for activity in activities:
            writer.writerow([
                activity.id, activity.user_id, activity.activity_type,
                activity.action, activity.category, activity.success,
                activity.timestamp, activity.ip_address, activity.description
            ])
        
        output.seek(0)
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=activity_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        }
    
    else:
        # Return JSON format
        return jsonify({
            'activities': [activity.to_dict() for activity in activities],
            'exported_at': datetime.utcnow().isoformat(),
            'total_records': len(activities)
        })

# ============================================
# INVENTORY MANAGEMENT ROUTES
# ============================================

@admin_bp.route('/inventory')
@login_required
@admin_required
def inventory_dashboard():
    """Inventory management dashboard"""
    try:
        # Get inventory statistics
        total_locations = InventoryLocation.query.filter_by(is_active=True).count()
        total_items = InventoryItem.query.filter_by(status='active').count()
        low_stock_count = InventoryItem.query.filter(
            InventoryItem.status == 'active',
            InventoryItem.current_stock <= InventoryItem.reorder_point
        ).count()
        out_of_stock_count = InventoryItem.query.filter(
            InventoryItem.status == 'active',
            InventoryItem.current_stock <= 0
        ).count()
        
        # Get recent low stock alerts
        recent_alerts = LowStockAlert.query.filter_by(status='active')\
            .order_by(LowStockAlert.created_at.desc()).limit(10).all()
        
        # Get recent stock movements
        recent_movements = StockMovement.query\
            .order_by(StockMovement.movement_date.desc()).limit(10).all()
        
        # Get locations for dropdown
        locations = InventoryLocation.query.filter_by(is_active=True).all()
        
        return render_template('admin/inventory/dashboard.html',
                             total_locations=total_locations,
                             total_items=total_items,
                             low_stock_count=low_stock_count,
                             out_of_stock_count=out_of_stock_count,
                             recent_alerts=recent_alerts,
                             recent_movements=recent_movements,
                             locations=locations)
    except Exception as e:
        flash(f'Error loading inventory dashboard: {str(e)}', 'error')
        return render_template('admin/inventory/dashboard.html',
                             total_locations=0,
                             total_items=0,
                             low_stock_count=0,
                             out_of_stock_count=0,
                             recent_alerts=[],
                             recent_movements=[],
                             locations=[])

@admin_bp.route('/inventory/upload-stock', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_stock():
    """Upload inventory stock via CSV/Excel"""
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                flash('No file selected', 'error')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.url)
            
            if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
                flash('Please upload a CSV or Excel file', 'error')
                return redirect(request.url)
            
            # Read the file
            if file.filename.lower().endswith('.csv'):
                # Read CSV
                df = pd.read_csv(file)
            else:
                # Read Excel
                df = pd.read_excel(file)
            
            # Validate required columns
            required_columns = ['name', 'sku', 'category', 'unit_cost', 'selling_price', 'current_stock', 'reorder_point']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                flash(f'Missing required columns: {", ".join(missing_columns)}', 'error')
                return redirect(request.url)
            
            success_count = 0
            error_count = 0
            errors = []
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    # Check if item already exists
                    existing_item = InventoryItem.query.filter_by(sku=row['sku']).first()
                    if existing_item:
                        # Update existing item
                        existing_item.name = row['name']
                        existing_item.category = row['category']
                        existing_item.unit_cost = float(row['unit_cost'])
                        existing_item.selling_price = float(row['selling_price'])
                        existing_item.current_stock += int(row['current_stock'])  # Add to existing stock
                        existing_item.reorder_point = int(row['reorder_point'])
                        existing_item.updated_at = datetime.utcnow()
                        
                        # Create stock movement record
                        movement = StockMovement(
                            item_id=existing_item.id,
                            movement_type='adjustment',
                            quantity=int(row['current_stock']),
                            unit_cost=float(row['unit_cost']),
                            reference_number=f'UPLOAD-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                            reason='Stock upload - file import',
                            performed_by_id=current_user.id
                        )
                        db.session.add(movement)
                    else:
                        # Create new item
                        new_item = InventoryItem(
                            name=row['name'],
                            sku=row['sku'],
                            category=row['category'],
                            description=row.get('description', ''),
                            unit_cost=float(row['unit_cost']),
                            selling_price=float(row['selling_price']),
                            current_stock=int(row['current_stock']),
                            reorder_point=int(row['reorder_point']),
                            supplier=row.get('supplier', ''),
                            status='active',
                            created_by_id=current_user.id
                        )
                        db.session.add(new_item)
                        db.session.flush()  # Get the ID
                        
                        # Create initial stock movement
                        movement = StockMovement(
                            item_id=new_item.id,
                            movement_type='initial_stock',
                            quantity=int(row['current_stock']),
                            unit_cost=float(row['unit_cost']),
                            reference_number=f'UPLOAD-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                            reason='Initial stock - file import',
                            performed_by_id=current_user.id
                        )
                        db.session.add(movement)
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f'Row {index + 2}: {str(e)}')
                    continue
            
            # Commit all changes
            db.session.commit()
            
            # Log the activity
            ActivityLogger.log_activity(
                user_id=current_user.id,
                action='bulk_stock_upload',
                description=f'Uploaded stock from file: {file.filename} - {success_count} successful, {error_count} errors',
                metadata={'filename': file.filename, 'success_count': success_count, 'error_count': error_count}
            )
            
            flash(f'Stock upload completed! {success_count} items processed successfully.', 'success')
            if error_count > 0:
                flash(f'{error_count} items had errors. Check the format and try again.', 'warning')
                for error in errors[:5]:  # Show first 5 errors
                    flash(error, 'error')
            
            return redirect(url_for('admin.inventory_items'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing file: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('admin/inventory/upload_stock.html')

@admin_bp.route('/inventory/add-item', methods=['GET', 'POST'])
@login_required
@admin_required
def add_inventory_item():
    """Add individual inventory item manually"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            sku = request.form.get('sku')
            category = request.form.get('category')
            description = request.form.get('description', '')
            unit_cost = float(request.form.get('unit_cost', 0))
            selling_price = float(request.form.get('selling_price', 0))
            current_stock = int(request.form.get('current_stock', 0))
            reorder_point = int(request.form.get('reorder_point', 0))
            supplier = request.form.get('supplier', '')
            location_id = request.form.get('location_id', type=int)
            
            # Check if SKU already exists
            existing_item = InventoryItem.query.filter_by(sku=sku).first()
            if existing_item:
                flash('An item with this SKU already exists', 'error')
                return redirect(request.url)
            
            # Create new inventory item
            new_item = InventoryItem(
                name=name,
                sku=sku,
                category=category,
                description=description,
                unit_cost=unit_cost,
                selling_price=selling_price,
                current_stock=current_stock,
                reorder_point=reorder_point,
                supplier=supplier,
                location_id=location_id,
                status='active',
                created_by_id=current_user.id
            )
            
            db.session.add(new_item)
            db.session.flush()  # Get the ID
            
            # Create initial stock movement
            if current_stock > 0:
                movement = StockMovement(
                    item_id=new_item.id,
                    movement_type='initial_stock',
                    quantity=current_stock,
                    unit_cost=unit_cost,
                    reference_number=f'MANUAL-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                    reason='Initial stock - manual entry',
                    performed_by_id=current_user.id
                )
                db.session.add(movement)
            
            db.session.commit()
            
            # Log the activity
            ActivityLogger.log_activity(
                user_id=current_user.id,
                action='add_inventory_item',
                description=f'Added new inventory item: {name} (SKU: {sku})',
                metadata={'item_id': new_item.id, 'sku': sku, 'initial_stock': current_stock}
            )
            
            flash(f'Inventory item "{name}" added successfully!', 'success')
            return redirect(url_for('admin.inventory_items'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding inventory item: {str(e)}', 'error')
            return redirect(request.url)
    
    # Get locations for dropdown
    locations = InventoryLocation.query.filter_by(is_active=True).all()
    return render_template('admin/inventory/add_item.html', locations=locations)

@admin_bp.route('/inventory/items')
@login_required
@admin_required
def inventory_items():
    """View all inventory items"""
    location_id = request.args.get('location_id', type=int)
    stock_status = request.args.get('stock_status', 'all')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = InventoryItem.query.filter_by(status='active')
    
    # Filter by location
    if location_id:
        query = query.filter_by(location_id=location_id)
    
    # Filter by stock status
    if stock_status == 'low_stock':
        query = query.filter(InventoryItem.current_stock <= InventoryItem.reorder_point)
    elif stock_status == 'out_of_stock':
        query = query.filter(InventoryItem.current_stock <= 0)
    elif stock_status == 'in_stock':
        query = query.filter(InventoryItem.current_stock > InventoryItem.reorder_point)
    
    # Search functionality
    if search:
        # Join with product tables for search
        product_query = query.join(Product, InventoryItem.product_id == Product.id, isouter=True)\
            .filter(Product.name.contains(search))
        jewelry_query = query.join(JewelryItem, InventoryItem.jewelry_item_id == JewelryItem.id, isouter=True)\
            .filter(JewelryItem.name.contains(search))
        # Combine queries
        query = product_query.union(jewelry_query)
    
    # Pagination
    items = query.order_by(InventoryItem.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    # Get locations for filter dropdown
    locations = InventoryLocation.query.filter_by(is_active=True).all()
    
    return render_template('admin/inventory/items.html',
                         items=items,
                         locations=locations,
                         current_location=location_id,
                         current_status=stock_status,
                         search=search)

@admin_bp.route('/inventory/out-of-stock')
@login_required
@admin_required
def out_of_stock_items():
    """View all out of stock items"""
    try:
        location_id = request.args.get('location_id', type=int)
        search = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        
        query = InventoryItem.query.filter(
            InventoryItem.status == 'active',
            InventoryItem.current_stock <= 0
        )
        
        # Filter by location
        if location_id:
            query = query.filter_by(location_id=location_id)
        
        # Search functionality
        if search:
            # Join with product tables for search
            product_query = query.join(Product, InventoryItem.product_id == Product.id, isouter=True)\
                .filter(Product.name.contains(search))
            jewelry_query = query.join(JewelryItem, InventoryItem.jewelry_item_id == JewelryItem.id, isouter=True)\
                .filter(JewelryItem.name.contains(search))
            # Combine queries
            query = product_query.union(jewelry_query)
        
        # Pagination
        items = query.order_by(InventoryItem.created_at.desc())\
            .paginate(page=page, per_page=20, error_out=False)
        
        # Get locations for filter dropdown
        locations = InventoryLocation.query.filter_by(is_active=True).all()
        
        return render_template('admin/inventory/out_of_stock.html',
                             items=items,
                             locations=locations,
                             current_location=location_id,
                             search=search)
    except Exception as e:
        flash(f'Error loading out of stock items: {str(e)}', 'error')
        return render_template('admin/inventory/out_of_stock.html',
                             items=None,
                             locations=[],
                             current_location=None,
                             search='')

@admin_bp.route('/inventory/items/<int:item_id>')
@login_required
@admin_required
def inventory_item_detail(item_id):
    """View inventory item details"""
    item = InventoryItem.query.get_or_404(item_id)
    
    # Get recent stock movements for this item
    movements = StockMovement.query.filter_by(inventory_item_id=item_id)\
        .order_by(StockMovement.movement_date.desc()).limit(20).all()
    
    # Get alerts for this item
    alerts = LowStockAlert.query.filter_by(inventory_item_id=item_id)\
        .order_by(LowStockAlert.created_at.desc()).limit(10).all()
    
    return render_template('admin/inventory/item_detail.html',
                         item=item,
                         movements=movements,
                         alerts=alerts)

@admin_bp.route('/inventory/items/<int:item_id>/adjust-stock', methods=['POST'])
@login_required
@admin_required
def adjust_stock(item_id):
    """Adjust inventory stock levels"""
    item = InventoryItem.query.get_or_404(item_id)
    
    try:
        adjustment_type = request.form.get('adjustment_type')  # increase, decrease
        quantity = int(request.form.get('quantity', 0))
        notes = request.form.get('notes', '')
        
        if quantity <= 0:
            flash('Quantity must be greater than 0', 'error')
            return redirect(url_for('admin.inventory_item_detail', item_id=item_id))
        
        # Record stock before adjustment
        stock_before = item.current_stock
        
        # Apply adjustment
        if adjustment_type == 'increase':
            item.current_stock += quantity
            movement_type = 'in'
        elif adjustment_type == 'decrease':
            item.current_stock = max(0, item.current_stock - quantity)
            movement_type = 'out'
        else:
            flash('Invalid adjustment type', 'error')
            return redirect(url_for('admin.inventory_item_detail', item_id=item_id))
        
        # Update available stock
        item.update_available_stock()
        
        # Create stock movement record
        movement = StockMovement(
            inventory_item_id=item_id,
            location_id=item.location_id,
            user_id=current_user.id,
            movement_type='adjustment',
            quantity=quantity if adjustment_type == 'increase' else -quantity,
            reference_type='manual_adjustment',
            notes=notes,
            stock_before=stock_before,
            stock_after=item.current_stock
        )
        
        db.session.add(movement)
        db.session.commit()
        
        # Check if low stock alert needs to be created or resolved
        if item.is_low_stock:
            # Create alert if none exists
            existing_alert = LowStockAlert.query.filter_by(
                inventory_item_id=item_id,
                status='active'
            ).first()
            
            if not existing_alert:
                alert = LowStockAlert(
                    inventory_item_id=item_id,
                    alert_level='critical' if item.current_stock < 2 else 'low',
                    current_stock=item.current_stock,
                    reorder_point=item.reorder_point
                )
                db.session.add(alert)
                db.session.commit()
        else:
            # Resolve any active alerts
            LowStockAlert.query.filter_by(
                inventory_item_id=item_id,
                status='active'
            ).update({
                'status': 'resolved',
                'resolved_at': datetime.utcnow()
            })
            db.session.commit()
        
        flash(f'Stock adjusted successfully. New stock level: {item.current_stock}', 'success')
        
    except ValueError:
        flash('Invalid quantity entered', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adjusting stock: {str(e)}', 'error')
    
    return redirect(url_for('admin.inventory_item_detail', item_id=item_id))

@admin_bp.route('/inventory/locations')
@login_required
@admin_required
def inventory_locations():
    """Manage inventory locations"""
    locations = InventoryLocation.query.filter_by(is_active=True).all()
    
    # Get item counts per location
    for location in locations:
        location.item_count = InventoryItem.query.filter_by(
            location_id=location.id,
            status='active'
        ).count()
        location.low_stock_count = InventoryItem.query.filter(
            InventoryItem.location_id == location.id,
            InventoryItem.status == 'active',
            InventoryItem.current_stock <= InventoryItem.reorder_point
        ).count()
    
    return render_template('admin/inventory/locations.html', locations=locations)

@admin_bp.route('/inventory/locations/<int:location_id>')
@login_required
@admin_required
def location_detail(location_id):
    """View location details and assigned staff"""
    location = InventoryLocation.query.get_or_404(location_id)
    
    # Get assigned staff
    staff_assignments = StaffLocationAssignment.query.filter_by(
        location_id=location_id,
        is_active=True
    ).all()
    
    # Get items in this location
    items = InventoryItem.query.filter_by(
        location_id=location_id,
        status='active'
    ).limit(10).all()
    
    # Get low stock items in this location
    low_stock_items = InventoryItem.query.filter(
        InventoryItem.location_id == location_id,
        InventoryItem.status == 'active',
        InventoryItem.current_stock <= InventoryItem.reorder_point
    ).all()
    
    return render_template('admin/inventory/location_detail.html',
                         location=location,
                         staff_assignments=staff_assignments,
                         items=items,
                         low_stock_items=low_stock_items)

@admin_bp.route('/inventory/alerts')
@login_required
@admin_required
def low_stock_alerts():
    """View and manage low stock alerts"""
    status_filter = request.args.get('status', 'active')
    location_id = request.args.get('location_id', type=int)
    
    query = LowStockAlert.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if location_id:
        query = query.join(InventoryItem).filter(InventoryItem.location_id == location_id)
    
    alerts = query.order_by(LowStockAlert.created_at.desc()).all()
    locations = InventoryLocation.query.filter_by(is_active=True).all()
    
    return render_template('admin/inventory/alerts.html',
                         alerts=alerts,
                         locations=locations,
                         current_status=status_filter,
                         current_location=location_id)

@admin_bp.route('/inventory/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@login_required
@admin_required
def acknowledge_alert(alert_id):
    """Acknowledge a low stock alert"""
    alert = LowStockAlert.query.get_or_404(alert_id)
    
    if alert.status == 'active':
        alert.status = 'acknowledged'
        alert.acknowledged_by_id = current_user.id
        alert.acknowledged_at = datetime.utcnow()
        
        db.session.commit()
        flash('Alert acknowledged successfully', 'success')
    else:
        flash('Alert has already been processed', 'info')
    
    return redirect(url_for('admin.low_stock_alerts'))

@admin_bp.route('/inventory/staff-assignments')
@login_required
@admin_required
def staff_assignments():
    """Manage staff location assignments"""
    assignments = StaffLocationAssignment.query.filter_by(is_active=True).all()
    staff_users = User.query.filter_by(role='staff', is_active=True).all()
    locations = InventoryLocation.query.filter_by(is_active=True).all()
    
    return render_template('admin/inventory/staff_assignments.html',
                         assignments=assignments,
                         staff_users=staff_users,
                         locations=locations)

@admin_bp.route('/inventory/staff-assignments/create', methods=['POST'])
@login_required
@admin_required
def create_staff_assignment():
    """Create new staff location assignment"""
    try:
        staff_id = request.form.get('staff_id', type=int)
        location_id = request.form.get('location_id', type=int)
        role = request.form.get('role', 'clerk')
        permissions = request.form.getlist('permissions')
        
        # Check if assignment already exists
        existing = StaffLocationAssignment.query.filter_by(
            staff_id=staff_id,
            location_id=location_id,
            is_active=True
        ).first()
        
        if existing:
            flash('Staff member is already assigned to this location', 'error')
            return redirect(url_for('admin.staff_assignments'))
        
        assignment = StaffLocationAssignment(
            staff_id=staff_id,
            location_id=location_id,
            role=role,
            permissions=permissions
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        flash('Staff assignment created successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating assignment: {str(e)}', 'error')
    
    return redirect(url_for('admin.staff_assignments'))

@admin_bp.route('/inventory/reports')
@login_required
@admin_required
def inventory_reports():
    """Inventory reports and analytics"""
    # Get summary statistics
    total_items = InventoryItem.query.filter_by(status='active').count()
    total_value = db.session.query(
        func.sum(InventoryItem.current_stock * InventoryItem.unit_cost)
    ).scalar() or 0
    
    low_stock_items = InventoryItem.query.filter(
        InventoryItem.status == 'active',
        InventoryItem.current_stock <= InventoryItem.reorder_point
    ).count()
    
    # Get stock movements for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_movements = StockMovement.query.filter(
        StockMovement.movement_date >= thirty_days_ago
    ).count()
    
    # Get top locations by item count
    location_stats = db.session.query(
        InventoryLocation.name,
        func.count(InventoryItem.id).label('item_count')
    ).join(InventoryItem).filter(
        InventoryLocation.is_active == True,
        InventoryItem.status == 'active'
    ).group_by(InventoryLocation.id, InventoryLocation.name).all()
    
    return render_template('admin/inventory/reports.html',
                         total_items=total_items,
                         total_value=total_value,
                         low_stock_items=low_stock_items,
                         recent_movements=recent_movements,
                         location_stats=location_stats)

# ============================================
# SERVICE MANAGEMENT ROUTES
# ============================================

@admin_bp.route('/services')
@login_required
@admin_required
def all_services():
    """View and manage all services"""
    try:
        category_filter = request.args.get('category', 'all')
        status_filter = request.args.get('status', 'all')
        search = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        
        query = Service.query if Service else []
        
        if Service:
            # Filter by category
            if category_filter != 'all':
                query = query.filter_by(category=category_filter)
            
            # Filter by status
            if status_filter == 'active':
                query = query.filter_by(is_active=True)
            elif status_filter == 'inactive':
                query = query.filter_by(is_active=False)
            elif status_filter == 'featured':
                query = query.filter_by(is_featured=True)
            
            # Search functionality
            if search:
                query = query.filter(
                    db.or_(
                        Service.name.contains(search),
                        Service.description.contains(search),
                        Service.short_description.contains(search)
                    )
                )
            
            # Pagination
            services = query.order_by(Service.created_at.desc())\
                .paginate(page=page, per_page=20, error_out=False)
            
            # Get categories for filter
            categories = db.session.query(Service.category.distinct()).all()
            categories = [cat[0] for cat in categories if cat[0]]
        else:
            services = None
            categories = []
        
        return render_template('admin/services/all_services.html',
                             services=services,
                             categories=categories,
                             current_category=category_filter,
                             current_status=status_filter,
                             search=search)
    except Exception as e:
        flash(f'Error loading services: {str(e)}', 'error')
        return render_template('admin/services/all_services.html',
                             services=None,
                             categories=[],
                             current_category='all',
                             current_status='all',
                             search='')

@admin_bp.route('/services/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_service():
    """Create a new service"""
    if not Service:
        flash('Service model not available', 'error')
        return redirect(url_for('admin.all_services'))
    
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            short_description = request.form.get('short_description')
            category = request.form.get('category')
            price = request.form.get('price', type=float)
            currency = request.form.get('currency', 'NGN')
            duration = request.form.get('duration')
            requirements = request.form.get('requirements')
            is_featured = 'is_featured' in request.form
            is_active = 'is_active' in request.form
            
            # Create slug from name
            import re
            slug = re.sub(r'[^\w\s-]', '', name.lower())
            slug = re.sub(r'[-\s]+', '-', slug)
            
            # Check if slug exists
            existing_service = Service.query.filter_by(slug=slug).first()
            if existing_service:
                slug = f"{slug}-{datetime.now().strftime('%Y%m%d')}"
            
            service = Service(
                name=name,
                description=description,
                short_description=short_description,
                category=category,
                price=price or 0.00,
                currency=currency,
                duration=duration,
                requirements=requirements,
                is_featured=is_featured,
                is_active=is_active,
                slug=slug
            )
            
            db.session.add(service)
            db.session.commit()
            
            flash(f'Service "{name}" created successfully!', 'success')
            return redirect(url_for('admin.all_services'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating service: {str(e)}', 'error')
    
    return render_template('admin/services/create_service.html')

@admin_bp.route('/services/<int:service_id>')
@login_required
@admin_required
def service_detail(service_id):
    """View service details"""
    if not Service:
        flash('Service model not available', 'error')
        return redirect(url_for('admin.all_services'))
    
    service = Service.query.get_or_404(service_id)
    
    # Get service requests if available
    service_requests = []
    if ServiceRequest:
        service_requests = ServiceRequest.query.filter_by(related_service_id=service_id)\
            .order_by(ServiceRequest.created_at.desc()).limit(10).all()
    
    return render_template('admin/services/service_detail.html',
                         service=service,
                         service_requests=service_requests)

@admin_bp.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_service(service_id):
    """Edit a service"""
    if not Service:
        flash('Service model not available', 'error')
        return redirect(url_for('admin.all_services'))
    
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'POST':
        try:
            service.name = request.form.get('name')
            service.description = request.form.get('description')
            service.short_description = request.form.get('short_description')
            service.category = request.form.get('category')
            service.price = request.form.get('price', type=float) or 0.00
            service.currency = request.form.get('currency', 'NGN')
            service.duration = request.form.get('duration')
            service.requirements = request.form.get('requirements')
            service.is_featured = 'is_featured' in request.form
            service.is_active = 'is_active' in request.form
            service.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash(f'Service "{service.name}" updated successfully!', 'success')
            return redirect(url_for('admin.service_detail', service_id=service_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating service: {str(e)}', 'error')
    
    return render_template('admin/services/edit_service.html', service=service)

@admin_bp.route('/services/<int:service_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_service_status(service_id):
    """Toggle service active status"""
    if not Service:
        flash('Service model not available', 'error')
        return redirect(url_for('admin.all_services'))
    
    service = Service.query.get_or_404(service_id)
    service.is_active = not service.is_active
    service.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    status = 'activated' if service.is_active else 'deactivated'
    flash(f'Service "{service.name}" has been {status}', 'success')
    
    return redirect(url_for('admin.service_detail', service_id=service_id))

@admin_bp.route('/service-requests')
@login_required
@admin_required
def service_requests():
    """View and manage service requests"""
    try:
        status_filter = request.args.get('status', 'all')
        urgency_filter = request.args.get('urgency', 'all')
        search = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        
        query = ServiceRequest.query
        
        # Filter by status
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        # Filter by urgency (not priority)
        if urgency_filter != 'all':
            query = query.filter_by(urgency=urgency_filter)
        
        # Search functionality using correct field names
        if search:
            query = query.filter(
                db.or_(
                    ServiceRequest.subject.contains(search),
                    ServiceRequest.description.contains(search),
                    ServiceRequest.customer_name.contains(search),
                    ServiceRequest.customer_email.contains(search),
                    ServiceRequest.request_number.contains(search)
                )
            )
        
        # Pagination
        requests = query.order_by(ServiceRequest.created_at.desc())\
            .paginate(page=page, per_page=20, error_out=False)
        
        return render_template('admin/services/service_requests.html',
                             requests=requests,
                             current_status=status_filter,
                             current_urgency=urgency_filter,
                             search=search)
    except Exception as e:
        flash(f'Error loading service requests: {str(e)}', 'error')
        return render_template('admin/services/service_requests.html',
                             requests=None,
                             current_status='all',
                             current_urgency='all',
                             search='')

@admin_bp.route('/service-requests/<int:request_id>')
@login_required
@admin_required
def service_request_detail(request_id):
    """View service request details"""
    if not ServiceRequest:
        flash('ServiceRequest model not available', 'error')
        return redirect(url_for('admin.service_requests'))
    
    service_request = ServiceRequest.query.get_or_404(request_id)
    return render_template('admin/services/service_request_detail.html',
                         service_request=service_request)

@admin_bp.route('/service-requests/<int:request_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_service_request_status(request_id):
    """Update service request status"""
    if not ServiceRequest:
        flash('ServiceRequest model not available', 'error')
        return redirect(url_for('admin.service_requests'))
    
    service_request = ServiceRequest.query.get_or_404(request_id)
    new_status = request.form.get('status')
    admin_notes = request.form.get('admin_notes')
    
    service_request.status = new_status
    service_request.admin_notes = admin_notes
    service_request.updated_at = datetime.utcnow()
    
    if new_status in ['completed', 'resolved']:
        service_request.resolved_at = datetime.utcnow()
        service_request.resolved_by_id = current_user.id
    
    db.session.commit()
    flash(f'Service request status updated to {new_status}', 'success')
    
    return redirect(url_for('admin.service_request_detail', request_id=request_id))