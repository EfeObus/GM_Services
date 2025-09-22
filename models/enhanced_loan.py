"""
Enhanced Loan Models
Handles personal, business, auto loans with credit assessment and repayment tracking
"""
from database import db
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

class LoanType(db.Model):
    """Loan Type Model - Personal, Business, Auto, etc."""
    
    __tablename__ = 'loan_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # Personal, Business, Auto, Mortgage
    description = db.Column(db.Text)
    
    # Loan Parameters
    min_amount = db.Column(db.Numeric(12, 2), nullable=False)
    max_amount = db.Column(db.Numeric(12, 2), nullable=False)
    min_term_months = db.Column(db.Integer, nullable=False)
    max_term_months = db.Column(db.Integer, nullable=False)
    base_interest_rate = db.Column(db.Float, nullable=False)  # Base rate percentage (Nigerian rates)
    
    # Requirements
    min_credit_score = db.Column(db.Integer, default=500)
    min_income_monthly = db.Column(db.Numeric(10, 2))
    required_documents = db.Column(db.JSON)  # List of required documents
    requires_collateral = db.Column(db.Boolean, default=False)  # For loans over 1M
    requires_employment_proof = db.Column(db.Boolean, default=False)  # For auto loans
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    processing_fee_percentage = db.Column(db.Float, default=1.0)  # Processing fee as percentage
    max_debt_to_income_ratio = db.Column(db.Float, default=40.0)  # Maximum DTI ratio allowed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('EnhancedLoanApplication', backref='loan_type', lazy='dynamic')
    
    @classmethod
    def create_default_types(cls):
        """Create default loan types with Nigerian bank rates"""
        default_types = [
            {
                'name': 'Personal Loan',
                'description': 'Quick personal loans for emergencies, education, or major purchases',
                'min_amount': 50000,
                'max_amount': 5000000,
                'min_term_months': 6,
                'max_term_months': 60,
                'base_interest_rate': 24.0,  # Nigerian personal loan rates 20-30%
                'min_income_monthly': 50000,
                'required_documents': ['identity', 'income_proof', 'bank_statement'],
                'requires_collateral': False,
                'requires_employment_proof': True
            },
            {
                'name': 'Business Loan',
                'description': 'Capital for business expansion, equipment, or working capital needs',
                'min_amount': 100000,
                'max_amount': 50000000,
                'min_term_months': 6,
                'max_term_months': 120,
                'base_interest_rate': 18.0,  # Nigerian business loan rates 15-25%
                'min_income_monthly': 100000,
                'required_documents': ['identity', 'business_registration', 'tax_certificate', 'bank_statement'],
                'requires_collateral': True,
                'requires_employment_proof': False
            },
            {
                'name': 'Auto Loan',
                'description': 'Financing for new and used vehicles with competitive rates',
                'min_amount': 500000,
                'max_amount': 20000000,
                'min_term_months': 12,
                'max_term_months': 84,
                'base_interest_rate': 15.0,  # Nigerian auto loan rates 12-20%
                'min_income_monthly': 100000,
                'required_documents': ['identity', 'income_proof', 'employment_letter', 'bank_statement'],
                'requires_collateral': False,
                'requires_employment_proof': True
            }
        ]
        
        for loan_data in default_types:
            existing = cls.query.filter_by(name=loan_data['name']).first()
            if not existing:
                loan_type = cls(**loan_data)
                db.session.add(loan_type)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error creating default loan types: {e}")
    
    def __repr__(self):
        return f'<LoanType {self.name}>'

