"""
Location models for Nigeria
Includes states and local government areas
"""
from datetime import datetime
from database import db

class NigerianState(db.Model):
    """Nigerian States Model - All 36 states plus FCT"""
    
    __tablename__ = 'nigerian_states'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(3), nullable=False, unique=True)  # e.g., 'LAG' for Lagos
    capital = db.Column(db.String(100), nullable=False)
    zone = db.Column(db.String(50), nullable=False)  # North-Central, North-East, North-West, South-East, South-South, South-West
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    local_governments = db.relationship('LocalGovernment', backref='state', lazy='dynamic')
    
    def __repr__(self):
        return f'<NigerianState {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'capital': self.capital,
            'zone': self.zone,
            'local_governments_count': self.local_governments.count()
        }

class LocalGovernment(db.Model):
    """Local Government Areas Model - All 774 LGAs in Nigeria"""
    
    __tablename__ = 'local_governments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10))  # LGA code if available
    state_id = db.Column(db.Integer, db.ForeignKey('nigerian_states.id'), nullable=False)
    headquarters = db.Column(db.String(100))  # Administrative headquarters
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<LocalGovernment {self.name}, {self.state.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'state_id': self.state_id,
            'state_name': self.state.name,
            'headquarters': self.headquarters
        }