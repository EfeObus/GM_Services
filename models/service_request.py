"""
Service Request Form Models
Handles general service requests and inquiries for GM Services
"""
from database import db
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

class ServiceRequestType(db.Model):
    """Types of service requests"""
    
    __tablename__ = 'service_request_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # inquiry, complaint, support, quote_request
    
    # Service Association
    related_services = db.Column(db.JSON)  # Which GM services this applies to
    
    # Processing Details
    typical_response_time_hours = db.Column(db.Integer, default=24)
    requires_approval = db.Column(db.Boolean, default=False)
    auto_assign_department = db.Column(db.String(100))
    
    # Form Configuration
    required_fields = db.Column(db.JSON)  # List of required form fields
    optional_fields = db.Column(db.JSON)  # List of optional form fields
    
    # Priority Handling
    default_priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    escalation_rules = db.Column(db.JSON)  # Auto-escalation rules
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Display
    display_order = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='request_type', lazy='dynamic')
    
    def __repr__(self):
        return f'<ServiceRequestType {self.name}>'

class ServiceRequest(db.Model):
    """Individual service requests and inquiries"""
    
    __tablename__ = 'service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Request Details
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    request_type_id = db.Column(db.Integer, db.ForeignKey('service_request_types.id'), nullable=False)
    
    # Subject and Description
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Service Context
    related_service = db.Column(db.String(50))  # automobile, hotel, jewelry, etc.
    related_service_id = db.Column(db.Integer)  # ID of related service record
    related_order_number = db.Column(db.String(50))  # Related order/booking
    
    # Customer Information
    customer_name = db.Column(db.String(200))
    customer_email = db.Column(db.String(120))
    customer_phone = db.Column(db.String(20))
    preferred_contact_method = db.Column(db.String(20), default='email')  # email, phone, sms
    
    # Location Information
    customer_state = db.Column(db.String(50))
    customer_city = db.Column(db.String(100))
    customer_address = db.Column(db.Text)
    
    # Request Specifics
    urgency = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    preferred_response_time = db.Column(db.String(50))  # within_1_hour, within_24_hours, within_week
    
    # Form Data
    form_data = db.Column(db.JSON)  # Additional form fields specific to request type
    
    # Attachments
    attachment_urls = db.Column(db.JSON)  # List of uploaded file URLs
    attachment_descriptions = db.Column(db.JSON)  # Descriptions for each attachment
    
    # Status and Assignment
    status = db.Column(db.String(30), default='submitted')  # submitted, assigned, in_progress, resolved, closed
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_department = db.Column(db.String(100))
    
    # Processing Timeline
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime)
    assigned_at = db.Column(db.DateTime)
    first_response_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    
    # SLA Tracking
    response_sla_hours = db.Column(db.Integer, default=24)
    resolution_sla_hours = db.Column(db.Integer, default=72)
    sla_breached = db.Column(db.Boolean, default=False)
    
    # Resolution
    resolution_summary = db.Column(db.Text)
    resolution_notes = db.Column(db.Text)
    actions_taken = db.Column(db.JSON)  # List of actions taken
    
    # Customer Satisfaction
    satisfaction_rating = db.Column(db.Integer)  # 1-5 stars
    satisfaction_feedback = db.Column(db.Text)
    would_recommend = db.Column(db.Boolean)
    
    # Follow-up
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date)
    follow_up_notes = db.Column(db.Text)
    
    # Escalation
    escalation_level = db.Column(db.Integer, default=0)
    escalated_at = db.Column(db.DateTime)
    escalated_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    escalation_reason = db.Column(db.Text)
    
    # Communication
    last_customer_contact = db.Column(db.DateTime)
    total_interactions = db.Column(db.Integer, default=0)
    
    # Internal Notes
    internal_notes = db.Column(db.Text)
    tags = db.Column(db.JSON)  # Tags for categorization
    
    # Source
    source_channel = db.Column(db.String(50), default='web')  # web, mobile, phone, email, chat
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='service_requests')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_requests')
    escalated_to = db.relationship('User', foreign_keys=[escalated_to_id], backref='escalated_requests')
    interactions = db.relationship('ServiceRequestInteraction', backref='service_request', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(ServiceRequest, self).__init__(**kwargs)
        if not self.request_number:
            self.request_number = self.generate_request_number()
    
    @staticmethod
    def generate_request_number():
        """Generate unique request number"""
        prefix = "SR"
        timestamp = datetime.now().strftime("%y%m%d")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<ServiceRequest {self.request_number} - {self.subject}>'
    
    @property
    def is_overdue(self):
        """Check if request is overdue based on SLA"""
        if self.status in ['resolved', 'closed']:
            return False
        
        hours_since_submission = (datetime.utcnow() - self.submitted_at).total_seconds() / 3600
        
        # Check response SLA
        if not self.first_response_at and hours_since_submission > self.response_sla_hours:
            return True
        
        # Check resolution SLA
        if hours_since_submission > self.resolution_sla_hours:
            return True
        
        return False
    
    @property
    def response_time_hours(self):
        """Calculate response time in hours"""
        if self.first_response_at:
            return (self.first_response_at - self.submitted_at).total_seconds() / 3600
        return None
    
    @property
    def resolution_time_hours(self):
        """Calculate resolution time in hours"""
        if self.resolved_at:
            return (self.resolved_at - self.submitted_at).total_seconds() / 3600
        return None

class ServiceRequestInteraction(db.Model):
    """Interactions/communications related to service requests"""
    
    __tablename__ = 'service_request_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id'), nullable=False)
    
    # Interaction Details
    interaction_type = db.Column(db.String(50), nullable=False)  # email, phone, chat, internal_note
    direction = db.Column(db.String(20), nullable=False)  # inbound, outbound
    
    # Participants
    staff_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    customer_contacted = db.Column(db.Boolean, default=False)
    
    # Content
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    
    # Communication Details
    duration_minutes = db.Column(db.Integer)  # For phone calls
    communication_method = db.Column(db.String(50))  # email, phone, sms, chat
    
    # Status Changes
    status_before = db.Column(db.String(30))
    status_after = db.Column(db.String(30))
    status_changed = db.Column(db.Boolean, default=False)
    
    # Attachments
    attachment_urls = db.Column(db.JSON)
    
    # Visibility
    visible_to_customer = db.Column(db.Boolean, default=True)
    is_internal_note = db.Column(db.Boolean, default=False)
    
    # Timing
    interaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    staff_user = db.relationship('User', backref='service_interactions')
    
    def __repr__(self):
        return f'<ServiceRequestInteraction {self.service_request.request_number} - {self.interaction_type}>'

class ServiceRequestTemplate(db.Model):
    """Templates for common service request responses"""
    
    __tablename__ = 'service_request_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Template Details
    template_type = db.Column(db.String(50))  # acknowledgment, resolution, follow_up
    service_types = db.Column(db.JSON)  # Which services this template applies to
    
    # Content
    subject_template = db.Column(db.String(200))
    body_template = db.Column(db.Text, nullable=False)
    
    # Variables
    template_variables = db.Column(db.JSON)  # Available variables for substitution
    
    # Usage
    usage_count = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ServiceRequestTemplate {self.name}>'

class ServiceRequestKnowledgeBase(db.Model):
    """Knowledge base articles for service requests"""
    
    __tablename__ = 'service_request_knowledge_base'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # Categorization
    category = db.Column(db.String(100))
    tags = db.Column(db.JSON)
    related_services = db.Column(db.JSON)
    
    # Article Details
    article_type = db.Column(db.String(50))  # faq, troubleshooting, procedure
    difficulty_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    
    # Content Management
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    review_date = db.Column(db.Date)
    
    # Usage Analytics
    view_count = db.Column(db.Integer, default=0)
    helpful_votes = db.Column(db.Integer, default=0)
    unhelpful_votes = db.Column(db.Integer, default=0)
    
    # SEO and Search
    search_keywords = db.Column(db.JSON)
    meta_description = db.Column(db.Text)
    
    # Status
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', foreign_keys=[author_id], backref='authored_kb_articles')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by_id], backref='reviewed_kb_articles')
    
    def __repr__(self):
        return f'<ServiceRequestKnowledgeBase {self.title}>'
    
    @property
    def helpfulness_score(self):
        """Calculate helpfulness score"""
        total_votes = self.helpful_votes + self.unhelpful_votes
        if total_votes == 0:
            return 0
        return (self.helpful_votes / total_votes) * 100