class EnhancedLoanApplication(db.Model):
    """Enhanced Loan Application Model"""
    
    __tablename__ = 'enhanced_loan_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    application_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Basic Information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    loan_type_id = db.Column(db.Integer, db.ForeignKey('loan_types.id'), nullable=False)
    
    # Loan Details
    requested_amount = db.Column(db.Numeric(12, 2), nullable=False)
    approved_amount = db.Column(db.Numeric(12, 2))
    currency = db.Column(db.String(3), default='NGN')
    term_months = db.Column(db.Integer, nullable=False)
    interest_rate = db.Column(db.Float)  # Final approved rate
    
    # Purpose and Details
    purpose = db.Column(db.String(200), nullable=False)
    purpose_description = db.Column(db.Text)
    
    # Bank Account Information (Required for loan disbursement)
    bank_name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(20), nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    bvn = db.Column(db.String(11))  # Bank Verification Number
    
    # Personal Information
    phone_number = db.Column(db.String(20), nullable=False)
    alternate_phone = db.Column(db.String(20))
    residential_address = db.Column(db.Text, nullable=False)
    state_of_origin = db.Column(db.String(50))
    lga = db.Column(db.String(100))  # Local Government Area
    next_of_kin_name = db.Column(db.String(200))
    next_of_kin_phone = db.Column(db.String(20))
    next_of_kin_relationship = db.Column(db.String(50))
    
    # Financial Information
    monthly_income = db.Column(db.Numeric(10, 2), nullable=False)
    employment_type = db.Column(db.String(50), nullable=False)  # employed, self-employed, business-owner
    employer_name = db.Column(db.String(200))
    employer_address = db.Column(db.Text)
    employer_phone = db.Column(db.String(20))
    employment_duration_months = db.Column(db.Integer)
    job_title = db.Column(db.String(100))
    other_income = db.Column(db.Numeric(10, 2), default=0)
    other_income_source = db.Column(db.String(200))
    
    # Business Information (for business owners/self-employed)
    business_name = db.Column(db.String(200))
    business_address = db.Column(db.Text)
    business_registration_number = db.Column(db.String(50))
    business_type = db.Column(db.String(100))
    years_in_business = db.Column(db.Integer)
    average_monthly_revenue = db.Column(db.Numeric(10, 2))
    
    # Existing Obligations
    existing_loans = db.Column(db.JSON)  # List of existing loans
    monthly_expenses = db.Column(db.Numeric(10, 2))
    credit_score = db.Column(db.Integer)
    
    # Collateral (for secured loans over 1M)
    collateral_type = db.Column(db.String(100))
    collateral_value = db.Column(db.Numeric(12, 2))
    collateral_description = db.Column(db.Text)
    collateral_location = db.Column(db.Text)
    
    # Loan Policy Agreement
    policy_agreed = db.Column(db.Boolean, default=False, nullable=False)
    terms_agreed = db.Column(db.Boolean, default=False, nullable=False)
    data_processing_agreed = db.Column(db.Boolean, default=False, nullable=False)
    
    # Application Status
    status = db.Column(db.String(30), default='submitted')  # submitted, under_review, assigned, approved, rejected, disbursed
    review_notes = db.Column(db.Text)
    rejection_reason = db.Column(db.Text)
    
    # Processing and Assignment
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))  # Staff assigned to review
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    processing_fee = db.Column(db.Numeric(8, 2))
    processing_fee_paid = db.Column(db.Boolean, default=False)
    
    # Documents - Enhanced for different file types
    identity_document = db.Column(db.String(255))  # National ID, Passport, Driver's License
    income_proof = db.Column(db.String(255))  # Salary slip, bank statement
    employment_letter = db.Column(db.String(255))  # Employment verification letter
    bank_statement = db.Column(db.String(255))  # 6 months bank statement
    collateral_documents = db.Column(db.JSON)  # For loans over 1M - property documents, etc.
    business_documents = db.Column(db.JSON)  # For business loans - CAC, Tax cert, etc.
    additional_documents = db.Column(db.JSON)  # Any other supporting documents
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_at = db.Column(db.DateTime)
    reviewed_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    disbursed_at = db.Column(db.DateTime)
    
    # Relationships
    applicant = db.relationship('User', foreign_keys=[user_id], backref='enhanced_loan_applications')
    assigned_staff = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_loan_applications')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_enhanced_loans')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_loan_applications')
    loan_account = db.relationship('LoanAccount', backref='enhanced_application', uselist=False)
    
    def __init__(self, **kwargs):
        super(EnhancedLoanApplication, self).__init__(**kwargs)
        if not self.application_number:
            self.application_number = self.generate_application_number()
    
    @staticmethod
    def generate_application_number():
        """Generate unique application number"""
        prefix = "LN"
        timestamp = datetime.now().strftime("%y%m")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def calculate_monthly_payment(self):
        """Calculate monthly payment based on approved amount and terms"""
        if not self.approved_amount or not self.interest_rate or not self.term_months:
            return None
        
        principal = float(self.approved_amount)
        monthly_rate = self.interest_rate / 100 / 12
        num_payments = self.term_months
        
        if monthly_rate == 0:
            return principal / num_payments
        
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                         ((1 + monthly_rate) ** num_payments - 1)
        
        return round(monthly_payment, 2)
    
    @property
    def debt_to_income_ratio(self):
        """Calculate debt-to-income ratio"""
        if not self.monthly_income or self.monthly_income == 0:
            return None
        
        total_monthly_debt = float(self.monthly_expenses or 0)
        if self.approved_amount and self.interest_rate and self.term_months:
            total_monthly_debt += self.calculate_monthly_payment() or 0
        
        return round((total_monthly_debt / float(self.monthly_income)) * 100, 2)
    
    @property
    def requires_collateral(self):
        """Check if loan requires collateral (loans over 1M NGN)"""
        return float(self.requested_amount) > 1000000
    
    @property
    def processing_fee_amount(self):
        """Calculate processing fee based on loan type"""
        if self.loan_type and self.requested_amount:
            fee_rate = self.loan_type.processing_fee_percentage / 100
            return round(float(self.requested_amount) * fee_rate, 2)
        return 0
    
    def assign_to_staff(self, staff_id, assigned_by_id=None):
        """Assign loan application to staff member"""
        self.assigned_to = staff_id
        self.assigned_at = datetime.utcnow()
        self.status = 'assigned'
        
        # Log the assignment
        if assigned_by_id:
            self.review_notes = f"Assigned to staff member {staff_id} by admin {assigned_by_id}"
        
        db.session.add(self)
        return True
    
    def approve_loan(self, approved_by_id, approved_amount=None, interest_rate=None):
        """Approve loan application"""
        self.status = 'approved'
        self.approved_by = approved_by_id
        self.approved_at = datetime.utcnow()
        
        if approved_amount:
            self.approved_amount = approved_amount
        else:
            self.approved_amount = self.requested_amount
            
        if interest_rate:
            self.interest_rate = interest_rate
        else:
            self.interest_rate = self.loan_type.base_interest_rate
        
        db.session.add(self)
        return True
    
    def reject_loan(self, rejected_by_id, reason):
        """Reject loan application"""
        self.status = 'rejected'
        self.reviewed_by = rejected_by_id
        self.reviewed_at = datetime.utcnow()
        self.rejection_reason = reason
        
        db.session.add(self)
        return True
    
    def get_document_url(self, document_type):
        """Get URL for specific document type"""
        document_mapping = {
            'identity_document': self.identity_document,
            'income_proof': self.income_proof,
            'employment_letter': self.employment_letter,
            'bank_statement': self.bank_statement
        }
        return document_mapping.get(document_type)
    
    @property
    def status_display(self):
        """Get user-friendly status display"""
        status_map = {
            'submitted': 'Application Submitted',
            'under_review': 'Under Review',
            'assigned': 'Assigned for Review',
            'approved': 'Approved',
            'rejected': 'Rejected',
            'disbursed': 'Loan Disbursed'
        }
        return status_map.get(self.status, self.status.title())
    
    def __repr__(self):
        return f'<EnhancedLoanApplication {self.application_number}>'

