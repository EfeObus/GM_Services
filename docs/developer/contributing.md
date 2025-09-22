# Contributing Guidelines

**GM Services Platform Contribution Guide**  
**Version 1.0**  
**Last Updated:** January 1, 2024

## Welcome Contributors! 🎉

Thank you for your interest in contributing to the GM Services platform! This guide will help you understand our development process, coding standards, and how to make meaningful contributions to our multi-service business platform.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Process](#development-process)
4. [Coding Standards](#coding-standards)
5. [Testing Requirements](#testing-requirements)
6. [Documentation Guidelines](#documentation-guidelines)
7. [Pull Request Process](#pull-request-process)
8. [Issue Reporting](#issue-reporting)
9. [Security Guidelines](#security-guidelines)
10. [Community and Support](#community-and-support)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. By participating in this project, you agree to abide by our code of conduct.

### Standards

**Positive behaviors include:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors include:**
- Harassment, discrimination, or offensive comments
- Publishing others' private information without permission
- Trolling, insulting comments, or personal attacks
- Public or private harassment
- Any conduct inappropriate for a professional setting

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the community leaders at conduct@gmservices.com. All complaints will be reviewed and investigated promptly and fairly.

## Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Technical Requirements:**
   - Python 3.11+
   - PostgreSQL 14+
   - Redis 6+
   - Node.js 18+
   - Docker Desktop
   - Git

2. **Account Setup:**
   - GitHub account
   - Access to development tools
   - Understanding of our tech stack

3. **Knowledge Base:**
   - Familiarity with Flask framework
   - Understanding of REST API principles
   - Basic knowledge of PostgreSQL
   - Frontend development skills (HTML/CSS/JavaScript)

### First-Time Setup

1. **Fork the Repository:**
   ```bash
   # Fork the repo on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/gm-services.git
   cd gm-services
   
   # Add upstream remote
   git remote add upstream https://github.com/gmservices/gm-services.git
   ```

2. **Set Up Development Environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   
   # Set up pre-commit hooks
   pre-commit install
   ```

3. **Configure Environment:**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your local configuration
   # Follow the Developer Guide for detailed setup
   ```

4. **Initialize Database:**
   ```bash
   # Create database
   createdb gmservices_dev
   
   # Run migrations
   flask db upgrade
   
   # Load test data (optional)
   python init_data.py
   ```

5. **Verify Setup:**
   ```bash
   # Run tests
   pytest
   
   # Start development server
   flask run
   
   # Visit http://localhost:5000
   ```

## Development Process

### Workflow Overview

We follow a **Git Flow** based workflow with some modifications for our needs:

```
main branch (production-ready code)
├── develop branch (integration branch)
    ├── feature/user-authentication
    ├── feature/payment-integration
    ├── bugfix/login-validation
    └── hotfix/security-patch
```

### Branch Naming Convention

- **Feature branches:** `feature/short-description`
- **Bug fixes:** `bugfix/issue-description`
- **Hotfixes:** `hotfix/critical-issue`
- **Documentation:** `docs/topic-name`
- **Refactoring:** `refactor/component-name`

### Development Steps

1. **Create an Issue:**
   - Search existing issues first
   - Use appropriate issue templates
   - Provide detailed description
   - Add relevant labels

2. **Create Feature Branch:**
   ```bash
   # Update your local repo
   git checkout develop
   git pull upstream develop
   
   # Create feature branch
   git checkout -b feature/your-feature-name
   ```

3. **Develop and Test:**
   ```bash
   # Make your changes
   # Write tests
   # Run tests locally
   pytest
   
   # Check code style
   black .
   flake8 .
   isort .
   ```

4. **Commit Changes:**
   ```bash
   # Stage changes
   git add .
   
   # Commit with conventional commit message
   git commit -m "feat: add user profile management"
   ```

5. **Push and Create PR:**
   ```bash
   # Push to your fork
   git push origin feature/your-feature-name
   
   # Create Pull Request on GitHub
   ```

## Coding Standards

### Python Code Style

We follow **PEP 8** with some project-specific conventions:

#### General Guidelines

```python
# Good: Clear, descriptive names
def calculate_service_price(service_type, duration, location):
    """Calculate the total price for a service request."""
    pass

# Bad: Unclear, abbreviated names
def calc_svc_pr(st, dur, loc):
    pass
```

#### Import Organization

```python
# Standard library imports
import os
import sys
from datetime import datetime

# Third-party imports
from flask import Flask, request, jsonify
from sqlalchemy import Column, Integer, String

# Local application imports
from models.user import User
from utils.helpers import format_currency
```

#### Function and Class Documentation

```python
class ServiceRequest:
    """Represents a service request in the system.
    
    Attributes:
        id (int): Unique identifier for the request
        user_id (int): ID of the requesting user
        service_type (str): Type of service requested
        status (str): Current status of the request
    """
    
    def calculate_total_cost(self, base_price: float, tax_rate: float = 0.1) -> float:
        """Calculate the total cost including taxes.
        
        Args:
            base_price: The base price before taxes
            tax_rate: Tax rate as decimal (default: 0.1 for 10%)
            
        Returns:
            Total cost including taxes
            
        Raises:
            ValueError: If base_price is negative
        """
        if base_price < 0:
            raise ValueError("Base price cannot be negative")
        
        return base_price * (1 + tax_rate)
```

#### Error Handling

```python
# Good: Specific exception handling
try:
    user = User.query.get(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    return user.process_payment(amount)
except ValueError as e:
    logger.error(f"Validation error: {e}")
    return {"error": "Invalid user"}, 400
except PaymentProcessingError as e:
    logger.error(f"Payment failed: {e}")
    return {"error": "Payment processing failed"}, 500

# Bad: Generic exception catching
try:
    return user.process_payment(amount)
except Exception as e:
    return {"error": "Something went wrong"}, 500
```

### Frontend Code Style

#### JavaScript Standards

```javascript
// Good: ES6+ syntax, clear naming
class PaymentProcessor {
    constructor(apiEndpoint) {
        this.apiEndpoint = apiEndpoint;
        this.retryAttempts = 3;
    }
    
    async processPayment(paymentData) {
        try {
            const response = await this.makeRequest(paymentData);
            return this.handleResponse(response);
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }
    
    async makeRequest(data) {
        return fetch(this.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(data)
        });
    }
}

// Bad: Old syntax, unclear naming
function pp(data) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/payment');
    xhr.send(data);
}
```

#### CSS/SCSS Organization

```scss
// Good: BEM methodology, organized structure
.service-card {
    border: 1px solid $border-color;
    border-radius: $border-radius;
    padding: $spacing-md;
    
    &__header {
        font-size: $font-size-lg;
        font-weight: $font-weight-bold;
        margin-bottom: $spacing-sm;
    }
    
    &__content {
        color: $text-color-secondary;
        line-height: $line-height-base;
    }
    
    &--featured {
        border-color: $primary-color;
        box-shadow: $shadow-elevated;
    }
}

// Bad: Unclear naming, no organization
.card1 {
    border: 1px solid #ccc;
}
.cardheader {
    font-size: 18px;
}
```

### Database Conventions

#### Model Design

```python
# Good: Clear relationships, proper constraints
class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    service_type = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text)
    priority = db.Column(db.Enum(Priority), default=Priority.NORMAL)
    status = db.Column(db.String(20), default='pending', index=True)
    estimated_cost = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with proper back references
    user = db.relationship('User', backref=db.backref('service_requests', lazy='dynamic'))
    payments = db.relationship('Payment', backref='service_request', cascade='all, delete-orphan')
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_service_user_status', 'user_id', 'status'),
        db.Index('idx_service_type_created', 'service_type', 'created_at'),
    )
```

## Testing Requirements

### Test Coverage Standards

- **Minimum coverage:** 80% overall
- **Critical components:** 95% coverage
- **New features:** 100% coverage required

### Test Types

#### Unit Tests

```python
# tests/test_models/test_service_request.py
import pytest
from decimal import Decimal
from models.service_request import ServiceRequest
from models.user import User

class TestServiceRequest:
    
    def test_create_service_request(self, db_session):
        """Test creating a valid service request."""
        user = User(username='testuser', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        service_request = ServiceRequest(
            user_id=user.id,
            service_type='automotive',
            description='Oil change needed',
            estimated_cost=Decimal('50.00')
        )
        
        db_session.add(service_request)
        db_session.commit()
        
        assert service_request.id is not None
        assert service_request.status == 'pending'
        assert service_request.user == user
    
    def test_calculate_total_cost(self):
        """Test cost calculation with taxes."""
        service_request = ServiceRequest()
        
        # Test normal calculation
        total = service_request.calculate_total_cost(100.0, 0.1)
        assert total == 110.0
        
        # Test with zero tax
        total = service_request.calculate_total_cost(100.0, 0.0)
        assert total == 100.0
        
        # Test error handling
        with pytest.raises(ValueError):
            service_request.calculate_total_cost(-50.0)
```

#### Integration Tests

```python
# tests/test_api/test_services.py
import json
import pytest
from flask import url_for

class TestServiceAPI:
    
    def test_create_service_request_api(self, client, auth_headers):
        """Test creating service request via API."""
        data = {
            'service_type': 'hotel',
            'description': 'Book a conference room',
            'estimated_cost': '200.00'
        }
        
        response = client.post(
            url_for('api.services.create'),
            data=json.dumps(data),
            content_type='application/json',
            headers=auth_headers
        )
        
        assert response.status_code == 201
        
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
        assert 'id' in response_data['data']
        
        # Verify database state
        service_request = ServiceRequest.query.get(response_data['data']['id'])
        assert service_request.service_type == 'hotel'
        assert service_request.description == 'Book a conference room'
```

#### End-to-End Tests

```python
# tests/test_e2e/test_service_workflow.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestServiceWorkflow:
    
    def test_complete_service_request_workflow(self, browser, live_server):
        """Test complete workflow from login to service completion."""
        # Login
        browser.get(f"{live_server.url}/login")
        
        username_field = browser.find_element(By.NAME, "username")
        password_field = browser.find_element(By.NAME, "password")
        
        username_field.send_keys("testuser")
        password_field.send_keys("testpass")
        
        submit_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Wait for redirect to dashboard
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
        )
        
        # Create service request
        browser.get(f"{live_server.url}/services/request")
        
        service_type = browser.find_element(By.NAME, "service_type")
        service_type.send_keys("automotive")
        
        description = browser.find_element(By.NAME, "description")
        description.send_keys("Need car inspection")
        
        submit_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Verify success
        success_message = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        
        assert "Request submitted successfully" in success_message.text
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/test_models/
pytest tests/test_api/
pytest tests/test_e2e/

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v

# Run only failed tests
pytest --lf
```

## Documentation Guidelines

### Code Documentation

#### Docstring Standards

```python
def process_payment_refund(payment_id: int, refund_amount: float, reason: str) -> dict:
    """Process a refund for a payment.
    
    This function handles the complete refund process including validation,
    payment gateway communication, and database updates.
    
    Args:
        payment_id: The ID of the payment to refund
        refund_amount: Amount to refund (must be <= original payment amount)
        reason: Reason for the refund (for audit purposes)
    
    Returns:
        Dictionary containing refund details:
        {
            'refund_id': str,
            'status': str,
            'amount': float,
            'processed_at': datetime
        }
    
    Raises:
        PaymentNotFoundError: If payment_id doesn't exist
        InvalidRefundAmountError: If refund_amount is invalid
        PaymentGatewayError: If payment gateway rejects the refund
    
    Example:
        >>> result = process_payment_refund(12345, 50.00, "Customer request")
        >>> print(result['status'])
        'completed'
    """
```

#### API Documentation

```python
@services_bp.route('/api/services', methods=['POST'])
def create_service_request():
    """Create a new service request.
    
    ---
    tags:
      - Services
    parameters:
      - in: body
        name: service_request
        description: Service request details
        required: true
        schema:
          type: object
          properties:
            service_type:
              type: string
              enum: [automotive, hotel, logistics, rental, gadgets, loans, jewelry, car_service, paperwork, creative_services, web_development]
              description: Type of service requested
            description:
              type: string
              description: Detailed description of the service needed
            estimated_cost:
              type: number
              format: decimal
              description: Estimated cost for the service
            priority:
              type: string
              enum: [low, normal, high, urgent]
              default: normal
              description: Priority level of the request
          required:
            - service_type
            - description
    responses:
      201:
        description: Service request created successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                id:
                  type: integer
                  description: ID of the created service request
                service_type:
                  type: string
                  description: Type of service
                status:
                  type: string
                  description: Current status
      400:
        description: Invalid input data
        schema:
          $ref: '#/definitions/ErrorResponse'
      401:
        description: Authentication required
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
```

### Updating Documentation

When making changes, update relevant documentation:

1. **API changes:** Update OpenAPI/Swagger specs
2. **New features:** Add to user guides and developer docs
3. **Configuration changes:** Update deployment documentation
4. **Breaking changes:** Update migration guides

## Pull Request Process

### Before Creating a PR

1. **Ensure your branch is up to date:**
   ```bash
   git checkout develop
   git pull upstream develop
   git checkout your-feature-branch
   git rebase develop
   ```

2. **Run the full test suite:**
   ```bash
   pytest
   npm test
   ```

3. **Check code quality:**
   ```bash
   black .
   flake8 .
   isort .
   mypy .
   ```

4. **Update documentation:**
   - API documentation
   - User guides (if applicable)
   - Developer documentation

### PR Title and Description

#### Title Format

Use conventional commit format:
- `feat: add user profile management`
- `fix: resolve payment processing timeout`
- `docs: update API documentation`
- `test: add integration tests for services`
- `refactor: improve database query performance`

#### Description Template

```markdown
## Description
Brief description of the changes and their purpose.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Related Issues
Fixes #123
Relates to #456

## Changes Made
- Added user profile management system
- Implemented avatar upload functionality
- Added profile validation
- Updated user dashboard

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] End-to-end tests pass
- [ ] Manual testing completed
- [ ] Cross-browser testing (if frontend changes)
- [ ] Mobile responsiveness tested (if UI changes)

## Screenshots (if applicable)
Before:
![Before](link-to-image)

After:
![After](link-to-image)

## Performance Impact
- [ ] No performance impact
- [ ] Performance improvement
- [ ] Performance impact analyzed and acceptable
- [ ] Performance benchmarks updated

## Security Considerations
- [ ] No security impact
- [ ] Security review completed
- [ ] Follows security best practices
- [ ] Input validation added
- [ ] Authorization checks implemented

## Database Changes
- [ ] No database changes
- [ ] Migration script included
- [ ] Backward compatible
- [ ] Data migration tested

## Deployment Notes
- [ ] No special deployment requirements
- [ ] Environment variables updated
- [ ] Configuration changes documented
- [ ] Dependencies updated

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] No breaking changes (or properly documented)
- [ ] Commits are properly formatted
```

### Review Process

1. **Automated Checks:**
   - CI/CD pipeline passes
   - Code quality checks pass
   - Security scans pass
   - Test coverage maintained

2. **Peer Review:**
   - At least 2 approvals required
   - Domain expert review for complex changes
   - Security team review for security-related changes

3. **Final Checks:**
   - Merge conflicts resolved
   - Branch up to date with target
   - Documentation updated

### Merging

- Use **squash and merge** for feature branches
- Use **merge commit** for hotfixes
- Delete branch after merging

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
## Bug Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
A clear and concise description of what actually happened.

## Screenshots
If applicable, add screenshots to help explain your problem.

## Environment
- OS: [e.g., macOS 12.0]
- Browser: [e.g., Chrome 96.0]
- Python Version: [e.g., 3.11.0]
- Application Version: [e.g., 1.2.3]

## Additional Context
Add any other context about the problem here.

## Possible Solution
If you have an idea of how to fix the issue, describe it here.
```

### Feature Requests

Use the feature request template:

```markdown
## Feature Description
A clear and concise description of the feature you'd like to see.

## Problem Statement
What problem does this feature solve? Who would benefit from it?

## Proposed Solution
Describe the solution you'd like to see implemented.

## Alternative Solutions
Describe any alternative solutions or features you've considered.

## Additional Context
Add any other context, mockups, or examples about the feature request.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Priority
- [ ] Low
- [ ] Medium
- [ ] High
- [ ] Critical
```

## Security Guidelines

### Security Best Practices

1. **Input Validation:**
   ```python
   from marshmallow import Schema, fields, validate
   
   class ServiceRequestSchema(Schema):
       service_type = fields.Str(
           required=True,
           validate=validate.OneOf(['automotive', 'hotel', 'logistics'])
       )
       description = fields.Str(
           required=True,
           validate=validate.Length(min=10, max=1000)
       )
       estimated_cost = fields.Decimal(
           places=2,
           validate=validate.Range(min=0, max=10000)
       )
   ```

2. **SQL Injection Prevention:**
   ```python
   # Good: Using ORM
   user = User.query.filter(User.email == email).first()
   
   # Good: Parameterized queries when raw SQL is necessary
   result = db.session.execute(
       text("SELECT * FROM users WHERE email = :email"),
       {"email": email}
   )
   
   # Bad: String concatenation
   query = f"SELECT * FROM users WHERE email = '{email}'"
   ```

3. **Authentication and Authorization:**
   ```python
   from functools import wraps
   from flask_login import current_user
   
   def require_role(role):
       def decorator(f):
           @wraps(f)
           def decorated_function(*args, **kwargs):
               if not current_user.is_authenticated:
                   abort(401)
               if not current_user.has_role(role):
                   abort(403)
               return f(*args, **kwargs)
           return decorated_function
       return decorator
   
   @services_bp.route('/admin/services')
   @require_role('admin')
   def admin_services():
       return render_template('admin/services.html')
   ```

### Security Review Process

1. **Automated Security Scanning:**
   ```bash
   # Run security checks
   bandit -r app/
   safety check
   npm audit
   ```

2. **Manual Security Review:**
   - Authentication and authorization checks
   - Input validation review
   - Output encoding verification
   - Configuration security review

3. **Security Testing:**
   - Penetration testing for major releases
   - Vulnerability scanning
   - Dependency security audits

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead:
1. Email security@gmservices.com
2. Include detailed description
3. Provide proof of concept (if applicable)
4. Allow time for patch before disclosure

## Community and Support

### Communication Channels

- **General Discussion:** [GitHub Discussions](https://github.com/gmservices/gm-services/discussions)
- **Development Chat:** [Discord Server](https://discord.gg/gmservices)
- **Email Support:** dev@gmservices.com
- **Security Issues:** security@gmservices.com

### Getting Help

1. **Check existing resources:**
   - Documentation
   - FAQ section
   - Closed issues
   - Discussions

2. **Ask questions:**
   - Use GitHub Discussions for general questions
   - Create issues for bugs or feature requests
   - Join our Discord for real-time help

3. **Provide context:**
   - Include relevant code snippets
   - Describe your environment
   - Share error messages
   - Explain what you've already tried

### Recognition

We recognize contributions through:

- **Contributors list** in README
- **Release notes** mentions
- **GitHub achievements** and badges
- **Annual recognition** program
- **Conference speaking** opportunities

### Maintainers

Current maintainers:

- **Project Lead:** [@project-lead](https://github.com/project-lead)
- **Backend Lead:** [@backend-lead](https://github.com/backend-lead)
- **Frontend Lead:** [@frontend-lead](https://github.com/frontend-lead)
- **DevOps Lead:** [@devops-lead](https://github.com/devops-lead)

### License

By contributing to GM Services, you agree that your contributions will be licensed under the same license as the project.

---

## Thank You! 🙏

Your contributions make the GM Services platform better for everyone. Whether you're fixing bugs, adding features, improving documentation, or helping other contributors, your efforts are appreciated!

**Happy coding!** 🚀

---

*This contributing guide is a living document. Please submit pull requests to improve it and help make contributing to GM Services even better.*

**Last Updated:** January 1, 2024  
**Next Review:** April 1, 2024  
**Maintainer:** Development Team