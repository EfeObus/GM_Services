"""
Rental Forms
Forms for rental services including vehicle, equipment, and property rental requests
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField, IntegerField, DateField, BooleanField, TimeField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, Length, ValidationError
from data.nigeria_data import NIGERIAN_STATES
from datetime import date, timedelta

class RentalBookingRequestForm(FlaskForm):
    """Base form for rental booking requests"""
    
    # Customer Information
    customer_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=200)])
    customer_email = StringField('Email Address', validators=[DataRequired(), Email()])
    customer_phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    customer_address = TextAreaField('Address', validators=[Optional(), Length(max=500)])
    
    # Rental Period
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    flexible_dates = BooleanField('I have flexible dates')
    
    # Location
    pickup_location = TextAreaField('Preferred Pickup Location', validators=[Optional(), Length(max=500)])
    delivery_required = BooleanField('Delivery Required')
    delivery_address = TextAreaField('Delivery Address', validators=[Optional(), Length(max=500)])
    
    # Budget
    budget_range_min = DecimalField('Minimum Budget (₦)', validators=[Optional(), NumberRange(min=0)], places=2)
    budget_range_max = DecimalField('Maximum Budget (₦)', validators=[Optional(), NumberRange(min=0)], places=2)
    
    # Usage
    usage_purpose = StringField('Purpose of Rental', validators=[Optional(), Length(max=200)])
    special_requirements = TextAreaField('Special Requirements/Notes', validators=[Optional(), Length(max=1000)])
    
    # Terms and Conditions
    terms_accepted = BooleanField('I accept the terms and conditions', validators=[DataRequired()])
    
    def validate_end_date(self, field):
        if field.data and self.start_date.data:
            if field.data <= self.start_date.data:
                raise ValidationError('End date must be after start date.')
    
    def validate_start_date(self, field):
        if field.data:
            if field.data < date.today():
                raise ValidationError('Start date cannot be in the past.')


class VehicleRentalRequestForm(RentalBookingRequestForm):
    """Form for vehicle rental requests"""
    
    # Vehicle Type
    vehicle_category = SelectField('Vehicle Category',
                                  choices=[
                                      ('', 'Select Category...'),
                                      ('economy_car', 'Economy Car'),
                                      ('compact_car', 'Compact Car'),
                                      ('mid_size_car', 'Mid-size Car'),
                                      ('luxury_car', 'Luxury Car'),
                                      ('suv', 'SUV'),
                                      ('pickup_truck', 'Pickup Truck'),
                                      ('van', 'Van'),
                                      ('minibus', 'Minibus'),
                                      ('bus', 'Bus'),
                                      ('motorcycle', 'Motorcycle'),
                                      ('bicycle', 'Bicycle')
                                  ],
                                  validators=[DataRequired()])
    
    # Vehicle Specifications
    preferred_make = StringField('Preferred Make/Brand', validators=[Optional(), Length(max=50)])
    preferred_model = StringField('Preferred Model', validators=[Optional(), Length(max=50)])
    year_preference = SelectField('Year Preference',
                                 choices=[
                                     ('', 'No Preference'),
                                     ('2024-2025', '2024-2025 (Latest)'),
                                     ('2020-2023', '2020-2023 (Recent)'),
                                     ('2015-2019', '2015-2019 (Good)'),
                                     ('2010-2014', '2010-2014 (Older)')
                                 ],
                                 validators=[Optional()])
    
    transmission = SelectField('Transmission',
                              choices=[
                                  ('', 'No Preference'),
                                  ('automatic', 'Automatic'),
                                  ('manual', 'Manual')
                              ],
                              validators=[Optional()])
    
    fuel_type = SelectField('Fuel Type',
                           choices=[
                               ('', 'No Preference'),
                               ('petrol', 'Petrol'),
                               ('diesel', 'Diesel'),
                               ('hybrid', 'Hybrid'),
                               ('electric', 'Electric')
                           ],
                           validators=[Optional()])
    
    seating_capacity = SelectField('Seating Capacity',
                                  choices=[
                                      ('', 'No Preference'),
                                      ('2', '2 Seats'),
                                      ('4', '4 Seats'),
                                      ('5', '5 Seats'),
                                      ('7', '7 Seats'),
                                      ('8+', '8+ Seats')
                                  ],
                                  validators=[Optional()])
    
    # Additional Services
    driver_required = BooleanField('Driver Required')
    insurance_required = BooleanField('Insurance Required')
    gps_required = BooleanField('GPS Navigation Required')
    child_seat_required = BooleanField('Child Seat Required')
    
    # Vehicle Features
    air_conditioning = BooleanField('Air Conditioning Required')
    bluetooth = BooleanField('Bluetooth/Audio System')
    luggage_space = SelectField('Luggage Space Requirements',
                               choices=[
                                   ('', 'No Specific Requirements'),
                                   ('small', 'Small (1-2 bags)'),
                                   ('medium', 'Medium (3-4 bags)'),
                                   ('large', 'Large (5+ bags)')
                               ],
                               validators=[Optional()])


class EquipmentRentalRequestForm(RentalBookingRequestForm):
    """Form for equipment rental requests"""
    
    # Equipment Type
    equipment_category = SelectField('Equipment Category',
                                    choices=[
                                        ('', 'Select Category...'),
                                        ('construction', 'Construction Equipment'),
                                        ('power_tools', 'Power Tools'),
                                        ('generators', 'Generators & Power'),
                                        ('event_equipment', 'Event Equipment'),
                                        ('office_furniture', 'Office Furniture'),
                                        ('cleaning_equipment', 'Cleaning Equipment'),
                                        ('catering_equipment', 'Catering Equipment'),
                                        ('audio_visual', 'Audio Visual Equipment'),
                                        ('lighting', 'Lighting Equipment'),
                                        ('safety_equipment', 'Safety Equipment'),
                                        ('other', 'Other Equipment')
                                    ],
                                    validators=[DataRequired()])
    
    # Equipment Specifications
    equipment_name = StringField('Specific Equipment Name/Type', 
                                validators=[DataRequired(), Length(min=2, max=200)])
    brand_preference = StringField('Preferred Brand', validators=[Optional(), Length(max=50)])
    model_preference = StringField('Preferred Model', validators=[Optional(), Length(max=50)])
    
    # Technical Specifications
    power_requirements = StringField('Power Requirements (e.g., 220V, 5kW)', 
                                    validators=[Optional(), Length(max=100)])
    capacity_requirements = StringField('Capacity/Size Requirements', 
                                       validators=[Optional(), Length(max=100)])
    
    # Quantity
    quantity_needed = IntegerField('Quantity Needed', 
                                  validators=[DataRequired(), NumberRange(min=1, max=100)])
    
    # Additional Services
    installation_required = BooleanField('Installation/Setup Required')
    operator_required = BooleanField('Trained Operator Required')
    maintenance_included = BooleanField('Maintenance Service Required')
    training_required = BooleanField('Training on Usage Required')
    
    # Technical Support
    technical_support = BooleanField('24/7 Technical Support Required')
    backup_equipment = BooleanField('Backup Equipment Required')
    
    # Usage Environment
    indoor_use = BooleanField('Indoor Use')
    outdoor_use = BooleanField('Outdoor Use')
    weather_protection = BooleanField('Weather Protection Required')
    
    # Safety Requirements
    safety_training = BooleanField('Safety Training Required')
    safety_equipment = BooleanField('Safety Equipment Included')


class PropertyRentalRequestForm(RentalBookingRequestForm):
    """Form for property rental requests"""
    
    # Property Type
    property_category = SelectField('Property Type',
                                   choices=[
                                       ('', 'Select Property Type...'),
                                       ('apartment', 'Apartment'),
                                       ('house', 'House'),
                                       ('villa', 'Villa'),
                                       ('office_space', 'Office Space'),
                                       ('warehouse', 'Warehouse'),
                                       ('retail_space', 'Retail Space'),
                                       ('event_venue', 'Event Venue'),
                                       ('conference_room', 'Conference Room'),
                                       ('studio', 'Studio/Workshop'),
                                       ('short_stay', 'Short Stay Accommodation'),
                                       ('vacation_rental', 'Vacation Rental')
                                   ],
                                   validators=[DataRequired()])
    
    # Location Preferences
    preferred_area = StringField('Preferred Area/Location', 
                                validators=[DataRequired(), Length(min=2, max=200)])
    preferred_state = SelectField('Preferred State',
                                 choices=[(state, state) for state in NIGERIAN_STATES],
                                 validators=[DataRequired()])
    proximity_requirements = TextAreaField('Proximity Requirements (e.g., near airport, schools)', 
                                          validators=[Optional(), Length(max=500)])
    
    # Property Specifications
    bedrooms = SelectField('Number of Bedrooms',
                          choices=[
                              ('', 'N/A'),
                              ('1', '1 Bedroom'),
                              ('2', '2 Bedrooms'),
                              ('3', '3 Bedrooms'),
                              ('4', '4 Bedrooms'),
                              ('5+', '5+ Bedrooms')
                          ],
                          validators=[Optional()])
    
    bathrooms = SelectField('Number of Bathrooms',
                           choices=[
                               ('', 'N/A'),
                               ('1', '1 Bathroom'),
                               ('2', '2 Bathrooms'),
                               ('3', '3 Bathrooms'),
                               ('4+', '4+ Bathrooms')
                           ],
                           validators=[Optional()])
    
    # Size and Capacity
    minimum_size_sqm = DecimalField('Minimum Size (Square Meters)', 
                                   validators=[Optional(), NumberRange(min=1)], 
                                   places=2)
    maximum_occupancy = IntegerField('Maximum Occupancy (People)', 
                                    validators=[Optional(), NumberRange(min=1, max=1000)])
    
    # Amenities and Features
    furnished = BooleanField('Furnished Required')
    air_conditioning = BooleanField('Air Conditioning')
    parking = BooleanField('Parking Required')
    parking_spaces = SelectField('Number of Parking Spaces',
                                choices=[
                                    ('', 'N/A'),
                                    ('1', '1 Space'),
                                    ('2', '2 Spaces'),
                                    ('3', '3 Spaces'),
                                    ('4+', '4+ Spaces')
                                ],
                                validators=[Optional()])
    
    # Utilities and Services
    electricity_included = BooleanField('Electricity Included')
    water_included = BooleanField('Water Included')
    internet_included = BooleanField('Internet/WiFi Included')
    security = BooleanField('Security Service Required')
    cleaning_service = BooleanField('Cleaning Service Required')
    
    # Business Requirements (for commercial properties)
    business_license_support = BooleanField('Business License Support Required')
    equipment_provided = BooleanField('Equipment/Furniture Provided')
    
    # Accessibility
    wheelchair_accessible = BooleanField('Wheelchair Accessible')
    elevator_access = BooleanField('Elevator Access Required')
    ground_floor = BooleanField('Ground Floor Preferred')
    
    # Additional Requirements
    pet_friendly = BooleanField('Pet Friendly')
    smoking_allowed = BooleanField('Smoking Allowed')
    event_hosting_allowed = BooleanField('Event Hosting Allowed')


class RentalTermsAcceptanceForm(FlaskForm):
    """Form for accepting rental terms and conditions"""
    
    rental_type = SelectField('Rental Type',
                             choices=[
                                 ('vehicle', 'Vehicle Rental'),
                                 ('equipment', 'Equipment Rental'),
                                 ('property', 'Property Rental')
                             ],
                             validators=[DataRequired()])
    
    terms_read = BooleanField('I have read and understood the terms and conditions', 
                             validators=[DataRequired()])
    
    terms_accepted = BooleanField('I accept all terms and conditions', 
                                 validators=[DataRequired()])
    
    privacy_policy_accepted = BooleanField('I accept the privacy policy', 
                                          validators=[DataRequired()])
    
    age_confirmation = BooleanField('I confirm that I am 18 years or older', 
                                   validators=[DataRequired()])
    
    liability_acknowledged = BooleanField('I acknowledge my liability and responsibilities', 
                                         validators=[DataRequired()])