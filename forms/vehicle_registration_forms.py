"""
Vehicle Registration Forms
Forms for new vehicle registration and renewal services
"""
from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField, IntegerField, DateField, 
                    TextAreaField, BooleanField, DecimalField, SubmitField,
                    ValidationError)
from wtforms.validators import DataRequired, Length, Email, Optional, NumberRange
from datetime import datetime, date
from data.nigeria_data import NIGERIAN_STATES, LOCAL_GOVERNMENTS

class VehicleRegistrationForm(FlaskForm):
    """Base form for vehicle registration"""
    
    # Registration Type
    registration_type = SelectField(
        'Registration Type',
        choices=[
            ('new_registration', 'New Vehicle Registration'),
            ('renewal', 'Registration Renewal')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    # Vehicle Information
    vehicle_make = StringField(
        'Vehicle Make',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={'placeholder': 'e.g., Toyota, Honda, Mercedes', 'class': 'form-control'}
    )
    
    vehicle_model = StringField(
        'Vehicle Model',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={'placeholder': 'e.g., Camry, Accord, C-Class', 'class': 'form-control'}
    )
    
    vehicle_year = IntegerField(
        'Vehicle Year',
        validators=[
            DataRequired(),
            NumberRange(min=1950, max=datetime.now().year + 1, message="Please enter a valid year")
        ],
        render_kw={'placeholder': f'e.g., {datetime.now().year}', 'class': 'form-control'}
    )
    
    vehicle_color = StringField(
        'Vehicle Color',
        validators=[DataRequired(), Length(min=2, max=50)],
        render_kw={'placeholder': 'e.g., Black, White, Silver', 'class': 'form-control'}
    )
    
    engine_number = StringField(
        'Engine Number',
        validators=[Optional(), Length(min=5, max=100)],
        render_kw={'placeholder': 'Engine identification number', 'class': 'form-control'}
    )
    
    chassis_number = StringField(
        'Chassis Number',
        validators=[Optional(), Length(min=5, max=100)],
        render_kw={'placeholder': 'Vehicle identification number (VIN)', 'class': 'form-control'}
    )
    
    # For Renewals
    current_registration_number = StringField(
        'Current Registration Number',
        validators=[Optional(), Length(min=3, max=20)],
        render_kw={'placeholder': 'Current plate number (for renewals)', 'class': 'form-control'}
    )
    
    expiry_date = DateField(
        'Current Registration Expiry Date',
        validators=[Optional()],
        render_kw={'class': 'form-control'}
    )
    
    # Owner Information
    owner_name = StringField(
        'Vehicle Owner Full Name',
        validators=[DataRequired(), Length(min=2, max=200)],
        render_kw={'placeholder': 'Full name as it appears on ID', 'class': 'form-control'}
    )
    
    owner_address = TextAreaField(
        'Owner Address',
        validators=[DataRequired(), Length(min=10, max=500)],
        render_kw={'placeholder': 'Complete residential address', 'class': 'form-control', 'rows': '3'}
    )
    
    owner_phone = StringField(
        'Owner Phone Number',
        validators=[DataRequired(), Length(min=10, max=20)],
        render_kw={'placeholder': '+234 or 0', 'class': 'form-control'}
    )
    
    owner_email = StringField(
        'Owner Email Address',
        validators=[Optional(), Email()],
        render_kw={'placeholder': 'owner@example.com', 'class': 'form-control'}
    )
    
    owner_state = SelectField(
        'Owner State',
        choices=[('', 'Select State')] + [(state['name'], state['name']) for state in NIGERIAN_STATES],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    owner_lga = SelectField(
        'Owner Local Government Area',
        choices=[('', 'Select LGA')],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    # Vehicle Use
    vehicle_purpose = SelectField(
        'Vehicle Purpose',
        choices=[
            ('', 'Select Purpose'),
            ('private', 'Private Use'),
            ('commercial', 'Commercial Use'),
            ('government', 'Government Use')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    # Documentation Checklist
    purchase_receipt = BooleanField(
        'Purchase Receipt Available',
        render_kw={'class': 'form-check-input'}
    )
    
    customs_papers = BooleanField(
        'Customs Papers Available (for imported vehicles)',
        render_kw={'class': 'form-check-input'}
    )
    
    insurance_certificate = BooleanField(
        'Valid Insurance Certificate',
        render_kw={'class': 'form-check-input'}
    )
    
    roadworthiness_certificate = BooleanField(
        'Roadworthiness Certificate',
        render_kw={'class': 'form-check-input'}
    )
    
    driver_license = BooleanField(
        'Valid Driver\'s License',
        render_kw={'class': 'form-check-input'}
    )
    
    # Service Options
    service_center = SelectField(
        'Preferred Service Center',
        choices=[
            ('', 'Select Service Center'),
            ('lagos_mainland', 'Lagos - Mainland Office'),
            ('lagos_island', 'Lagos - Victoria Island Office'),
            ('abuja', 'Abuja - Central Office'),
            ('kano', 'Kano - Regional Office'),
            ('port_harcourt', 'Port Harcourt - Regional Office'),
            ('ibadan', 'Ibadan - Regional Office')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    processing_priority = SelectField(
        'Processing Priority',
        choices=[
            ('standard', 'Standard (7-14 days) - ₦45,000'),
            ('express', 'Express (3-5 days) - ₦65,000'),
            ('same_day', 'Same Day Service - ₦85,000')
        ],
        validators=[DataRequired()],
        default='standard',
        render_kw={'class': 'form-select'}
    )
    
    # Contact Information
    contact_phone = StringField(
        'Contact Phone Number',
        validators=[DataRequired(), Length(min=10, max=20)],
        render_kw={'placeholder': 'Primary contact number', 'class': 'form-control'}
    )
    
    contact_email = StringField(
        'Contact Email Address',
        validators=[Optional(), Email()],
        render_kw={'placeholder': 'contact@example.com', 'class': 'form-control'}
    )
    
    pickup_required = BooleanField(
        'Document Pickup Required',
        render_kw={'class': 'form-check-input'}
    )
    
    pickup_address = TextAreaField(
        'Pickup Address',
        validators=[Optional(), Length(max=500)],
        render_kw={'placeholder': 'Address for document pickup (if different from owner address)', 'class': 'form-control', 'rows': '2'}
    )
    
    # Terms and Conditions
    terms_accepted = BooleanField(
        'I accept the terms and conditions',
        validators=[DataRequired(message="You must accept the terms and conditions")],
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField('Submit Registration Request', render_kw={'class': 'btn btn-success btn-lg'})
    
    def validate_expiry_date(self, field):
        """Validate renewal expiry date"""
        if self.registration_type.data == 'renewal':
            if not field.data:
                raise ValidationError('Expiry date is required for renewals')
            if field.data > date.today():
                raise ValidationError('Registration has not expired yet')
    
    def validate_current_registration_number(self, field):
        """Validate current registration number for renewals"""
        if self.registration_type.data == 'renewal':
            if not field.data:
                raise ValidationError('Current registration number is required for renewals')
    
    def validate_engine_number(self, field):
        """Validate engine number for new registrations"""
        if self.registration_type.data == 'new_registration':
            if not field.data:
                raise ValidationError('Engine number is required for new registrations')
    
    def validate_chassis_number(self, field):
        """Validate chassis number for new registrations"""
        if self.registration_type.data == 'new_registration':
            if not field.data:
                raise ValidationError('Chassis number is required for new registrations')


class NewVehicleRegistrationForm(VehicleRegistrationForm):
    """Form specifically for new vehicle registration"""
    
    def __init__(self, *args, **kwargs):
        super(NewVehicleRegistrationForm, self).__init__(*args, **kwargs)
        # Hide renewal-specific fields
        self.registration_type.data = 'new_registration'
        # Make engine and chassis numbers required
        self.engine_number.validators = [DataRequired(), Length(min=5, max=100)]
        self.chassis_number.validators = [DataRequired(), Length(min=5, max=100)]


class VehicleRenewalForm(VehicleRegistrationForm):
    """Form specifically for vehicle registration renewal"""
    
    def __init__(self, *args, **kwargs):
        super(VehicleRenewalForm, self).__init__(*args, **kwargs)
        # Hide new registration specific fields
        self.registration_type.data = 'renewal'
        # Make renewal fields required
        self.current_registration_number.validators = [DataRequired(), Length(min=3, max=20)]
        self.expiry_date.validators = [DataRequired()]
        # Update processing priority choices for renewals
        self.processing_priority.choices = [
            ('standard', 'Standard Renewal (5-7 days) - ₦25,000'),
            ('express', 'Express Renewal (2-3 days) - ₦35,000'),
            ('same_day', 'Same Day Renewal - ₦45,000')
        ]