"""
Staff Blueprint
Staff portal for task management, customer support, and service updates
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models.user import User
from models.chat import ChatMessage
from models.activity_tracking import ActivityLog, UsageStatistics
from models.inventory import InventoryLocation, InventoryItem, StockMovement, LowStockAlert, StaffLocationAssignment
from models.ecommerce import Product
from models.jewelry import JewelryItem
from database import db
from datetime import datetime, timedelta
from utils.decorators import staff_required
from utils.activity_logger import ActivityLogger
from sqlalchemy import func

# Try to import Service and ServiceRequest models
try:
    from models.service import Service
except ImportError:
    Service = None

try:
    from models.service_request import ServiceRequest  
except ImportError:
    ServiceRequest = None

# Try to import loan models
try:
    from models.enhanced_loan import EnhancedLoanApplication, LoanType
except ImportError:
    EnhancedLoanApplication = None
    LoanType = None

# Create blueprint
staff_bp = Blueprint('staff', __name__, template_folder='templates')

@staff_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
@staff_required
def change_password():
    """Force password change for first-time staff login"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'error')
            return render_template('staff/change_password.html')
        
        # Validate new password
        if not new_password or len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'error')
            return render_template('staff/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('staff/change_password.html')
        
        if new_password == current_password:
            flash('New password must be different from current password.', 'error')
            return render_template('staff/change_password.html')
        
        # Update password
        current_user.set_password(new_password)
        current_user.password_change_required = False
        current_user.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Password changed successfully! Welcome to GM Services.', 'success')
            return redirect(url_for('staff.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating password. Please try again.', 'error')
            return render_template('staff/change_password.html')
    
    return render_template('staff/change_password.html')

@staff_bp.route('/dashboard')
@login_required
@staff_required
def dashboard():
    """Staff dashboard"""
    if not ServiceRequest:
        # If ServiceRequest model is not available, show basic dashboard
        return render_template('staff/dashboard.html',
                             assigned_requests=[],
                             pending_requests=0,
                             today_tasks=0,
                             completed_this_month=0,
                             user_activities=[])
    
    # Get assigned service requests
    assigned_requests = ServiceRequest.query.filter_by(
        assigned_to_id=current_user.id
    ).order_by(ServiceRequest.created_at.desc()).limit(10).all()
    
    # Get pending requests that need assignment
    pending_requests = ServiceRequest.query.filter_by(
        status='pending', assigned_to_id=None
    ).count()
    
    # Get today's tasks (requests with follow-up due today)
    today = datetime.utcnow().date()
    today_tasks = ServiceRequest.query.filter(
        ServiceRequest.assigned_to_id == current_user.id,
        ServiceRequest.follow_up_date == today
    ).count()
    
    # Get completed tasks this month
    from calendar import monthrange
    today = datetime.utcnow().date()
    first_day_of_month = today.replace(day=1)
    completed_this_month = ServiceRequest.query.filter(
        ServiceRequest.assigned_to_id == current_user.id,
        ServiceRequest.status == 'completed',
        ServiceRequest.updated_at >= datetime.combine(first_day_of_month, datetime.min.time())
    ).count()
    
    # Get loan statistics if available
    loan_stats = {}
    if EnhancedLoanApplication:
        loan_stats = {
            'assigned_loans_count': EnhancedLoanApplication.query.filter_by(
                assigned_staff_id=current_user.id, status='assigned'
            ).count(),
            'under_review_loans_count': EnhancedLoanApplication.query.filter_by(
                assigned_staff_id=current_user.id, status='under_review'
            ).count(),
            'approved_loans_count': EnhancedLoanApplication.query.filter_by(
                assigned_staff_id=current_user.id, status='approved'
            ).count()
        }

    return render_template('staff/dashboard.html', 
                         assigned_requests=assigned_requests,
                         pending_requests=pending_requests,
                         today_tasks=today_tasks,
                         completed_this_month=completed_this_month,
                         **loan_stats)

@staff_bp.route('/tasks')
@login_required
@staff_required
def tasks():
    """All assigned tasks"""
    status_filter = request.args.get('status', 'all')
    
    query = ServiceRequest.query.filter_by(assigned_to_id=current_user.id)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    tasks = query.order_by(ServiceRequest.created_at.desc()).all()
    
    return render_template('staff/tasks.html', tasks=tasks, status_filter=status_filter)

@staff_bp.route('/tasks/<int:task_id>')
@login_required
@staff_required
def task_detail(task_id):
    """Task detail page"""
    task = ServiceRequest.query.get_or_404(task_id)
    
    # Check if staff is assigned to this task or is admin
    if current_user.role != 'admin' and task.assigned_to_id != current_user.id:
        flash('Access denied. You are not assigned to this task.', 'error')
        return redirect(url_for('staff.tasks'))
    
    return render_template('staff/task_detail.html', task=task)

@staff_bp.route('/tasks/<int:task_id>/update', methods=['POST'])
@login_required
@staff_required
def update_task(task_id):
    """Update task status"""
    task = ServiceRequest.query.get_or_404(task_id)
    
    # Check if staff is assigned to this task or is admin
    if current_user.role != 'admin' and task.assigned_to_id != current_user.id:
        flash('Access denied. You are not assigned to this task.', 'error')
        return redirect(url_for('staff.tasks'))
    
    new_status = request.form.get('status')
    notes = request.form.get('notes')
    
    if new_status in ['pending', 'in_progress', 'completed', 'cancelled']:
        task.status = new_status
        if notes:
            task.staff_notes = notes
        task.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Task updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating task. Please try again.', 'error')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('staff.task_detail', task_id=task_id))

@staff_bp.route('/customers')
@login_required
@staff_required
def customers():
    """Customer list"""
    customers = User.query.filter_by(role='customer').order_by(User.created_at.desc()).all()
    return render_template('staff/customers.html', customers=customers)

@staff_bp.route('/customers/<int:customer_id>')
@login_required
@staff_required
def customer_detail(customer_id):
    """Customer detail page"""
    customer = User.query.get_or_404(customer_id)
    
    if customer.role != 'customer':
        flash('Invalid customer.', 'error')
        return redirect(url_for('staff.customers'))
    
    # Get customer's service requests
    service_requests = ServiceRequest.query.filter_by(
        user_id=customer_id
    ).order_by(ServiceRequest.created_at.desc()).all()
    
    return render_template('staff/customer_detail.html', 
                         customer=customer,
                         service_requests=service_requests)

@staff_bp.route('/chat')
@login_required
@staff_required
def chat():
    """Staff chat interface"""
    return render_template('staff/chat.html')

@staff_bp.route('/chat/rooms')
@login_required
@staff_required
def chat_rooms():
    """Active chat rooms"""
    # TODO: Implement chat room logic
    return jsonify({'rooms': []})

@staff_bp.route('/services')
@login_required
@staff_required
def services():
    """Services management"""
    services = Service.query.all()
    return render_template('staff/services.html', services=services)

@staff_bp.route('/reports')
@login_required
@staff_required
def reports():
    """Staff reports and analytics"""
    # Get staff performance data
    completed_tasks = ServiceRequest.query.filter_by(
        assigned_to_id=current_user.id,
        status='completed'
    ).count()
    
    pending_tasks = ServiceRequest.query.filter_by(
        assigned_to_id=current_user.id,
        status='pending'
    ).count()
    
    in_progress_tasks = ServiceRequest.query.filter_by(
        assigned_to_id=current_user.id,
        status='in_progress'
    ).count()
    
    stats = {
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'total_tasks': completed_tasks + pending_tasks + in_progress_tasks
    }
    
    return render_template('staff/reports.html', stats=stats)

@staff_bp.route('/schedule')
@login_required
@staff_required
def schedule():
    """Staff schedule"""
    return render_template('staff/schedule.html')

@staff_bp.route('/profile')
@login_required
@staff_required
def profile():
    """Staff profile"""
    return render_template('staff/profile.html')

# ===== ACTIVITY MONITORING ROUTES =====

@staff_bp.route('/monitoring')
@login_required
@staff_required
def monitoring():
    """Staff monitoring dashboard"""
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
    
    # Get user activities that staff can monitor
    user_activities = ActivityLogger.get_staff_monitoring_data(
        staff_user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get summary statistics
    total_activities = len(user_activities)
    unique_users = len(set(activity.user_id for activity in user_activities if activity.user_id))
    
    # Activity breakdown by type
    activity_types = {}
    for activity in user_activities:
        activity_types[activity.activity_type] = activity_types.get(activity.activity_type, 0) + 1
    
    return render_template('staff/monitoring.html',
                         activities=user_activities[:50],  # Limit to 50 most recent
                         total_activities=total_activities,
                         unique_users=unique_users,
                         activity_types=activity_types,
                         start_date=start_date.strftime('%Y-%m-%d'),
                         end_date=end_date.strftime('%Y-%m-%d'))

@staff_bp.route('/monitoring/user/<int:user_id>')
@login_required
@staff_required
def monitor_user(user_id):
    """Monitor specific user activity"""
    user = User.query.get_or_404(user_id)
    
    # Check if staff can monitor this user (basic check)
    if user.role == 'admin' or (user.role == 'staff' and user.id != current_user.id):
        flash('You do not have permission to monitor this user.', 'error')
        return redirect(url_for('staff.monitoring'))
    
    # Get user activities
    activities = ActivityLogger.get_user_activities(
        user_id=user_id,
        limit=100
    )
    
    return render_template('staff/user_monitoring.html',
                         user=user,
                         activities=activities)

@staff_bp.route('/api/monitoring/activities')
@login_required
@staff_required
def api_monitoring_activities():
    """API endpoint for staff monitoring data"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    activity_type = request.args.get('type')
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Build query
    query = ActivityLog.query
    
    if activity_type:
        query = query.filter_by(activity_type=activity_type)
    
    if start_date:
        query = query.filter(ActivityLog.timestamp >= start_date)
    
    if end_date:
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

# Loan Review Routes
@staff_bp.route('/loan_reviews')
@login_required
@staff_required
def loan_reviews():
    """Display loan applications assigned to staff for review"""
    if not EnhancedLoanApplication:
        flash('Loan management system not available.', 'error')
        return redirect(url_for('staff.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    filter_status = request.args.get('status', 'assigned')
    
    # Base query for applications
    query = EnhancedLoanApplication.query
    
    if filter_status == 'assigned':
        # Show applications assigned to current staff
        query = query.filter_by(assigned_staff_id=current_user.id, status='assigned')
    elif filter_status == 'under_review':
        # Show applications under review by current staff
        query = query.filter_by(assigned_staff_id=current_user.id, status='under_review')
    elif filter_status == 'all':
        # Show all applications for current staff
        query = query.filter_by(assigned_staff_id=current_user.id)
    
    # Get paginated applications
    applications = query.order_by(EnhancedLoanApplication.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get counts for tabs
    assigned_count = EnhancedLoanApplication.query.filter_by(
        assigned_staff_id=current_user.id, status='assigned'
    ).count()
    
    under_review_count = EnhancedLoanApplication.query.filter_by(
        assigned_staff_id=current_user.id, status='under_review'
    ).count()
    
    total_count = EnhancedLoanApplication.query.filter_by(
        assigned_staff_id=current_user.id
    ).count()
    
    return render_template('staff/loan_reviews.html',
                         applications=applications.items,
                         pagination=applications,
                         filter_status=filter_status,
                         assigned_count=assigned_count,
                         under_review_count=under_review_count,
                         total_count=total_count,
                         assigned_applications=applications.items)

@staff_bp.route('/loan_reviews/<int:application_id>')
@login_required
@staff_required
def loan_review_detail(application_id):
    """Display detailed view of a loan application for review"""
    if not EnhancedLoanApplication:
        flash('Loan management system not available.', 'error')
        return redirect(url_for('staff.dashboard'))
    
    application = EnhancedLoanApplication.query.get_or_404(application_id)
    
    # Check if staff has access to this application
    if application.assigned_staff_id != current_user.id:
        flash('You do not have access to this loan application.', 'error')
        return redirect(url_for('staff.loan_reviews'))
    
    # Get customer's previous loans count
    previous_loans_count = EnhancedLoanApplication.query.filter_by(
        user_id=application.user_id,
        status='approved'
    ).filter(EnhancedLoanApplication.id != application.id).count()
    
    return render_template('staff/loan_review_detail.html',
                         application=application,
                         previous_loans_count=previous_loans_count)

@staff_bp.route('/loan_reviews/<int:application_id>/start_review', methods=['POST'])
@login_required
@staff_required
def start_loan_review(application_id):
    """Start reviewing a loan application"""
    if not EnhancedLoanApplication:
        return jsonify({'success': False, 'message': 'Loan management system not available'})
    
    application = EnhancedLoanApplication.query.get_or_404(application_id)
    
    # Check if staff has access to this application
    if application.assigned_staff_id != current_user.id:
        return jsonify({'success': False, 'message': 'Access denied'})
    
    # Check if application is in correct status
    if application.status != 'assigned':
        return jsonify({'success': False, 'message': 'Application is not in assigned status'})
    
    try:
        # Update status to under_review
        application.status = 'under_review'
        application.review_started_at = datetime.utcnow()
        
        # Log activity
        ActivityLogger.log_activity(
            user_id=current_user.id,
            activity_type='loan_review_started',
            description=f'Started reviewing loan application {application.id}',
            metadata={'application_id': application.id}
        )
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Review started successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@staff_bp.route('/loan_reviews/<int:application_id>/notes', methods=['POST'])
@login_required
@staff_required
def save_review_notes(application_id):
    """Save review notes for a loan application"""
    if not EnhancedLoanApplication:
        return jsonify({'success': False, 'message': 'Loan management system not available'})
    
    application = EnhancedLoanApplication.query.get_or_404(application_id)
    
    # Check if staff has access to this application
    if application.assigned_staff_id != current_user.id:
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        data = request.get_json()
        notes = data.get('notes', '')
        
        application.review_notes = notes
        application.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Notes saved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@staff_bp.route('/loan_reviews/<int:application_id>/approve', methods=['POST'])
@login_required
@staff_required
def approve_loan(application_id):
    """Approve a loan application"""
    if not EnhancedLoanApplication:
        return jsonify({'success': False, 'message': 'Loan management system not available'})
    
    application = EnhancedLoanApplication.query.get_or_404(application_id)
    
    # Check if staff has access to this application
    if application.assigned_staff_id != current_user.id:
        return jsonify({'success': False, 'message': 'Access denied'})
    
    # Check if application can be approved
    if application.status not in ['assigned', 'under_review']:
        return jsonify({'success': False, 'message': 'Application cannot be approved in current status'})
    
    try:
        data = request.get_json()
        approved_amount = float(data.get('approved_amount', 0))
        interest_rate = float(data.get('interest_rate', 24))
        notes = data.get('notes', '')
        
        # Validate approved amount
        requested_amount = getattr(application, 'requested_amount', getattr(application, 'amount', 0))
        if approved_amount <= 0 or approved_amount > requested_amount:
            return jsonify({'success': False, 'message': 'Invalid approved amount'})
        
        # Update application
        application.status = 'approved'
        application.approved_amount = approved_amount
        application.interest_rate = interest_rate
        application.approved_at = datetime.utcnow()
        application.reviewed_by_id = current_user.id
        application.approval_notes = notes
        application.updated_at = datetime.utcnow()
        
        # Log activity
        ActivityLogger.log_activity(
            user_id=current_user.id,
            activity_type='loan_approved',
            description=f'Approved loan application {application.id} for ₦{approved_amount:,.0f}',
            metadata={
                'application_id': application.id,
                'approved_amount': approved_amount,
                'interest_rate': interest_rate
            }
        )
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Loan approved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@staff_bp.route('/loan_reviews/<int:application_id>/reject', methods=['POST'])
@login_required
@staff_required
def reject_loan(application_id):
    """Reject a loan application"""
    if not EnhancedLoanApplication:
        return jsonify({'success': False, 'message': 'Loan management system not available'})
    
    application = EnhancedLoanApplication.query.get_or_404(application_id)
    
    # Check if staff has access to this application
    if application.assigned_staff_id != current_user.id:
        return jsonify({'success': False, 'message': 'Access denied'})
    
    # Check if application can be rejected
    if application.status not in ['assigned', 'under_review']:
        return jsonify({'success': False, 'message': 'Application cannot be rejected in current status'})
    
    try:
        data = request.get_json()
        reason = data.get('reason', '')
        notes = data.get('notes', '')
        
        if not reason:
            return jsonify({'success': False, 'message': 'Rejection reason is required'})
        
        # Update application
        application.status = 'rejected'
        application.rejection_reason = reason
        application.rejection_notes = notes
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by_id = current_user.id
        application.updated_at = datetime.utcnow()
        
        # Log activity
        ActivityLogger.log_activity(
            user_id=current_user.id,
            activity_type='loan_rejected',
            description=f'Rejected loan application {application.id}: {reason}',
            metadata={
                'application_id': application.id,
                'rejection_reason': reason
            }
        )
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Loan rejected successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# ============================================
# INVENTORY MANAGEMENT ROUTES FOR STAFF
# ============================================

@staff_bp.route('/inventory')
@login_required
@staff_required
def inventory_dashboard():
    """Staff inventory dashboard - shows only assigned locations"""
    try:
        # Get staff's assigned locations
        assigned_locations = StaffLocationAssignment.query.filter_by(
            staff_id=current_user.id,
            is_active=True
        ).all()
        
        if not assigned_locations:
            flash('You are not assigned to any inventory locations. Please contact an administrator.', 'warning')
            return render_template('staff/inventory/no_assignment.html')
        
        location_ids = [assignment.location_id for assignment in assigned_locations]
        
        # Get inventory statistics for assigned locations
        total_items = InventoryItem.query.filter(
            InventoryItem.location_id.in_(location_ids),
            InventoryItem.status == 'active'
        ).count()
        
        low_stock_count = InventoryItem.query.filter(
            InventoryItem.location_id.in_(location_ids),
            InventoryItem.status == 'active',
            InventoryItem.current_stock <= InventoryItem.reorder_point
        ).count()
        
        out_of_stock_count = InventoryItem.query.filter(
            InventoryItem.location_id.in_(location_ids),
            InventoryItem.status == 'active',
            InventoryItem.current_stock <= 0
        ).count()
        
        # Get recent low stock alerts for assigned locations
        recent_alerts = LowStockAlert.query\
            .join(InventoryItem)\
            .filter(
                InventoryItem.location_id.in_(location_ids),
                LowStockAlert.status == 'active'
            )\
            .order_by(LowStockAlert.created_at.desc()).limit(10).all()
        
        # Get recent stock movements for assigned locations
        recent_movements = StockMovement.query.filter(
            StockMovement.location_id.in_(location_ids)
        ).order_by(StockMovement.movement_date.desc()).limit(10).all()
        
        return render_template('staff/inventory/dashboard.html',
                             assigned_locations=assigned_locations,
                             total_items=total_items,
                             low_stock_count=low_stock_count,
                             out_of_stock_count=out_of_stock_count,
                             recent_alerts=recent_alerts,
                             recent_movements=recent_movements)
                             
    except Exception as e:
        flash(f'Error loading inventory dashboard: {str(e)}', 'error')
        return render_template('staff/inventory/dashboard.html',
                             assigned_locations=[],
                             total_items=0,
                             low_stock_count=0,
                             out_of_stock_count=0,
                             recent_alerts=[],
                             recent_movements=[])

@staff_bp.route('/inventory/items')
@login_required
@staff_required
def inventory_items():
    """View inventory items in assigned locations"""
    # Get staff's assigned locations
    assigned_locations = StaffLocationAssignment.query.filter_by(
        staff_id=current_user.id,
        is_active=True
    ).all()
    
    if not assigned_locations:
        flash('You are not assigned to any inventory locations.', 'warning')
        return redirect(url_for('staff.inventory_dashboard'))
    
    location_ids = [assignment.location_id for assignment in assigned_locations]
    
    # Get filter parameters
    location_id = request.args.get('location_id', type=int)
    stock_status = request.args.get('stock_status', 'all')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    # Base query for assigned locations only
    query = InventoryItem.query.filter(
        InventoryItem.location_id.in_(location_ids),
        InventoryItem.status == 'active'
    )
    
    # Filter by specific location if provided and staff has access
    if location_id and location_id in location_ids:
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
    
    return render_template('staff/inventory/items.html',
                         items=items,
                         assigned_locations=assigned_locations,
                         current_location=location_id,
                         current_status=stock_status,
                         search=search)

@staff_bp.route('/inventory/items/<int:item_id>')
@login_required
@staff_required
def inventory_item_detail(item_id):
    """View inventory item details - only if in assigned location"""
    item = InventoryItem.query.get_or_404(item_id)
    
    # Check if staff has access to this item's location
    assigned_locations = StaffLocationAssignment.query.filter_by(
        staff_id=current_user.id,
        location_id=item.location_id,
        is_active=True
    ).first()
    
    if not assigned_locations:
        flash('You do not have access to this inventory location.', 'error')
        return redirect(url_for('staff.inventory_items'))
    
    # Get recent stock movements for this item
    movements = StockMovement.query.filter_by(inventory_item_id=item_id)\
        .order_by(StockMovement.movement_date.desc()).limit(20).all()
    
    # Get alerts for this item
    alerts = LowStockAlert.query.filter_by(inventory_item_id=item_id)\
        .order_by(LowStockAlert.created_at.desc()).limit(10).all()
    
    return render_template('staff/inventory/item_detail.html',
                         item=item,
                         movements=movements,
                         alerts=alerts,
                         assignment=assigned_locations)

@staff_bp.route('/inventory/items/<int:item_id>/adjust-stock', methods=['POST'])
@login_required
@staff_required
def adjust_inventory_stock(item_id):
    """Adjust inventory stock levels - staff with proper permissions only"""
    item = InventoryItem.query.get_or_404(item_id)
    
    # Check if staff has access to this item's location
    assignment = StaffLocationAssignment.query.filter_by(
        staff_id=current_user.id,
        location_id=item.location_id,
        is_active=True
    ).first()
    
    if not assignment:
        flash('You do not have access to this inventory location.', 'error')
        return redirect(url_for('staff.inventory_items'))
    
    # Check if staff has stock adjustment permissions
    if 'adjust_stock' not in (assignment.permissions or []):
        flash('You do not have permission to adjust stock levels.', 'error')
        return redirect(url_for('staff.inventory_item_detail', item_id=item_id))
    
    try:
        adjustment_type = request.form.get('adjustment_type')  # increase, decrease
        quantity = int(request.form.get('quantity', 0))
        notes = request.form.get('notes', '')
        
        if quantity <= 0:
            flash('Quantity must be greater than 0', 'error')
            return redirect(url_for('staff.inventory_item_detail', item_id=item_id))
        
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
            return redirect(url_for('staff.inventory_item_detail', item_id=item_id))
        
        # Update available stock
        item.update_available_stock()
        
        # Create stock movement record
        movement = StockMovement(
            inventory_item_id=item_id,
            location_id=item.location_id,
            user_id=current_user.id,
            movement_type='adjustment',
            quantity=quantity if adjustment_type == 'increase' else -quantity,
            reference_type='staff_adjustment',
            notes=notes,
            stock_before=stock_before,
            stock_after=item.current_stock
        )
        
        db.session.add(movement)
        db.session.commit()
        
        # Check if low stock alert needs to be created
        if item.is_low_stock:
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
        
        flash(f'Stock adjusted successfully. New stock level: {item.current_stock}', 'success')
        
    except ValueError:
        flash('Invalid quantity entered', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adjusting stock: {str(e)}', 'error')
    
    return redirect(url_for('staff.inventory_item_detail', item_id=item_id))

@staff_bp.route('/inventory/alerts')
@login_required
@staff_required
def low_stock_alerts():
    """View low stock alerts for assigned locations"""
    # Get staff's assigned locations
    assigned_locations = StaffLocationAssignment.query.filter_by(
        staff_id=current_user.id,
        is_active=True
    ).all()
    
    if not assigned_locations:
        flash('You are not assigned to any inventory locations.', 'warning')
        return redirect(url_for('staff.inventory_dashboard'))
    
    location_ids = [assignment.location_id for assignment in assigned_locations]
    
    # Get alerts for assigned locations only
    status_filter = request.args.get('status', 'active')
    location_id = request.args.get('location_id', type=int)
    
    query = LowStockAlert.query.join(InventoryItem)\
        .filter(InventoryItem.location_id.in_(location_ids))
    
    if status_filter != 'all':
        query = query.filter(LowStockAlert.status == status_filter)
    
    if location_id and location_id in location_ids:
        query = query.filter(InventoryItem.location_id == location_id)
    
    alerts = query.order_by(LowStockAlert.created_at.desc()).all()
    
    return render_template('staff/inventory/alerts.html',
                         alerts=alerts,
                         assigned_locations=assigned_locations,
                         current_status=status_filter,
                         current_location=location_id)

@staff_bp.route('/inventory/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@login_required
@staff_required
def acknowledge_inventory_alert(alert_id):
    """Acknowledge a low stock alert - staff can only acknowledge alerts in their assigned locations"""
    alert = LowStockAlert.query.get_or_404(alert_id)
    
    # Check if staff has access to this alert's location
    assigned_locations = StaffLocationAssignment.query.filter_by(
        staff_id=current_user.id,
        location_id=alert.inventory_item.location_id,
        is_active=True
    ).first()
    
    if not assigned_locations:
        flash('You do not have access to this inventory location.', 'error')
        return redirect(url_for('staff.low_stock_alerts'))
    
    if alert.status == 'active':
        alert.status = 'acknowledged'
        alert.acknowledged_by_id = current_user.id
        alert.acknowledged_at = datetime.utcnow()
        
        db.session.commit()
        flash('Alert acknowledged successfully', 'success')
    else:
        flash('Alert has already been processed', 'info')
    
    return redirect(url_for('staff.low_stock_alerts'))