# Developer Guide

**GM Services Platform Developer Guide**  
**Version 1.0**  
**Last Updated:** January 1, 2024

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Architecture Overview](#architecture-overview)
4. [API Development](#api-development)
5. [Database Development](#database-development)
6. [Frontend Development](#frontend-development)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Contributing](#contributing)
10. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

Before you begin development on the GM Services platform, ensure you have:

- **Python 3.11+** - Primary programming language
- **PostgreSQL 14+** - Database system
- **Redis 6+** - Caching and session storage
- **Node.js 18+** - Frontend build tools
- **Docker Desktop** - Containerization platform
- **Git** - Version control system

### Quick Start

```bash
# Clone the repository
git clone https://github.com/gmservices/gm-services.git
cd gm-services

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your local configuration

# Initialize database
flask db upgrade

# Run the application
flask run
```

## Development Environment Setup

### Local Development

#### 1. Environment Configuration

Create a `.env` file in the project root:

```bash
# Application Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/gmservices_dev

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Payment Configuration (Development)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYSTACK_PUBLIC_KEY=pk_test_...

# Email Configuration
MAIL_SERVER=localhost
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password

# Security Configuration
JWT_SECRET_KEY=your-jwt-secret-key
BCRYPT_LOG_ROUNDS=12

# File Upload Configuration
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

#### 2. Database Setup

```bash
# Create PostgreSQL database
createdb gmservices_dev

# Run migrations
flask db upgrade

# Load initial data (optional)
python init_data.py
```

#### 3. Frontend Setup

```bash
# Install frontend dependencies
npm install

# Build frontend assets
npm run build

# Watch for changes (development)
npm run watch
```

### Docker Development

For a consistent development environment across teams:

```bash
# Build and start services
docker-compose up -d

# Run migrations
docker-compose exec web flask db upgrade

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

## Architecture Overview

### Project Structure

```
gm-services/
├── app.py                 # Application factory and main entry point
├── config.py             # Configuration management
├── database.py           # Database initialization and utilities
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker services configuration
│
├── blueprints/           # Flask blueprints (modules)
│   ├── admin/           # Administrative interface
│   ├── auth/            # Authentication and authorization
│   ├── gadgets/         # Technology services
│   ├── services/        # Core business services
│   ├── staff/           # Staff management
│   └── users/           # User management
│
├── models/              # Database models (SQLAlchemy)
│   ├── user.py         # User and authentication models
│   ├── service.py      # Service-related models
│   ├── payment.py      # Payment and transaction models
│   └── ...             # Other domain models
│
├── forms/               # WTForms form definitions
│   ├── car_service_forms.py
│   ├── hotel_forms.py
│   └── ...
│
├── templates/           # Jinja2 HTML templates
│   ├── base.html       # Base template
│   ├── auth/           # Authentication templates
│   ├── services/       # Service-specific templates
│   └── ...
│
├── static/              # Static assets
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   ├── images/         # Image assets
│   └── uploads/        # User uploads
│
├── migrations/          # Database migrations (Alembic)
├── chat/               # Real-time chat functionality
├── tasks/              # Background tasks (Celery)
├── utils/              # Utility functions and helpers
└── docs/               # Documentation
```

### Technology Stack

#### Backend
- **Flask 2.3.3** - Web framework
- **SQLAlchemy 2.0** - ORM and database toolkit
- **Flask-Migrate** - Database migrations
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and CSRF protection
- **Flask-Mail** - Email functionality
- **Flask-SocketIO** - Real-time communication
- **Celery** - Background task processing
- **Redis** - Caching and task queue
- **Gunicorn** - WSGI HTTP server

#### Frontend
- **HTML5/CSS3** - Markup and styling
- **JavaScript ES6+** - Client-side functionality
- **Bootstrap 5** - CSS framework
- **Socket.IO** - Real-time client communication
- **Chart.js** - Data visualization
- **DataTables** - Interactive tables

#### Database
- **PostgreSQL** - Primary database
- **Redis** - Session storage and caching

#### Payment Processing
- **Stripe** - Credit card processing
- **PayPal** - PayPal payments
- **Paystack** - African payment processing

## API Development

### Blueprint Structure

Each service category is organized as a Flask blueprint:

```python
# blueprints/services/__init__.py
from flask import Blueprint

services_bp = Blueprint('services', __name__, url_prefix='/services')

from . import routes, models, forms
```

### Route Definition

```python
# blueprints/services/routes.py
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from . import services_bp
from .models import ServiceRequest
from .forms import ServiceRequestForm

@services_bp.route('/request', methods=['GET', 'POST'])
@login_required
def create_request():
    form = ServiceRequestForm()
    
    if form.validate_on_submit():
        service_request = ServiceRequest(
            user_id=current_user.id,
            service_type=form.service_type.data,
            description=form.description.data
        )
        
        db.session.add(service_request)
        db.session.commit()
        
        return jsonify({'status': 'success', 'id': service_request.id})
    
    return render_template('services/request.html', form=form)
```

### API Response Format

All API endpoints should follow this response format:

```python
# Success Response
{
    "status": "success",
    "data": {
        "id": 123,
        "message": "Request created successfully"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}

# Error Response
{
    "status": "error",
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {
            "field": "email",
            "message": "Invalid email format"
        }
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Handling

Implement consistent error handling:

```python
from flask import jsonify
from werkzeug.exceptions import HTTPException

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    return jsonify({
        'status': 'error',
        'error': {
            'code': e.name,
            'message': e.description
        }
    }), e.code

@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({
        'status': 'error',
        'error': {
            'code': 'VALIDATION_ERROR',
            'message': 'Invalid input data',
            'details': e.messages
        }
    }), 400
```

## Database Development

### Model Definition

Use SQLAlchemy models with proper relationships:

```python
# models/service.py
from database import db
from datetime import datetime

class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='service_requests')
    payments = db.relationship('Payment', backref='service_request', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'service_type': self.service_type,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'user': self.user.username
        }
```

### Migrations

Create and apply database migrations:

```bash
# Create a new migration
flask db migrate -m "Add service request table"

# Apply migrations
flask db upgrade

# Downgrade (if needed)
flask db downgrade
```

### Database Queries

Use efficient queries with proper relationships:

```python
# Efficient query with joins
service_requests = db.session.query(ServiceRequest)\
    .join(User)\
    .filter(ServiceRequest.status == 'active')\
    .options(db.joinedload(ServiceRequest.user))\
    .all()

# Pagination
def get_paginated_requests(page=1, per_page=20):
    return ServiceRequest.query\
        .filter(ServiceRequest.status == 'active')\
        .order_by(ServiceRequest.created_at.desc())\
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
```

## Frontend Development

### Template Structure

Use template inheritance for consistent layouts:

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}GM Services{% endblock %}</title>
    
    <!-- CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/custom.css') }}" rel="stylesheet">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <!-- Navigation content -->
    </nav>
    
    <main class="container-fluid">
        {% block content %}{% endblock %}
    </main>
    
    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Form Handling

Implement forms with proper validation:

```html
<!-- templates/services/request.html -->
{% extends "base.html" %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h4>Request Service</h4>
            </div>
            <div class="card-body">
                <form id="service-request-form" method="POST">
                    {{ form.hidden_tag() }}
                    
                    <div class="mb-3">
                        {{ form.service_type.label(class="form-label") }}
                        {{ form.service_type(class="form-select") }}
                        {% if form.service_type.errors %}
                            <div class="invalid-feedback d-block">
                                {{ form.service_type.errors[0] }}
                            </div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        {{ form.description.label(class="form-label") }}
                        {{ form.description(class="form-control", rows="4") }}
                    </div>
                    
                    <button type="submit" class="btn btn-primary">Submit Request</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.getElementById('service-request-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    fetch('{{ url_for("services.create_request") }}', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Request submitted successfully!');
            window.location.href = '{{ url_for("services.list_requests") }}';
        } else {
            alert('Error: ' + data.error.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
});
</script>
{% endblock %}
```

### JavaScript Modules

Organize JavaScript code in modules:

```javascript
// static/js/services.js
class ServiceManager {
    constructor() {
        this.apiBase = '/api/services';
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadServices();
    }
    
    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('delete-service')) {
                this.deleteService(e.target.dataset.serviceId);
            }
        });
    }
    
    async loadServices() {
        try {
            const response = await fetch(`${this.apiBase}/list`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderServices(data.data);
            }
        } catch (error) {
            console.error('Error loading services:', error);
        }
    }
    
    async deleteService(serviceId) {
        if (!confirm('Are you sure you want to delete this service?')) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/${serviceId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.loadServices(); // Reload the list
            } else {
                alert('Error: ' + data.error.message);
            }
        } catch (error) {
            console.error('Error deleting service:', error);
        }
    }
    
    getCSRFToken() {
        return document.querySelector('meta[name=csrf-token]').getAttribute('content');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ServiceManager();
});
```

## Testing

### Unit Tests

Write comprehensive unit tests:

```python
# tests/test_services.py
import pytest
from flask import url_for
from models.service import ServiceRequest
from models.user import User

