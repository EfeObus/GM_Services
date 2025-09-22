"""
Services Blueprint
Public service showcase and detailed information for all GM Services offerings
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.service import Service
from models.user import User
from models.service_request import ServiceRequest, ServiceRequestType
from models.location import NigerianState, LocalGovernment
from models.automobile import Vehicle, VehicleMake, VehicleModel, MaintenanceRequest, InsuranceRequest, VehicleRegistrationRequest
from models.car_service import CarServiceBookingRequest
from models.enhanced_loan import LoanType, EnhancedLoanApplication, LoanPolicy
from models.hotel import HotelServiceRequest
from models.logistics import LogisticsQuoteRequest
from models.rental import RentalBookingRequest
from models.jewelry import JewelryServiceRequest, JewelryCollection, JewelryItem, JewelryCategory
from forms.loan_forms import EnhancedLoanApplicationForm
from forms.hotel_forms import OperationsManagementForm, BookingSystemForm, StaffTrainingForm, HotelConsultationForm
from forms.logistics_forms import LogisticsQuoteRequestForm, FreightTransportQuoteForm, ExpressDeliveryQuoteForm, SupplyChainQuoteForm
from forms.rental_forms import VehicleRentalRequestForm, EquipmentRentalRequestForm, PropertyRentalRequestForm, RentalTermsAcceptanceForm
from forms.car_service_forms import OilChangeMaintenanceForm, BrakeSuspensionForm, ACElectricalForm
from forms.vehicle_registration_forms import VehicleRegistrationForm, NewVehicleRegistrationForm, VehicleRenewalForm
from forms.jewelry_forms import JewelryConsultationForm, JewelryQuoteRequestForm
from forms.creative_forms import (
    CreativeProjectForm, LogoDesignForm, BrandingForm, PrintDesignForm, 
    DigitalDesignForm, WebsiteDesignForm, QuickQuoteForm
)
from models.creative_services import CreativeProject, CreativeServiceCategory, CreativeDesigner, WebsiteProject
from models.inventory import InventoryItem, InventoryLocation
from models.ecommerce import Product, ProductCategory
from data.nigeria_data import NIGERIAN_STATES, LOCAL_GOVERNMENTS
from database import db
from utils.decorators import admin_required, staff_required
from werkzeug.utils import secure_filename
import json
import os
import uuid
from datetime import datetime, timedelta

# Create blueprint
services_bp = Blueprint('services', __name__, template_folder='templates')

@services_bp.route('/')
def index():
    """All services overview"""
    try:
        services = Service.query.filter_by(is_active=True).order_by(Service.category, Service.name).all()
        
        # Group services by category
        services_by_category = {}
        for service in services:
            if service.category not in services_by_category:
                services_by_category[service.category] = []
            services_by_category[service.category].append(service)
        
        return render_template('services/index.html', services_by_category=services_by_category)
    except Exception as e:
        # Database not ready, render template without services data
        return render_template('services.html', services_by_category={})

@services_bp.route('/automobile')
def automobile():
    """Automobile dealership services"""
    try:
        services = Service.query.filter_by(category='automobile', is_active=True).all()
    except Exception as e:
        # Database not ready, use empty list
        services = []
    return render_template('services/automobile.html', services=services)

@services_bp.route('/loans')
def loans():
    """Loan services"""
    try:
        services = Service.query.filter_by(category='loans', is_active=True).all()
        loan_types = LoanType.query.filter_by(is_active=True).all()
    except Exception as e:
        # Database not ready, use empty list
        services = []
        loan_types = []
    return render_template('services/loans.html', services=services, loan_types=loan_types)

@services_bp.route('/loans/policy')
def loan_policy():
    """Display loan policy and agreement"""
    return render_template('services/loan_policy.html')

@services_bp.route('/loans/apply/<int:loan_type_id>')
@login_required
def apply_loan_form(loan_type_id):
    """Display loan application form"""
    try:
        loan_type = LoanType.query.get_or_404(loan_type_id)
        policies = LoanPolicy.query.filter_by(is_active=True).all()
        form = EnhancedLoanApplicationForm()
        
        return render_template('services/loan_application.html', 
                             loan_type=loan_type, 
                             policies=policies, 
                             form=form)
    except Exception as e:
        flash(f'Error loading loan application form: {str(e)}', 'error')
        return redirect(url_for('services.loans'))

@services_bp.route('/loans/apply/<int:loan_type_id>', methods=['POST'])
@login_required
def apply_loan(loan_type_id):
    """Process loan application submission"""
    try:
        loan_type = LoanType.query.get_or_404(loan_type_id)
        form = EnhancedLoanApplicationForm()
        
        if form.validate_on_submit():
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join('static', 'uploads', 'loans', str(current_user.id))
            os.makedirs(upload_dir, exist_ok=True)
            
            # Handle file uploads
            uploaded_files = {}
            
            # Required documents
            if form.identity_document.data:
                filename = secure_filename(f"identity_{uuid.uuid4().hex[:8]}.pdf")
                filepath = os.path.join(upload_dir, filename)
                form.identity_document.data.save(filepath)
                uploaded_files['identity_document'] = os.path.join('uploads', 'loans', str(current_user.id), filename)
            
            if form.income_proof.data:
                filename = secure_filename(f"income_{uuid.uuid4().hex[:8]}.pdf")
                filepath = os.path.join(upload_dir, filename)
                form.income_proof.data.save(filepath)
                uploaded_files['income_proof'] = os.path.join('uploads', 'loans', str(current_user.id), filename)
            
            if form.bank_statement.data:
                filename = secure_filename(f"bank_statement_{uuid.uuid4().hex[:8]}.pdf")
                filepath = os.path.join(upload_dir, filename)
                form.bank_statement.data.save(filepath)
                uploaded_files['bank_statement'] = os.path.join('uploads', 'loans', str(current_user.id), filename)
            
            # Optional documents
            if form.employment_letter.data:
                filename = secure_filename(f"employment_{uuid.uuid4().hex[:8]}.pdf")
                filepath = os.path.join(upload_dir, filename)
                form.employment_letter.data.save(filepath)
                uploaded_files['employment_letter'] = os.path.join('uploads', 'loans', str(current_user.id), filename)
            
            # Handle multiple business documents
            business_docs = []
            if 'business_documents[]' in request.files:
                for file in request.files.getlist('business_documents[]'):
                    if file and file.filename:
                        filename = secure_filename(f"business_{uuid.uuid4().hex[:8]}.pdf")
                        filepath = os.path.join(upload_dir, filename)
                        file.save(filepath)
                        business_docs.append(os.path.join('uploads', 'loans', str(current_user.id), filename))
            
            # Handle multiple collateral documents
            collateral_docs = []
            if 'collateral_documents[]' in request.files:
                for file in request.files.getlist('collateral_documents[]'):
                    if file and file.filename:
                        filename = secure_filename(f"collateral_{uuid.uuid4().hex[:8]}.pdf")
                        filepath = os.path.join(upload_dir, filename)
                        file.save(filepath)
                        collateral_docs.append(os.path.join('uploads', 'loans', str(current_user.id), filename))
            
            # Create loan application
            loan_application = EnhancedLoanApplication(
                user_id=current_user.id,
                loan_type_id=loan_type_id,
                requested_amount=form.requested_amount.data,
                term_months=form.term_months.data,
                purpose=form.purpose.data,
                purpose_description=form.purpose_description.data,
                
                # Personal Information
                phone_number=form.phone_number.data,
                alternate_phone=form.alternate_phone.data,
                residential_address=form.residential_address.data,
                state_of_origin=form.state_of_origin.data,
                lga=form.lga.data,
                next_of_kin_name=form.next_of_kin_name.data,
                next_of_kin_phone=form.next_of_kin_phone.data,
                next_of_kin_relationship=form.next_of_kin_relationship.data,
                
                # Bank Information
                bank_name=form.bank_name.data,
                account_number=form.account_number.data,
                account_name=form.account_name.data,
                bvn=form.bvn.data,
                
                # Employment Information
                employment_type=form.employment_type.data,
                monthly_income=form.monthly_income.data,
                employer_name=form.employer_name.data,
                employer_address=form.employer_address.data,
                employer_phone=form.employer_phone.data,
                job_title=form.job_title.data,
                employment_duration_months=form.employment_duration_months.data,
                
                # Business Information
                business_name=form.business_name.data,
                business_address=form.business_address.data,
                business_registration_number=form.business_registration_number.data,
                business_type=form.business_type.data,
                years_in_business=form.years_in_business.data,
                average_monthly_revenue=form.average_monthly_revenue.data,
                
                # Additional Information
                other_income=form.other_income.data,
                other_income_source=form.other_income_source.data,
                monthly_expenses=form.monthly_expenses.data,
                credit_score=form.credit_score.data,
                
                # Collateral Information
                collateral_type=form.collateral_type.data,
                collateral_value=form.collateral_value.data,
                collateral_location=form.collateral_location.data,
                collateral_description=form.collateral_description.data,
                
                # Agreement
                policy_agreed=form.policy_agreed.data,
                terms_agreed=form.terms_agreed.data,
                data_processing_agreed=form.data_processing_agreed.data,
                
                # Documents
                identity_document=uploaded_files.get('identity_document'),
                income_proof=uploaded_files.get('income_proof'),
                employment_letter=uploaded_files.get('employment_letter'),
                bank_statement=uploaded_files.get('bank_statement'),
                business_documents=business_docs if business_docs else None,
                collateral_documents=collateral_docs if collateral_docs else None
            )
            
            db.session.add(loan_application)
            db.session.commit()
            
            flash(f'Loan application submitted successfully! Application Number: {loan_application.application_number}', 'success')
            return redirect(url_for('users.loan_applications'))
            
        else:
            # Form validation failed
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')
            
            policies = LoanPolicy.query.filter_by(is_active=True).all()
            return render_template('services/loan_application.html', 
                                 loan_type=loan_type, 
                                 policies=policies, 
                                 form=form)
    
    except Exception as e:
        flash(f'Error processing loan application: {str(e)}', 'error')
        return redirect(url_for('services.loans'))

@services_bp.route('/loans/terms')
def loan_terms():
    """Loan terms and conditions page"""
    return render_template('services/loan_terms.html')

@services_bp.route('/loans/privacy')
def loan_privacy():
    """Loan privacy policy page"""
    return render_template('services/loan_privacy.html')

@services_bp.route('/gadgets')
def gadgets():
    """Gadgets and accessories"""
    try:
        services = Service.query.filter_by(category='gadgets', is_active=True).all()
    except Exception as e:
        # Database not ready, use empty list
        services = []
    return render_template('services/gadgets.html', services=services)

@services_bp.route('/hotel')
def hotel():
    """Hotel management services"""
    try:
        services = Service.query.filter_by(category='hotel', is_active=True).all()
    except Exception as e:
        # Database not ready, use empty list
        services = []
    return render_template('services/hotel.html', services=services)

@services_bp.route('/hotel/operations-management', methods=['GET', 'POST'])
def hotel_operations_management():
    """Hotel operations management request"""
    form = OperationsManagementForm()
    
    if form.validate_on_submit():
        try:
            # Create hotel service request
            request_data = HotelServiceRequest(
                service_type='operations_management',
                client_name=form.client_name.data,
                client_email=form.client_email.data,
                client_phone=form.client_phone.data,
                company_name=form.company_name.data,
                hotel_name=form.hotel_name.data,
                hotel_location=form.hotel_location.data,
                hotel_size=form.hotel_size.data,
                current_management_system=form.current_management_system.data,
                specific_requirements=form.specific_requirements.data,
                budget_range=form.budget_range.data,
                timeline=form.timeline.data,
                priority_level=form.priority_level.data,
                current_operations_challenges=form.current_operations_challenges.data,
                departments_to_manage=form.departments_to_manage.data,
                quality_standards_required=form.quality_standards_required.data
            )
            
            db.session.add(request_data)
            db.session.commit()
            
            flash('Your operations management request has been submitted successfully! We will contact you within 24 hours.', 'success')
            return redirect(url_for('services.hotel'))
            
        except Exception as e:
            db.session.rollback()
            flash('There was an error submitting your request. Please try again.', 'error')
    
    return render_template('services/hotel_request_form.html', 
                         form=form, 
                         service_type='Operations Management',
                         service_description='Comprehensive operational oversight and management systems for your hotel.')

@services_bp.route('/hotel/booking-system', methods=['GET', 'POST'])
def hotel_booking_system():
    """Hotel booking system request"""
    form = BookingSystemForm()
    
    if form.validate_on_submit():
        try:
            # Create hotel service request
            request_data = HotelServiceRequest(
                service_type='booking_system',
                client_name=form.client_name.data,
                client_email=form.client_email.data,
                client_phone=form.client_phone.data,
                company_name=form.company_name.data,
                hotel_name=form.hotel_name.data,
                hotel_location=form.hotel_location.data,
                hotel_size=form.hotel_size.data,
                current_booking_system=form.current_booking_system.data,
                specific_requirements=form.specific_requirements.data,
                budget_range=form.budget_range.data,
                timeline=form.timeline.data,
                priority_level=form.priority_level.data,
                integration_requirements=form.integration_requirements.data,
                expected_monthly_bookings=form.expected_monthly_bookings.data
            )
            
            db.session.add(request_data)
            db.session.commit()
            
            flash('Your booking system request has been submitted successfully! We will contact you within 24 hours.', 'success')
            return redirect(url_for('services.hotel'))
            
        except Exception as e:
            db.session.rollback()
            flash('There was an error submitting your request. Please try again.', 'error')
    
    return render_template('services/hotel_request_form.html', 
                         form=form, 
                         service_type='Booking System',
                         service_description='Advanced reservation and booking management platform for your hotel.')

@services_bp.route('/hotel/staff-training', methods=['GET', 'POST'])
def hotel_staff_training():
    """Hotel staff training request"""
    form = StaffTrainingForm()
    
    if form.validate_on_submit():
        try:
            # Create hotel service request
            request_data = HotelServiceRequest(
                service_type='staff_training',
                client_name=form.client_name.data,
                client_email=form.client_email.data,
                client_phone=form.client_phone.data,
                company_name=form.company_name.data,
                hotel_name=form.hotel_name.data,
                hotel_location=form.hotel_location.data,
                hotel_size=form.hotel_size.data,
                specific_requirements=form.specific_requirements.data,
                budget_range=form.budget_range.data,
                timeline=form.timeline.data,
                priority_level=form.priority_level.data,
                number_of_staff=form.number_of_staff.data,
                training_areas=form.training_areas.data,
                current_skill_level=form.current_skill_level.data
            )
            
            db.session.add(request_data)
            db.session.commit()
            
            flash('Your staff training request has been submitted successfully! We will contact you within 24 hours.', 'success')
            return redirect(url_for('services.hotel'))
            
        except Exception as e:
            db.session.rollback()
            flash('There was an error submitting your request. Please try again.', 'error')
    
    return render_template('services/hotel_request_form.html', 
                         form=form, 
                         service_type='Staff Training',
                         service_description='Professional hospitality training and development programs for your staff.')

@services_bp.route('/hotel/consultation', methods=['GET', 'POST'])
def hotel_consultation():
    """Hotel consultation request"""
    form = HotelConsultationForm()
    
    if form.validate_on_submit():
        try:
            # Create a general hotel service request for consultation
            request_data = HotelServiceRequest(
                service_type=form.consultation_type.data,
                client_name=form.client_name.data,
                client_email=form.client_email.data,
                client_phone=form.client_phone.data,
                company_name=form.company_name.data,
                specific_requirements=form.specific_questions.data or 'General consultation requested',
                priority_level='medium'
            )
            
            db.session.add(request_data)
            db.session.commit()
            
            flash('Your consultation request has been submitted successfully! We will contact you to schedule your consultation.', 'success')
            return redirect(url_for('services.hotel'))
            
        except Exception as e:
            db.session.rollback()
            flash('There was an error submitting your request. Please try again.', 'error')
    
    return render_template('services/hotel_consultation_form.html', form=form)

@services_bp.route('/logistics')
def logistics():
    """Logistics services"""
    try:
        services = Service.query.filter_by(category='logistics', is_active=True).all()
    except Exception as e:
        # Database not ready, use empty list
        services = []
    return render_template('services/logistics.html', services=services)


@services_bp.route('/logistics/quote/<service_type>')
def logistics_quote_form(service_type):
    """Display logistics quote request form"""
    valid_service_types = ['freight_transport', 'express_delivery', 'supply_chain']
    
    if service_type not in valid_service_types:
        flash('Invalid service type requested.', 'error')
        return redirect(url_for('services.logistics'))
    
    # Choose appropriate form based on service type
    if service_type == 'freight_transport':
        form = FreightTransportQuoteForm()
        template = 'services/logistics_quote_freight.html'
        service_title = 'Freight Transport'
    elif service_type == 'express_delivery':
        form = ExpressDeliveryQuoteForm()
        template = 'services/logistics_quote_express.html'
        service_title = 'Express Delivery'
    elif service_type == 'supply_chain':
        form = SupplyChainQuoteForm()
        template = 'services/logistics_quote_supply_chain.html'
        service_title = 'Supply Chain Management'
    
    return render_template(template, form=form, service_type=service_type, service_title=service_title)


@services_bp.route('/logistics/quote/<service_type>', methods=['POST'])
def submit_logistics_quote(service_type):
    """Handle logistics quote request submission"""
    valid_service_types = ['freight_transport', 'express_delivery', 'supply_chain']
    
    if service_type not in valid_service_types:
        flash('Invalid service type requested.', 'error')
        return redirect(url_for('services.logistics'))
    
    # Choose appropriate form based on service type
    if service_type == 'freight_transport':
        form = FreightTransportQuoteForm()
    elif service_type == 'express_delivery':
        form = ExpressDeliveryQuoteForm()
    elif service_type == 'supply_chain':
        form = SupplyChainQuoteForm()
    
    if form.validate_on_submit():
        try:
            # Create logistics quote request
            quote_request = LogisticsQuoteRequest(
                customer_id=current_user.id if current_user.is_authenticated else None,
                customer_name=form.customer_name.data,
                customer_email=form.customer_email.data,
                customer_phone=form.customer_phone.data,
                service_type=service_type
            )
            
            # Add common fields
            if hasattr(form, 'company_name') and form.company_name.data:
                quote_request.company_name = form.company_name.data
            
            quote_request.pickup_address = form.pickup_address.data
            quote_request.pickup_city = form.pickup_city.data
            quote_request.pickup_state = form.pickup_state.data
            
            quote_request.delivery_address = form.delivery_address.data
            quote_request.delivery_city = form.delivery_city.data
            quote_request.delivery_state = form.delivery_state.data
            
            quote_request.package_description = form.package_description.data
            
            if hasattr(form, 'package_weight') and form.package_weight.data:
                quote_request.package_weight = form.package_weight.data
            
            if hasattr(form, 'package_value') and form.package_value.data:
                quote_request.package_value = form.package_value.data
            
            if hasattr(form, 'special_requirements') and form.special_requirements.data:
                quote_request.special_requirements = form.special_requirements.data
            
            # Service-specific fields
            if service_type == 'freight_transport':
                quote_request.freight_type = form.freight_type.data
                quote_request.urgency_level = form.urgency_level.data
                quote_request.insurance_required = form.insurance_required.data
                
            elif service_type == 'express_delivery':
                quote_request.urgency_level = form.urgency_level.data
                quote_request.insurance_required = form.insurance_required.data
                
            elif service_type == 'supply_chain':
                quote_request.supply_chain_type = form.supply_chain_type.data
                if hasattr(form, 'duration_months') and form.duration_months.data:
                    quote_request.duration_months = form.duration_months.data
                if hasattr(form, 'volume_per_month') and form.volume_per_month.data:
                    quote_request.volume_per_month = form.volume_per_month.data
            
            # Set package dimensions if provided
            if (hasattr(form, 'package_length') and form.package_length.data and
                hasattr(form, 'package_width') and form.package_width.data and
                hasattr(form, 'package_height') and form.package_height.data):
                quote_request.package_dimensions = {
                    'length': float(form.package_length.data),
                    'width': float(form.package_width.data),
                    'height': float(form.package_height.data)
                }
            
            # Add to database
            db.session.add(quote_request)
            db.session.commit()
            
            # Send notification to admin and staff
            notify_admin_new_logistics_quote(quote_request)
            
            flash(f'Your {service_type.replace("_", " ").title()} quote request has been submitted successfully! '
                  f'Quote reference: {quote_request.quote_number}. '
                  f'We will contact you within 24 hours.', 'success')
            
            return redirect(url_for('services.logistics'))
            
        except Exception as e:
            db.session.rollback()
            flash('There was an error submitting your quote request. Please try again.', 'error')
            print(f"Error submitting logistics quote: {str(e)}")
    
    # If form validation failed, re-render form with errors
    service_titles = {
        'freight_transport': 'Freight Transport',
        'express_delivery': 'Express Delivery',
        'supply_chain': 'Supply Chain Management'
    }
    
    templates = {
        'freight_transport': 'services/logistics_quote_freight.html',
        'express_delivery': 'services/logistics_quote_express.html',
        'supply_chain': 'services/logistics_quote_supply_chain.html'
    }
    
    return render_template(templates[service_type], 
                         form=form, 
                         service_type=service_type, 
                         service_title=service_titles[service_type])

@services_bp.route('/rentals')
def rentals():
    """Rental services"""
    try:
        services = Service.query.filter_by(category='rentals', is_active=True).all()
    except Exception as e:
        # Database not ready, use empty list
        services = []
    return render_template('services/rentals.html', services=services)


@services_bp.route('/rentals/terms/<rental_type>')
def rental_terms(rental_type):
    """Display rental terms and conditions"""
    valid_rental_types = ['vehicle', 'equipment', 'property']
    
    if rental_type not in valid_rental_types:
        flash('Invalid rental type.', 'error')
        return redirect(url_for('services.rentals'))
    
    rental_titles = {
        'vehicle': 'Vehicle Rental',
        'equipment': 'Equipment Rental', 
        'property': 'Property Rental'
    }
    
    return render_template(f'services/rental_terms_{rental_type}.html', 
                         rental_type=rental_type,
                         rental_title=rental_titles[rental_type])


@services_bp.route('/rentals/book/<rental_type>')
def rental_booking_form(rental_type):
    """Display rental booking request form"""
    valid_rental_types = ['vehicle', 'equipment', 'property']
    
    if rental_type not in valid_rental_types:
        flash('Invalid rental type requested.', 'error')
        return redirect(url_for('services.rentals'))
    
    # Choose appropriate form based on rental type
    if rental_type == 'vehicle':
        form = VehicleRentalRequestForm()
        template = 'services/rental_booking_vehicle.html'
        service_title = 'Vehicle Rental'
    elif rental_type == 'equipment':
        form = EquipmentRentalRequestForm()
        template = 'services/rental_booking_equipment.html'
        service_title = 'Equipment Rental'
    elif rental_type == 'property':
        form = PropertyRentalRequestForm()
        template = 'services/rental_booking_property.html'
        service_title = 'Property Rental'
    
    return render_template(template, 
                         form=form, 
                         rental_type=rental_type, 
                         service_title=service_title)


@services_bp.route('/rentals/book/<rental_type>', methods=['POST'])
def submit_rental_booking(rental_type):
    """Handle rental booking request submission"""
    valid_rental_types = ['vehicle', 'equipment', 'property']
    
    if rental_type not in valid_rental_types:
        flash('Invalid rental type requested.', 'error')
        return redirect(url_for('services.rentals'))
    
    # Choose appropriate form based on rental type
    if rental_type == 'vehicle':
        form = VehicleRentalRequestForm()
    elif rental_type == 'equipment':
        form = EquipmentRentalRequestForm()
    elif rental_type == 'property':
        form = PropertyRentalRequestForm()
    
    if form.validate_on_submit():
        try:
            # Create rental booking request
            booking_request = RentalBookingRequest(
                customer_id=current_user.id if current_user.is_authenticated else None,
                customer_name=form.customer_name.data,
                customer_email=form.customer_email.data,
                customer_phone=form.customer_phone.data,
                rental_type=rental_type
            )
            
            # Add common fields
            if hasattr(form, 'customer_address') and form.customer_address.data:
                booking_request.customer_address = form.customer_address.data
            
            booking_request.start_date = form.start_date.data
            booking_request.end_date = form.end_date.data
            booking_request.flexible_dates = form.flexible_dates.data
            
            if form.pickup_location.data:
                booking_request.pickup_location = form.pickup_location.data
            
            booking_request.delivery_required = form.delivery_required.data
            if form.delivery_address.data:
                booking_request.delivery_address = form.delivery_address.data
            
            if form.budget_range_min.data:
                booking_request.budget_range_min = form.budget_range_min.data
            if form.budget_range_max.data:
                booking_request.budget_range_max = form.budget_range_max.data
            
            if form.usage_purpose.data:
                booking_request.usage_purpose = form.usage_purpose.data
            if form.special_requirements.data:
                booking_request.special_requirements = form.special_requirements.data
            
            # Set terms acceptance
            booking_request.terms_accepted = form.terms_accepted.data
            if form.terms_accepted.data:
                booking_request.terms_accepted_at = datetime.now()
                booking_request.terms_version = "1.0"
            
            # Service-specific fields
            preferred_specs = {}
            
            if rental_type == 'vehicle':
                booking_request.item_category = form.vehicle_category.data
                booking_request.driver_required = form.driver_required.data
                booking_request.insurance_required = form.insurance_required.data
                
                # Build specifications JSON
                if form.preferred_make.data:
                    preferred_specs['make'] = form.preferred_make.data
                if form.preferred_model.data:
                    preferred_specs['model'] = form.preferred_model.data
                if form.year_preference.data:
                    preferred_specs['year'] = form.year_preference.data
                if form.transmission.data:
                    preferred_specs['transmission'] = form.transmission.data
                if form.fuel_type.data:
                    preferred_specs['fuel_type'] = form.fuel_type.data
                if form.seating_capacity.data:
                    preferred_specs['seating_capacity'] = form.seating_capacity.data
                
                # Additional features
                features = []
                if form.air_conditioning.data:
                    features.append('air_conditioning')
                if form.bluetooth.data:
                    features.append('bluetooth')
                if form.gps_required.data:
                    features.append('gps')
                if form.child_seat_required.data:
                    features.append('child_seat')
                
                if features:
                    preferred_specs['features'] = features
                if form.luggage_space.data:
                    preferred_specs['luggage_space'] = form.luggage_space.data
                
                # Build description
                booking_request.item_description = f"{form.vehicle_category.data.replace('_', ' ').title()}"
                if form.preferred_make.data:
                    booking_request.item_description += f" - {form.preferred_make.data}"
                if form.preferred_model.data:
                    booking_request.item_description += f" {form.preferred_model.data}"
                
            elif rental_type == 'equipment':
                booking_request.item_category = form.equipment_category.data
                booking_request.item_description = form.equipment_name.data
                booking_request.installation_required = form.installation_required.data
                booking_request.setup_required = form.setup_required.data
                
                # Build specifications JSON
                if form.brand_preference.data:
                    preferred_specs['brand'] = form.brand_preference.data
                if form.model_preference.data:
                    preferred_specs['model'] = form.model_preference.data
                if form.power_requirements.data:
                    preferred_specs['power_requirements'] = form.power_requirements.data
                if form.capacity_requirements.data:
                    preferred_specs['capacity'] = form.capacity_requirements.data
                if form.quantity_needed.data:
                    preferred_specs['quantity'] = form.quantity_needed.data
                
                # Additional services
                services = []
                if form.operator_required.data:
                    services.append('operator_required')
                if form.maintenance_included.data:
                    services.append('maintenance_included')
                if form.training_required.data:
                    services.append('training_required')
                if form.technical_support.data:
                    services.append('technical_support')
                if form.backup_equipment.data:
                    services.append('backup_equipment')
                
                if services:
                    preferred_specs['services'] = services
                    
                # Environment and safety
                environment = []
                if form.indoor_use.data:
                    environment.append('indoor')
                if form.outdoor_use.data:
                    environment.append('outdoor')
                if form.weather_protection.data:
                    environment.append('weather_protection')
                if form.safety_training.data:
                    environment.append('safety_training')
                if form.safety_equipment.data:
                    environment.append('safety_equipment')
                
                if environment:
                    preferred_specs['environment'] = environment
                
            elif rental_type == 'property':
                booking_request.item_category = form.property_category.data
                booking_request.item_description = f"{form.property_category.data.replace('_', ' ').title()} in {form.preferred_area.data}"
                
                # Build specifications JSON
                preferred_specs['preferred_area'] = form.preferred_area.data
                preferred_specs['preferred_state'] = form.preferred_state.data
                
                if form.proximity_requirements.data:
                    preferred_specs['proximity'] = form.proximity_requirements.data
                if form.bedrooms.data:
                    preferred_specs['bedrooms'] = form.bedrooms.data
                if form.bathrooms.data:
                    preferred_specs['bathrooms'] = form.bathrooms.data
                if form.minimum_size_sqm.data:
                    preferred_specs['minimum_size'] = float(form.minimum_size_sqm.data)
                if form.maximum_occupancy.data:
                    preferred_specs['max_occupancy'] = form.maximum_occupancy.data
                if form.parking_spaces.data:
                    preferred_specs['parking_spaces'] = form.parking_spaces.data
                
                # Amenities and features
                amenities = []
                if form.furnished.data:
                    amenities.append('furnished')
                if form.air_conditioning.data:
                    amenities.append('air_conditioning')
                if form.parking.data:
                    amenities.append('parking')
                if form.electricity_included.data:
                    amenities.append('electricity')
                if form.water_included.data:
                    amenities.append('water')
                if form.internet_included.data:
                    amenities.append('internet')
                if form.security.data:
                    amenities.append('security')
                if form.cleaning_service.data:
                    amenities.append('cleaning')
                
                if amenities:
                    preferred_specs['amenities'] = amenities
                    
                # Accessibility and special requirements
                accessibility = []
                if form.wheelchair_accessible.data:
                    accessibility.append('wheelchair_accessible')
                if form.elevator_access.data:
                    accessibility.append('elevator')
                if form.ground_floor.data:
                    accessibility.append('ground_floor')
                if form.pet_friendly.data:
                    accessibility.append('pet_friendly')
                if form.smoking_allowed.data:
                    accessibility.append('smoking_allowed')
                if form.event_hosting_allowed.data:
                    accessibility.append('events_allowed')
                
                if accessibility:
                    preferred_specs['accessibility'] = accessibility
            
            # Set preferred specifications
            if preferred_specs:
                booking_request.preferred_specifications = preferred_specs
            
            # Add to database
            db.session.add(booking_request)
            db.session.commit()
            
            # Send notification to admin (implement later)
            # notify_admin_new_rental_request(booking_request)
            
            flash(f'Your {rental_type} rental request has been submitted successfully! '
                  f'Request reference: {booking_request.request_number}. '
                  f'Our team will review your request and contact you within 24 hours.', 'success')
            
            return redirect(url_for('services.rentals'))
            
        except Exception as e:
            db.session.rollback()
            flash('There was an error submitting your rental request. Please try again.', 'error')
            print(f"Error submitting rental request: {str(e)}")
    
    # If form validation failed, re-render form with errors
    service_titles = {
        'vehicle': 'Vehicle Rental',
        'equipment': 'Equipment Rental',
        'property': 'Property Rental'
    }
    
    templates = {
        'vehicle': 'services/rental_booking_vehicle.html',
        'equipment': 'services/rental_booking_equipment.html',
        'property': 'services/rental_booking_property.html'
    }
    
    return render_template(templates[rental_type], 
                         form=form, 
                         rental_type=rental_type, 
                         service_title=service_titles[rental_type])

@services_bp.route('/car-services')
def car_services():
    """Car maintenance and repair services"""
    try:
        services = Service.query.filter_by(category='car_services', is_active=True).all()
    except Exception as e:
        # Database not ready, use empty list
        services = []
    return render_template('services/car_services.html', services=services)

@services_bp.route('/car-services/book/<service_type>')
def car_service_booking_form(service_type):
    """Display car service booking form"""
    from database import db
    
    # Validate service type
    valid_types = ['oil_maintenance', 'brake_suspension', 'ac_electrical']
    if service_type not in valid_types:
        flash('Invalid service type.', 'error')
        return redirect(url_for('services.car_services'))
    
    # Create appropriate form
    if service_type == 'oil_maintenance':
        form = OilChangeMaintenanceForm()
        template = 'services/car_service_booking_oil.html'
        service_title = 'Oil Change & Maintenance'
    elif service_type == 'brake_suspension':
        form = BrakeSuspensionForm()
        template = 'services/car_service_booking_brake.html'
        service_title = 'Brake & Suspension Service'
    elif service_type == 'ac_electrical':
        form = ACElectricalForm()
        template = 'services/car_service_booking_ac.html'
        service_title = 'AC & Electrical Service'
    
    return render_template(template, form=form, service_type=service_type, service_title=service_title)

@services_bp.route('/car-services/book/<service_type>', methods=['POST'])
def car_service_booking_submit(service_type):
    """Handle car service booking form submission"""
    from database import db
    
    # Validate service type
    valid_types = ['oil_maintenance', 'brake_suspension', 'ac_electrical']
    if service_type not in valid_types:
        flash('Invalid service type.', 'error')
        return redirect(url_for('services.car_services'))
    
    # Create appropriate form
    if service_type == 'oil_maintenance':
        form = OilChangeMaintenanceForm()
        template = 'services/car_service_booking_oil.html'
        service_title = 'Oil Change & Maintenance'
        service_category = 'maintenance'
    elif service_type == 'brake_suspension':
        form = BrakeSuspensionForm()
        template = 'services/car_service_booking_brake.html'
        service_title = 'Brake & Suspension Service'
        service_category = 'safety'
    elif service_type == 'ac_electrical':
        form = ACElectricalForm()
        template = 'services/car_service_booking_ac.html'
        service_title = 'AC & Electrical Service'
        service_category = 'comfort'
    
    if form.validate_on_submit():
        try:
            # Prepare service specifications based on service type
            service_specifications = {}
            additional_services = []
            
            if service_type == 'oil_maintenance':
                service_specifications = {
                    'oil_type_preference': form.oil_type_preference.data,
                    'last_service_date': form.last_service_date.data.isoformat() if form.last_service_date.data else None,
                    'last_service_mileage': form.last_service_mileage.data
                }
                # Collect additional services
                if form.oil_filter_change.data:
                    additional_services.append('oil_filter_change')
                if form.air_filter_change.data:
                    additional_services.append('air_filter_change')
                if form.transmission_fluid_check.data:
                    additional_services.append('transmission_fluid_check')
                if form.brake_fluid_check.data:
                    additional_services.append('brake_fluid_check')
                if form.coolant_check.data:
                    additional_services.append('coolant_check')
                if form.battery_check.data:
                    additional_services.append('battery_check')
                if form.tire_pressure_check.data:
                    additional_services.append('tire_pressure_check')
                if form.basic_inspection.data:
                    additional_services.append('basic_inspection')
                    
            elif service_type == 'brake_suspension':
                service_specifications = {
                    'brake_issues': form.brake_issues.data,
                    'suspension_issues': form.suspension_issues.data,
                    'last_brake_service': form.last_brake_service.data.isoformat() if form.last_brake_service.data else None,
                    'last_alignment': form.last_alignment.data.isoformat() if form.last_alignment.data else None
                }
                # Collect additional services
                if form.brake_pad_replacement.data:
                    additional_services.append('brake_pad_replacement')
                if form.brake_rotor_service.data:
                    additional_services.append('brake_rotor_service')
                if form.brake_fluid_change.data:
                    additional_services.append('brake_fluid_change')
                if form.suspension_struts.data:
                    additional_services.append('suspension_struts')
                if form.wheel_alignment.data:
                    additional_services.append('wheel_alignment')
                if form.wheel_balancing.data:
                    additional_services.append('wheel_balancing')
                if form.tire_rotation.data:
                    additional_services.append('tire_rotation')
                if form.safety_inspection.data:
                    additional_services.append('safety_inspection')
                    
            elif service_type == 'ac_electrical':
                service_specifications = {
                    'ac_issues': form.ac_issues.data,
                    'electrical_issues': form.electrical_issues.data,
                    'last_ac_service': form.last_ac_service.data.isoformat() if form.last_ac_service.data else None,
                    'last_battery_replacement': form.last_battery_replacement.data.isoformat() if form.last_battery_replacement.data else None
                }
                # Collect additional services
                if form.ac_refrigerant_recharge.data:
                    additional_services.append('ac_refrigerant_recharge')
                if form.ac_compressor_service.data:
                    additional_services.append('ac_compressor_service')
                if form.ac_filter_replacement.data:
                    additional_services.append('ac_filter_replacement')
                if form.battery_replacement.data:
                    additional_services.append('battery_replacement')
                if form.alternator_service.data:
                    additional_services.append('alternator_service')
                if form.starter_service.data:
                    additional_services.append('starter_service')
                if form.electrical_diagnostics.data:
                    additional_services.append('electrical_diagnostics')
                if form.charging_system_test.data:
                    additional_services.append('charging_system_test')
            
            # Create the booking request
            booking_request = CarServiceBookingRequest(
                customer_name=form.customer_name.data,
                customer_email=form.customer_email.data,
                customer_phone=form.customer_phone.data,
                vehicle_make=form.vehicle_make.data,
                vehicle_model=form.vehicle_model.data,
                vehicle_year=form.vehicle_year.data,
                registration_number=form.registration_number.data,
                current_mileage=form.current_mileage.data,
                service_type=service_type,
                service_category=service_category,
                preferred_date=form.preferred_date.data,
                preferred_time=form.preferred_time.data,
                service_location=form.service_location.data,
                service_specifications=service_specifications,
                additional_services=additional_services,
                customer_complaints=form.customer_complaints.data,
                special_instructions=form.special_instructions.data,
                budget_range=form.budget_range.data,
                emergency_contact_name=form.emergency_contact_name.data,
                emergency_contact_phone=form.emergency_contact_phone.data,
                terms_accepted=form.terms_accepted.data
            )
            
            # Save to database
            db.session.add(booking_request)
            db.session.commit()
            
            # Send notification to admin (similar to other services)
            from models.user import User
            try:
                admin_users = User.query.filter_by(role='admin').all()
                # In a real application, you would send actual notifications here
                # For now, we'll just log the creation
                print(f"New car service booking request: {booking_request.request_number}")
            except Exception as e:
                print(f"Error notifying admins: {e}")
            
            flash(f'Your {service_title.lower()} booking request has been submitted successfully! '
                  f'Request number: {booking_request.request_number}. '
                  f'You will receive a confirmation email shortly.', 'success')
            
            return redirect(url_for('services.car_services'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your booking. Please try again.', 'error')
            print(f"Car service booking error: {e}")
    
    # If form validation failed, redisplay form with errors
    return render_template(template, form=form, service_type=service_type, service_title=service_title)

@services_bp.route('/license-plates')
def license_plates():
    """License plates and paperwork services"""
    try:
        services = Service.query.filter_by(category='license_plates', is_active=True).all()
    except Exception as e:
        # Database not ready, use empty list
        services = []
    return render_template('services/license_plates.html', services=services)

@services_bp.route('/vehicle-registration/new', methods=['GET', 'POST'])
@login_required
def new_vehicle_registration():
    """New vehicle registration form"""
    form = NewVehicleRegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Create new vehicle registration request
            registration_request = VehicleRegistrationRequest(
                customer_id=current_user.id,
                registration_type='new_registration',
                vehicle_make=form.vehicle_make.data,
                vehicle_model=form.vehicle_model.data,
                vehicle_year=form.vehicle_year.data,
                vehicle_color=form.vehicle_color.data,
                engine_number=form.engine_number.data,
                chassis_number=form.chassis_number.data,
                owner_name=form.owner_name.data,
                owner_address=form.owner_address.data,
                owner_phone=form.owner_phone.data,
                owner_email=form.owner_email.data,
                owner_state=form.owner_state.data,
                owner_lga=form.owner_lga.data,
                vehicle_purpose=form.vehicle_purpose.data,
                purchase_receipt=form.purchase_receipt.data,
                customs_papers=form.customs_papers.data,
                insurance_certificate=form.insurance_certificate.data,
                roadworthiness_certificate=form.roadworthiness_certificate.data,
                driver_license=form.driver_license.data,
                service_center=form.service_center.data,
                processing_priority=form.processing_priority.data,
                contact_phone=form.contact_phone.data,
                contact_email=form.contact_email.data,
                pickup_required=form.pickup_required.data,
                pickup_address=form.pickup_address.data
            )
            
            # Set pricing based on processing priority
            if registration_request.processing_priority == 'standard':
                registration_request.total_amount = 45000
            elif registration_request.processing_priority == 'express':
                registration_request.total_amount = 65000
            elif registration_request.processing_priority == 'same_day':
                registration_request.total_amount = 85000
            
            db.session.add(registration_request)
            db.session.commit()
            
            flash(f'Your vehicle registration request has been submitted successfully! Request Number: {registration_request.request_number}', 'success')
            return redirect(url_for('services.registration_success', request_number=registration_request.request_number))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your registration request. Please try again.', 'error')
            print(f"New vehicle registration error: {e}")
    
    return render_template('services/new_vehicle_registration.html', form=form)

@services_bp.route('/vehicle-registration/renewal', methods=['GET', 'POST'])
@login_required
def vehicle_renewal():
    """Vehicle registration renewal form"""
    form = VehicleRenewalForm()
    
    if form.validate_on_submit():
        try:
            # Create vehicle renewal request
            registration_request = VehicleRegistrationRequest(
                customer_id=current_user.id,
                registration_type='renewal',
                vehicle_make=form.vehicle_make.data,
                vehicle_model=form.vehicle_model.data,
                vehicle_year=form.vehicle_year.data,
                vehicle_color=form.vehicle_color.data,
                current_registration_number=form.current_registration_number.data,
                expiry_date=form.expiry_date.data,
                owner_name=form.owner_name.data,
                owner_address=form.owner_address.data,
                owner_phone=form.owner_phone.data,
                owner_email=form.owner_email.data,
                owner_state=form.owner_state.data,
                owner_lga=form.owner_lga.data,
                vehicle_purpose=form.vehicle_purpose.data,
                purchase_receipt=form.purchase_receipt.data,
                customs_papers=form.customs_papers.data,
                insurance_certificate=form.insurance_certificate.data,
                roadworthiness_certificate=form.roadworthiness_certificate.data,
                driver_license=form.driver_license.data,
                service_center=form.service_center.data,
                processing_priority=form.processing_priority.data,
                contact_phone=form.contact_phone.data,
                contact_email=form.contact_email.data,
                pickup_required=form.pickup_required.data,
                pickup_address=form.pickup_address.data
            )
            
            # Set pricing based on processing priority for renewals
            if registration_request.processing_priority == 'standard':
                registration_request.total_amount = 25000
            elif registration_request.processing_priority == 'express':
                registration_request.total_amount = 35000
            elif registration_request.processing_priority == 'same_day':
                registration_request.total_amount = 45000
            
            db.session.add(registration_request)
            db.session.commit()
            
            flash(f'Your vehicle renewal request has been submitted successfully! Request Number: {registration_request.request_number}', 'success')
            return redirect(url_for('services.registration_success', request_number=registration_request.request_number))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your renewal request. Please try again.', 'error')
            print(f"Vehicle renewal error: {e}")
    
    return render_template('services/vehicle_renewal.html', form=form)

@services_bp.route('/vehicle-registration/success/<request_number>')
@login_required
def registration_success(request_number):
    """Registration request success page"""
    try:
        registration_request = VehicleRegistrationRequest.query.filter_by(
            request_number=request_number,
            customer_id=current_user.id
        ).first_or_404()
        
        return render_template('services/registration_success.html', request=registration_request)
    except Exception as e:
        flash('Registration request not found.', 'error')
        return redirect(url_for('services.license_plates'))

@services_bp.route('/api/lgas/<state>')
def get_lgas(state):
    """API endpoint to get LGAs for a state"""
    try:
        lgas = LOCAL_GOVERNMENTS.get(state, [])
        return jsonify({'lgas': lgas})
    except Exception as e:
        return jsonify({'error': 'Failed to fetch LGAs'}), 500

@services_bp.route('/jewelry')
def jewelry():
    """Luxury jewelry services"""
    try:
        services = Service.query.filter_by(category='jewelry', is_active=True).all()
        collections = JewelryCollection.query.filter_by(is_active=True).order_by(JewelryCollection.display_order).all()
        featured_items = JewelryItem.query.filter_by(is_featured=True, status='active').limit(6).all()
    except Exception as e:
        # Database not ready, use empty lists
        services = []
        collections = []
        featured_items = []
    
    return render_template('services/jewelry.html', 
                         services=services, 
                         collections=collections, 
                         featured_items=featured_items)

@services_bp.route('/jewelry/collection/<collection_type>')
def jewelry_collection(collection_type):
    """Display jewelry collection items"""
    try:
        # Get the collection info
        collection = JewelryCollection.query.filter_by(
            collection_type=collection_type, 
            is_active=True
        ).first()
        
        if not collection:
            # Create default collection info if not found in database
            collection_info = {
                'gold': {
                    'name': 'Gold Collections',
                    'description': 'Pure gold jewelry in traditional and contemporary designs',
                    'features': ['18k & 24k gold pieces', 'Traditional Nigerian designs', 'Wedding collections', 'Custom engravings']
                },
                'diamond': {
                    'name': 'Diamond Collections', 
                    'description': 'Certified diamonds in elegant settings and designs',
                    'features': ['Certified diamonds', 'Engagement rings', 'Diamond necklaces', 'Anniversary pieces']
                }
            }.get(collection_type, {
                'name': 'Jewelry Collection',
                'description': 'Premium jewelry collection',
                'features': []
            })
        else:
            collection_info = {
                'name': collection.name,
                'description': collection.description,
                'features': collection.key_features or []
            }
        
        # Get jewelry items for this collection type
        jewelry_items = JewelryItem.query.join(JewelryCategory).filter(
            JewelryCategory.name.ilike(f'%{collection_type}%'),
            JewelryItem.status == 'active'
        ).order_by(JewelryItem.is_featured.desc(), JewelryItem.created_at.desc()).limit(12).all()
        
        # If no items found by category, get featured items
        if not jewelry_items:
            jewelry_items = JewelryItem.query.filter_by(
                status='active',
                is_featured=True
            ).limit(8).all()
        
    except Exception as e:
        # Database not ready or error, use defaults
        collection_info = {
            'name': f'{collection_type.title()} Collection',
            'description': 'Premium jewelry collection',
            'features': []
        }
        jewelry_items = []
    
    return render_template('services/jewelry_collection.html', 
                         collection_info=collection_info,
                         collection_type=collection_type,
                         jewelry_items=jewelry_items)

@services_bp.route('/jewelry/consultation', methods=['GET', 'POST'])
def jewelry_consultation():
    """Jewelry consultation request form"""
    form = JewelryConsultationForm()
    
    if form.validate_on_submit():
        try:
            # Create new jewelry service request
            jewelry_request = JewelryServiceRequest(
                customer_id=current_user.id if current_user.is_authenticated else None,
                customer_name=form.full_name.data,
                customer_email=form.email.data,
                customer_phone=form.phone.data,
                request_type='consultation',
                consultation_type=form.consultation_type.data,
                jewelry_type=form.jewelry_type.data,
                preferred_metal=form.preferred_metal.data,
                preferred_gemstone=form.preferred_gemstone.data,
                budget_range=form.budget_range.data,
                occasion=form.occasion.data,
                design_style=form.design_style.data,
                timeline=form.timeline.data,
                description=form.description.data,
                additional_notes=form.additional_notes.data,
                engraving_required=form.engraving_required.data,
                engraving_text=form.engraving_text.data,
                size_known=form.size_known.data,
                ring_size=form.ring_size.data,
                preferred_contact_method=form.preferred_contact_method.data,
                preferred_contact_time=form.preferred_time.data
            )
            
            # Generate request number
            jewelry_request.generate_request_number()
            
            # Handle file upload
            if form.reference_images.data:
                filename = secure_filename(form.reference_images.data.filename)
                file_path = os.path.join('static/uploads/jewelry/', filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                form.reference_images.data.save(file_path)
                jewelry_request.reference_images = [file_path]
            
            db.session.add(jewelry_request)
            db.session.commit()
            
            flash('Your jewelry consultation request has been submitted successfully! We will contact you within 24-48 hours.', 'success')
            return redirect(url_for('services.jewelry_consultation_success', request_id=jewelry_request.id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while submitting your request. Please try again.', 'error')
    
    return render_template('services/jewelry_consultation.html', form=form)

@services_bp.route('/jewelry/quote-request', methods=['GET', 'POST'])
def jewelry_quote_request():
    """Jewelry quote request form"""
    form = JewelryQuoteRequestForm()
    
    if form.validate_on_submit():
        try:
            # Create new jewelry service request
            jewelry_request = JewelryServiceRequest(
                customer_id=current_user.id if current_user.is_authenticated else None,
                customer_name=form.full_name.data,
                customer_email=form.email.data,
                customer_phone=form.phone.data,
                request_type='quote_request',
                quote_type=form.quote_type.data,
                item_description=form.item_description.data,
                metal_type=form.metal_type.data,
                gemstone_details=form.gemstone_details.data,
                weight_grams=form.weight_grams.data,
                dimensions=form.dimensions.data,
                additional_notes=form.additional_info.data,
                priority='urgent' if form.urgency.data == 'rush' else 'medium'
            )
            
            # Generate request number
            jewelry_request.generate_request_number()
            
            # Handle file upload
            if form.item_images.data:
                filename = secure_filename(form.item_images.data.filename)
                file_path = os.path.join('static/uploads/jewelry/', filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                form.item_images.data.save(file_path)
                jewelry_request.item_images = [file_path]
            
            db.session.add(jewelry_request)
            db.session.commit()
            
            flash('Your quote request has been submitted successfully! We will provide a detailed quote within 24-48 hours.', 'success')
            return redirect(url_for('services.jewelry_quote_success', request_id=jewelry_request.id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while submitting your request. Please try again.', 'error')
    
    return render_template('services/jewelry_quote_request.html', form=form)

@services_bp.route('/jewelry/consultation/success/<int:request_id>')
def jewelry_consultation_success(request_id):
    """Jewelry consultation request success page"""
    try:
        jewelry_request = JewelryServiceRequest.query.get_or_404(request_id)
        return render_template('services/jewelry_consultation_success.html', request=jewelry_request)
    except Exception as e:
        flash('Request not found.', 'error')
        return redirect(url_for('services.jewelry'))

@services_bp.route('/jewelry/quote/success/<int:request_id>')
def jewelry_quote_success(request_id):
    """Jewelry quote request success page"""
    try:
        jewelry_request = JewelryServiceRequest.query.get_or_404(request_id)
        return render_template('services/jewelry_quote_success.html', request=jewelry_request)
    except Exception as e:
        flash('Request not found.', 'error')
        return redirect(url_for('services.jewelry'))

@services_bp.route('/graphic-design')
def graphic_design():
    """Redirect to creative services"""
    return redirect(url_for('services.creative_services'))

@services_bp.route('/web-design')
def web_design():
    """Redirect to creative services"""
    return redirect(url_for('services.creative_services'))

@services_bp.route('/<int:service_id>')
def service_detail(service_id):
    """Individual service detail page"""
    service = Service.query.get_or_404(service_id)
    
    if not service.is_active:
        return render_template('errors/404.html'), 404
    
    # Get related services in same category
    related_services = Service.query.filter(
        Service.category == service.category,
        Service.id != service.id,
        Service.is_active == True
    ).limit(3).all()
    
    return render_template('services/detail.html', service=service, related_services=related_services)

@services_bp.route('/search')
def search():
    """Search services"""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    if not query and not category:
        return render_template('services/search.html', services=[], query='', category='')
    
    # Build search query
    search_query = Service.query.filter_by(is_active=True)
    
    if query:
        search_query = search_query.filter(
            Service.name.contains(query) | 
            Service.description.contains(query)
        )
    
    if category:
        search_query = search_query.filter_by(category=category)
    
    services = search_query.order_by(Service.name).all()
    
    return render_template('services/search.html', 
                         services=services, 
                         query=query, 
                         category=category)

@services_bp.route('/categories')
def categories():
    """Service categories"""
    categories = [
        {
            'name': 'automobile',
            'title': 'Automobile Dealerships',
            'description': 'New and used car sales, financing, and trade-ins',
            'icon': 'car'
        },
        {
            'name': 'loans',
            'title': 'Loan Services',
            'description': 'Personal, business, and auto loans with competitive rates',
            'icon': 'dollar-sign'
        },
        {
            'name': 'gadgets',
            'title': 'Gadgets & Accessories',
            'description': 'Latest electronics, gadgets, and tech accessories',
            'icon': 'smartphone'
        },
        {
            'name': 'hotel',
            'title': 'Hotel Management',
            'description': 'Hospitality services and accommodation booking',
            'icon': 'bed'
        },
        {
            'name': 'logistics',
            'title': 'Logistics',
            'description': 'Shipping, delivery, and supply chain solutions',
            'icon': 'truck'
        },
        {
            'name': 'rentals',
            'title': 'Rental Services',
            'description': 'Vehicle rentals, equipment, and property rentals',
            'icon': 'key'
        },
        {
            'name': 'car_services',
            'title': 'Car Services',
            'description': 'Maintenance, repair, and automotive services',
            'icon': 'wrench'
        },
        {
            'name': 'license_plates',
            'title': 'License Plates & Paperwork',
            'description': 'Vehicle registration, plates, and documentation',
            'icon': 'clipboard'
        },
        {
            'name': 'jewelry',
            'title': 'Luxury Jewelry',
            'description': 'Fine jewelry, custom designs, and appraisals',
            'icon': 'gem'
        },
        {
            'name': 'graphic_design',
            'title': 'Graphic Design',
            'description': 'Creative design solutions for all your needs',
            'icon': 'paint-brush'
        },
        {
            'name': 'web_design',
            'title': 'Website & Logo Design',
            'description': 'Professional web development and branding',
            'icon': 'globe'
        }
    ]
    
    return render_template('services/categories.html', categories=categories)

@services_bp.route('/api/search')
def api_search():
    """API endpoint for service search (for autocomplete/AJAX)"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    
    if not query:
        return jsonify([])
    
    services = Service.query.filter(
        Service.is_active == True,
        Service.name.contains(query) | Service.description.contains(query)
    ).limit(limit).all()
    
    results = []
    for service in services:
        results.append({
            'id': service.id,
            'name': service.name,
            'category': service.category,
            'price': service.price
        })
    
    return jsonify(results)

