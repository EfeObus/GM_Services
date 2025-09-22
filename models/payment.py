"""
Payment Integration Models
Handles bank transfer payments for all GM Services in Nigeria
"""
from database import db
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

class BankAccount(db.Model):
    """Company bank accounts for receiving payments"""
    
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(100), nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    account_number = db.Column(db.String(20), nullable=False, unique=True)
    
    # Bank Details
    bank_code = db.Column(db.String(10))  # CBN bank code
    sort_code = db.Column(db.String(10))
    swift_code = db.Column(db.String(20))
    
    # Account Type
    account_type = db.Column(db.String(50), default='current')  # current, savings
    currency = db.Column(db.String(3), default='NGN')
    
    # Service Assignment
    services_supported = db.Column(db.JSON)  # Which services use this account
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_primary = db.Column(db.Boolean, default=False)
    
    # Display
    display_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('BankTransferPayment', backref='bank_account', lazy='dynamic')
    
    def __repr__(self):
        return f'<BankAccount {self.bank_name} - {self.account_number}>'

class BankTransferPayment(db.Model):
    """Bank transfer payment transactions"""
    
    __tablename__ = 'bank_transfer_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_reference = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Payment Details
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    
    # Service Information
    service_type = db.Column(db.String(50), nullable=False)  # automobile, loan, hotel, etc.
    service_id = db.Column(db.Integer, nullable=False)  # ID of the related service record
    order_number = db.Column(db.String(50))  # Order/booking number
    
    # Amount Details
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), default='NGN')
    
    # Customer Bank Details
    customer_bank_name = db.Column(db.String(100))
    customer_account_name = db.Column(db.String(200))
    customer_account_number = db.Column(db.String(20))
    
    # Transfer Details
    transfer_date = db.Column(db.DateTime)
    bank_reference = db.Column(db.String(100))  # Bank's transaction reference
    deposit_slip_url = db.Column(db.String(255))  # Upload receipt/slip
    
    # Payment Status
    status = db.Column(db.String(30), default='pending')  # pending, confirmed, verified, rejected
    
    # Verification
    verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    verification_date = db.Column(db.DateTime)
    verification_notes = db.Column(db.Text)
    
    # Customer Information
    customer_phone = db.Column(db.String(20))
    customer_email = db.Column(db.String(120))
    
    # Notification
    customer_notified = db.Column(db.Boolean, default=False)
    notification_sent_at = db.Column(db.DateTime)
    
    # Timing
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    
    # Refund Information
    is_refunded = db.Column(db.Boolean, default=False)
    refund_amount = db.Column(db.Numeric(12, 2), default=0)
    refund_reason = db.Column(db.Text)
    refund_date = db.Column(db.DateTime)
    
    # Notes
    payment_notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='bank_payments')
    verified_by = db.relationship('User', foreign_keys=[verified_by_id], backref='verified_payments')
    
    def __init__(self, **kwargs):
        super(BankTransferPayment, self).__init__(**kwargs)
        if not self.payment_reference:
            self.payment_reference = self.generate_payment_reference()
    
    @staticmethod
    def generate_payment_reference():
        """Generate unique payment reference"""
        prefix = "GM"
        timestamp = datetime.now().strftime("%y%m%d")
        random_part = str(uuid.uuid4().hex)[:8].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<BankTransferPayment {self.payment_reference} - {self.amount} NGN>'
    
    @property
    def is_verified(self):
        """Check if payment is verified"""
        return self.status == 'verified'
    
    @property
    def can_be_refunded(self):
        """Check if payment can be refunded"""
        return self.is_verified and not self.is_refunded

class PaymentAnalytics(db.Model):
    """Payment analytics and reporting"""
    
    __tablename__ = 'payment_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Time Period
    date = db.Column(db.Date, nullable=False, index=True)
    period_type = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly, yearly
    
    # Service Breakdown
    service_type = db.Column(db.String(50))  # automobile, hotel, etc., or 'total'
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))
    
    # Transaction Counts
    total_payments = db.Column(db.Integer, default=0)
    verified_payments = db.Column(db.Integer, default=0)
    pending_payments = db.Column(db.Integer, default=0)
    rejected_payments = db.Column(db.Integer, default=0)
    
    # Financial Metrics
    total_volume = db.Column(db.Numeric(15, 2), default=0)
    verified_volume = db.Column(db.Numeric(15, 2), default=0)
    pending_volume = db.Column(db.Numeric(15, 2), default=0)
    
    # Performance Metrics
    verification_rate = db.Column(db.Float, default=0)  # Percentage
    average_payment_value = db.Column(db.Numeric(10, 2), default=0)
    average_verification_time_hours = db.Column(db.Float, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bank_account = db.relationship('BankAccount', backref='analytics')
    
    def __repr__(self):
        return f'<PaymentAnalytics {self.date} - {self.service_type or "All"}>'