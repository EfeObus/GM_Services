"""
Car Service Booking Forms
Forms for booking different types of car services
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, BooleanField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange
from wtforms.widgets import DateInput, TimeInput
from data.nigeria_data import NIGERIAN_STATES
from datetime import date, datetime, time

class CarServiceBookingForm(FlaskForm):
    """Base form for car service bookings"""
    
    # Customer Information
    customer_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    customer_email = StringField('Email Address', validators=[DataRequired(), Email()])
    customer_phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    
    # Vehicle Information
    vehicle_make = StringField('Vehicle Make', validators=[DataRequired(), Length(min=2, max=50)])
    vehicle_model = StringField('Vehicle Model', validators=[DataRequired(), Length(min=2, max=50)])
    vehicle_year = IntegerField('Vehicle Year', validators=[DataRequired(), NumberRange(min=1990, max=2030)])
    registration_number = StringField('Registration Number', validators=[DataRequired(), Length(min=3, max=20)])
    current_mileage = IntegerField('Current Mileage (km)', validators=[Optional(), NumberRange(min=0)])
    
    # Service Details
    preferred_date = DateField('Preferred Service Date', validators=[DataRequired()], widget=DateInput())
    preferred_time = SelectField('Preferred Time', choices=[
        ('09:00', '9:00 AM'),
        ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'),
        ('12:00', '12:00 PM'),
        ('13:00', '1:00 PM'),
        ('14:00', '2:00 PM'),
        ('15:00', '3:00 PM'),
        ('16:00', '4:00 PM'),
        ('17:00', '5:00 PM')
    ], validators=[DataRequired()])
    
    # Location
    service_location = SelectField('Preferred Service Location', choices=[
        ('center_lagos', 'Lagos Service Center'),
        ('center_abuja', 'Abuja Service Center'),
        ('center_ibadan', 'Ibadan Service Center'),
        ('center_kano', 'Kano Service Center'),
        ('mobile_service', 'Mobile Service (Additional charges apply)')
    ], validators=[DataRequired()])
    
    # Customer Requirements
    customer_complaints = TextAreaField('Vehicle Issues/Complaints', validators=[Optional(), Length(max=1000)])
    special_instructions = TextAreaField('Special Instructions', validators=[Optional(), Length(max=500)])
    
    # Emergency Contact
    emergency_contact_name = StringField('Emergency Contact Name', validators=[Optional(), Length(max=100)])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[Optional(), Length(max=20)])
    
    # Terms and Conditions
    terms_accepted = BooleanField('I accept the terms and conditions', validators=[DataRequired()])
    
    submit = SubmitField('Book Service')

class OilChangeMaintenanceForm(CarServiceBookingForm):
    """Form for Oil Change & Maintenance services"""
    
    # Oil Change Specific Fields
    oil_type_preference = SelectField('Oil Type Preference', choices=[
        ('conventional', 'Conventional Oil'),
        ('blend', 'High Mileage/Blend'),
        ('synthetic', 'Full Synthetic'),
        ('dealer_recommendation', 'Let mechanic recommend')
    ], validators=[DataRequired()])
    
    last_service_date = DateField('Last Service Date', validators=[Optional()], widget=DateInput())
    last_service_mileage = IntegerField('Last Service Mileage (km)', validators=[Optional(), NumberRange(min=0)])
    
    # Additional Services
    oil_filter_change = BooleanField('Oil Filter Change')
    air_filter_change = BooleanField('Air Filter Change')
    transmission_fluid_check = BooleanField('Transmission Fluid Check')
    brake_fluid_check = BooleanField('Brake Fluid Check')
    coolant_check = BooleanField('Coolant System Check')
    battery_check = BooleanField('Battery Check')
    tire_pressure_check = BooleanField('Tire Pressure Check')
    basic_inspection = BooleanField('Basic Vehicle Inspection')
    
    # Budget Range
    budget_range = SelectField('Budget Range', choices=[
        ('8500-12000', '₦8,500 - ₦12,000'),
        ('12000-18000', '₦12,000 - ₦18,000'),
        ('18000-25000', '₦18,000 - ₦25,000'),
        ('25000-35000', '₦25,000 - ₦35,000'),
        ('flexible', 'Flexible based on recommendations')
    ], validators=[DataRequired()])

class BrakeSuspensionForm(CarServiceBookingForm):
    """Form for Brake & Suspension services"""
    
    # Brake/Suspension Specific Issues
    brake_issues = SelectField('Brake Related Issues', choices=[
        ('none', 'No specific issues - routine check'),
        ('squeaking', 'Squeaking or grinding noise'),
        ('soft_pedal', 'Soft or spongy brake pedal'),
        ('pulling', 'Vehicle pulls to one side when braking'),
        ('vibration', 'Steering wheel vibration when braking'),
        ('warning_light', 'Brake warning light'),
        ('other', 'Other brake issues')
    ], validators=[DataRequired()])
    
    suspension_issues = SelectField('Suspension Related Issues', choices=[
        ('none', 'No specific issues - routine check'),
        ('rough_ride', 'Rough or bumpy ride'),
        ('bouncing', 'Excessive bouncing'),
        ('noise', 'Clunking or rattling noise'),
        ('uneven_tire_wear', 'Uneven tire wear'),
        ('pulling', 'Vehicle pulls to one side'),
        ('low_ride_height', 'Vehicle sits lower than normal'),
        ('other', 'Other suspension issues')
    ], validators=[DataRequired()])
    
    # Specific Services Needed
    brake_pad_replacement = BooleanField('Brake Pad Replacement')
    brake_rotor_service = BooleanField('Brake Rotor Service/Replacement')
    brake_fluid_change = BooleanField('Brake Fluid Change')
    suspension_struts = BooleanField('Suspension Struts/Shocks')
    wheel_alignment = BooleanField('Wheel Alignment')
    wheel_balancing = BooleanField('Wheel Balancing')
    tire_rotation = BooleanField('Tire Rotation')
    safety_inspection = BooleanField('Comprehensive Safety Inspection')
    
    # Last Service Information
    last_brake_service = DateField('Last Brake Service Date', validators=[Optional()], widget=DateInput())
    last_alignment = DateField('Last Wheel Alignment Date', validators=[Optional()], widget=DateInput())
    
    # Budget Range
    budget_range = SelectField('Budget Range', choices=[
        ('15000-25000', '₦15,000 - ₦25,000'),
        ('25000-40000', '₦25,000 - ₦40,000'),
        ('40000-60000', '₦40,000 - ₦60,000'),
        ('60000-100000', '₦60,000 - ₦100,000'),
        ('flexible', 'Flexible based on recommendations')
    ], validators=[DataRequired()])

class ACElectricalForm(CarServiceBookingForm):
    """Form for AC & Electrical services"""
    
    # AC Issues
    ac_issues = SelectField('Air Conditioning Issues', choices=[
        ('none', 'No specific issues - routine service'),
        ('not_cooling', 'AC not cooling properly'),
        ('warm_air', 'Blowing warm air'),
        ('weak_airflow', 'Weak airflow'),
        ('strange_odor', 'Strange odor from AC'),
        ('noisy_operation', 'Noisy AC operation'),
        ('intermittent', 'AC works intermittently'),
        ('refrigerant_leak', 'Suspected refrigerant leak'),
        ('other', 'Other AC issues')
    ], validators=[DataRequired()])
    
    # Electrical Issues
    electrical_issues = SelectField('Electrical System Issues', choices=[
        ('none', 'No specific issues - routine check'),
        ('battery_dead', 'Battery frequently dies'),
        ('starting_problems', 'Difficulty starting engine'),
        ('lights_dim', 'Dim or flickering lights'),
        ('alternator_noise', 'Alternator making noise'),
        ('electrical_smell', 'Burning electrical smell'),
        ('dashboard_warnings', 'Dashboard warning lights'),
        ('power_accessories', 'Power accessories not working'),
        ('other', 'Other electrical issues')
    ], validators=[DataRequired()])
    
    # Specific Services
    ac_refrigerant_recharge = BooleanField('AC Refrigerant Recharge')
    ac_compressor_service = BooleanField('AC Compressor Service')
    ac_filter_replacement = BooleanField('Cabin Air Filter Replacement')
    battery_replacement = BooleanField('Battery Replacement')
    alternator_service = BooleanField('Alternator Service/Replacement')
    starter_service = BooleanField('Starter Motor Service')
    electrical_diagnostics = BooleanField('Comprehensive Electrical Diagnostics')
    charging_system_test = BooleanField('Charging System Test')
    
    # Last Service Information
    last_ac_service = DateField('Last AC Service Date', validators=[Optional()], widget=DateInput())
    last_battery_replacement = DateField('Last Battery Replacement', validators=[Optional()], widget=DateInput())
    
    # Budget Range
    budget_range = SelectField('Budget Range', choices=[
        ('12000-20000', '₦12,000 - ₦20,000'),
        ('20000-35000', '₦20,000 - ₦35,000'),
        ('35000-50000', '₦35,000 - ₦50,000'),
        ('50000-80000', '₦50,000 - ₦80,000'),
        ('flexible', 'Flexible based on recommendations')
    ], validators=[DataRequired()])