# ======================== SERVICE REQUEST ROUTES ========================

@services_bp.route('/request')
def service_request_form():
    """Display service request form"""
    # Get all active service request types
    request_types = ServiceRequestType.query.filter_by(is_active=True).order_by(ServiceRequestType.display_order, ServiceRequestType.name).all()
    
    # Get Nigerian states for location dropdown
    states = NigerianState.query.order_by(NigerianState.name).all()
    
    return render_template('services/service_request_form.html', 
                         request_types=request_types, 
                         states=states)

@services_bp.route('/request', methods=['POST'])
def submit_service_request():
    """Handle service request form submission"""
    try:
        # Get form data
        request_type_id = request.form.get('request_type_id')
        subject = request.form.get('subject')
        description = request.form.get('description')
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        preferred_contact_method = request.form.get('preferred_contact_method', 'email')
        urgency = request.form.get('urgency', 'medium')
        preferred_response_time = request.form.get('preferred_response_time', 'within_24_hours')
        customer_state = request.form.get('customer_state')
        customer_lga = request.form.get('customer_lga')
        customer_address = request.form.get('customer_address')
        related_service = request.form.get('related_service')
        
        # Validate required fields
        if not all([request_type_id, subject, description, customer_name, customer_email]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('services.service_request_form'))
        
        # Create service request
        service_request = ServiceRequest(
            request_type_id=request_type_id,
            subject=subject,
            description=description,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            preferred_contact_method=preferred_contact_method,
            urgency=urgency,
            preferred_response_time=preferred_response_time,
            customer_state=customer_state,
            customer_city=customer_lga,
            customer_address=customer_address,
            related_service=related_service,
            source_channel='web',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        # If user is logged in, associate with their account
        # For now, we'll handle anonymous requests
        
        db.session.add(service_request)
        db.session.commit()
        
        flash(f'Your service request has been submitted successfully! Reference number: {service_request.request_number}', 'success')
        return redirect(url_for('services.service_request_success', request_number=service_request.request_number))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while submitting your request. Please try again.', 'error')
        return redirect(url_for('services.service_request_form'))

@services_bp.route('/request/success/<request_number>')
def service_request_success(request_number):
    """Service request success page"""
    service_request = ServiceRequest.query.filter_by(request_number=request_number).first_or_404()
    return render_template('services/service_request_success.html', service_request=service_request)

@services_bp.route('/request/track')
def track_request():
    """Track service request status"""
    return render_template('services/track_request.html')

@services_bp.route('/request/track', methods=['POST'])
def track_request_submit():
    """Handle service request tracking"""
    request_number = request.form.get('request_number')
    email = request.form.get('email')
    
    if not request_number:
        flash('Please enter a request number.', 'error')
        return redirect(url_for('services.track_request'))
    
    service_request = ServiceRequest.query.filter_by(request_number=request_number).first()
    
    if not service_request:
        flash('Request not found. Please check your request number.', 'error')
        return redirect(url_for('services.track_request'))
    
    # Optional email verification
    if email and service_request.customer_email.lower() != email.lower():
        flash('Email does not match our records.', 'error')
        return redirect(url_for('services.track_request'))
    
    return render_template('services/request_status.html', service_request=service_request)

# ======================== LOCATION API ROUTES ========================

@services_bp.route('/api/states')
def api_get_states():
    """Get all Nigerian states"""
    states = NigerianState.query.order_by(NigerianState.name).all()
    return jsonify([{
        'id': state.id,
        'name': state.name,
        'code': state.code,
        'zone': state.zone
    } for state in states])

@services_bp.route('/api/states/<int:state_id>/lgas')
def api_get_lgas(state_id):
    """Get local government areas for a specific state"""
    state = NigerianState.query.get_or_404(state_id)
    lgas = LocalGovernment.query.filter_by(state_id=state_id).order_by(LocalGovernment.name).all()
    
    return jsonify([{
        'id': lga.id,
        'name': lga.name,
        'headquarters': lga.headquarters
    } for lga in lgas])

@services_bp.route('/api/request-types')
def api_get_request_types():
    """Get available service request types"""
    request_types = ServiceRequestType.query.filter_by(is_active=True).order_by(ServiceRequestType.display_order, ServiceRequestType.name).all()
    
    return jsonify([{
        'id': rt.id,
        'name': rt.name,
        'description': rt.description,
        'category': rt.category,
        'required_fields': rt.required_fields or [],
        'optional_fields': rt.optional_fields or []
    } for rt in request_types])

# ======================== DATA INITIALIZATION ROUTES ========================

@services_bp.route('/admin/init-locations')
def init_locations():
    """Initialize Nigerian states and LGA data (Admin only)"""
    try:
        # Add states
        for state_data in NIGERIAN_STATES:
            existing_state = NigerianState.query.filter_by(name=state_data['name']).first()
            if not existing_state:
                state = NigerianState(**state_data)
                db.session.add(state)
        
        db.session.commit()
        
        # Add LGAs
        for state_name, lgas_data in LOCAL_GOVERNMENTS.items():
            state = NigerianState.query.filter_by(name=state_name).first()
            if state:
                for lga_data in lgas_data:
                    existing_lga = LocalGovernment.query.filter_by(
                        name=lga_data['name'], 
                        state_id=state.id
                    ).first()
                    if not existing_lga:
                        lga = LocalGovernment(
                            name=lga_data['name'],
                            headquarters=lga_data['headquarters'],
                            state_id=state.id
                        )
                        db.session.add(lga)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': 'Location data initialized successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error', 
            'message': f'Error initializing location data: {str(e)}'
        }), 500

