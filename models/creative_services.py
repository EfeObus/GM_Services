"""
Creative Services Models
Handles graphic design services and website/logo design projects
"""
from database import db
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

class CreativeServiceCategory(db.Model):
    """Categories of creative services"""
    
    __tablename__ = 'creative_service_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    service_type = db.Column(db.String(50))  # graphic_design, web_design, branding
    
    # Category Details
    typical_deliverables = db.Column(db.JSON)  # List of typical deliverables
    estimated_duration_days = db.Column(db.Integer)
    skill_requirements = db.Column(db.JSON)  # Required skills
    
    # Pricing
    base_price_range = db.Column(db.JSON)  # Min and max price range
    currency = db.Column(db.String(3), default='NGN')
    
    # Display
    icon = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = db.relationship('CreativeProject', backref='service_category', lazy='dynamic')
    
    def __repr__(self):
        return f'<CreativeServiceCategory {self.name}>'

class CreativeDesigner(db.Model):
    """Creative designers and their portfolios"""
    
    __tablename__ = 'creative_designers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Professional Details
    designer_name = db.Column(db.String(200))  # Professional/Studio name
    bio = db.Column(db.Text)
    specializations = db.Column(db.JSON)  # Areas of expertise
    experience_years = db.Column(db.Integer)
    
    # Contact Information
    professional_email = db.Column(db.String(120))
    website = db.Column(db.String(255))
    portfolio_url = db.Column(db.String(255))
    
    # Social Media
    instagram_handle = db.Column(db.String(100))
    behance_profile = db.Column(db.String(255))
    dribbble_profile = db.Column(db.String(255))
    linkedin_profile = db.Column(db.String(255))
    
    # Skills and Tools
    software_skills = db.Column(db.JSON)  # Adobe Creative Suite, Figma, etc.
    design_styles = db.Column(db.JSON)    # Modern, vintage, minimalist, etc.
    
    # Availability
    is_available = db.Column(db.Boolean, default=True)
    availability_schedule = db.Column(db.JSON)  # Weekly availability
    
    # Pricing
    hourly_rate = db.Column(db.Numeric(6, 2))
    project_rate_range = db.Column(db.JSON)  # Min and max project rates
    rush_fee_percentage = db.Column(db.Float, default=50)  # Rush job fee
    
    # Performance Metrics
    total_projects_completed = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0.0)
    on_time_delivery_rate = db.Column(db.Float, default=100.0)
    client_satisfaction_rate = db.Column(db.Float, default=100.0)
    
    # Certifications
    certifications = db.Column(db.JSON)
    awards = db.Column(db.JSON)
    
    # Status
    status = db.Column(db.String(30), default='active')  # active, busy, unavailable, inactive
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='designer_profile')
    projects = db.relationship('CreativeProject', backref='assigned_designer', lazy='dynamic')
    portfolio_items = db.relationship('PortfolioItem', backref='designer', lazy='dynamic')
    
    def __repr__(self):
        return f'<CreativeDesigner {self.designer_name or self.user.full_name}>'

class PortfolioItem(db.Model):
    """Portfolio items showcasing designer work"""
    
    __tablename__ = 'portfolio_items'
    
    id = db.Column(db.Integer, primary_key=True)
    designer_id = db.Column(db.Integer, db.ForeignKey('creative_designers.id'), nullable=False)
    
    # Portfolio Item Details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    project_type = db.Column(db.String(50))  # logo, website, brochure, etc.
    
    # Client Information (Optional)
    client_name = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    
    # Media
    featured_image = db.Column(db.String(255))
    additional_images = db.Column(db.JSON)
    video_url = db.Column(db.String(255))
    
    # Project Details
    completion_date = db.Column(db.Date)
    project_duration = db.Column(db.Integer)  # Days
    tools_used = db.Column(db.JSON)
    design_approach = db.Column(db.Text)
    
    # Display Settings
    is_featured = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    
    # Tags and Categories
    tags = db.Column(db.JSON)
    categories = db.Column(db.JSON)
    
    # Visibility
    is_public = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PortfolioItem {self.title}>'

