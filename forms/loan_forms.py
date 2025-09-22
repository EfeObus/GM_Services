"""
Enhanced Loan Application Forms
Comprehensive forms for different loan types with validation
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, IntegerField, DecimalField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Email, Optional, Regexp
from data.nigeria_data import NIGERIAN_STATES_SIMPLE, NIGERIAN_BANKS

class EnhancedLoanApplicationForm(FlaskForm):
    """Comprehensive loan application form"""
    
    # Basic Loan Information
    requested_amount = DecimalField(
        'Loan Amount (₦)', 
        validators=[DataRequired(), NumberRange(min=50000, max=50000000)],
        render_kw={"placeholder": "Enter amount in Naira"}
    )
    
    term_months = SelectField(
        'Loan Term (Months)',
        choices=[
            (6, '6 months'), (12, '12 months'), (18, '18 months'), (24, '24 months'),
            (36, '36 months'), (48, '48 months'), (60, '60 months'), (72, '72 months'),
            (84, '84 months'), (96, '96 months'), (108, '108 months'), (120, '120 months')
        ],
        coerce=int,
        validators=[DataRequired()]
    )
    
    purpose = SelectField(
        'Loan Purpose',
        choices=[
            ('personal_expense', 'Personal Expense'),
            ('education', 'Education'),
            ('medical', 'Medical Emergency'),
            ('home_improvement', 'Home Improvement'),
            ('debt_consolidation', 'Debt Consolidation'),
            ('business_expansion', 'Business Expansion'),
            ('equipment_purchase', 'Equipment Purchase'),
            ('working_capital', 'Working Capital'),
            ('vehicle_purchase', 'Vehicle Purchase'),
            ('property_purchase', 'Property Purchase'),
            ('other', 'Other')
        ],
        validators=[DataRequired()]
    )
    
    purpose_description = TextAreaField(
        'Purpose Description',
        validators=[Length(max=500)],
        render_kw={"placeholder": "Provide detailed description of loan purpose"}
    )
    
    # Personal Information
    phone_number = StringField(
        'Phone Number',
        validators=[
            DataRequired(),
            Regexp(r'^\+?234[789]\d{9}$|^[089]\d{10}$', message="Enter valid Nigerian phone number")
        ],
        render_kw={"placeholder": "+234XXXXXXXXXX or 08XXXXXXXXX"}
    )
    
    alternate_phone = StringField(
        'Alternate Phone Number',
        validators=[
            Optional(),
            Regexp(r'^\+?234[789]\d{9}$|^[089]\d{10}$', message="Enter valid Nigerian phone number")
        ]
    )
    
    residential_address = TextAreaField(
        'Residential Address',
        validators=[DataRequired(), Length(min=10, max=500)],
        render_kw={"placeholder": "Enter your complete residential address"}
    )
    
    state_of_origin = SelectField(
        'State of Origin',
        choices=[(state, state) for state in NIGERIAN_STATES_SIMPLE],
        validators=[Optional()]
    )
    
    lga = StringField(
        'Local Government Area (LGA)',
        validators=[Optional(), Length(max=100)]
    )
    
    # Next of Kin Information
    next_of_kin_name = StringField(
        'Next of Kin Name',
        validators=[DataRequired(), Length(min=2, max=200)]
    )
    
    next_of_kin_phone = StringField(
        'Next of Kin Phone',
        validators=[
            DataRequired(),
            Regexp(r'^\+?234[789]\d{9}$|^[089]\d{10}$', message="Enter valid Nigerian phone number")
        ]
    )
    
    next_of_kin_relationship = SelectField(
        'Relationship',
        choices=[
            ('spouse', 'Spouse'),
            ('parent', 'Parent'),
            ('sibling', 'Sibling'),
            ('child', 'Child'),
            ('friend', 'Friend'),
            ('other_relative', 'Other Relative')
        ],
        validators=[DataRequired()]
    )
    
    # Bank Information
    bank_name = SelectField(
        'Bank Name',
        choices=[(bank, bank) for bank in NIGERIAN_BANKS],
        validators=[DataRequired()]
    )
    
    account_number = StringField(
        'Account Number',
        validators=[
            DataRequired(),
            Regexp(r'^\d{10}$', message="Account number must be 10 digits")
        ]
    )
    
    account_name = StringField(
        'Account Name',
        validators=[DataRequired(), Length(min=2, max=200)],
        render_kw={"placeholder": "Account name as it appears in bank records"}
    )
    
    bvn = StringField(
        'Bank Verification Number (BVN)',
        validators=[
            DataRequired(),
            Regexp(r'^\d{11}$', message="BVN must be 11 digits")
        ]
    )
    
    # Employment Information
    employment_type = SelectField(
        'Employment Type',
        choices=[
            ('employed', 'Employed (Salary Earner)'),
            ('self-employed', 'Self Employed'),
            ('business-owner', 'Business Owner'),
            ('unemployed', 'Unemployed'),
            ('retired', 'Retired'),
            ('student', 'Student')
        ],
        validators=[DataRequired()]
    )
    
    monthly_income = DecimalField(
        'Monthly Income (₦)',
        validators=[DataRequired(), NumberRange(min=30000, max=10000000)],
        render_kw={"placeholder": "Enter monthly income in Naira"}
    )
    
    employer_name = StringField(
        'Employer/Company Name',
        validators=[Optional(), Length(max=200)]
    )
    
    employer_address = TextAreaField(
        'Employer Address',
        validators=[Optional(), Length(max=500)]
    )
    
    employer_phone = StringField(
        'Employer Phone Number',
        validators=[
            Optional(),
            Regexp(r'^\+?234[789]\d{9}$|^[089]\d{10}$', message="Enter valid Nigerian phone number")
        ]
    )
    
    job_title = StringField(
        'Job Title/Position',
        validators=[Optional(), Length(max=100)]
    )
    
    employment_duration_months = IntegerField(
        'Employment Duration (Months)',
        validators=[Optional(), NumberRange(min=1, max=600)]
    )
    
    # Business Information (for business owners)
    business_name = StringField(
        'Business Name',
        validators=[Optional(), Length(max=200)]
    )
    
    business_address = TextAreaField(
        'Business Address',
        validators=[Optional(), Length(max=500)]
    )
    
    business_registration_number = StringField(
        'Business Registration Number (RC Number)',
        validators=[Optional(), Length(max=50)]
    )
    
    business_type = SelectField(
        'Business Type',
        choices=[
            ('', 'Select Business Type'),
            ('sole_proprietorship', 'Sole Proprietorship'),
            ('partnership', 'Partnership'),
            ('limited_liability', 'Limited Liability Company'),
            ('cooperative', 'Cooperative Society'),
            ('ngo', 'Non-Governmental Organization'),
            ('other', 'Other')
        ],
        validators=[Optional()]
    )
    
    years_in_business = IntegerField(
        'Years in Business',
        validators=[Optional(), NumberRange(min=0, max=50)]
    )
    
    average_monthly_revenue = DecimalField(
        'Average Monthly Revenue (₦)',
        validators=[Optional(), NumberRange(min=0)],
        render_kw={"placeholder": "Enter average monthly business revenue"}
    )
    
    # Additional Income
    other_income = DecimalField(
        'Other Monthly Income (₦)',
        validators=[Optional(), NumberRange(min=0)],
        render_kw={"placeholder": "Rental, investment income, etc."}
    )
    
    other_income_source = StringField(
        'Other Income Source',
        validators=[Optional(), Length(max=200)]
    )
    
    # Financial Information
    monthly_expenses = DecimalField(
        'Monthly Expenses (₦)',
        validators=[DataRequired(), NumberRange(min=0)],
        render_kw={"placeholder": "Total monthly living expenses"}
    )
    
    credit_score = IntegerField(
        'Credit Score',
        validators=[Optional(), NumberRange(min=300, max=850)],
        render_kw={"placeholder": "If you know your credit score"}
    )
    
    # Collateral Information (for loans over 1M)
    collateral_type = SelectField(
        'Collateral Type',
        choices=[
            ('', 'Select Collateral Type'),
            ('real_estate', 'Real Estate/Property'),
            ('vehicle', 'Vehicle'),
            ('equipment', 'Equipment/Machinery'),
            ('savings', 'Savings/Fixed Deposit'),
            ('stocks', 'Stocks/Shares'),
            ('other', 'Other')
        ],
        validators=[Optional()]
    )
    
    collateral_value = DecimalField(
        'Collateral Value (₦)',
        validators=[Optional(), NumberRange(min=0)],
        render_kw={"placeholder": "Estimated current market value"}
    )
    
    collateral_location = StringField(
        'Collateral Location',
        validators=[Optional(), Length(max=500)],
        render_kw={"placeholder": "Address/location of collateral"}
    )
    
    collateral_description = TextAreaField(
        'Collateral Description',
        validators=[Optional(), Length(max=1000)],
        render_kw={"placeholder": "Detailed description of collateral"}
    )
    
    # Document Uploads
    identity_document = FileField(
        'Identity Document',
        validators=[
            FileRequired(),
            FileAllowed(['pdf'], 'PDF files only')
        ]
    )
    
    income_proof = FileField(
        'Income Proof',
        validators=[
            FileRequired(),
            FileAllowed(['pdf'], 'PDF files only')
        ]
    )
    
    employment_letter = FileField(
        'Employment Letter',
        validators=[
            Optional(),
            FileAllowed(['pdf'], 'PDF files only')
        ]
    )
    
    bank_statement = FileField(
        'Bank Statement (6 months)',
        validators=[
            FileRequired(),
            FileAllowed(['pdf'], 'PDF files only')
        ]
    )
    
    # Agreement Checkboxes
    policy_agreed = BooleanField(
        'I have read and agree to the loan terms and conditions',
        validators=[DataRequired()]
    )
    
    terms_agreed = BooleanField(
        'I agree to the interest rates and repayment terms',
        validators=[DataRequired()]
    )
    
    data_processing_agreed = BooleanField(
        'I consent to the processing of my personal data for loan assessment',
        validators=[DataRequired()]
    )
    
    def validate_requested_amount(self, field):
        """Custom validation for loan amount based on loan type"""
        # This will be enhanced with loan type specific validation
        pass
    
    def validate_collateral_info(self):
        """Validate collateral information for large loans"""
        if self.requested_amount.data and float(self.requested_amount.data) > 1000000:
            if not self.collateral_type.data:
                self.collateral_type.errors.append('Collateral information is required for loans over ₦1,000,000')
                return False
            if not self.collateral_value.data:
                self.collateral_value.errors.append('Collateral value is required for loans over ₦1,000,000')
                return False
        return True
    
    def validate_employment_info(self):
        """Validate employment information based on employment type"""
        if self.employment_type.data in ['employed', 'self-employed']:
            if not self.employer_name.data:
                self.employer_name.errors.append('Employer name is required')
                return False
            if not self.employment_duration_months.data:
                self.employment_duration_months.errors.append('Employment duration is required')
                return False
        
        elif self.employment_type.data == 'business-owner':
            if not self.business_name.data:
                self.business_name.errors.append('Business name is required for business owners')
                return False
            if not self.business_type.data:
                self.business_type.errors.append('Business type is required')
                return False
        
        return True