@services_bp.route('/admin/init-request-types')
def init_request_types():
    """Initialize default service request types (Admin only)"""
    try:
        default_request_types = [
            {
                'name': 'General Inquiry',
                'description': 'General questions about our services',
                'category': 'inquiry',
                'related_services': ['general'],
                'required_fields': ['subject', 'description', 'customer_name', 'customer_email'],
                'optional_fields': ['customer_phone', 'preferred_contact_method'],
                'default_priority': 'low',
                'typical_response_time_hours': 24,
                'display_order': 1
            },
            {
                'name': 'Service Quote Request',
                'description': 'Request a quote for any of our services',
                'category': 'quote_request',
                'related_services': ['automobile', 'hotel', 'jewelry', 'logistics', 'creative_services'],
                'required_fields': ['subject', 'description', 'customer_name', 'customer_email', 'customer_phone'],
                'optional_fields': ['customer_address', 'preferred_response_time'],
                'default_priority': 'medium',
                'typical_response_time_hours': 12,
                'display_order': 2
            },
            {
                'name': 'Complaint',
                'description': 'Report an issue with our services',
                'category': 'complaint',
                'related_services': ['automobile', 'hotel', 'jewelry', 'logistics', 'creative_services'],
                'required_fields': ['subject', 'description', 'customer_name', 'customer_email'],
                'optional_fields': ['related_order_number', 'customer_phone'],
                'default_priority': 'high',
                'typical_response_time_hours': 6,
                'escalation_rules': {'auto_escalate_hours': 12},
                'display_order': 3
            },
            {
                'name': 'Technical Support',
                'description': 'Get help with technical issues',
                'category': 'support',
                'related_services': ['creative_services'],
                'required_fields': ['subject', 'description', 'customer_name', 'customer_email'],
                'optional_fields': ['customer_phone', 'urgency'],
                'default_priority': 'medium',
                'typical_response_time_hours': 8,
                'display_order': 4
            },
            {
                'name': 'Partnership Inquiry',
                'description': 'Explore partnership opportunities',
                'category': 'inquiry',
                'related_services': ['general'],
                'required_fields': ['subject', 'description', 'customer_name', 'customer_email', 'customer_phone'],
                'optional_fields': ['customer_address'],
                'default_priority': 'medium',
                'typical_response_time_hours': 48,
                'requires_approval': True,
                'display_order': 5
            }
        ]
        
        for rt_data in default_request_types:
            existing_rt = ServiceRequestType.query.filter_by(name=rt_data['name']).first()
            if not existing_rt:
                request_type = ServiceRequestType(**rt_data)
                db.session.add(request_type)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Service request types initialized successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Error initializing request types: {str(e)}'
        }), 500


