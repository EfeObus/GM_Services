"""
Hotel Service Request Forms
Forms for hotel operations management, booking system, and staff training requests
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, DateField, BooleanField, FieldList, FormField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange
from wtforms.widgets import CheckboxInput, ListWidget

class MultiCheckboxField(SelectField):
    """
    A multiple-select, except displays a list of checkboxes.
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class HotelServiceRequestForm(FlaskForm):
    """Base form for hotel service requests"""
    
    # Client Information
    client_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=200)])
    client_email = StringField('Email Address', validators=[DataRequired(), Email()])
    client_phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    company_name = StringField('Company/Hotel Name', validators=[Optional(), Length(max=200)])
    
    # Hotel Details
    hotel_name = StringField('Hotel Name', validators=[Optional(), Length(max=200)])
    hotel_location = StringField('Hotel Location', validators=[Optional(), Length(max=200)])
    hotel_size = SelectField('Hotel Size', choices=[
        ('', 'Select hotel size'),
        ('small', 'Small (1-50 rooms)'),
        ('medium', 'Medium (51-200 rooms)'),
        ('large', 'Large (200+ rooms)')
    ], validators=[Optional()])
    
    # Service Details
    specific_requirements = TextAreaField('Specific Requirements', 
                                        validators=[DataRequired(), Length(min=10, max=2000)],
                                        description='Please describe your specific needs and requirements')
    budget_range = SelectField('Budget Range', choices=[
        ('', 'Select budget range'),
        ('under_100k', 'Under ₦100,000'),
        ('100k_500k', '₦100,000 - ₦500,000'),
        ('500k_1m', '₦500,000 - ₦1,000,000'),
        ('1m_5m', '₦1,000,000 - ₦5,000,000'),
        ('above_5m', 'Above ₦5,000,000'),
        ('custom', 'Custom (will discuss)')
    ], validators=[Optional()])
    
    timeline = SelectField('Expected Timeline', choices=[
        ('', 'Select timeline'),
        ('immediate', 'Immediate (within 1 week)'),
        ('1_month', 'Within 1 month'),
        ('3_months', 'Within 3 months'),
        ('6_months', 'Within 6 months'),
        ('flexible', 'Flexible timeline')
    ], validators=[Optional()])
    
    priority_level = SelectField('Priority Level', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium', validators=[DataRequired()])

class OperationsManagementForm(HotelServiceRequestForm):
    """Form for operations management requests"""
    
    current_management_system = StringField('Current Management System', 
                                          validators=[Optional(), Length(max=200)],
                                          description='What system do you currently use?')
    
    current_operations_challenges = TextAreaField('Current Operational Challenges',
                                                validators=[Optional(), Length(max=1000)],
                                                description='What challenges are you facing with current operations?')
    
    departments_to_manage = MultiCheckboxField('Departments to Manage', choices=[
        ('front_desk', 'Front Desk Operations'),
        ('housekeeping', 'Housekeeping'),
        ('maintenance', 'Maintenance'),
        ('guest_services', 'Guest Services'),
        ('food_beverage', 'Food & Beverage'),
        ('security', 'Security'),
        ('accounting', 'Accounting/Finance'),
        ('marketing', 'Marketing'),
        ('hr', 'Human Resources'),
        ('all', 'All Departments')
    ], description='Select all departments that need management')
    
    quality_standards_required = TextAreaField('Quality Standards Required',
                                             validators=[Optional(), Length(max=1000)],
                                             description='Any specific quality standards or certifications needed?')

class BookingSystemForm(HotelServiceRequestForm):
    """Form for booking system requests"""
    
    current_booking_system = StringField('Current Booking System',
                                       validators=[Optional(), Length(max=200)],
                                       description='What booking system do you currently use?')
    
    integration_requirements = TextAreaField('Integration Requirements',
                                           validators=[Optional(), Length(max=1000)],
                                           description='Do you need integration with other systems? (PMS, Channel Manager, etc.)')
    
    expected_monthly_bookings = IntegerField('Expected Monthly Bookings',
                                           validators=[Optional(), NumberRange(min=1, max=10000)],
                                           description='Approximately how many bookings do you expect per month?')
    
    channel_management_needed = BooleanField('Channel Management Needed',
                                           description='Do you need management of multiple booking channels?')
    
    payment_gateway_needed = BooleanField('Payment Gateway Integration',
                                        description='Do you need payment processing integration?')
    
    reporting_requirements = TextAreaField('Reporting Requirements',
                                         validators=[Optional(), Length(max=1000)],
                                         description='What kind of reports and analytics do you need?')

class StaffTrainingForm(HotelServiceRequestForm):
    """Form for staff training requests"""
    
    number_of_staff = IntegerField('Number of Staff to Train',
                                 validators=[DataRequired(), NumberRange(min=1, max=1000)],
                                 description='How many staff members need training?')
    
    current_skill_level = SelectField('Current Skill Level', choices=[
        ('', 'Select current skill level'),
        ('beginner', 'Beginner (New to hospitality)'),
        ('intermediate', 'Intermediate (Some experience)'),
        ('advanced', 'Advanced (Experienced)')
    ], validators=[DataRequired()])
    
    training_areas = MultiCheckboxField('Training Areas Needed', choices=[
        ('customer_service', 'Customer Service Excellence'),
        ('front_desk', 'Front Desk Operations'),
        ('housekeeping', 'Housekeeping Standards'),
        ('food_service', 'Food & Beverage Service'),
        ('sales', 'Sales & Marketing'),
        ('management', 'Management & Leadership'),
        ('safety', 'Safety & Emergency Procedures'),
        ('technology', 'Hotel Technology Systems'),
        ('communication', 'Communication Skills'),
        ('problem_solving', 'Problem Solving'),
        ('cultural_sensitivity', 'Cultural Sensitivity'),
        ('upselling', 'Upselling Techniques'),
        ('all', 'Comprehensive Training Program')
    ], validators=[DataRequired()], description='Select all areas where training is needed')
    
    certification_needed = BooleanField('Certification Required',
                                      description='Do you need certified training programs?')
    
    on_site_training = BooleanField('On-site Training Preferred',
                                  description='Do you prefer training at your location?')
    
    training_schedule_preference = SelectField('Training Schedule Preference', choices=[
        ('', 'Select schedule preference'),
        ('weekdays', 'Weekdays only'),
        ('weekends', 'Weekends only'),
        ('flexible', 'Flexible schedule'),
        ('intensive', 'Intensive (short duration)'),
        ('extended', 'Extended (spread over weeks)')
    ], validators=[Optional()])
    
    current_training_programs = TextAreaField('Current Training Programs',
                                            validators=[Optional(), Length(max=1000)],
                                            description='What training programs do you currently have in place?')

class HotelConsultationForm(FlaskForm):
    """Form for requesting hotel consultation"""
    
    # Client Information
    client_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=200)])
    client_email = StringField('Email Address', validators=[DataRequired(), Email()])
    client_phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    company_name = StringField('Company/Hotel Name', validators=[Optional(), Length(max=200)])
    
    # Consultation Details
    consultation_type = SelectField('Consultation Type', choices=[
        ('', 'Select consultation type'),
        ('operations_management', 'Operations Management'),
        ('booking_system', 'Booking System'),
        ('staff_training', 'Staff Training'),
        ('general', 'General Hotel Management'),
        ('all', 'Comprehensive Assessment')
    ], validators=[DataRequired()])
    
    preferred_date = DateField('Preferred Date', validators=[Optional()])
    preferred_time = SelectField('Preferred Time', choices=[
        ('', 'Select preferred time'),
        ('morning', 'Morning (9 AM - 12 PM)'),
        ('afternoon', 'Afternoon (12 PM - 5 PM)'),
        ('evening', 'Evening (5 PM - 8 PM)')
    ], validators=[Optional()])
    
    consultation_mode = SelectField('Consultation Mode', choices=[
        ('', 'Select consultation mode'),
        ('in_person', 'In-person at hotel'),
        ('virtual', 'Virtual meeting'),
        ('phone', 'Phone call'),
        ('office', 'At GM Services office')
    ], validators=[DataRequired()])
    
    specific_questions = TextAreaField('Specific Questions/Topics',
                                     validators=[Optional(), Length(max=2000)],
                                     description='What specific topics would you like to discuss?')