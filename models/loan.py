"""
Loan Application Model
Handles loan applications and loan management for GM Services
"""
from database import db
from datetime import datetime

class LoanApplication(db.Model):
    """Loan application model"""
    
    __tablename__ = 'loan_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Applicant Information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Loan Details
    loan_type = db.Column(db.String(50), nullable=False)  # personal, auto, business, mortgage
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    purpose = db.Column(db.Text, nullable=False)
    term_months = db.Column(db.Integer)  # Loan term in months
    
    # Financial Information
    monthly_income = db.Column(db.Numeric(10, 2), nullable=False)
    employment_status = db.Column(db.String(50), nullable=False)  # employed, self_employed, unemployed, retired
    employer_name = db.Column(db.String(200))
    employment_duration = db.Column(db.String(50))  # e.g., "2 years"
    
    # Additional Financial Details
    other_income = db.Column(db.Numeric(10, 2), default=0.00)
    monthly_expenses = db.Column(db.Numeric(10, 2))
    existing_debts = db.Column(db.Numeric(10, 2), default=0.00)
    credit_score = db.Column(db.Integer)
    
    # Collateral Information (for secured loans)
    collateral_type = db.Column(db.String(100))
    collateral_value = db.Column(db.Numeric(12, 2))
    collateral_description = db.Column(db.Text)
    
    # Application Status
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)
    # Status options: pending, under_review, approved, rejected, disbursed, closed
    
    # Loan Terms (if approved)
    approved_amount = db.Column(db.Numeric(12, 2))
    interest_rate = db.Column(db.Numeric(5, 2))  # Annual percentage rate
    monthly_payment = db.Column(db.Numeric(10, 2))
    
    # Processing Information
    assigned_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    application_number = db.Column(db.String(50), unique=True, index=True)
    
    # Documents and Verification
    documents_submitted = db.Column(db.JSON)  # Array of document types submitted
    documents_verified = db.Column(db.Boolean, default=False)
    identity_verified = db.Column(db.Boolean, default=False)
    income_verified = db.Column(db.Boolean, default=False)
    
    # Communication and Notes
    customer_notes = db.Column(db.Text)
    officer_notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    rejection_reason = db.Column(db.Text)
    
    # Important Dates
    application_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    review_date = db.Column(db.DateTime)
    approval_date = db.Column(db.DateTime)
    disbursement_date = db.Column(db.DateTime)
    first_payment_date = db.Column(db.DateTime)
    maturity_date = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_officer = db.relationship('User', foreign_keys=[assigned_officer_id], backref='assigned_loans')
    
    def __repr__(self):
        return f'<LoanApplication {self.application_number}: {self.loan_type} - ${self.amount}>'
    
    def generate_application_number(self):
        """Generate unique application number"""
        if not self.application_number:
            # Format: LOAN-YYYY-MMDD-XXXX (where XXXX is ID padded to 4 digits)
            today = datetime.utcnow()
            date_part = today.strftime('%Y-%m%d')
            self.application_number = f"LOAN-{date_part}-{self.id:04d}"
    
    def get_status_badge_class(self):
        """Get CSS class for status badge"""
        status_classes = {
            'pending': 'badge-warning',
            'under_review': 'badge-info',
            'approved': 'badge-success',
            'rejected': 'badge-danger',
            'disbursed': 'badge-primary',
            'closed': 'badge-secondary'
        }
        return status_classes.get(self.status, 'badge-secondary')
    
    def calculate_monthly_payment(self):
        """Calculate monthly payment if approved"""
        if self.approved_amount and self.interest_rate and self.term_months:
            principal = float(self.approved_amount)
            monthly_rate = float(self.interest_rate) / 100 / 12
            num_payments = self.term_months
            
            if monthly_rate > 0:
                monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                                ((1 + monthly_rate) ** num_payments - 1)
            else:
                monthly_payment = principal / num_payments
            
            return round(monthly_payment, 2)
        return None
    
    def get_debt_to_income_ratio(self):
        """Calculate debt-to-income ratio"""
        if self.monthly_income and self.existing_debts:
            return round((float(self.existing_debts) / float(self.monthly_income)) * 100, 2)
        return 0
    
    def is_overdue_for_review(self):
        """Check if application is overdue for review (7 days)"""
        if self.status == 'pending':
            return (datetime.utcnow() - self.created_at).days > 7
        return False
    
    def get_processing_days(self):
        """Get number of days since application was submitted"""
        return (datetime.utcnow() - self.created_at).days
    
    def to_dict(self):
        """Convert loan application to dictionary"""
        return {
            'id': self.id,
            'application_number': self.application_number,
            'user_id': self.user_id,
            'applicant_name': self.applicant.full_name if self.applicant else None,
            'loan_type': self.loan_type,
            'amount': float(self.amount),
            'currency': self.currency,
            'purpose': self.purpose,
            'term_months': self.term_months,
            'monthly_income': float(self.monthly_income),
            'employment_status': self.employment_status,
            'status': self.status,
            'approved_amount': float(self.approved_amount) if self.approved_amount else None,
            'interest_rate': float(self.interest_rate) if self.interest_rate else None,
            'monthly_payment': float(self.monthly_payment) if self.monthly_payment else None,
            'assigned_officer_id': self.assigned_officer_id,
            'assigned_officer_name': self.assigned_officer.full_name if self.assigned_officer else None,
            'documents_verified': self.documents_verified,
            'identity_verified': self.identity_verified,
            'income_verified': self.income_verified,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'disbursement_date': self.disbursement_date.isoformat() if self.disbursement_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }