"""
Service Models
Handles services offered by GM Services and service requests from customers
"""
from database import db
from datetime import datetime

class Service(db.Model):
    """Service model for all GM Services offerings"""
    
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    short_description = db.Column(db.String(500))
    
    # Service Details
    category = db.Column(db.String(50), nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), default=0.00)
    currency = db.Column(db.String(3), default='USD')
    
    # Service Features
    features = db.Column(db.JSON)  # Store features as JSON array
    requirements = db.Column(db.Text)
    duration = db.Column(db.String(100))  # e.g., "2-3 business days"
    
    # Media
    image_url = db.Column(db.String(255))
    gallery_images = db.Column(db.JSON)  # Array of image URLs
    video_url = db.Column(db.String(255))
    
    # Status and Availability
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    availability = db.Column(db.String(50), default='available')  # available, limited, unavailable
    
    # SEO and Metadata
    slug = db.Column(db.String(255), unique=True, index=True)
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.String(500))
    tags = db.Column(db.JSON)  # Array of tags
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # Note: ServiceRequest uses related_service field instead of direct foreign key
    
    def __repr__(self):
        return f'<Service {self.name}>'
    
    def get_requests_count(self):
        """Get total number of requests for this service"""
        from models.service_request import ServiceRequest
        return ServiceRequest.query.filter_by(related_service=self.category).count()
    
    def get_pending_requests_count(self):
        """Get pending requests count"""
        from models.service_request import ServiceRequest
        return ServiceRequest.query.filter_by(
            related_service=self.category, 
            status='pending'
        ).count()
    
    def to_dict(self):
        """Convert service to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'short_description': self.short_description,
            'category': self.category,
            'price': float(self.price) if self.price else 0.00,
            'currency': self.currency,
            'features': self.features,
            'duration': self.duration,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'availability': self.availability,
            'slug': self.slug,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }