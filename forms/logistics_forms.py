"""
Logistics Forms
Forms for logistics services including quote requests
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField, IntegerField, DateField, BooleanField, TimeField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, Length
from data.nigeria_data import NIGERIAN_STATES

class LogisticsQuoteRequestForm(FlaskForm):
    """Form for requesting logistics quotes"""
    
    # Customer Information
    customer_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=200)])
    customer_email = StringField('Email Address', validators=[DataRequired(), Email()])
    customer_phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    company_name = StringField('Company Name (Optional)', validators=[Optional(), Length(max=200)])
    
    # Service Type
    service_type = SelectField('Service Type', 
                             choices=[
                                 ('freight_transport', 'Freight Transport'),
                                 ('express_delivery', 'Express Delivery'),
                                 ('supply_chain', 'Supply Chain Management')
                             ],
                             validators=[DataRequired()])
    
    # Pickup Information
    pickup_address = TextAreaField('Pickup Address', validators=[DataRequired(), Length(max=500)])
    pickup_city = StringField('Pickup City', validators=[DataRequired(), Length(max=100)])
    pickup_state = SelectField('Pickup State', 
                              choices=[(state, state) for state in NIGERIAN_STATES],
                              validators=[DataRequired()])
    pickup_date = DateField('Preferred Pickup Date', validators=[Optional()])
    pickup_time = SelectField('Preferred Pickup Time',
                             choices=[
                                 ('morning', 'Morning (8AM - 12PM)'),
                                 ('afternoon', 'Afternoon (12PM - 4PM)'),
                                 ('evening', 'Evening (4PM - 6PM)'),
                                 ('flexible', 'Flexible')
                             ],
                             validators=[Optional()])
    
    # Delivery Information
    delivery_address = TextAreaField('Delivery Address', validators=[DataRequired(), Length(max=500)])
    delivery_city = StringField('Delivery City', validators=[DataRequired(), Length(max=100)])
    delivery_state = SelectField('Delivery State',
                                choices=[(state, state) for state in NIGERIAN_STATES],
                                validators=[DataRequired()])
    delivery_date = DateField('Preferred Delivery Date', validators=[Optional()])
    delivery_time = SelectField('Preferred Delivery Time',
                               choices=[
                                   ('morning', 'Morning (8AM - 12PM)'),
                                   ('afternoon', 'Afternoon (12PM - 4PM)'),
                                   ('evening', 'Evening (4PM - 6PM)'),
                                   ('flexible', 'Flexible')
                               ],
                               validators=[Optional()])
    
    # Package/Shipment Details
    package_description = TextAreaField('Package/Shipment Description', 
                                       validators=[DataRequired(), Length(max=1000)])
    package_weight = DecimalField('Estimated Weight (kg)', 
                                 validators=[Optional(), NumberRange(min=0.1, max=50000)],
                                 places=2)
    package_length = DecimalField('Length (cm)', validators=[Optional(), NumberRange(min=1, max=1000)], places=2)
    package_width = DecimalField('Width (cm)', validators=[Optional(), NumberRange(min=1, max=1000)], places=2)
    package_height = DecimalField('Height (cm)', validators=[Optional(), NumberRange(min=1, max=1000)], places=2)
    package_value = DecimalField('Declared Value (₦)', 
                                validators=[Optional(), NumberRange(min=0)],
                                places=2)
    
    # Service-specific fields
    freight_type = SelectField('Freight Type',
                              choices=[
                                  ('', 'Select...'),
                                  ('full_load', 'Full Load'),
                                  ('partial_load', 'Partial Load'),
                                  ('container', 'Container')
                              ],
                              validators=[Optional()])
    
    vehicle_type = SelectField('Preferred Vehicle Type',
                              choices=[
                                  ('', 'No Preference'),
                                  ('motorcycle', 'Motorcycle'),
                                  ('van', 'Van'),
                                  ('truck', 'Truck'),
                                  ('trailer', 'Trailer')
                              ],
                              validators=[Optional()])
    
    urgency_level = SelectField('Urgency Level',
                               choices=[
                                   ('standard', 'Standard'),
                                   ('urgent', 'Urgent'),
                                   ('emergency', 'Emergency')
                               ],
                               validators=[DataRequired()])
    
    insurance_required = BooleanField('Insurance Required')
    
    # Supply Chain specific fields
    supply_chain_type = SelectField('Supply Chain Service',
                                   choices=[
                                       ('', 'Select...'),
                                       ('warehousing', 'Warehousing'),
                                       ('distribution', 'Distribution'),
                                       ('inventory_management', 'Inventory Management'),
                                       ('full_service', 'Full Service Solution')
                                   ],
                                   validators=[Optional()])
    
    duration_months = IntegerField('Contract Duration (months)', 
                                  validators=[Optional(), NumberRange(min=1, max=120)])
    
    volume_per_month = IntegerField('Expected Monthly Volume (packages/units)',
                                   validators=[Optional(), NumberRange(min=1)])
    
    # Additional requirements
    special_requirements = TextAreaField('Special Requirements/Instructions', 
                                        validators=[Optional(), Length(max=1000)])
    customer_notes = TextAreaField('Additional Notes', 
                                  validators=[Optional(), Length(max=1000)])


class FreightTransportQuoteForm(FlaskForm):
    """Simplified form specifically for Freight Transport quotes"""
    
    # Customer Information
    customer_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=200)])
    customer_email = StringField('Email Address', validators=[DataRequired(), Email()])
    customer_phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    company_name = StringField('Company Name (Optional)', validators=[Optional(), Length(max=200)])
    
    # Pickup Information
    pickup_address = TextAreaField('Pickup Address', validators=[DataRequired(), Length(max=500)])
    pickup_city = StringField('Pickup City', validators=[DataRequired(), Length(max=100)])
    pickup_state = SelectField('Pickup State', 
                              choices=[(state, state) for state in NIGERIAN_STATES],
                              validators=[DataRequired()])
    
    # Delivery Information
    delivery_address = TextAreaField('Delivery Address', validators=[DataRequired(), Length(max=500)])
    delivery_city = StringField('Delivery City', validators=[DataRequired(), Length(max=100)])
    delivery_state = SelectField('Delivery State',
                                choices=[(state, state) for state in NIGERIAN_STATES],
                                validators=[DataRequired()])
    
    # Freight Details
    package_description = TextAreaField('Freight Description', 
                                       validators=[DataRequired(), Length(max=1000)])
    package_weight = DecimalField('Weight (kg)', 
                                 validators=[DataRequired(), NumberRange(min=0.1, max=50000)],
                                 places=2)
    freight_type = SelectField('Freight Type',
                              choices=[
                                  ('full_load', 'Full Load'),
                                  ('partial_load', 'Partial Load'),
                                  ('container', 'Container')
                              ],
                              validators=[DataRequired()])
    urgency_level = SelectField('Urgency Level',
                               choices=[
                                   ('standard', 'Standard'),
                                   ('urgent', 'Urgent')
                               ],
                               validators=[DataRequired()])
    insurance_required = BooleanField('Insurance Required')
    special_requirements = TextAreaField('Special Requirements', validators=[Optional(), Length(max=1000)])


class ExpressDeliveryQuoteForm(FlaskForm):
    """Simplified form specifically for Express Delivery quotes"""
    
    # Customer Information
    customer_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=200)])
    customer_email = StringField('Email Address', validators=[DataRequired(), Email()])
    customer_phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    
    # Pickup Information
    pickup_address = TextAreaField('Pickup Address', validators=[DataRequired(), Length(max=500)])
    pickup_city = StringField('Pickup City', validators=[DataRequired(), Length(max=100)])
    pickup_state = SelectField('Pickup State', 
                              choices=[(state, state) for state in NIGERIAN_STATES],
                              validators=[DataRequired()])
    
    # Delivery Information
    delivery_address = TextAreaField('Delivery Address', validators=[DataRequired(), Length(max=500)])
    delivery_city = StringField('Delivery City', validators=[DataRequired(), Length(max=100)])
    delivery_state = SelectField('Delivery State',
                                choices=[(state, state) for state in NIGERIAN_STATES],
                                validators=[DataRequired()])
    
    # Package Details
    package_description = TextAreaField('Package Description', 
                                       validators=[DataRequired(), Length(max=500)])
    package_weight = DecimalField('Weight (kg)', 
                                 validators=[Optional(), NumberRange(min=0.01, max=100)],
                                 places=2)
    urgency_level = SelectField('Delivery Speed',
                               choices=[
                                   ('same_day', 'Same Day'),
                                   ('next_day', 'Next Day'),
                                   ('standard', 'Standard (2-3 days)')
                               ],
                               validators=[DataRequired()])
    package_value = DecimalField('Package Value (₦)', 
                                validators=[Optional(), NumberRange(min=0)],
                                places=2)
    insurance_required = BooleanField('Insurance Required')
    special_requirements = TextAreaField('Special Instructions', validators=[Optional(), Length(max=500)])


class SupplyChainQuoteForm(FlaskForm):
    """Simplified form specifically for Supply Chain Management quotes"""
    
    # Customer Information
    customer_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=200)])
    customer_email = StringField('Email Address', validators=[DataRequired(), Email()])
    customer_phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=200)])
    
    # Business Information
    business_type = SelectField('Business Type',
                               choices=[
                                   ('', 'Select...'),
                                   ('retail', 'Retail'),
                                   ('wholesale', 'Wholesale'),
                                   ('manufacturing', 'Manufacturing'),
                                   ('ecommerce', 'E-commerce'),
                                   ('other', 'Other')
                               ],
                               validators=[DataRequired()])
    
    # Service Requirements
    supply_chain_type = SelectField('Service Required',
                                   choices=[
                                       ('warehousing', 'Warehousing'),
                                       ('distribution', 'Distribution'),
                                       ('inventory_management', 'Inventory Management'),
                                       ('full_service', 'Full Service Solution')
                                   ],
                                   validators=[DataRequired()])
    
    # Location Information
    business_location = TextAreaField('Business Location', validators=[DataRequired(), Length(max=500)])
    business_city = StringField('City', validators=[DataRequired(), Length(max=100)])
    business_state = SelectField('State',
                                choices=[(state, state) for state in NIGERIAN_STATES],
                                validators=[DataRequired()])
    
    # Volume Information
    volume_per_month = IntegerField('Expected Monthly Volume (units/packages)',
                                   validators=[DataRequired(), NumberRange(min=1)])
    duration_months = IntegerField('Contract Duration (months)', 
                                  validators=[DataRequired(), NumberRange(min=1, max=120)])
    
    # Additional Details
    product_description = TextAreaField('Product/Inventory Description', 
                                       validators=[DataRequired(), Length(max=1000)])
    special_requirements = TextAreaField('Special Requirements', validators=[Optional(), Length(max=1000)])
    current_challenges = TextAreaField('Current Supply Chain Challenges', validators=[Optional(), Length(max=1000)])