# =============================
# AUTOMOBILE SPECIFIC ROUTES
# =============================

@services_bp.route('/automobile/vehicles')
def automobile_vehicles():
    """Vehicle sales page - display all available vehicles"""
    try:
        # Get filter parameters
        make_filter = request.args.get('make', '')
        model_filter = request.args.get('model', '')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        condition = request.args.get('condition', '')
        year_from = request.args.get('year_from', type=int)
        year_to = request.args.get('year_to', type=int)
        
        # Build query
        vehicles_query = Vehicle.query.filter_by(status='available')
        
        # Apply filters
        if make_filter:
            vehicles_query = vehicles_query.join(VehicleModel).join(VehicleMake).filter(
                VehicleMake.name.ilike(f'%{make_filter}%')
            )
        if model_filter:
            vehicles_query = vehicles_query.join(VehicleModel).filter(
                VehicleModel.name.ilike(f'%{model_filter}%')
            )
        if min_price:
            vehicles_query = vehicles_query.filter(Vehicle.selling_price >= min_price)
        if max_price:
            vehicles_query = vehicles_query.filter(Vehicle.selling_price <= max_price)
        if condition:
            vehicles_query = vehicles_query.filter(Vehicle.condition == condition)
        if year_from:
            vehicles_query = vehicles_query.filter(Vehicle.year >= year_from)
        if year_to:
            vehicles_query = vehicles_query.filter(Vehicle.year <= year_to)
        
        vehicles = vehicles_query.order_by(Vehicle.created_at.desc()).all()
        
        # Get all makes for filter dropdown
        makes = VehicleMake.query.filter_by(is_active=True).order_by(VehicleMake.name).all()
        
        return render_template('services/automobile_vehicles.html', 
                             vehicles=vehicles, 
                             makes=makes,
                             filters={
                                 'make': make_filter,
                                 'model': model_filter,
                                 'min_price': min_price,
                                 'max_price': max_price,
                                 'condition': condition,
                                 'year_from': year_from,
                                 'year_to': year_to
                             })
    except Exception as e:
        flash(f'Error loading vehicles: {str(e)}', 'error')
        return render_template('services/automobile_vehicles.html', vehicles=[], makes=[])


