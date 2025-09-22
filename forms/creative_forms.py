"""
Creative Services Forms
Forms for graphic design, web design, and creative project requests
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import (
    StringField, TextAreaField, SelectField, IntegerField, DecimalField,
    BooleanField, DateField, SelectMultipleField, RadioField, HiddenField,
    FieldList, FormField
)
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Email, URL
from wtforms.widgets import CheckboxInput, ListWidget
from models.creative_services import CreativeServiceCategory
from data.nigeria_data import NIGERIAN_STATES
from datetime import datetime, timedelta


class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class CreativeProjectForm(FlaskForm):
    """Base form for creative projects"""
    
    # Project Basic Information
    project_title = StringField(
        'Project Title',
        validators=[DataRequired(), Length(min=3, max=200)],
        render_kw={'placeholder': 'Enter a descriptive title for your project'}
    )
    
    project_description = TextAreaField(
        'Project Description',
        validators=[DataRequired(), Length(min=10, max=2000)],
        render_kw={
            'placeholder': 'Describe your project in detail. What are you looking to create?',
            'rows': 4
        }
    )
    
    project_type = SelectField(
        'Project Type',
        validators=[DataRequired()],
        choices=[
            ('logo_design', 'Logo Design'),
            ('brand_identity', 'Brand Identity Package'),
            ('business_card', 'Business Card Design'),
            ('brochure', 'Brochure/Flyer Design'),
            ('poster', 'Poster/Banner Design'),
            ('packaging', 'Packaging Design'),
            ('social_media', 'Social Media Graphics'),
            ('web_banner', 'Web Banner/Header'),
            ('presentation', 'Presentation Design'),
            ('other', 'Other (Specify in description)')
        ]
    )
    
    # Timeline
    requested_completion_date = DateField(
        'Completion Date',
        validators=[DataRequired()],
        default=datetime.now() + timedelta(days=7)
    )
    
    is_rush_job = BooleanField(
        'Rush Job (Additional fees may apply)',
        default=False
    )
    
    rush_reason = TextAreaField(
        'Rush Reason',
        validators=[Optional(), Length(max=500)],
        render_kw={'placeholder': 'Please explain why this is urgent'}
    )
    
    # Budget
    budget_range = SelectField(
        'Budget Range',
        validators=[DataRequired()],
        choices=[
            ('5000-15000', '₦5,000 - ₦15,000'),
            ('15000-30000', '₦15,000 - ₦30,000'),
            ('30000-50000', '₦30,000 - ₦50,000'),
            ('50000-100000', '₦50,000 - ₦100,000'),
            ('100000+', '₦100,000+'),
            ('custom', 'Custom (Discuss with designer)')
        ]
    )
    
    # Client Information
    company_name = StringField(
        'Company/Organization Name',
        validators=[Optional(), Length(max=200)],
        render_kw={'placeholder': 'Leave blank if personal project'}
    )
    
    industry = StringField(
        'Industry/Sector',
        validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': 'e.g., Healthcare, Technology, Retail'}
    )
    
    # Target Audience
    target_audience = TextAreaField(
        'Target Audience',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Describe your target audience (age, gender, interests, etc.)',
            'rows': 3
        }
    )
    
    # Design Preferences
    preferred_colors = StringField(
        'Preferred Colors',
        validators=[Optional(), Length(max=200)],
        render_kw={'placeholder': 'e.g., Blue, Red, Corporate colors, No preference'}
    )
    
    design_style = MultiCheckboxField(
        'Design Style Preferences',
        choices=[
            ('modern', 'Modern/Contemporary'),
            ('classic', 'Classic/Traditional'),
            ('minimalist', 'Minimalist'),
            ('bold', 'Bold/Vibrant'),
            ('elegant', 'Elegant/Sophisticated'),
            ('playful', 'Playful/Fun'),
            ('professional', 'Professional/Corporate'),
            ('vintage', 'Vintage/Retro')
        ]
    )
    
    # Deliverables
    file_formats = MultiCheckboxField(
        'Required File Formats',
        choices=[
            ('png', 'PNG (Web/Digital use)'),
            ('jpg', 'JPEG (Web/Print)'),
            ('pdf', 'PDF (Print ready)'),
            ('ai', 'Adobe Illustrator (Source file)'),
            ('psd', 'Photoshop (Source file)'),
            ('eps', 'EPS (Vector format)'),
            ('svg', 'SVG (Web vector)')
        ],
        default=['png', 'pdf']
    )
    
    # Special Requirements
    brand_guidelines = TextAreaField(
        'Existing Brand Guidelines',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Do you have existing brand guidelines, fonts, or style requirements?',
            'rows': 3
        }
    )
    
    # Reference Materials
    reference_notes = TextAreaField(
        'Reference Materials/Inspiration',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Describe any examples, competitors, or styles you like/dislike',
            'rows': 3
        }
    )
    
    reference_files = MultipleFileField(
        'Upload Reference Files',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'pdf', 'ai', 'psd'], 
                       'Only image and design files allowed!')
        ]
    )
    
    # Communication Preferences
    preferred_contact = SelectField(
        'Preferred Contact Method',
        validators=[DataRequired()],
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('whatsapp', 'WhatsApp'),
            ('platform', 'Platform Messages')
        ],
        default='email'
    )
    
    # Additional Notes
    additional_notes = TextAreaField(
        'Additional Notes',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Any other important information about your project',
            'rows': 3
        }
    )


class LogoDesignForm(CreativeProjectForm):
    """Specialized form for logo design projects"""
    
    # Logo-specific fields
    logo_type = SelectField(
        'Logo Type',
        validators=[DataRequired()],
        choices=[
            ('text_only', 'Text/Wordmark Only'),
            ('symbol_only', 'Symbol/Icon Only'),
            ('combination', 'Text + Symbol Combination'),
            ('emblem', 'Emblem/Badge Style'),
            ('not_sure', 'Not Sure (Designer\'s recommendation)')
        ]
    )
    
    logo_usage = MultiCheckboxField(
        'Where will the logo be used?',
        choices=[
            ('business_cards', 'Business Cards'),
            ('letterhead', 'Letterhead/Stationery'),
            ('website', 'Website'),
            ('social_media', 'Social Media'),
            ('signage', 'Signage/Storefront'),
            ('merchandise', 'Merchandise/Apparel'),
            ('vehicle', 'Vehicle Graphics'),
            ('advertising', 'Print Advertising')
        ]
    )
    
    company_description = TextAreaField(
        'Company Description',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Briefly describe what your company does and its values',
            'rows': 3
        }
    )
    
    competitors = StringField(
        'Main Competitors',
        validators=[Optional(), Length(max=300)],
        render_kw={'placeholder': 'List 2-3 main competitors (helps avoid similar designs)'}
    )


class BrandingForm(CreativeProjectForm):
    """Form for complete branding packages"""
    
    # Branding-specific fields
    branding_scope = MultiCheckboxField(
        'Branding Package Includes',
        choices=[
            ('logo', 'Logo Design'),
            ('color_palette', 'Color Palette'),
            ('typography', 'Typography/Fonts'),
            ('business_cards', 'Business Card Design'),
            ('letterhead', 'Letterhead Design'),
            ('brand_guidelines', 'Brand Guidelines Document'),
            ('social_media_kit', 'Social Media Kit'),
            ('email_signature', 'Email Signature'),
            ('presentation_template', 'Presentation Template')
        ],
        default=['logo', 'color_palette', 'typography', 'business_cards']
    )
    
    business_stage = SelectField(
        'Business Stage',
        validators=[DataRequired()],
        choices=[
            ('startup', 'Startup/New Business'),
            ('established', 'Established Business'),
            ('rebranding', 'Rebranding Existing Business'),
            ('expansion', 'Business Expansion')
        ]
    )
    
    brand_personality = MultiCheckboxField(
        'Desired Brand Personality',
        choices=[
            ('professional', 'Professional'),
            ('friendly', 'Friendly/Approachable'),
            ('innovative', 'Innovative/Cutting-edge'),
            ('trustworthy', 'Trustworthy/Reliable'),
            ('luxurious', 'Luxurious/Premium'),
            ('creative', 'Creative/Artistic'),
            ('energetic', 'Energetic/Dynamic'),
            ('calm', 'Calm/Peaceful')
        ]
    )


class PrintDesignForm(CreativeProjectForm):
    """Form for print design projects"""
    
    # Print-specific fields
    print_type = SelectField(
        'Print Material Type',
        validators=[DataRequired()],
        choices=[
            ('brochure', 'Brochure'),
            ('flyer', 'Flyer/Leaflet'),
            ('poster', 'Poster'),
            ('banner', 'Banner'),
            ('business_card', 'Business Card'),
            ('catalog', 'Catalog'),
            ('annual_report', 'Annual Report'),
            ('magazine', 'Magazine/Newsletter'),
            ('packaging', 'Packaging'),
            ('menu', 'Menu Design'),
            ('invitation', 'Invitation/Event Card'),
            ('other', 'Other (Specify)')
        ]
    )
    
    print_dimensions = StringField(
        'Print Dimensions',
        validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': 'e.g., A4, 8.5x11 inches, Custom size'}
    )
    
    print_quantity = IntegerField(
        'Expected Print Quantity',
        validators=[Optional(), NumberRange(min=1, max=1000000)],
        render_kw={'placeholder': '100'}
    )
    
    print_method = SelectField(
        'Printing Method',
        validators=[Optional()],
        choices=[
            ('', 'Not Sure'),
            ('digital', 'Digital Printing'),
            ('offset', 'Offset Printing'),
            ('large_format', 'Large Format Printing'),
            ('screen', 'Screen Printing')
        ]
    )
    
    pages_count = IntegerField(
        'Number of Pages/Sides',
        validators=[Optional(), NumberRange(min=1, max=200)],
        default=1
    )
    
    color_specification = SelectField(
        'Color Specification',
        validators=[Optional()],
        choices=[
            ('', 'Not Sure'),
            ('full_color', 'Full Color (CMYK)'),
            ('black_white', 'Black & White'),
            ('spot_color', 'Spot Colors'),
            ('pantone', 'Pantone Colors')
        ]
    )


class DigitalDesignForm(CreativeProjectForm):
    """Form for digital design projects"""
    
    # Digital-specific fields
    digital_type = SelectField(
        'Digital Design Type',
        validators=[DataRequired()],
        choices=[
            ('social_media', 'Social Media Graphics'),
            ('web_banner', 'Web Banner/Header'),
            ('email_template', 'Email Template'),
            ('presentation', 'Presentation Design'),
            ('infographic', 'Infographic'),
            ('digital_ad', 'Digital Advertisement'),
            ('app_graphics', 'App/Mobile Graphics'),
            ('web_graphics', 'Website Graphics'),
            ('other', 'Other Digital Graphics')
        ]
    )
    
    digital_platforms = MultiCheckboxField(
        'Target Platforms',
        choices=[
            ('facebook', 'Facebook'),
            ('instagram', 'Instagram'),
            ('twitter', 'Twitter/X'),
            ('linkedin', 'LinkedIn'),
            ('youtube', 'YouTube'),
            ('tiktok', 'TikTok'),
            ('website', 'Website'),
            ('email', 'Email Marketing'),
            ('google_ads', 'Google Ads'),
            ('print_digital', 'Print & Digital Use')
        ]
    )
    
    dimensions_needed = MultiCheckboxField(
        'Dimensions/Sizes Needed',
        choices=[
            ('square', 'Square (1080x1080)'),
            ('story', 'Story/Portrait (1080x1920)'),
            ('landscape', 'Landscape (1920x1080)'),
            ('banner', 'Banner (Various sizes)'),
            ('profile', 'Profile/Cover Images'),
            ('custom', 'Custom Dimensions'),
            ('multiple', 'Multiple Sizes')
        ]
    )
    
    animation_needed = BooleanField(
        'Animation/Motion Graphics Needed',
        default=False
    )
    
    content_provided = SelectField(
        'Content Provided By',
        validators=[DataRequired()],
        choices=[
            ('client', 'I will provide all text/content'),
            ('designer', 'Designer to create content'),
            ('collaborate', 'Collaborative content creation')
        ]
    )


class WebsiteDesignForm(FlaskForm):
    """Form for website design projects"""
    
    # Website Basic Information
    website_name = StringField(
        'Website/Business Name',
        validators=[DataRequired(), Length(min=2, max=200)],
        render_kw={'placeholder': 'Your business or website name'}
    )
    
    website_description = TextAreaField(
        'Website Description',
        validators=[DataRequired(), Length(min=10, max=2000)],
        render_kw={
            'placeholder': 'Describe what your website is for and what it should accomplish',
            'rows': 4
        }
    )
    
    website_type = SelectField(
        'Website Type',
        validators=[DataRequired()],
        choices=[
            ('business', 'Business Website'),
            ('ecommerce', 'E-commerce Store'),
            ('portfolio', 'Portfolio Website'),
            ('blog', 'Blog/News Site'),
            ('landing', 'Landing Page'),
            ('nonprofit', 'Non-profit Organization'),
            ('personal', 'Personal Website'),
            ('service', 'Service-based Business'),
            ('restaurant', 'Restaurant/Food Business'),
            ('real_estate', 'Real Estate'),
            ('education', 'Educational Institution'),
            ('other', 'Other (Specify)')
        ]
    )
    
    # Domain and Hosting
    domain_name = StringField(
        'Preferred Domain Name',
        validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': 'e.g., yourwebsite.com (optional)'}
    )
    
    existing_website = StringField(
        'Existing Website URL',
        validators=[Optional(), URL()],
        render_kw={'placeholder': 'If you have a current website to redesign'}
    )
    
    # Website Features
    website_features = MultiCheckboxField(
        'Required Features',
        choices=[
            ('contact_form', 'Contact Form'),
            ('blog', 'Blog/News Section'),
            ('gallery', 'Photo Gallery'),
            ('testimonials', 'Customer Testimonials'),
            ('about_page', 'About Us Page'),
            ('services_page', 'Services/Products Page'),
            ('booking', 'Online Booking System'),
            ('payment', 'Payment Integration'),
            ('user_accounts', 'User Registration/Login'),
            ('search', 'Search Functionality'),
            ('multilingual', 'Multiple Languages'),
            ('social_media', 'Social Media Integration'),
            ('newsletter', 'Newsletter Signup'),
            ('chat', 'Live Chat'),
            ('analytics', 'Analytics Integration')
        ]
    )
    
    # E-commerce specific
    ecommerce_products = IntegerField(
        'Number of Products (for e-commerce)',
        validators=[Optional(), NumberRange(min=1, max=10000)],
        render_kw={'placeholder': 'Approximate number of products'}
    )
    
    payment_methods = MultiCheckboxField(
        'Payment Methods Needed',
        choices=[
            ('paystack', 'Paystack'),
            ('flutterwave', 'Flutterwave'),
            ('bank_transfer', 'Bank Transfer'),
            ('paypal', 'PayPal'),
            ('stripe', 'Stripe'),
            ('pos', 'POS Integration'),
            ('other', 'Other Payment Gateway')
        ]
    )
    
    # Content and Pages
    page_count = SelectField(
        'Estimated Number of Pages',
        validators=[DataRequired()],
        choices=[
            ('1-5', '1-5 pages'),
            ('6-10', '6-10 pages'),
            ('11-20', '11-20 pages'),
            ('21-50', '21-50 pages'),
            ('50+', '50+ pages')
        ]
    )
    
    content_ready = SelectField(
        'Content Readiness',
        validators=[DataRequired()],
        choices=[
            ('ready', 'All content is ready'),
            ('partial', 'Some content is ready'),
            ('need_help', 'Need help with content creation'),
            ('copywriting', 'Need professional copywriting')
        ]
    )
    
    # Design Preferences
    design_inspiration = TextAreaField(
        'Design Inspiration',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Share links to websites you like or describe your vision',
            'rows': 3
        }
    )
    
    color_scheme = StringField(
        'Color Scheme Preferences',
        validators=[Optional(), Length(max=200)],
        render_kw={'placeholder': 'Brand colors or preferred color combinations'}
    )
    
    # Technical Requirements
    mobile_responsive = BooleanField(
        'Mobile Responsive Design Required',
        default=True
    )
    
    seo_optimization = BooleanField(
        'SEO Optimization Required',
        default=True
    )
    
    # Timeline and Budget
    launch_date = DateField(
        'Desired Launch Date',
        validators=[Optional()],
        default=datetime.now() + timedelta(days=30)
    )
    
    budget_range = SelectField(
        'Budget Range',
        validators=[DataRequired()],
        choices=[
            ('50000-100000', '₦50,000 - ₦100,000'),
            ('100000-200000', '₦100,000 - ₦200,000'),
            ('200000-500000', '₦200,000 - ₦500,000'),
            ('500000-1000000', '₦500,000 - ₦1,000,000'),
            ('1000000+', '₦1,000,000+'),
            ('custom', 'Custom (Discuss with developer)')
        ]
    )
    
    # Maintenance
    maintenance_needed = SelectField(
        'Ongoing Maintenance',
        validators=[DataRequired()],
        choices=[
            ('yes', 'Yes, I need ongoing maintenance'),
            ('no', 'No, one-time project only'),
            ('discuss', 'Let\'s discuss options')
        ]
    )
    
    # Additional Requirements
    hosting_help = BooleanField(
        'Need Help with Hosting Setup',
        default=False
    )
    
    training_needed = BooleanField(
        'Need Training on Website Management',
        default=False
    )
    
    # Contact and Communication
    preferred_contact = SelectField(
        'Preferred Contact Method',
        validators=[DataRequired()],
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('whatsapp', 'WhatsApp'),
            ('platform', 'Platform Messages')
        ],
        default='email'
    )
    
    additional_notes = TextAreaField(
        'Additional Requirements',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Any other specific requirements or questions',
            'rows': 3
        }
    )


class QuickQuoteForm(FlaskForm):
    """Quick quote form for simple design requests"""
    
    service_type = SelectField(
        'Service Type',
        validators=[DataRequired()],
        choices=[
            ('logo', 'Logo Design'),
            ('business_card', 'Business Card'),
            ('flyer', 'Flyer/Brochure'),
            ('social_media', 'Social Media Graphics'),
            ('website', 'Website Design'),
            ('other', 'Other Design Service')
        ]
    )
    
    project_description = TextAreaField(
        'Brief Description',
        validators=[DataRequired(), Length(min=10, max=500)],
        render_kw={
            'placeholder': 'Briefly describe what you need designed',
            'rows': 3
        }
    )
    
    timeline = SelectField(
        'Timeline',
        validators=[DataRequired()],
        choices=[
            ('1-3', '1-3 days'),
            ('1-week', '1 week'),
            ('2-weeks', '2 weeks'),
            ('1-month', '1 month'),
            ('flexible', 'Flexible')
        ]
    )
    
    budget = SelectField(
        'Budget Range',
        validators=[DataRequired()],
        choices=[
            ('5000-15000', '₦5,000 - ₦15,000'),
            ('15000-30000', '₦15,000 - ₦30,000'),
            ('30000-50000', '₦30,000 - ₦50,000'),
            ('50000+', '₦50,000+')
        ]
    )
    
    contact_method = SelectField(
        'Preferred Contact',
        validators=[DataRequired()],
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('whatsapp', 'WhatsApp')
        ],
        default='email'
    )