class TestServiceRequests:
    
    def test_create_service_request(self, client, authenticated_user):
        """Test creating a new service request."""
        data = {
            'service_type': 'automotive',
            'description': 'Need car maintenance'
        }
        
        response = client.post(
            url_for('services.create_request'),
            data=data,
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert ServiceRequest.query.count() == 1
        
        service_request = ServiceRequest.query.first()
        assert service_request.service_type == 'automotive'
        assert service_request.user_id == authenticated_user.id
    
    def test_list_service_requests(self, client, authenticated_user):
        """Test listing service requests."""
        # Create test data
        service_request = ServiceRequest(
            user_id=authenticated_user.id,
            service_type='hotel',
            description='Book a room'
        )
        db.session.add(service_request)
        db.session.commit()
        
        response = client.get(url_for('services.list_requests'))
        
        assert response.status_code == 200
        assert b'Book a room' in response.data
```

### Integration Tests

Test API endpoints:

```python
# tests/test_api.py
import json
import pytest

class TestServiceAPI:
    
    def test_api_create_service_request(self, client, authenticated_user):
        """Test API endpoint for creating service requests."""
        data = {
            'service_type': 'logistics',
            'description': 'Need package delivery'
        }
        
        response = client.post(
            '/api/services',
            data=json.dumps(data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {authenticated_user.get_token()}'}
        )
        
        assert response.status_code == 201
        
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
        assert 'id' in response_data['data']
    
    def test_api_unauthorized_access(self, client):
        """Test that unauthorized requests are rejected."""
        response = client.get('/api/services')
        assert response.status_code == 401
```

### Frontend Testing

Use JavaScript testing frameworks:

```javascript
// tests/frontend/test_services.js
describe('ServiceManager', () => {
    let serviceManager;
    let mockFetch;
    
    beforeEach(() => {
        mockFetch = jest.fn();
        global.fetch = mockFetch;
        serviceManager = new ServiceManager();
    });
    
    test('should load services on initialization', async () => {
        const mockResponse = {
            status: 'success',
            data: [
                { id: 1, service_type: 'automotive', description: 'Test service' }
            ]
        };
        
        mockFetch.mockResolvedValueOnce({
            json: () => Promise.resolve(mockResponse)
        });
        
        await serviceManager.loadServices();
        
        expect(mockFetch).toHaveBeenCalledWith('/api/services/list');
    });
    
    test('should delete service when confirmed', async () => {
        global.confirm = jest.fn(() => true);
        
        mockFetch.mockResolvedValueOnce({
            json: () => Promise.resolve({ status: 'success' })
        });
        
        await serviceManager.deleteService(1);
        
        expect(mockFetch).toHaveBeenCalledWith('/api/services/1', {
            method: 'DELETE',
            headers: { 'X-CSRFToken': expect.any(String) }
        });
    });
});
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_services.py

# Run frontend tests
npm test
```

## Deployment

### Production Configuration

Configure for production deployment:

```python
# config.py
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Performance settings
    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_POOL_RECYCLE = 3600
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/gmservices/app.log'
```

### Docker Deployment

Use Docker for consistent deployments:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
```

### CI/CD Pipeline

GitHub Actions workflow:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest --cov=app
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        # Your deployment script here
        echo "Deploying to production..."
```

## Contributing

### Development Workflow

1. **Fork the repository** and create a feature branch
2. **Write code** following the style guidelines
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Submit a pull request** with a clear description

### Code Style

Follow PEP 8 for Python code:

```bash
# Install development tools
pip install black flake8 isort

# Format code
black .

# Check style
flake8 .

# Sort imports
isort .
```

### Commit Messages

Use conventional commit format:

```
feat: add user authentication system
fix: resolve payment processing bug
docs: update API documentation
test: add unit tests for service module
refactor: improve database query performance
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## Troubleshooting

### Common Issues

#### Database Connection Issues

```bash
# Check PostgreSQL status
systemctl status postgresql

# Test connection
psql -h localhost -U username -d gmservices_dev

# Check environment variables
echo $DATABASE_URL
```

#### Migration Issues

```bash
# Reset migrations (development only)
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Fix migration conflicts
flask db merge -m "Merge migrations"
```

#### Performance Issues

```python
# Enable SQL query logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Use database profiling
from flask_sqlalchemy import get_debug_queries

@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= app.config.get('SLOW_QUERY_THRESHOLD', 0.1):
            app.logger.warning(
                f"Slow query: {query.statement} "
                f"Parameters: {query.parameters} "
                f"Duration: {query.duration}s"
            )
    return response
```

### Debug Mode

Enable debug mode for development:

```python
# In your .env file
FLASK_ENV=development
DEBUG=True

# In code
if app.debug:
    app.logger.setLevel(logging.DEBUG)
```

### Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/gmservices.log',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('GM Services startup')
```

---

## Resources

### Documentation Links
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)

### Development Tools
- [VS Code](https://code.visualstudio.com/) - Recommended IDE
- [Postman](https://www.postman.com/) - API testing
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL administration
- [Redis CLI](https://redis.io/topics/rediscli) - Redis management

### Support
- **Development Team:** dev@gmservices.com
- **Technical Lead:** tech-lead@gmservices.com
- **Documentation:** docs@gmservices.com

---

*This developer guide is maintained by the GM Services development team. Please submit pull requests for improvements and updates.*