@services_bp.route('/automobile/vehicle/<int:vehicle_id>')
def automobile_vehicle_detail(vehicle_id):
    """Vehicle detail page"""
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        # Get related vehicles (same make, different models)
        related_vehicles = Vehicle.query.join(VehicleModel).join(VehicleMake).filter(
            VehicleMake.id == vehicle.model.make.id,
            Vehicle.id != vehicle.id,
            Vehicle.status == 'available'
        ).limit(4).all()
        
        return render_template('services/automobile_vehicle_detail.html', 
                             vehicle=vehicle, 
                             related_vehicles=related_vehicles)
    except Exception as e:
        flash(f'Error loading vehicle details: {str(e)}', 'error')
        return redirect(url_for('services.automobile_vehicles'))


@services_bp.route('/automobile/maintenance/request', methods=['GET', 'POST'])
@login_required
def maintenance_request():
    """Maintenance service request form"""
    if request.method == 'POST':
        try:
            # Generate request number
            request_number = f"MAINT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            maintenance_req = MaintenanceRequest(
                request_number=request_number,
                customer_id=current_user.id,
                vehicle_make=request.form.get('vehicle_make'),
                vehicle_model=request.form.get('vehicle_model'),
                vehicle_year=int(request.form.get('vehicle_year')),
                license_plate=request.form.get('license_plate'),
                mileage=int(request.form.get('mileage', 0)) if request.form.get('mileage') else None,
                service_type=request.form.get('service_type'),
                service_category=request.form.get('service_category'),
                description=request.form.get('description'),
                priority=request.form.get('priority', 'normal'),
                preferred_date=datetime.strptime(request.form.get('preferred_date'), '%Y-%m-%d').date() if request.form.get('preferred_date') else None,
                preferred_time=request.form.get('preferred_time'),
                contact_phone=request.form.get('contact_phone'),
                contact_email=request.form.get('contact_email'),
                pickup_required=bool(request.form.get('pickup_required')),
                pickup_address=request.form.get('pickup_address') if request.form.get('pickup_required') else None
            )
            
            db.session.add(maintenance_req)
            db.session.commit()
            
            flash('Maintenance request submitted successfully! You will be contacted soon.', 'success')
            return redirect(url_for('services.automobile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting request: {str(e)}', 'error')
    
    # Service types for dropdown
    service_types = [
        'Oil Change', 'Brake Service', 'Engine Repair', 'Transmission Service',
        'Air Conditioning', 'Electrical Repair', 'Tire Service', 'Battery Service',
        'Suspension Repair', 'Exhaust System', 'Cooling System', 'Tune-up',
        'Inspection', 'Other'
    ]
    
    return render_template('services/maintenance_request.html', service_types=service_types)


@services_bp.route('/automobile/insurance/request', methods=['GET', 'POST'])
@login_required
def insurance_request():
    """Insurance service request form"""
    if request.method == 'POST':
        try:
            # Generate request number
            request_number = f"INS-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            insurance_req = InsuranceRequest(
                request_number=request_number,
                customer_id=current_user.id,
                vehicle_make=request.form.get('vehicle_make'),
                vehicle_model=request.form.get('vehicle_model'),
                vehicle_year=int(request.form.get('vehicle_year')),
                license_plate=request.form.get('license_plate'),
                vin=request.form.get('vin'),
                vehicle_value=float(request.form.get('vehicle_value')) if request.form.get('vehicle_value') else None,
                insurance_type=request.form.get('insurance_type'),
                coverage_type=request.form.get('coverage_type'),
                current_insurer=request.form.get('current_insurer'),
                current_policy_number=request.form.get('current_policy_number'),
                previous_claims=bool(request.form.get('previous_claims')),
                coverage_amount=float(request.form.get('coverage_amount')) if request.form.get('coverage_amount') else None,
                deductible_preference=float(request.form.get('deductible_preference')) if request.form.get('deductible_preference') else None,
                driver_license_number=request.form.get('driver_license_number'),
                years_of_experience=int(request.form.get('years_of_experience')) if request.form.get('years_of_experience') else None,
                age=int(request.form.get('age')) if request.form.get('age') else None,
                previous_accidents=bool(request.form.get('previous_accidents')),
                accident_details=request.form.get('accident_details') if request.form.get('previous_accidents') else None,
                contact_phone=request.form.get('contact_phone'),
                contact_email=request.form.get('contact_email'),
                preferred_contact_method=request.form.get('preferred_contact_method', 'phone'),
                payment_frequency=request.form.get('payment_frequency')
            )
            
            # Handle additional coverage
            additional_coverage = request.form.getlist('additional_coverage')
            if additional_coverage:
                insurance_req.additional_coverage = additional_coverage
            
            db.session.add(insurance_req)
            db.session.commit()
            
            flash('Insurance request submitted successfully! You will be contacted soon.', 'success')
            return redirect(url_for('services.automobile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting request: {str(e)}', 'error')
    
    return render_template('services/insurance_request.html')


# =============================
# ADMIN/STAFF MANAGEMENT ROUTES
# =============================

@services_bp.route('/admin/vehicles')
@login_required
@staff_required
def admin_vehicles():
    """Admin vehicle management page"""
    vehicles = Vehicle.query.order_by(Vehicle.created_at.desc()).all()
    return render_template('admin/vehicles.html', vehicles=vehicles)


@services_bp.route('/admin/vehicles/add', methods=['GET', 'POST'])
@login_required
@staff_required
def admin_add_vehicle():
    """Add new vehicle"""
    if request.method == 'POST':
        try:
            # Handle file uploads
            uploaded_files = request.files.getlist('photos')
            photo_urls = []
            
            if uploaded_files:
                for file in uploaded_files:
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        # Add timestamp to prevent conflicts
                        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file_path = os.path.join('static/uploads/vehicles', filename)
                        
                        # Ensure directory exists
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        
                        file.save(file_path)
                        photo_urls.append(f'/static/uploads/vehicles/{filename}')
            
            # Handle features as JSON
            features_text = request.form.get('features', '')
            features = [f.strip() for f in features_text.split('\n') if f.strip()] if features_text else []
            
            vehicle = Vehicle(
                vin=request.form.get('vin'),
                stock_number=request.form.get('stock_number'),
                model_id=int(request.form.get('model_id')),
                year=int(request.form.get('year')),
                trim=request.form.get('trim'),
                engine=request.form.get('engine'),
                transmission=request.form.get('transmission'),
                drivetrain=request.form.get('drivetrain'),
                fuel_type=request.form.get('fuel_type'),
                fuel_economy_city=float(request.form.get('fuel_economy_city')) if request.form.get('fuel_economy_city') else None,
                fuel_economy_highway=float(request.form.get('fuel_economy_highway')) if request.form.get('fuel_economy_highway') else None,
                exterior_color=request.form.get('exterior_color'),
                interior_color=request.form.get('interior_color'),
                mileage=int(request.form.get('mileage', 0)),
                msrp=float(request.form.get('msrp')) if request.form.get('msrp') else None,
                selling_price=float(request.form.get('selling_price')),
                cost_price=float(request.form.get('cost_price')) if request.form.get('cost_price') else None,
                condition=request.form.get('condition'),
                features=features,
                description=request.form.get('description'),
                images=photo_urls,
                location=request.form.get('location')
            )
            
            db.session.add(vehicle)
            db.session.commit()
            
            flash('Vehicle added successfully!', 'success')
            return redirect(url_for('services.admin_vehicles'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding vehicle: {str(e)}', 'error')
    
    # Get makes and models for form
    makes = VehicleMake.query.filter_by(is_active=True).order_by(VehicleMake.name).all()
    models = VehicleModel.query.filter_by(is_active=True).order_by(VehicleModel.name).all()
    
    return render_template('admin/add_vehicle.html', makes=makes, models=models)


@services_bp.route('/admin/maintenance-requests')
@login_required
@staff_required
def admin_maintenance_requests():
    """Admin maintenance requests management"""
    status_filter = request.args.get('status', '')
    
    query = MaintenanceRequest.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    requests = query.order_by(MaintenanceRequest.created_at.desc()).all()
    
    return render_template('admin/maintenance_requests.html', 
                         requests=requests, 
                         status_filter=status_filter)


@services_bp.route('/admin/insurance-requests')
@login_required
@staff_required
def admin_insurance_requests():
    """Admin insurance requests management"""
    status_filter = request.args.get('status', '')
    
    query = InsuranceRequest.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    requests = query.order_by(InsuranceRequest.created_at.desc()).all()
    
    return render_template('admin/insurance_requests.html', 
                         requests=requests, 
                         status_filter=status_filter)


@services_bp.route('/admin/maintenance-request/<int:request_id>/update', methods=['POST'])
@login_required
@staff_required
def update_maintenance_request(request_id):
    """Update maintenance request status"""
    try:
        maintenance_req = MaintenanceRequest.query.get_or_404(request_id)
        
        status = request.form.get('status')
        notes = request.form.get('notes')
        estimated_cost = request.form.get('estimated_cost')
        final_cost = request.form.get('final_cost')
        
        if status:
            maintenance_req.status = status
        
        if estimated_cost:
            maintenance_req.estimated_cost = float(estimated_cost)
        
        if final_cost:
            maintenance_req.final_cost = float(final_cost)
        
        # Add progress note
        if notes:
            if not maintenance_req.progress_notes:
                maintenance_req.progress_notes = []
            
            progress_note = {
                'timestamp': datetime.now().isoformat(),
                'staff_id': current_user.id,
                'staff_name': current_user.full_name,
                'note': notes,
                'status': status
            }
            maintenance_req.progress_notes.append(progress_note)
        
        # Assign staff if not already assigned
        if not maintenance_req.assigned_staff_id:
            maintenance_req.assigned_staff_id = current_user.id
        
        # Set completion date if status is completed
        if status == 'completed':
            maintenance_req.completed_at = datetime.now()
        
        db.session.commit()
        
        flash('Maintenance request updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating request: {str(e)}', 'error')
    
    return redirect(url_for('services.admin_maintenance_requests'))


@services_bp.route('/admin/insurance-request/<int:request_id>/update', methods=['POST'])
@login_required
@staff_required
def update_insurance_request(request_id):
    """Update insurance request status"""
    try:
        insurance_req = InsuranceRequest.query.get_or_404(request_id)
        
        status = request.form.get('status')
        notes = request.form.get('notes')
        quoted_premium = request.form.get('quoted_premium')
        final_premium = request.form.get('final_premium')
        policy_number = request.form.get('policy_number')
        
        if status:
            insurance_req.status = status
        
        if quoted_premium:
            insurance_req.quoted_premium = float(quoted_premium)
        
        if final_premium:
            insurance_req.final_premium = float(final_premium)
        
        if policy_number:
            insurance_req.policy_number = policy_number
        
        # Add progress note
        if notes:
            if not insurance_req.progress_notes:
                insurance_req.progress_notes = []
            
            progress_note = {
                'timestamp': datetime.now().isoformat(),
                'staff_id': current_user.id,
                'staff_name': current_user.full_name,
                'note': notes,
                'status': status
            }
            insurance_req.progress_notes.append(progress_note)
        
        # Assign staff if not already assigned
        if not insurance_req.assigned_staff_id:
            insurance_req.assigned_staff_id = current_user.id
        
        # Set dates based on status
        if status == 'quoted' and not insurance_req.quoted_at:
            insurance_req.quoted_at = datetime.now()
        elif status == 'approved' and not insurance_req.approved_at:
            insurance_req.approved_at = datetime.now()
        
        db.session.commit()
        
        flash('Insurance request updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating request: {str(e)}', 'error')
    
    return redirect(url_for('services.admin_insurance_requests'))


# ==================== CREATIVE SERVICES ROUTES ====================

@services_bp.route('/graphic-design/logo-request', methods=['GET', 'POST'])
@login_required
def logo_design_request():
    """Logo design project request"""
    form = LogoDesignForm()
    
    if form.validate_on_submit():
        try:
            # Create creative project
            project = CreativeProject(
                client_id=current_user.id,
                project_title=form.project_title.data,
                project_description=form.project_description.data,
                project_type='logo_design',
                target_audience=form.target_audience.data,
                preferred_colors=form.preferred_colors.data,
                preferred_styles=form.design_style.data,
                deliverables=form.file_formats.data,
                file_formats_required=form.file_formats.data,
                requested_completion_date=form.requested_completion_date.data,
                is_rush_job=form.is_rush_job.data,
                rush_reason=form.rush_reason.data,
                priority_level='high' if form.is_rush_job.data else 'normal',
                client_notes=f"Logo Type: {form.logo_type.data}\n"
                           f"Logo Usage: {', '.join(form.logo_usage.data)}\n"
                           f"Company Description: {form.company_description.data}\n"
                           f"Competitors: {form.competitors.data}\n"
                           f"Budget Range: {form.budget_range.data}\n"
                           f"Additional Notes: {form.additional_notes.data}",
                brand_guidelines=form.brand_guidelines.data
            )
            
            # Set quoted price based on budget range
            budget_mapping = {
                '5000-15000': 15000,
                '15000-30000': 30000,
                '30000-50000': 50000,
                '50000-100000': 100000,
                '100000+': 150000
            }
            project.quoted_price = budget_mapping.get(form.budget_range.data, 50000)
            
            db.session.add(project)
            db.session.commit()
            
            # Handle file uploads if any
            handle_creative_project_files(project, form.reference_files.data)
            
            # Notify admin
            notify_admin_new_creative_project(project)
            
            flash('Your logo design request has been submitted successfully! We will contact you soon.', 'success')
            return redirect(url_for('services.creative_project_success', project_id=project.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting request: {str(e)}', 'error')
    
    return render_template('services/logo_design_request.html', form=form)


@services_bp.route('/graphic-design/branding-request', methods=['GET', 'POST'])
@login_required
def branding_request():
    """Complete branding package request"""
    form = BrandingForm()
    
    if form.validate_on_submit():
        try:
            # Create creative project
            project = CreativeProject(
                client_id=current_user.id,
                project_title=form.project_title.data,
                project_description=form.project_description.data,
                project_type='brand_identity',
                target_audience=form.target_audience.data,
                preferred_colors=form.preferred_colors.data,
                preferred_styles=form.design_style.data,
                deliverables=form.branding_scope.data,
                file_formats_required=form.file_formats.data,
                requested_completion_date=form.requested_completion_date.data,
                is_rush_job=form.is_rush_job.data,
                rush_reason=form.rush_reason.data,
                priority_level='high' if form.is_rush_job.data else 'normal',
                client_notes=f"Branding Scope: {', '.join(form.branding_scope.data)}\n"
                           f"Business Stage: {form.business_stage.data}\n"
                           f"Brand Personality: {', '.join(form.brand_personality.data)}\n"
                           f"Company: {form.company_name.data}\n"
                           f"Industry: {form.industry.data}\n"
                           f"Budget Range: {form.budget_range.data}\n"
                           f"Additional Notes: {form.additional_notes.data}",
                brand_guidelines=form.brand_guidelines.data
            )
            
            # Set quoted price based on scope and budget
            scope_multiplier = len(form.branding_scope.data) * 5000
            budget_mapping = {
                '5000-15000': 25000,
                '15000-30000': 50000,
                '30000-50000': 75000,
                '50000-100000': 125000,
                '100000+': 200000
            }
            base_price = budget_mapping.get(form.budget_range.data, 75000)
            project.quoted_price = base_price + scope_multiplier
            
            db.session.add(project)
            db.session.commit()
            
            # Handle file uploads
            handle_creative_project_files(project, form.reference_files.data)
            
            # Notify admin
            notify_admin_new_creative_project(project)
            
            flash('Your branding package request has been submitted successfully!', 'success')
            return redirect(url_for('services.creative_project_success', project_id=project.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting request: {str(e)}', 'error')
    
    return render_template('services/branding_request.html', form=form)


@services_bp.route('/graphic-design/print-request', methods=['GET', 'POST'])
@login_required
def print_design_request():
    """Print design project request"""
    form = PrintDesignForm()
    
    if form.validate_on_submit():
        try:
            # Create creative project
            project = CreativeProject(
                client_id=current_user.id,
                project_title=form.project_title.data,
                project_description=form.project_description.data,
                project_type=form.print_type.data,
                target_audience=form.target_audience.data,
                preferred_colors=form.preferred_colors.data,
                preferred_styles=form.design_style.data,
                deliverables=form.file_formats.data,
                file_formats_required=form.file_formats.data,
                requested_completion_date=form.requested_completion_date.data,
                is_rush_job=form.is_rush_job.data,
                rush_reason=form.rush_reason.data,
                priority_level='high' if form.is_rush_job.data else 'normal',
                client_notes=f"Print Type: {form.print_type.data}\n"
                           f"Dimensions: {form.print_dimensions.data}\n"
                           f"Quantity: {form.print_quantity.data}\n"
                           f"Print Method: {form.print_method.data}\n"
                           f"Pages: {form.pages_count.data}\n"
                           f"Colors: {form.color_specification.data}\n"
                           f"Company: {form.company_name.data}\n"
                           f"Industry: {form.industry.data}\n"
                           f"Budget Range: {form.budget_range.data}\n"
                           f"Additional Notes: {form.additional_notes.data}",
                brand_guidelines=form.brand_guidelines.data
            )
            
            # Set quoted price based on type and complexity
            type_pricing = {
                'business_card': 8000,
                'flyer': 12000,
                'brochure': 20000,
                'poster': 15000,
                'banner': 25000,
                'catalog': 50000,
                'annual_report': 100000,
                'magazine': 75000,
                'packaging': 40000,
                'menu': 18000,
                'invitation': 15000
            }
            base_price = type_pricing.get(form.print_type.data, 20000)
            
            # Apply multipliers
            if form.pages_count.data and form.pages_count.data > 1:
                base_price *= form.pages_count.data
            if form.print_quantity.data and form.print_quantity.data > 500:
                base_price *= 1.2
                
            project.quoted_price = base_price
            
            db.session.add(project)
            db.session.commit()
            
            # Handle file uploads
            handle_creative_project_files(project, form.reference_files.data)
            
            # Notify admin
            notify_admin_new_creative_project(project)
            
            flash('Your print design request has been submitted successfully!', 'success')
            return redirect(url_for('services.creative_project_success', project_id=project.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting request: {str(e)}', 'error')
    
    return render_template('services/print_design_request.html', form=form)


@services_bp.route('/graphic-design/digital-request', methods=['GET', 'POST'])
@login_required
def digital_design_request():
    """Digital design project request"""
    form = DigitalDesignForm()
    
    if form.validate_on_submit():
        try:
            # Create creative project
            project = CreativeProject(
                client_id=current_user.id,
                project_title=form.project_title.data,
                project_description=form.project_description.data,
                project_type=form.digital_type.data,
                target_audience=form.target_audience.data,
                preferred_colors=form.preferred_colors.data,
                preferred_styles=form.design_style.data,
                deliverables=form.file_formats.data,
                file_formats_required=form.file_formats.data,
                requested_completion_date=form.requested_completion_date.data,
                is_rush_job=form.is_rush_job.data,
                rush_reason=form.rush_reason.data,
                priority_level='high' if form.is_rush_job.data else 'normal',
                client_notes=f"Digital Type: {form.digital_type.data}\n"
                           f"Platforms: {', '.join(form.digital_platforms.data)}\n"
                           f"Dimensions: {', '.join(form.dimensions_needed.data)}\n"
                           f"Animation Needed: {'Yes' if form.animation_needed.data else 'No'}\n"
                           f"Content Provider: {form.content_provided.data}\n"
                           f"Company: {form.company_name.data}\n"
                           f"Industry: {form.industry.data}\n"
                           f"Budget Range: {form.budget_range.data}\n"
                           f"Additional Notes: {form.additional_notes.data}",
                brand_guidelines=form.brand_guidelines.data
            )
            
            # Set quoted price based on digital type and features
            type_pricing = {
                'social_media': 8000,
                'web_banner': 12000,
                'email_template': 15000,
                'presentation': 25000,
                'infographic': 30000,
                'digital_ad': 18000,
                'app_graphics': 35000,
                'web_graphics': 20000
            }
            base_price = type_pricing.get(form.digital_type.data, 15000)
            
            # Apply multipliers for additional features
            platform_count = len(form.digital_platforms.data)
            dimension_count = len(form.dimensions_needed.data)
            
            if platform_count > 2:
                base_price *= 1.3
            if dimension_count > 3:
                base_price *= 1.2
            if form.animation_needed.data:
                base_price *= 1.5
                
            project.quoted_price = base_price
            
            db.session.add(project)
            db.session.commit()
            
            # Handle file uploads
            handle_creative_project_files(project, form.reference_files.data)
            
            # Notify admin
            notify_admin_new_creative_project(project)
            
            flash('Your digital design request has been submitted successfully!', 'success')
            return redirect(url_for('services.creative_project_success', project_id=project.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting request: {str(e)}', 'error')
    
    return render_template('services/digital_design_request.html', form=form)


@services_bp.route('/web-design/website-request', methods=['GET', 'POST'])
@login_required
def website_design_request():
    """Website design project request"""
    form = WebsiteDesignForm()
    
    if form.validate_on_submit():
        try:
            # Create website project
            website_project = WebsiteProject(
                client_id=current_user.id,
                website_name=form.website_name.data,
                project_description=form.website_description.data,
                website_type=form.website_type.data,
                domain_name=form.domain_name.data,
                existing_website=form.existing_website.data,
                features_required=form.website_features.data,
                estimated_pages=form.page_count.data,
                content_ready=form.content_ready.data == 'ready',
                mobile_responsive=form.mobile_responsive.data,
                seo_optimization=form.seo_optimization.data,
                requested_completion_date=form.launch_date.data,
                maintenance_included=form.maintenance_needed.data == 'yes',
                client_notes=f"Website Type: {form.website_type.data}\n"
                           f"Features: {', '.join(form.website_features.data)}\n"
                           f"E-commerce Products: {form.ecommerce_products.data}\n"
                           f"Payment Methods: {', '.join(form.payment_methods.data or [])}\n"
                           f"Content Status: {form.content_ready.data}\n"
                           f"Design Inspiration: {form.design_inspiration.data}\n"
                           f"Colors: {form.color_scheme.data}\n"
                           f"Budget Range: {form.budget_range.data}\n"
                           f"Hosting Help: {'Yes' if form.hosting_help.data else 'No'}\n"
                           f"Training Needed: {'Yes' if form.training_needed.data else 'No'}\n"
                           f"Additional Notes: {form.additional_notes.data}"
            )
            
            # Set quoted price based on complexity
            budget_mapping = {
                '50000-100000': 100000,
                '100000-200000': 200000,
                '200000-500000': 500000,
                '500000-1000000': 1000000,
                '1000000+': 1500000
            }
            base_price = budget_mapping.get(form.budget_range.data, 200000)
            
            # Adjust price based on features
            feature_count = len(form.website_features.data)
            if feature_count > 5:
                base_price *= 1.2
            if form.ecommerce_products.data and form.ecommerce_products.data > 50:
                base_price *= 1.3
            if form.website_type.data == 'ecommerce':
                base_price *= 1.4
                
            website_project.quoted_price = base_price
            
            db.session.add(website_project)
            db.session.commit()
            
            # Notify admin
            notify_admin_new_website_project(website_project)
            
            flash('Your website design request has been submitted successfully!', 'success')
            return redirect(url_for('services.website_project_success', project_id=website_project.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting request: {str(e)}', 'error')
    
    return render_template('services/website_design_request.html', form=form)


@services_bp.route('/creative/quick-quote', methods=['GET', 'POST'])
@login_required
def creative_quick_quote():
    """Quick quote for simple design services"""
    form = QuickQuoteForm()
    
    if form.validate_on_submit():
        try:
            # Create simple creative project
            project = CreativeProject(
                client_id=current_user.id,
                project_title=f"{form.service_type.data.replace('_', ' ').title()} Project",
                project_description=form.project_description.data,
                project_type=form.service_type.data,
                requested_completion_date=datetime.now().date() + timedelta(days=int(form.timeline.data.split('-')[0]) if '-' in form.timeline.data else 7),
                client_notes=f"Timeline: {form.timeline.data}\n"
                           f"Budget Range: {form.budget.data}\n"
                           f"Contact Method: {form.contact_method.data}",
                priority_level='normal'
            )
            
            # Set quoted price based on service type and budget
            budget_mapping = {
                '5000-15000': 15000,
                '15000-30000': 30000,
                '30000-50000': 50000,
                '50000+': 75000
            }
            project.quoted_price = budget_mapping.get(form.budget.data, 25000)
            
            db.session.add(project)
            db.session.commit()
            
            # Notify admin
            notify_admin_new_creative_project(project)
            
            flash('Your quick quote request has been submitted! We will contact you soon.', 'success')
            return redirect(url_for('services.creative_project_success', project_id=project.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting request: {str(e)}', 'error')
    
    return render_template('services/creative_quick_quote.html', form=form)


@services_bp.route('/creative/project-success/<int:project_id>')
@login_required
def creative_project_success(project_id):
    """Success page for creative projects"""
    try:
        project = CreativeProject.query.filter_by(id=project_id, client_id=current_user.id).first_or_404()
        return render_template('services/creative_project_success.html', project=project)
    except Exception as e:
        flash('Project not found.', 'error')
        return redirect(url_for('services.graphic_design'))


@services_bp.route('/website/project-success/<int:project_id>')
@login_required
def website_project_success(project_id):
    """Success page for website projects"""
    try:
        project = WebsiteProject.query.filter_by(id=project_id, client_id=current_user.id).first_or_404()
        return render_template('services/website_project_success.html', project=project)
    except Exception as e:
        flash('Project not found.', 'error')
        return redirect(url_for('services.web_design'))


def handle_creative_project_files(project, files):
    """Handle file uploads for creative projects"""
    try:
        if not files:
            return
            
        upload_folder = os.path.join('static', 'uploads', 'creative_projects', str(project.id))
        os.makedirs(upload_folder, exist_ok=True)
        
        uploaded_files = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Add timestamp to prevent naming conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                uploaded_files.append({
                    'filename': filename,
                    'path': file_path,
                    'size': os.path.getsize(file_path)
                })
        
        # Update project with file information
        if uploaded_files:
            project.reference_materials = uploaded_files
            db.session.commit()
            
    except Exception as e:
        print(f"Error handling file uploads: {str(e)}")


def notify_admin_new_creative_project(project):
    """Send notification to admin about new creative project"""
    try:
        from models.admin import AdminNotification
        from models.user import User
        
        # Get all admin and staff users
        admin_users = User.query.filter(
            (User.role == 'admin') | (User.role == 'staff')
        ).all()
        
        project_type_display = project.project_type.replace('_', ' ').title()
        
        # Create notification for each admin/staff
        for admin in admin_users:
            notification = AdminNotification(
                user_id=admin.id,
                title=f"New {project_type_display} Project",
                message=f"A new creative project has been submitted by {project.client.full_name}. "
                       f"Project: {project.project_title} ({project.project_number})",
                notification_type='creative_project',
                priority='normal',
                related_model='CreativeProject',
                related_id=project.id
            )
            db.session.add(notification)
        
        db.session.commit()
        
    except Exception as e:
        print(f"Error sending admin notification: {str(e)}")


def notify_admin_new_website_project(project):
    """Send notification to admin about new website project"""
    try:
        from models.admin import AdminNotification
        from models.user import User
        
        # Get all admin and staff users
        admin_users = User.query.filter(
            (User.role == 'admin') | (User.role == 'staff')
        ).all()
        
        # Create notification for each admin/staff
        for admin in admin_users:
            notification = AdminNotification(
                user_id=admin.id,
                title=f"New Website Project",
                message=f"A new website project has been submitted by {project.client.full_name}. "
                       f"Website: {project.website_name} ({project.project_number})",
                notification_type='website_project',
                priority='normal',
                related_model='WebsiteProject',
                related_id=project.id
            )
            db.session.add(notification)
        
        db.session.commit()
        
    except Exception as e:
        print(f"Error sending admin notification: {str(e)}")


def notify_admin_new_logistics_quote(quote_request):
    """Send notification to admin and staff about new logistics quote request"""
    try:
        from models.admin import AdminNotification
        from models.user import User
        
        # Get all admin and staff users
        admin_users = User.query.filter(
            (User.role == 'admin') | (User.role == 'staff')
        ).all()
        
        service_type_display = quote_request.service_type.replace('_', ' ').title()
        
        # Create notification for each admin/staff
        for admin in admin_users:
            notification = AdminNotification(
                user_id=admin.id,
                title=f"New {service_type_display} Quote Request",
                message=f"A new quote request has been submitted by {quote_request.customer_name} "
                       f"for {service_type_display}. Quote number: {quote_request.quote_number}",
                notification_type='logistics_quote',
                priority='normal',
                related_model='LogisticsQuoteRequest',
                related_id=quote_request.id
            )
            db.session.add(notification)
        
        db.session.commit()
        
        # You can also add email notification here if needed
        # send_email_notification(admin_users, quote_request)
        
    except Exception as e:
        print(f"Error sending admin notification: {str(e)}")
        # Don't let notification errors break the main flow


# ==============================================================================
# MISSING SERVICE ROUTES - SECURITY, DOCUMENTS, ETC.
# ==============================================================================

@services_bp.route('/security')
def security_services():
    """Security services overview and booking"""
    return render_template('services/security.html')

@services_bp.route('/security/book/<service_type>')
def security_book_service(service_type):
    """Book security service"""
    service_types = {
        'personal': 'Personal Security',
        'property': 'Property Protection', 
        'surveillance': 'Surveillance Systems',
        'event': 'Event Security'
    }
    
    if service_type not in service_types:
        flash('Invalid security service type.', 'error')
        return redirect(url_for('services.security_services'))
    
    return render_template('services/security_booking.html', 
                         service_type=service_type,
                         service_name=service_types[service_type])

@services_bp.route('/security/book/<service_type>', methods=['POST'])
@login_required
def security_book_service_post(service_type):
    """Process security service booking"""
    try:
        # Create a general service request for security
        service_request = ServiceRequest(
            customer_id=current_user.id,
            request_type_id=1,  # General service request type
            subject=f"Security Service Request - {service_type.title()}",
            description=request.form.get('description', ''),
            related_service='security',
            customer_name=current_user.full_name,
            customer_email=current_user.email,
            customer_phone=request.form.get('phone'),
            customer_state=request.form.get('state'),
            customer_city=request.form.get('city'),
            customer_address=request.form.get('address'),
            urgency=request.form.get('urgency', 'medium'),
            form_data={
                'service_type': service_type,
                'start_date': request.form.get('start_date'),
                'duration': request.form.get('duration'),
                'location': request.form.get('location'),
                'special_requirements': request.form.get('special_requirements')
            }
        )
        
        db.session.add(service_request)
        db.session.commit()
        
        # Assign to admin/staff
        assign_to_admin_and_staff(service_request)
        
        flash('Security service request submitted successfully!', 'success')
        return redirect(url_for('services.request_success', request_number=service_request.request_number))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting request: {str(e)}', 'error')
        return redirect(url_for('services.security_book_service', service_type=service_type))

@services_bp.route('/documents')
def document_services():
    """Document services overview"""
    return render_template('services/documents.html')

@services_bp.route('/documents/request/<service_type>')
def document_request_service(service_type):
    """Request document service"""
    service_types = {
        'visa': 'Visa Application Assistance',
        'legal': 'Legal Document Preparation',
        'notarization': 'Notarization Services',
        'certification': 'Document Certification'
    }
    
    if service_type not in service_types:
        flash('Invalid document service type.', 'error')
        return redirect(url_for('services.document_services'))
    
    return render_template('services/document_request.html',
                         service_type=service_type,
                         service_name=service_types[service_type])

@services_bp.route('/documents/request/<service_type>', methods=['POST'])
@login_required
def document_request_service_post(service_type):
    """Process document service request"""
    try:
        service_request = ServiceRequest(
            customer_id=current_user.id,
            request_type_id=1,
            subject=f"Document Service Request - {service_type.title()}",
            description=request.form.get('description', ''),
            related_service='documents',
            customer_name=current_user.full_name,
            customer_email=current_user.email,
            customer_phone=request.form.get('phone'),
            customer_state=request.form.get('state'),
            customer_city=request.form.get('city'),
            urgency=request.form.get('urgency', 'medium'),
            form_data={
                'service_type': service_type,
                'document_type': request.form.get('document_type'),
                'deadline': request.form.get('deadline'),
                'special_instructions': request.form.get('special_instructions')
            }
        )
        
        db.session.add(service_request)
        db.session.commit()
        
        # Assign to admin/staff
        assign_to_admin_and_staff(service_request)
        
        flash('Document service request submitted successfully!', 'success')
        return redirect(url_for('services.request_success', request_number=service_request.request_number))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting request: {str(e)}', 'error')
        return redirect(url_for('services.document_request_service', service_type=service_type))

@services_bp.route('/creative')
def creative_services():
    """Creative services overview (combining graphic design and web design)"""
    return render_template('services/creative.html')

@services_bp.route('/creative/request/<service_type>')
def creative_request_service(service_type):
    """Request creative service"""
    service_types = {
        'graphic_design': 'Graphic Design',
        'logo_design': 'Logo Design',
        'branding': 'Brand Identity',
        'web_design': 'Website Design',
        'web_development': 'Web Development',
        'print_design': 'Print Design'
    }
    
    if service_type not in service_types:
        flash('Invalid creative service type.', 'error')
        return redirect(url_for('services.creative_services'))
    
    return render_template('services/creative_request.html',
                         service_type=service_type,
                         service_name=service_types[service_type])

@services_bp.route('/creative/request/<service_type>', methods=['POST'])
@login_required
def creative_request_service_post(service_type):
    """Process creative service request"""
    try:
        service_request = ServiceRequest(
            customer_id=current_user.id,
            request_type_id=1,
            subject=f"Creative Service Request - {service_type.replace('_', ' ').title()}",
            description=request.form.get('description', ''),
            related_service='creative',
            customer_name=current_user.full_name,
            customer_email=current_user.email,
            customer_phone=request.form.get('phone'),
            urgency=request.form.get('urgency', 'medium'),
            form_data={
                'service_type': service_type,
                'project_scope': request.form.get('project_scope'),
                'timeline': request.form.get('timeline'),
                'budget_range': request.form.get('budget_range'),
                'design_preferences': request.form.get('design_preferences'),
                'target_audience': request.form.get('target_audience')
            }
        )
        
        db.session.add(service_request)
        db.session.commit()
        
        # Assign to admin/staff
        assign_to_admin_and_staff(service_request)
        
        flash('Creative service request submitted successfully!', 'success')
        return redirect(url_for('services.request_success', request_number=service_request.request_number))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting request: {str(e)}', 'error')
        return redirect(url_for('services.creative_request_service', service_type=service_type))


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def assign_to_admin_and_staff(service_request):
    """Assign service request to admin and staff for processing"""
    try:
        from models.user import User
        from models.admin import AdminNotification
        
        # Get admin and staff users
        admin_staff_users = User.query.filter(
            User.role.in_(['admin', 'staff'])
        ).all()
        
        if admin_staff_users:
            # Assign to first available admin or staff
            service_request.assigned_to_id = admin_staff_users[0].id
            service_request.assigned_department = 'Customer Service'
            service_request.assigned_at = datetime.utcnow()
            service_request.status = 'assigned'
            
            # Create notifications for all admin/staff
            for user in admin_staff_users:
                try:
                    notification = AdminNotification(
                        user_id=user.id,
                        title=f"New Service Request: {service_request.subject}",
                        message=f"Customer {service_request.customer_name} has submitted a new {service_request.related_service} service request. Request #{service_request.request_number}",
                        notification_type='service_request',
                        priority='normal',
                        related_model='ServiceRequest',
                        related_id=service_request.id
                    )
                    db.session.add(notification)
                except Exception as e:
                    print(f"Error creating notification for user {user.id}: {str(e)}")
                    continue
            
            db.session.commit()
            
    except Exception as e:
        print(f"Error assigning to admin and staff: {str(e)}")
        # Don't break the flow if assignment fails

@services_bp.route('/inventory/create-sample-data')
@admin_required
def create_sample_inventory():
    """Create sample inventory data for testing"""
    try:
        # Check if we already have data
        if InventoryItem.query.count() > 0:
            return jsonify({'message': 'Sample data already exists'})
        
        # Create sample locations if they don't exist
        locations = [
            {'name': 'Main Warehouse', 'address': 'Lagos Main Store', 'is_active': True},
            {'name': 'Abuja Branch', 'address': 'Abuja Showroom', 'is_active': True},
            {'name': 'Port Harcourt Store', 'address': 'PH Sales Center', 'is_active': True}
        ]
        
        for loc_data in locations:
            if not InventoryLocation.query.filter_by(name=loc_data['name']).first():
                location = InventoryLocation(**loc_data)
                db.session.add(location)
        
        db.session.commit()
        
        # Create sample products if they don't exist
        from models.ecommerce import ProductCategory, ProductBrand
        
        # Create categories
        categories = ['Electronics', 'Gadgets', 'Accessories']
        for cat_name in categories:
            if not ProductCategory.query.filter_by(name=cat_name).first():
                category = ProductCategory(name=cat_name, description=f'{cat_name} category')
                db.session.add(category)
        
        db.session.commit()
        
        # Create sample products
        electronics_cat = ProductCategory.query.filter_by(name='Electronics').first()
        main_location = InventoryLocation.query.filter_by(name='Main Warehouse').first()
        
        if electronics_cat and main_location:
            sample_products = [
                {
                    'name': 'Samsung Galaxy S23',
                    'description': 'Latest Samsung smartphone with advanced features',
                    'sku': 'SAMSUNG-S23-001',
                    'price': 450000.00,
                    'category_id': electronics_cat.id,
                    'stock_quantity': 25
                },
                {
                    'name': 'iPhone 15 Pro',
                    'description': 'Apple iPhone 15 Pro with titanium design',
                    'sku': 'IPHONE-15P-001',
                    'price': 750000.00,
                    'category_id': electronics_cat.id,
                    'stock_quantity': 15
                },
                {
                    'name': 'MacBook Air M2',
                    'description': 'Apple MacBook Air with M2 chip',
                    'sku': 'MBA-M2-001',
                    'price': 850000.00,
                    'category_id': electronics_cat.id,
                    'stock_quantity': 8
                }
            ]
            
            for prod_data in sample_products:
                if not Product.query.filter_by(sku=prod_data['sku']).first():
                    product = Product(**prod_data)
                    db.session.add(product)
                    db.session.flush()  # Get the ID
                    
                    # Create inventory item
                    inventory_item = InventoryItem(
                        product_id=product.id,
                        location_id=main_location.id,
                        current_stock=prod_data['stock_quantity'],
                        available_stock=prod_data['stock_quantity'],
                        reorder_point=5,
                        unit_cost=prod_data['price'] * 0.7,  # 70% of selling price
                        total_value=prod_data['price'] * prod_data['stock_quantity'],
                        status='active'
                    )
                    db.session.add(inventory_item)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Sample inventory data created successfully',
            'items_created': InventoryItem.query.count()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'Failed to create sample data'
        })

@services_bp.route('/inventory/test')
def inventory_test():
    """Test inventory database connection"""
    try:
        # Check if we have any inventory items
        item_count = InventoryItem.query.count()
        location_count = InventoryLocation.query.count()
        product_count = Product.query.count()
        
        return jsonify({
            'status': 'success',
            'inventory_items': item_count,
            'locations': location_count,
            'products': product_count,
            'message': 'Database connection working properly'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'Database connection failed'
        })

@services_bp.route('/inventory')
def inventory():
    """Public inventory view for customers"""
    try:
        # Get filter parameters
        category = request.args.get('category', '')
        location_id = request.args.get('location_id', type=int)
        search = request.args.get('search', '')
        in_stock_only = request.args.get('in_stock_only', '1') == '1'
        
        # Build query with proper joins to get product/item details
        query = db.session.query(InventoryItem).join(
            InventoryLocation, InventoryItem.location_id == InventoryLocation.id
        ).filter(InventoryItem.status == 'active')
        
        if in_stock_only:
            query = query.filter(InventoryItem.current_stock > 0)
            
        if location_id:
            query = query.filter(InventoryItem.location_id == location_id)
            
        # Handle search and category filtering with joins
        if search or category:
            # Add subqueries for different item types
            from models.ecommerce import Product, ProductCategory
            
            product_conditions = []
            if search:
                product_conditions.extend([
                    Product.name.ilike(f'%{search}%'),
                    Product.sku.ilike(f'%{search}%'),
                    Product.description.ilike(f'%{search}%')
                ])
            if category:
                query = query.outerjoin(Product).outerjoin(ProductCategory)
                product_conditions.append(ProductCategory.name.ilike(f'%{category}%'))
            
            if product_conditions:
                query = query.outerjoin(Product).filter(
                    db.or_(*product_conditions)
                )
        
        items = query.order_by(InventoryItem.id).all()
        
        # Get categories from products for filters
        categories = []
        try:
            from models.ecommerce import ProductCategory
            product_categories = db.session.query(ProductCategory.name).join(
                Product
            ).join(InventoryItem).filter(
                InventoryItem.status == 'active'
            ).distinct().all()
            categories = [cat[0] for cat in product_categories if cat[0]]
        except:
            pass
        
        locations = InventoryLocation.query.filter_by(is_active=True).all()
        
        return render_template('services/inventory.html',
                             items=items,
                             categories=categories,
                             locations=locations,
                             current_category=category,
                             current_location=location_id,
                             current_search=search,
                             in_stock_only=in_stock_only)
        
    except Exception as e:
        flash(f'Error loading inventory: {str(e)}', 'error')
        # If inventory models don't exist, show empty page
        return render_template('services/inventory.html',
                             items=[],
                             categories=[],
                             locations=[],
                             current_category='',
                             current_location=None,
                             current_search='',
                             in_stock_only=True,
                             error=str(e))

@services_bp.route('/inventory/request', methods=['POST'])
@login_required
def request_inventory_item():
    """Request an inventory item"""
    try:
        from models.inventory import InventoryItem
        
        item_id = request.form.get('item_id', type=int)
        quantity = request.form.get('quantity', type=int)
        purpose = request.form.get('purpose')
        urgency = request.form.get('urgency')
        
        if not all([item_id, quantity, purpose, urgency]):
            flash('All fields are required', 'error')
            return redirect(url_for('services.inventory'))
        
        item = InventoryItem.query.get_or_404(item_id)
        
        if item.current_stock < quantity:
            flash(f'Insufficient stock. Only {item.current_stock} units available.', 'error')
            return redirect(url_for('services.inventory'))
        
        # Get or create a service request type for inventory requests
        inventory_request_type = ServiceRequestType.query.filter_by(name='Inventory Request').first()
        if not inventory_request_type:
            inventory_request_type = ServiceRequestType(
                name='Inventory Request',
                description='Request for inventory items and stock',
                category='inventory',
                related_services=['inventory', 'gadgets', 'ecommerce'],
                default_priority='medium',
                is_active=True
            )
            db.session.add(inventory_request_type)
            db.session.flush()  # Get the ID before using it

        # Create a service request for the inventory item
        service_request = ServiceRequest(
            request_number=ServiceRequest.generate_request_number(),
            customer_id=current_user.id,
            request_type_id=inventory_request_type.id,
            subject=f'Inventory Request: {item.get_item_name()}',
            description=f'Request for {quantity} units of {item.get_item_name()} - {purpose}',
            related_service='inventory',
            related_service_id=item_id,
            customer_name=current_user.full_name,
            customer_email=current_user.email,
            customer_phone=getattr(current_user, 'phone', ''),
            urgency=urgency,
            form_data={
                'item_id': item_id,
                'item_name': item.get_item_name(),
                'item_sku': item.get_item_sku(),
                'quantity_requested': quantity,
                'purpose': purpose,
                'unit_price': float(item.get_item_price()) if item.get_item_price() else 0,
                'total_estimated_cost': float(item.get_item_price() * quantity) if item.get_item_price() else 0
            }
        )
        
        db.session.add(service_request)
        db.session.commit()
        
        flash(f'Your request for {quantity} units of "{item.get_item_name()}" has been submitted successfully!', 'success')
        return redirect(url_for('services.inventory'))
        
    except Exception as e:
        flash(f'Error submitting request: {str(e)}', 'error')
        return redirect(url_for('services.inventory'))