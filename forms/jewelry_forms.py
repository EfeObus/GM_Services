"""
Jewelry Service Forms
Forms for jewelry consultation, collection viewing, and custom design requests
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DecimalField, BooleanField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from wtforms.widgets import TextArea

class JewelryConsultationForm(FlaskForm):
    """Form for jewelry consultation and custom design requests"""
    
    # Personal Information
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=200)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    
    # Consultation Type
    consultation_type = SelectField('Consultation Type', 
                                  choices=[
                                      ('custom_design', 'Custom Design'),
                                      ('repair', 'Jewelry Repair'),
                                      ('appraisal', 'Jewelry Appraisal'),
                                      ('upgrade', 'Jewelry Upgrade'),
                                      ('consultation', 'General Consultation')
                                  ],
                                  validators=[DataRequired()])
    
    # Jewelry Details
    jewelry_type = SelectField('Jewelry Type',
                              choices=[
                                  ('ring', 'Ring'),
                                  ('necklace', 'Necklace'),
                                  ('bracelet', 'Bracelet'),
                                  ('earrings', 'Earrings'),
                                  ('watch', 'Watch'),
                                  ('brooch', 'Brooch/Pin'),
                                  ('pendant', 'Pendant'),
                                  ('set', 'Jewelry Set'),
                                  ('other', 'Other')
                              ],
                              validators=[Optional()])
    
    # Material Preferences
    preferred_metal = SelectField('Preferred Metal',
                                 choices=[
                                     ('gold_18k', '18K Gold'),
                                     ('gold_24k', '24K Gold'),
                                     ('white_gold', 'White Gold'),
                                     ('rose_gold', 'Rose Gold'),
                                     ('platinum', 'Platinum'),
                                     ('silver', 'Sterling Silver'),
                                     ('titanium', 'Titanium'),
                                     ('mixed', 'Mixed Metals'),
                                     ('no_preference', 'No Preference')
                                 ],
                                 validators=[Optional()])
    
    # Gemstone Preferences
    preferred_gemstone = SelectField('Preferred Gemstone',
                                   choices=[
                                       ('diamond', 'Diamond'),
                                       ('emerald', 'Emerald'),
                                       ('ruby', 'Ruby'),
                                       ('sapphire', 'Sapphire'),
                                       ('pearl', 'Pearl'),
                                       ('topaz', 'Topaz'),
                                       ('amethyst', 'Amethyst'),
                                       ('garnet', 'Garnet'),
                                       ('birthstone', 'Birthstone'),
                                       ('no_gemstone', 'No Gemstone'),
                                       ('other', 'Other')
                                   ],
                                   validators=[Optional()])
    
    # Budget Range
    budget_range = SelectField('Budget Range',
                              choices=[
                                  ('under_50k', 'Under ₦50,000'),
                                  ('50k_100k', '₦50,000 - ₦100,000'),
                                  ('100k_250k', '₦100,000 - ₦250,000'),
                                  ('250k_500k', '₦250,000 - ₦500,000'),
                                  ('500k_1m', '₦500,000 - ₦1,000,000'),
                                  ('1m_2m', '₦1,000,000 - ₦2,000,000'),
                                  ('above_2m', 'Above ₦2,000,000'),
                                  ('flexible', 'Flexible')
                              ],
                              validators=[Optional()])
    
    # Special Occasion
    occasion = SelectField('Special Occasion',
                          choices=[
                              ('engagement', 'Engagement'),
                              ('wedding', 'Wedding'),
                              ('anniversary', 'Anniversary'),
                              ('birthday', 'Birthday'),
                              ('graduation', 'Graduation'),
                              ('promotion', 'Promotion'),
                              ('gift', 'Gift'),
                              ('personal', 'Personal'),
                              ('other', 'Other')
                          ],
                          validators=[Optional()])
    
    # Design Details
    design_style = SelectField('Design Style',
                              choices=[
                                  ('traditional', 'Traditional Nigerian'),
                                  ('modern', 'Modern/Contemporary'),
                                  ('vintage', 'Vintage/Antique'),
                                  ('classic', 'Classic/Timeless'),
                                  ('minimalist', 'Minimalist'),
                                  ('ornate', 'Ornate/Elaborate'),
                                  ('mixed', 'Mixed Styles')
                              ],
                              validators=[Optional()])
    
    # Description and Requirements
    description = TextAreaField('Description/Requirements',
                               widget=TextArea(),
                               render_kw={'rows': 5, 'placeholder': 'Please describe your jewelry requirements, design ideas, or specific requests...'},
                               validators=[DataRequired(), Length(min=10, max=1000)])
    
    # Timeline
    timeline = SelectField('Timeline',
                          choices=[
                              ('rush', 'Rush (1-2 weeks)'),
                              ('standard', 'Standard (3-4 weeks)'),
                              ('flexible', 'Flexible (5-8 weeks)'),
                              ('no_rush', 'No Rush (8+ weeks)')
                          ],
                          validators=[Optional()])
    
    # Special Requirements
    engraving_required = BooleanField('Engraving Required')
    engraving_text = StringField('Engraving Text', validators=[Optional(), Length(max=100)])
    
    size_known = BooleanField('I know the size')
    ring_size = StringField('Ring Size (if applicable)', validators=[Optional(), Length(max=10)])
    
    # Consultation Preferences
    preferred_contact_method = SelectField('Preferred Contact Method',
                                         choices=[
                                             ('phone', 'Phone Call'),
                                             ('email', 'Email'),
                                             ('whatsapp', 'WhatsApp'),
                                             ('in_person', 'In-Person Meeting')
                                         ],
                                         validators=[Optional()])
    
    preferred_time = SelectField('Preferred Contact Time',
                               choices=[
                                   ('morning', 'Morning (9AM - 12PM)'),
                                   ('afternoon', 'Afternoon (12PM - 5PM)'),
                                   ('evening', 'Evening (5PM - 8PM)'),
                                   ('anytime', 'Anytime')
                               ],
                               validators=[Optional()])
    
    # File Uploads
    reference_images = FileField('Reference Images',
                               validators=[Optional(),
                                         FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'],
                                                   'Only image files are allowed!')])
    
    # Additional Information
    additional_notes = TextAreaField('Additional Notes',
                                   widget=TextArea(),
                                   render_kw={'rows': 3, 'placeholder': 'Any additional information or special requests...'},
                                   validators=[Optional(), Length(max=500)])

class JewelryQuoteRequestForm(FlaskForm):
    """Form for requesting jewelry quotes"""
    
    # Personal Information
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=200)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    
    # Quote Type
    quote_type = SelectField('Quote Type',
                           choices=[
                               ('purchase', 'Purchase Quote'),
                               ('custom_design', 'Custom Design Quote'),
                               ('repair', 'Repair Quote'),
                               ('appraisal', 'Appraisal Quote'),
                               ('insurance', 'Insurance Valuation')
                           ],
                           validators=[DataRequired()])
    
    # Item Details
    item_description = TextAreaField('Item Description',
                                   widget=TextArea(),
                                   render_kw={'rows': 4, 'placeholder': 'Please describe the jewelry item in detail...'},
                                   validators=[DataRequired(), Length(min=10, max=500)])
    
    # Specifications
    metal_type = SelectField('Metal Type',
                           choices=[
                               ('gold_18k', '18K Gold'),
                               ('gold_24k', '24K Gold'),
                               ('white_gold', 'White Gold'),
                               ('rose_gold', 'Rose Gold'),
                               ('platinum', 'Platinum'),
                               ('silver', 'Sterling Silver'),
                               ('other', 'Other'),
                               ('unknown', 'Unknown')
                           ],
                           validators=[Optional()])
    
    gemstone_details = TextAreaField('Gemstone Details',
                                   widget=TextArea(),
                                   render_kw={'rows': 2, 'placeholder': 'Type, size, quality of gemstones (if any)...'},
                                   validators=[Optional(), Length(max=300)])
    
    # Weight and Size
    weight_grams = DecimalField('Weight (grams)', validators=[Optional(), NumberRange(min=0)])
    dimensions = StringField('Dimensions', validators=[Optional(), Length(max=100)])
    
    # Images
    item_images = FileField('Item Images',
                          validators=[Optional(),
                                    FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'],
                                              'Only image files are allowed!')])
    
    # Additional Information
    additional_info = TextAreaField('Additional Information',
                                  widget=TextArea(),
                                  render_kw={'rows': 3, 'placeholder': 'Any additional details that might affect the quote...'},
                                  validators=[Optional(), Length(max=400)])
    
    # Urgency
    urgency = SelectField('Urgency',
                        choices=[
                            ('standard', 'Standard (3-5 business days)'),
                            ('urgent', 'Urgent (1-2 business days)'),
                            ('rush', 'Rush (Same day)')
                        ],
                        validators=[Optional()])