class LoanAccount(db.Model):
    """Active Loan Account for approved loans"""
    
    __tablename__ = 'loan_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    application_id = db.Column(db.Integer, db.ForeignKey('enhanced_loan_applications.id'), nullable=False)
    
    # Loan Details
    principal_amount = db.Column(db.Numeric(12, 2), nullable=False)
    current_balance = db.Column(db.Numeric(12, 2), nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    term_months = db.Column(db.Integer, nullable=False)
    monthly_payment = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Account Status
    status = db.Column(db.String(20), default='active')  # active, paid_off, defaulted, closed
    next_payment_date = db.Column(db.Date, nullable=False)
    payment_day = db.Column(db.Integer, default=1)  # Day of month for payments
    
    # Tracking
    total_paid = db.Column(db.Numeric(12, 2), default=0)
    payments_made = db.Column(db.Integer, default=0)
    payments_remaining = db.Column(db.Integer)
    last_payment_date = db.Column(db.Date)
    
    # Late Payment Tracking
    days_past_due = db.Column(db.Integer, default=0)
    late_fees = db.Column(db.Numeric(8, 2), default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    # Relationships
    payments = db.relationship('LoanPayment', backref='loan_account', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(LoanAccount, self).__init__(**kwargs)
        if not self.account_number:
            self.account_number = self.generate_account_number()
        if not self.next_payment_date:
            self.next_payment_date = (datetime.now() + timedelta(days=30)).date()
        if not self.payments_remaining:
            self.payments_remaining = self.term_months
    
    @staticmethod
    def generate_account_number():
        """Generate unique account number"""
        prefix = "LA"
        timestamp = datetime.now().strftime("%y%m")
        random_part = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}{timestamp}{random_part}"
    
    def make_payment(self, amount, payment_method='bank_transfer', reference=None):
        """Record a payment"""
        payment = LoanPayment(
            loan_account_id=self.id,
            amount=amount,
            payment_method=payment_method,
            reference=reference
        )
        
        # Update account balance
        self.current_balance -= amount
        self.total_paid += amount
        self.payments_made += 1
        self.payments_remaining = max(0, self.payments_remaining - 1)
        self.last_payment_date = datetime.now().date()
        
        # Update next payment date
        if self.current_balance > 0:
            self.next_payment_date = (datetime.now() + timedelta(days=30)).date()
        else:
            self.status = 'paid_off'
            self.closed_at = datetime.utcnow()
        
        # Reset late payment tracking
        self.days_past_due = 0
        
        db.session.add(payment)
        db.session.add(self)
        
        return payment
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        return datetime.now().date() > self.next_payment_date
    
    def __repr__(self):
        return f'<LoanAccount {self.account_number}>'

class LoanPayment(db.Model):
    """Loan Payment Records"""
    
    __tablename__ = 'loan_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_account_id = db.Column(db.Integer, db.ForeignKey('loan_accounts.id'), nullable=False)
    
    # Payment Details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    principal_amount = db.Column(db.Numeric(10, 2))  # Amount towards principal
    interest_amount = db.Column(db.Numeric(10, 2))   # Amount towards interest
    late_fee_amount = db.Column(db.Numeric(8, 2), default=0)
    
    # Payment Information
    payment_method = db.Column(db.String(50), nullable=False)  # bank_transfer, card, cash, etc.
    reference = db.Column(db.String(100))  # Payment reference/transaction ID
    status = db.Column(db.String(20), default='completed')  # pending, completed, failed, reversed
    
    # Timestamps
    payment_date = db.Column(db.Date, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<LoanPayment {self.amount} for {self.loan_account.account_number}>'

class CreditAssessment(db.Model):
    """Credit Assessment for loan applications"""
    
    __tablename__ = 'credit_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('enhanced_loan_applications.id'), nullable=False)
    
    # Credit Scores
    credit_score = db.Column(db.Integer)  # Calculated or provided credit score
    credit_grade = db.Column(db.String(5))  # A, B, C, D, F
    
    # Risk Assessment
    risk_level = db.Column(db.String(20))  # low, medium, high
    risk_score = db.Column(db.Float)  # 0-100 risk score
    debt_to_income_ratio = db.Column(db.Float)
    
    # Assessment Details
    income_verification = db.Column(db.Boolean, default=False)
    employment_verification = db.Column(db.Boolean, default=False)
    identity_verification = db.Column(db.Boolean, default=False)
    
    # Recommendations
    recommended_action = db.Column(db.String(20))  # approve, reject, conditional
    recommended_amount = db.Column(db.Numeric(12, 2))
    recommended_rate = db.Column(db.Float)
    
    # Assessment Notes
    assessment_notes = db.Column(db.Text)
    assessor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    application = db.relationship('EnhancedLoanApplication', backref='credit_assessment')
    assessor = db.relationship('User', backref='credit_assessments')
    
    def __repr__(self):
        return f'<CreditAssessment for {self.application.application_number}>'

class LoanPolicy(db.Model):
    """Loan Policy and Agreement Document"""
    
    __tablename__ = 'loan_policies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    version = db.Column(db.String(10), default='1.0')
    policy_type = db.Column(db.String(50), default='general')  # general, personal, business, auto
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    effective_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    @classmethod
    def create_default_policies(cls):
        """Create default loan policies"""
        policies = [
            {
                'title': 'GM Services Loan Policy - General Terms',
                'policy_type': 'general',
                'content': '''
1. LOAN TERMS AND CONDITIONS

1.1 Interest Rates
- Interest rates are determined based on loan type, amount, term, and applicant's creditworthiness
- Rates are competitive with Nigerian banking industry standards
- All rates are annual percentage rates (APR)

1.2 Repayment Terms
- Monthly repayments are due on the same date each month
- Late payment fees apply after 7 days past due date
- Early repayment is allowed without penalty

1.3 Eligibility Requirements
- Must be 18 years or older
- Nigerian citizen or legal resident
- Verifiable source of income
- Valid bank account for loan disbursement
- Complete required documentation

1.4 Documentation Requirements
- Valid means of identification (National ID, Passport, Driver's License)
- Proof of income (salary slips, bank statements)
- Bank verification number (BVN)
- Employment verification letter
- Recent utility bill for address verification

1.5 Loan Processing
- Application review takes 3-5 business days
- Additional documentation may be requested
- Processing fee is 1-2% of loan amount
- Successful applications are disbursed within 24 hours of approval

2. TERMS AND CONDITIONS

2.1 By applying for this loan, you agree to:
- Provide accurate and complete information
- Allow verification of provided information
- Authorize credit checks and employment verification
- Accept the loan terms if approved

2.2 Loan Disbursement
- Funds are disbursed directly to your provided bank account
- Processing fees are deducted from loan amount
- Disbursement occurs only after all documentation is verified

2.3 Default and Collections
- Default occurs after 30 days of missed payment
- Collection activities will commence according to Nigerian law
- Additional fees and legal costs may apply

I acknowledge that I have read, understood, and agree to the above terms and conditions.
                '''
            },
            {
                'title': 'Data Processing and Privacy Policy',
                'policy_type': 'privacy',
                'content': '''
DATA PROCESSING AND PRIVACY NOTICE

1. INFORMATION COLLECTION
We collect personal and financial information necessary to process your loan application including:
- Personal identification details
- Financial information and credit history
- Employment details
- Contact information
- Banking details

2. USE OF INFORMATION
Your information is used for:
- Loan application processing and underwriting
- Credit assessment and verification
- Communication regarding your application
- Legal and regulatory compliance
- Risk management

3. INFORMATION SHARING
We may share your information with:
- Credit bureaus for credit assessment
- Employment verification services
- Banking partners for disbursement
- Legal authorities when required by law

4. DATA SECURITY
- We implement appropriate security measures
- Access to your data is restricted to authorized personnel
- Data is encrypted and stored securely

5. YOUR RIGHTS
You have the right to:
- Access your personal data
- Request corrections to inaccurate data
- Withdraw consent (may affect loan processing)

I consent to the collection, processing, and sharing of my personal data as described above.
                '''
            }
        ]
        
        for policy_data in policies:
            existing = cls.query.filter_by(title=policy_data['title']).first()
            if not existing:
                policy = cls(**policy_data)
                db.session.add(policy)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error creating default policies: {e}")
    
    def __repr__(self):
        return f'<LoanPolicy {self.title}>'