class CreativeProject(db.Model):
    """Creative design projects"""
    
    __tablename__ = 'creative_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Project Basic Information
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_category_id = db.Column(db.Integer, db.ForeignKey('creative_service_categories.id'), nullable=False)
    designer_id = db.Column(db.Integer, db.ForeignKey('creative_designers.id'))
    
    # Project Details
    project_title = db.Column(db.String(200), nullable=False)
    project_description = db.Column(db.Text, nullable=False)
    project_type = db.Column(db.String(50))  # logo_design, website, brochure, etc.
    
    # Client Brief
    target_audience = db.Column(db.Text)
    brand_guidelines = db.Column(db.Text)
    preferred_colors = db.Column(db.JSON)
    preferred_styles = db.Column(db.JSON)
    reference_materials = db.Column(db.JSON)  # URLs or file paths
    
    # Requirements
    deliverables = db.Column(db.JSON)  # List of expected deliverables
    file_formats_required = db.Column(db.JSON)  # AI, PSD, PNG, etc.
    dimensions_specs = db.Column(db.JSON)  # Size requirements
    
    # Timeline
    requested_start_date = db.Column(db.Date)
    requested_completion_date = db.Column(db.Date, nullable=False)
    actual_start_date = db.Column(db.Date)
    actual_completion_date = db.Column(db.Date)
    
    # Priority and Rush Jobs
    priority_level = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    is_rush_job = db.Column(db.Boolean, default=False)
    rush_reason = db.Column(db.Text)
    
    # Project Status
    status = db.Column(db.String(30), default='pending')  # pending, assigned, in_progress, review, revision, completed, cancelled
    progress_percentage = db.Column(db.Integer, default=0)
    
    # Pricing
    quoted_price = db.Column(db.Numeric(10, 2))
    final_price = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='NGN')
    
    # Payment
    payment_status = db.Column(db.String(30), default='pending')  # pending, partial, paid
    deposit_amount = db.Column(db.Numeric(8, 2))
    deposit_paid = db.Column(db.Boolean, default=False)
    
    # Revisions
    max_revisions_included = db.Column(db.Integer, default=3)
    revisions_used = db.Column(db.Integer, default=0)
    revision_fee_per_round = db.Column(db.Numeric(6, 2))
    
    # Communication
    client_notes = db.Column(db.Text)
    designer_notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    
    # Quality Assurance
    qa_approved = db.Column(db.Boolean, default=False)
    qa_notes = db.Column(db.Text)
    qa_approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Client Feedback
    client_rating = db.Column(db.Integer)  # 1-5 stars
    client_feedback = db.Column(db.Text)
    would_recommend = db.Column(db.Boolean)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('User', foreign_keys=[client_id], backref='creative_projects')
    qa_approver = db.relationship('User', foreign_keys=[qa_approved_by_id], backref='qa_approved_projects')
    deliverables_files = db.relationship('ProjectDeliverable', backref='project', lazy='dynamic')
    revisions = db.relationship('ProjectRevision', backref='project', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(CreativeProject, self).__init__(**kwargs)
        if not self.project_number:
            self.project_number = self.generate_project_number()
    
    @staticmethod
    def generate_project_number():
        """Generate unique project number"""
        prefix = "CRT"
        timestamp = datetime.now().strftime("%y%m")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<CreativeProject {self.project_number} - {self.project_title}>'
    
    @property
    def is_overdue(self):
        """Check if project is overdue"""
        if self.status in ['completed', 'cancelled']:
            return False
        return date.today() > self.requested_completion_date

class ProjectDeliverable(db.Model):
    """Files and deliverables for creative projects"""
    
    __tablename__ = 'project_deliverables'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('creative_projects.id'), nullable=False)
    
    # File Information
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))  # ai, psd, png, jpg, pdf, etc.
    file_size = db.Column(db.Integer)  # File size in bytes
    
    # Deliverable Details
    deliverable_type = db.Column(db.String(50))  # final, draft, revision, source_file
    version_number = db.Column(db.String(20), default='1.0')
    description = db.Column(db.Text)
    
    # Specifications
    dimensions = db.Column(db.String(100))  # Width x Height
    resolution = db.Column(db.String(50))   # DPI/PPI
    color_mode = db.Column(db.String(20))   # RGB, CMYK
    
    # Status
    status = db.Column(db.String(30), default='draft')  # draft, review, approved, final
    is_final_version = db.Column(db.Boolean, default=False)
    
    # Client Access
    client_accessible = db.Column(db.Boolean, default=False)
    download_count = db.Column(db.Integer, default=0)
    last_downloaded = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProjectDeliverable {self.file_name}>'

class ProjectRevision(db.Model):
    """Project revision requests and feedback"""
    
    __tablename__ = 'project_revisions'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('creative_projects.id'), nullable=False)
    
    # Revision Details
    revision_number = db.Column(db.Integer, nullable=False)
    requested_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Feedback
    feedback_text = db.Column(db.Text, nullable=False)
    specific_changes = db.Column(db.JSON)  # Detailed change requests
    
    # Priority
    urgency = db.Column(db.String(20), default='normal')  # low, normal, high
    
    # Files
    reference_files = db.Column(db.JSON)  # Files uploaded with feedback
    
    # Response
    designer_response = db.Column(db.Text)
    estimated_completion_date = db.Column(db.Date)
    actual_completion_date = db.Column(db.Date)
    
    # Status
    status = db.Column(db.String(30), default='pending')  # pending, in_progress, completed, rejected
    
    # Additional Charges
    additional_fee = db.Column(db.Numeric(6, 2), default=0)
    fee_approved = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requested_by = db.relationship('User', backref='requested_revisions')
    
    def __repr__(self):
        return f'<ProjectRevision {self.project.project_number} - R{self.revision_number}>'

class CreativeTemplate(db.Model):
    """Pre-designed templates for quick projects"""
    
    __tablename__ = 'creative_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Template Details
    template_type = db.Column(db.String(50))  # logo, business_card, flyer, website
    category = db.Column(db.String(100))
    style_tags = db.Column(db.JSON)  # modern, vintage, minimalist, etc.
    
    # Media
    preview_image = db.Column(db.String(255))
    additional_previews = db.Column(db.JSON)
    template_files = db.Column(db.JSON)  # Source files
    
    # Customization
    customizable_elements = db.Column(db.JSON)  # What can be customized
    customization_complexity = db.Column(db.String(20))  # easy, medium, complex
    
    # Pricing
    base_price = db.Column(db.Numeric(8, 2))
    customization_fee = db.Column(db.Numeric(6, 2))
    currency = db.Column(db.String(3), default='NGN')
    
    # Usage Rights
    license_type = db.Column(db.String(50))  # personal, commercial, extended
    usage_restrictions = db.Column(db.Text)
    
    # Popularity
    download_count = db.Column(db.Integer, default=0)
    usage_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Designer Information
    designer_id = db.Column(db.Integer, db.ForeignKey('creative_designers.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    designer = db.relationship('CreativeDesigner', backref='created_templates')
    
    def __repr__(self):
        return f'<CreativeTemplate {self.name}>'

class WebsiteProject(db.Model):
    """Website development projects"""
    
    __tablename__ = 'website_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Project Details
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    designer_id = db.Column(db.Integer, db.ForeignKey('creative_designers.id'))
    
    # Website Information
    website_name = db.Column(db.String(200), nullable=False)
    website_purpose = db.Column(db.Text)
    target_audience = db.Column(db.Text)
    
    # Website Type
    website_type = db.Column(db.String(50))  # business, portfolio, ecommerce, blog
    platform = db.Column(db.String(50))     # wordpress, custom, react, etc.
    
    # Requirements
    pages_required = db.Column(db.JSON)     # List of pages needed
    features_required = db.Column(db.JSON)  # Contact forms, galleries, etc.
    integrations_needed = db.Column(db.JSON) # Social media, payment, etc.
    
    # Design Preferences
    preferred_colors = db.Column(db.JSON)
    design_style = db.Column(db.String(100)) # modern, classic, minimalist
    reference_websites = db.Column(db.JSON)
    
    # Content
    content_provided = db.Column(db.Boolean, default=False)
    content_writing_needed = db.Column(db.Boolean, default=False)
    images_provided = db.Column(db.Boolean, default=False)
    
    # Technical Requirements
    hosting_required = db.Column(db.Boolean, default=False)
    domain_required = db.Column(db.Boolean, default=False)
    ssl_required = db.Column(db.Boolean, default=True)
    mobile_responsive = db.Column(db.Boolean, default=True)
    seo_optimization = db.Column(db.Boolean, default=True)
    
    # Timeline
    requested_completion_date = db.Column(db.Date, nullable=False)
    actual_completion_date = db.Column(db.Date)
    launch_date = db.Column(db.Date)
    
    # Status
    status = db.Column(db.String(30), default='planning')  # planning, design, development, testing, launched
    progress_percentage = db.Column(db.Integer, default=0)
    
    # Pricing
    quoted_price = db.Column(db.Numeric(12, 2))
    final_price = db.Column(db.Numeric(12, 2))
    monthly_maintenance_fee = db.Column(db.Numeric(6, 2))
    currency = db.Column(db.String(3), default='NGN')
    
    # URLs
    staging_url = db.Column(db.String(255))
    live_url = db.Column(db.String(255))
    admin_url = db.Column(db.String(255))
    
    # Maintenance
    maintenance_included = db.Column(db.Boolean, default=False)
    maintenance_period_months = db.Column(db.Integer, default=6)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('User', backref='website_projects')
    assigned_designer = db.relationship('CreativeDesigner', backref='website_projects')
    
    def __init__(self, **kwargs):
        super(WebsiteProject, self).__init__(**kwargs)
        if not self.project_number:
            self.project_number = self.generate_project_number()
    
    @staticmethod
    def generate_project_number():
        """Generate unique project number"""
        prefix = "WEB"
        timestamp = datetime.now().strftime("%y%m")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<WebsiteProject {self.project_number} - {self.website_name}>'