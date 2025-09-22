# System Architecture

**GM Services Platform System Architecture**  
**Version 1.0**  
**Last Updated:** January 1, 2024

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [Data Architecture](#data-architecture)
4. [Security Architecture](#security-architecture)
5. [Integration Architecture](#integration-architecture)
6. [Deployment Architecture](#deployment-architecture)
7. [Performance Architecture](#performance-architecture)
8. [Monitoring and Observability](#monitoring-and-observability)
9. [Scalability Design](#scalability-design)
10. [Disaster Recovery](#disaster-recovery)

## Architecture Overview

### System Vision

GM Services is designed as a **multi-tenant, microservices-oriented platform** that provides comprehensive business services across multiple domains. The architecture emphasizes scalability, security, and maintainability while supporting rapid feature development and deployment.

### Architectural Principles

1. **Modularity:** Each service domain is independently deployable
2. **Scalability:** Horizontal scaling capabilities for all components
3. **Security:** Defense-in-depth security architecture
4. **Reliability:** 99.9% uptime with automated failover
5. **Performance:** Sub-200ms response times for critical operations
6. **Maintainability:** Clear separation of concerns and standardized interfaces

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Load Balancer                          │
│                      (AWS ALB/CloudFlare)                     │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    Web Application Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Flask     │  │   Gunicorn  │  │    Nginx    │             │
│  │ Application │  │   Workers   │  │  (Reverse   │             │
│  │             │  │             │  │   Proxy)    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                   Service Layer                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ Authentication│ │   Business   │ │  Integration │            │
│  │   Service     │ │   Services   │ │   Services   │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    Data Layer                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ PostgreSQL  │  │    Redis    │  │  File Store │             │
│  │  (Primary)  │  │  (Cache/    │  │   (S3/Local)│             │
│  │             │  │  Sessions)  │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## System Components

### 1. Web Application Layer

#### Flask Application Core

```python
# Application Factory Pattern
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)
    
    # Register blueprints
    register_blueprints(app)
    
    return app
```

**Key Features:**
- Modular blueprint architecture
- Extension-based configuration
- Environment-specific settings
- Centralized error handling

#### Blueprint Organization

```
blueprints/
├── auth/              # Authentication & Authorization
│   ├── routes.py     # Login, logout, registration
│   ├── models.py     # User, Role, Permission models
│   └── forms.py      # Authentication forms
├── admin/            # Administrative Interface
├── services/         # Core Business Services
│   ├── automotive/   # Vehicle services
│   ├── hotel/        # Hospitality services
│   ├── logistics/    # Delivery and logistics
│   ├── loans/        # Financial services
│   └── ...          # Other service categories
├── api/              # REST API endpoints
├── chat/             # Real-time communication
└── payments/         # Payment processing
```

### 2. Service Layer Architecture

#### Business Service Organization

```python
# Service Interface Pattern
class ServiceInterface(ABC):
    @abstractmethod
    def create_request(self, user_id: int, data: dict) -> ServiceRequest:
        pass
    
    @abstractmethod
    def process_request(self, request_id: int) -> ProcessResult:
        pass
    
    @abstractmethod
    def get_status(self, request_id: int) -> ServiceStatus:
        pass

# Concrete Implementation
class AutomotiveService(ServiceInterface):
    def __init__(self, db_session, payment_processor, notification_service):
        self.db = db_session
        self.payment = payment_processor
        self.notifications = notification_service
    
    def create_request(self, user_id: int, data: dict) -> ServiceRequest:
        # Validate input
        # Create database record
        # Initialize workflow
        # Send notifications
        pass
```

#### Service Categories

1. **Automotive Services**
   - Vehicle maintenance and repair
   - Car inspection and registration
   - Parts ordering and installation
   - Roadside assistance

2. **Hospitality Services**
   - Hotel bookings and management
   - Event space reservations
   - Catering services
   - Guest service management

3. **Financial Services**
   - Loan applications and processing
   - Credit assessments
   - Payment plan management
   - Financial consulting

4. **Technology Services**
   - Software development
   - IT consulting
   - Hardware procurement
   - System maintenance

5. **Logistics Services**
   - Package delivery
   - Supply chain management
   - Inventory tracking
   - Route optimization

### 3. Integration Layer

#### Payment Gateway Integration

```python
class PaymentGatewayManager:
    def __init__(self):
        self.gateways = {
            'stripe': StripeGateway(),
            'paypal': PayPalGateway(),
            'paystack': PaystackGateway()
        }
    
    def process_payment(self, amount, currency, gateway, payment_data):
        gateway_instance = self.gateways.get(gateway)
        if not gateway_instance:
            raise UnsupportedGatewayError(f"Gateway {gateway} not supported")
        
        return gateway_instance.charge(amount, currency, payment_data)
```

#### External Service Integrations

- **Email Services:** SendGrid, AWS SES
- **SMS Services:** Twilio, AWS SNS
- **Storage Services:** AWS S3, Google Cloud Storage
- **Maps Services:** Google Maps API, OpenStreetMap
- **Analytics:** Google Analytics, Mixpanel

## Data Architecture

### Database Design

#### Core Entity Relationships

```sql
-- User Management
Users (id, username, email, password_hash, created_at, updated_at)
Roles (id, name, description)
UserRoles (user_id, role_id)
Permissions (id, name, resource, action)
RolePermissions (role_id, permission_id)

-- Service Management
ServiceRequests (id, user_id, service_type, status, data, created_at)
ServiceProviders (id, name, service_types, rating, active)
ServiceAssignments (id, request_id, provider_id, assigned_at)

-- Payment Management
Payments (id, user_id, request_id, amount, currency, status, gateway)
PaymentMethods (id, user_id, type, data, is_default)
Transactions (id, payment_id, type, amount, status, gateway_id)

-- Communication
Messages (id, sender_id, recipient_id, content, type, created_at)
Notifications (id, user_id, type, title, content, read_at, created_at)
ChatRooms (id, name, type, participants, created_at)
```

#### Data Partitioning Strategy

```sql
-- Partition large tables by date for performance
CREATE TABLE service_requests_2024_01 PARTITION OF service_requests
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE service_requests_2024_02 PARTITION OF service_requests
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Index strategy for performance
CREATE INDEX CONCURRENTLY idx_service_requests_user_status 
    ON service_requests (user_id, status) 
    WHERE status IN ('pending', 'in_progress');

CREATE INDEX CONCURRENTLY idx_service_requests_created_at 
    ON service_requests (created_at DESC);
```

### Caching Strategy

#### Redis Cache Architecture

```python
class CacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_configs = {
            'user_sessions': {'ttl': 3600, 'prefix': 'session:'},
            'service_data': {'ttl': 1800, 'prefix': 'service:'},
            'payment_cache': {'ttl': 300, 'prefix': 'payment:'},
            'rate_limits': {'ttl': 60, 'prefix': 'rate:'}
        }
    
    def get_cached_service(self, service_id):
        cache_key = f"service:{service_id}"
        cached_data = self.redis.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        
        # Fetch from database
        service_data = self.fetch_from_db(service_id)
        
        # Cache for future requests
        self.redis.setex(
            cache_key,
            self.cache_configs['service_data']['ttl'],
            json.dumps(service_data)
        )
        
        return service_data
```

#### Cache Invalidation Strategy

- **Time-based expiration** for frequently changing data
- **Event-driven invalidation** for critical updates
- **Cache warming** for predictable access patterns
- **Distributed cache** for multi-instance deployments

## Security Architecture

### Defense in Depth

#### Layer 1: Network Security

```nginx
# Nginx Security Configuration
server {
    listen 443 ssl http2;
    server_name gmservices.com;
    
    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    
    location /auth/login {
        limit_req zone=login burst=3 nodelay;
        proxy_pass http://app_servers;
    }
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://app_servers;
    }
}
```

#### Layer 2: Application Security

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Rate Limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour", "100 per minute"]
)

# Input Validation
class ServiceRequestValidator:
    def __init__(self):
        self.schema = {
            'service_type': {'type': 'string', 'allowed': ALLOWED_SERVICE_TYPES},
            'description': {'type': 'string', 'minlength': 10, 'maxlength': 1000},
            'estimated_cost': {'type': 'float', 'min': 0, 'max': 10000}
        }
    
    def validate(self, data):
        v = Validator(self.schema)
        if not v.validate(data):
            raise ValidationError(v.errors)
        return v.document

# CSRF Protection
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# SQL Injection Prevention
from sqlalchemy import text

def get_user_services(user_id):
    # Parameterized query
    query = text("""
        SELECT s.* FROM service_requests s 
        WHERE s.user_id = :user_id 
        AND s.status = :status
    """)
    
    return db.session.execute(query, {
        'user_id': user_id,
        'status': 'active'
    }).fetchall()
```

#### Layer 3: Data Security

```python
# Data Encryption
class DataEncryption:
    def __init__(self, encryption_key):
        self.cipher_suite = Fernet(encryption_key)
    
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive data before storing in database."""
        if isinstance(data, str):
            data = data.encode()
        return self.cipher_suite.encrypt(data)
    
    def decrypt_sensitive_data(self, encrypted_data):
        """Decrypt sensitive data after retrieving from database."""
        decrypted = self.cipher_suite.decrypt(encrypted_data)
        return decrypted.decode()

# PII Handling
class PIIHandler:
    @staticmethod
    def mask_email(email):
        """Mask email for logging and display."""
        if '@' not in email:
            return email
        username, domain = email.split('@', 1)
        if len(username) <= 2:
            return f"{'*' * len(username)}@{domain}"
        return f"{username[0]}{'*' * (len(username) - 2)}{username[-1]}@{domain}"
    
    @staticmethod
    def mask_phone(phone):
        """Mask phone number for security."""
        if len(phone) < 4:
            return '*' * len(phone)
        return f"{'*' * (len(phone) - 4)}{phone[-4:]}"
```

### Authentication and Authorization

#### Multi-Factor Authentication

```python
class MFAManager:
    def __init__(self):
        self.totp = pyotp.TOTP
        self.qr_generator = qrcode
    
    def generate_secret(self, user):
        """Generate TOTP secret for user."""
        secret = pyotp.random_base32()
        user.mfa_secret = secret
        db.session.commit()
        
        return secret
    
    def generate_qr_code(self, user, secret):
        """Generate QR code for authenticator app setup."""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            user.email,
            issuer_name="GM Services"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        return qr.make_image(fill_color="black", back_color="white")
    
    def verify_token(self, user, token):
        """Verify TOTP token."""
        if not user.mfa_secret:
            return False
        
        totp = pyotp.TOTP(user.mfa_secret)
        return totp.verify(token, valid_window=1)
```

#### Role-Based Access Control

```python
class Permission:
    def __init__(self, resource, action):
        self.resource = resource
        self.action = action
    
    def __str__(self):
        return f"{self.action}:{self.resource}"

class Role:
    def __init__(self, name):
        self.name = name
        self.permissions = set()
    
    def add_permission(self, permission):
        self.permissions.add(permission)
    
    def has_permission(self, permission):
        return permission in self.permissions

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage
@services_bp.route('/admin/services')
@require_permission(Permission('services', 'admin'))
def admin_services():
    return render_template('admin/services.html')
```

## Integration Architecture

### API Gateway Pattern

```python
class APIGateway:
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.authenticator = JWTAuthenticator()
        self.validator = RequestValidator()
        self.logger = APILogger()
    
    def handle_request(self, request):
        try:
            # Rate limiting
            self.rate_limiter.check_rate_limit(request)
            
            # Authentication
            user = self.authenticator.authenticate(request)
            
            # Request validation
            validated_data = self.validator.validate(request)
            
            # Route to appropriate service
            response = self.route_request(validated_data, user)
            
            # Log request/response
            self.logger.log_api_call(request, response, user)
            
            return response
            
        except RateLimitExceeded:
            return {'error': 'Rate limit exceeded'}, 429
        except AuthenticationError:
            return {'error': 'Authentication required'}, 401
        except ValidationError as e:
            return {'error': 'Invalid request', 'details': e.errors}, 400
```

### Event-Driven Architecture

```python
class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)
    
    def subscribe(self, event_type, handler):
        self.subscribers[event_type].append(handler)
    
    def publish(self, event):
        for handler in self.subscribers[event.type]:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}")

# Event Handlers
@event_bus.subscribe('service_request_created')
def send_confirmation_email(event):
    email_service.send_template_email(
        to=event.user.email,
        template='service_confirmation',
        data=event.service_data
    )

@event_bus.subscribe('payment_completed')
def update_service_status(event):
    service_request = ServiceRequest.query.get(event.service_id)
    service_request.status = 'paid'
    db.session.commit()

# Publishing Events
def create_service_request(user_id, service_data):
    service_request = ServiceRequest(user_id=user_id, **service_data)
    db.session.add(service_request)
    db.session.commit()
    
    # Publish event
    event_bus.publish(ServiceRequestCreatedEvent(
        user_id=user_id,
        service_id=service_request.id,
        service_data=service_data
    ))
```

## Deployment Architecture

### Container Orchestration

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  web:
    image: gmservices/app:latest
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - db
      - redis
    networks:
      - app-network

  db:
    image: postgres:14
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:6-alpine
    deploy:
      replicas: 1
    volumes:
      - redis_data:/data
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: overlay
```

### Cloud Infrastructure

#### AWS Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Route 53                              │
│                      (DNS Management)                          │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                      CloudFront                               │
│                   (CDN + WAF)                                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                   Application Load Balancer                   │
│                      (Multi-AZ)                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                      ECS Fargate                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Service   │  │   Service   │  │   Service   │             │
│  │   Task 1    │  │   Task 2    │  │   Task 3    │             │
│  │  (AZ-1)     │  │  (AZ-2)     │  │  (AZ-1)     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    RDS PostgreSQL                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Primary   │  │  Read       │  │  Read       │             │
│  │  (AZ-1)     │  │ Replica 1   │  │ Replica 2   │             │
│  │             │  │  (AZ-2)     │  │  (AZ-3)     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

#### Infrastructure as Code

```terraform
# main.tf
provider "aws" {
  region = var.aws_region
}

# VPC Configuration
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "gm-services-vpc"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "gm-services-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier     = "gm-services-db"
  engine         = "postgres"
  engine_version = "14.7"
  instance_class = "db.t3.medium"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp2"
  storage_encrypted     = true
  
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  deletion_protection = true
  
  tags = {
    Name = "gm-services-database"
  }
}
```

## Performance Architecture

### Performance Monitoring

```python
import time
import functools
from flask import request, g

def monitor_performance():
    """Decorator to monitor endpoint performance."""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                status = 'success'
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                end_time = time.time()
                duration = end_time - start_time
                
                # Log performance metrics
                performance_logger.info({
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'duration': duration,
                    'status': status,
                    'user_id': getattr(g, 'user_id', None)
                })
                
                # Send to monitoring system
                metrics_client.histogram(
                    'request_duration',
                    duration,
                    tags={
                        'endpoint': request.endpoint,
                        'method': request.method,
                        'status': status
                    }
                )
        
        return decorated_function
    return decorator

# Usage
@services_bp.route('/api/services', methods=['POST'])
@monitor_performance()
def create_service():
    # Service logic here
    pass
```

### Caching Strategy

```python
class PerformanceOptimizer:
    def __init__(self):
        self.cache = Redis()
        self.db_pool = ConnectionPool()
    
    def cached_query(self, cache_key, query_func, ttl=3600):
        """Generic cached query wrapper."""
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Execute query
        result = query_func()
        
        # Cache result
        self.cache.setex(cache_key, ttl, json.dumps(result))
        
        return result
    
    def invalidate_cache_pattern(self, pattern):
        """Invalidate cache entries matching pattern."""
        keys = self.cache.keys(pattern)
        if keys:
            self.cache.delete(*keys)

# Database Query Optimization
class OptimizedQueries:
    @staticmethod
    def get_user_services_with_details(user_id, limit=20, offset=0):
        """Optimized query with eager loading."""
        return ServiceRequest.query\
            .filter_by(user_id=user_id)\
            .options(
                joinedload(ServiceRequest.payments),
                joinedload(ServiceRequest.user),
                selectinload(ServiceRequest.status_history)
            )\
            .order_by(ServiceRequest.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
```

## Monitoring and Observability

### Application Monitoring

```python
import logging
import structlog
from pythonjsonlogger import jsonlogger

# Structured Logging Configuration
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Application Logger
logger = structlog.get_logger()

class ServiceMonitor:
    def __init__(self):
        self.metrics_client = MetricsClient()
    
    def log_service_request(self, user_id, service_type, request_id):
        logger.info(
            "service_request_created",
            user_id=user_id,
            service_type=service_type,
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
        self.metrics_client.increment(
            'service_requests_total',
            tags={'service_type': service_type}
        )
    
    def log_payment_processed(self, payment_id, amount, gateway):
        logger.info(
            "payment_processed",
            payment_id=payment_id,
            amount=amount,
            gateway=gateway,
            timestamp=datetime.utcnow().isoformat()
        )
        
        self.metrics_client.histogram(
            'payment_amount',
            amount,
            tags={'gateway': gateway}
        )
```

### Health Check System

```python
class HealthCheckManager:
    def __init__(self):
        self.checks = []
    
    def register_check(self, name, check_func):
        self.checks.append((name, check_func))
    
    def run_all_checks(self):
        results = {}
        overall_status = 'healthy'
        
        for name, check_func in self.checks:
            try:
                result = check_func()
                results[name] = {
                    'status': 'healthy' if result else 'unhealthy',
                    'timestamp': datetime.utcnow().isoformat()
                }
                if not result:
                    overall_status = 'unhealthy'
            except Exception as e:
                results[name] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
                overall_status = 'unhealthy'
        
        return {
            'status': overall_status,
            'checks': results,
            'timestamp': datetime.utcnow().isoformat()
        }

# Health Check Implementations
def check_database_connectivity():
    try:
        db.session.execute(text('SELECT 1'))
        return True
    except Exception:
        return False

def check_redis_connectivity():
    try:
        redis_client.ping()
        return True
    except Exception:
        return False

def check_external_api_availability():
    try:
        response = requests.get('https://api.stripe.com/v1', timeout=5)
        return response.status_code == 401  # Expected unauthorized response
    except Exception:
        return False

# Register health checks
health_manager = HealthCheckManager()
health_manager.register_check('database', check_database_connectivity)
health_manager.register_check('redis', check_redis_connectivity)
health_manager.register_check('stripe_api', check_external_api_availability)
```

### Alerting System

```python
class AlertManager:
    def __init__(self):
        self.alert_channels = {
            'email': EmailAlertChannel(),
            'slack': SlackAlertChannel(),
            'pagerduty': PagerDutyAlertChannel()
        }
    
    def send_alert(self, severity, message, context=None):
        alert = Alert(
            severity=severity,
            message=message,
            context=context or {},
            timestamp=datetime.utcnow()
        )
        
        # Route based on severity
        if severity in ['critical', 'high']:
            self.alert_channels['pagerduty'].send(alert)
            self.alert_channels['slack'].send(alert)
        elif severity == 'medium':
            self.alert_channels['slack'].send(alert)
        else:
            self.alert_channels['email'].send(alert)

# Alert Triggers
@app.errorhandler(500)
def handle_server_error(error):
    alert_manager.send_alert(
        severity='high',
        message='Internal server error occurred',
        context={
            'error': str(error),
            'endpoint': request.endpoint,
            'user_id': getattr(g, 'user_id', None)
        }
    )
    return jsonify({'error': 'Internal server error'}), 500
```

## Scalability Design

### Horizontal Scaling Strategy

```yaml
# Kubernetes Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gm-services-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gm-services
  template:
    metadata:
      labels:
        app: gm-services
    spec:
      containers:
      - name: app
        image: gmservices/app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: gm-services-service
spec:
  selector:
    app: gm-services
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: gm-services-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: gm-services-app
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Database Scaling

```python
class DatabaseRouter:
    def __init__(self):
        self.write_db = create_engine(WRITE_DATABASE_URL)
        self.read_dbs = [
            create_engine(READ_REPLICA_1_URL),
            create_engine(READ_REPLICA_2_URL),
            create_engine(READ_REPLICA_3_URL)
        ]
        self.current_read_index = 0
    
    def get_write_connection(self):
        return self.write_db.connect()
    
    def get_read_connection(self):
        # Round-robin load balancing
        connection = self.read_dbs[self.current_read_index].connect()
        self.current_read_index = (self.current_read_index + 1) % len(self.read_dbs)
        return connection

# Usage in models
class ReadWriteModel:
    @classmethod
    def create(cls, **kwargs):
        # Write operations go to primary
        with db_router.get_write_connection() as conn:
            instance = cls(**kwargs)
            conn.execute(instance.insert_query())
            return instance
    
    @classmethod
    def find_by_id(cls, id):
        # Read operations can use replicas
        with db_router.get_read_connection() as conn:
            result = conn.execute(cls.select_query(id=id))
            return cls.from_result(result)
```

## Disaster Recovery

### Backup Strategy

```bash
#!/bin/bash
# backup.sh - Automated backup script

BACKUP_DIR="/backups/$(date +%Y-%m-%d)"
mkdir -p $BACKUP_DIR

# Database backup
pg_dump $DATABASE_URL | gzip > $BACKUP_DIR/database.sql.gz

# Application data backup
tar -czf $BACKUP_DIR/app_data.tar.gz /app/data/

# Upload to S3
aws s3 cp $BACKUP_DIR/ s3://gm-services-backups/$(date +%Y-%m-%d)/ --recursive

# Cleanup old backups (keep 30 days)
find /backups/ -type d -mtime +30 -exec rm -rf {} \;

# Verify backup integrity
if [ $? -eq 0 ]; then
    echo "Backup completed successfully"
else
    echo "Backup failed" | mail -s "Backup Alert" admin@gmservices.com
fi
```

### Recovery Procedures

```python
class DisasterRecoveryManager:
    def __init__(self):
        self.backup_storage = S3BackupStorage()
        self.notification_service = NotificationService()
    
    def initiate_recovery(self, recovery_point):
        """Initiate disaster recovery process."""
        try:
            # 1. Stop application services
            self.stop_application_services()
            
            # 2. Restore database
            self.restore_database(recovery_point)
            
            # 3. Restore application data
            self.restore_application_data(recovery_point)
            
            # 4. Start services
            self.start_application_services()
            
            # 5. Verify system health
            if self.verify_system_health():
                self.notification_service.send_alert(
                    "Disaster recovery completed successfully",
                    severity="info"
                )
            else:
                raise RecoveryVerificationError("System health check failed")
                
        except Exception as e:
            self.notification_service.send_alert(
                f"Disaster recovery failed: {str(e)}",
                severity="critical"
            )
            raise
    
    def restore_database(self, recovery_point):
        """Restore database from backup."""
        backup_file = self.backup_storage.get_backup(
            type='database',
            timestamp=recovery_point
        )
        
        # Restore using pg_restore
        subprocess.run([
            'pg_restore',
            '--host', DB_HOST,
            '--username', DB_USER,
            '--dbname', DB_NAME,
            backup_file
        ], check=True)
```

---

## Conclusion

The GM Services platform architecture is designed to be robust, scalable, and maintainable. Key architectural decisions prioritize:

1. **Modularity** - Independent service domains
2. **Security** - Multi-layered protection
3. **Performance** - Optimized for scale
4. **Reliability** - High availability design
5. **Observability** - Comprehensive monitoring

This architecture supports the platform's growth from startup to enterprise scale while maintaining security, performance, and reliability standards.

---

**Document Maintenance:**
- **Last Updated:** January 1, 2024
- **Next Review:** April 1, 2024
- **Owner:** Architecture Team
- **Reviewers:** CTO, Senior Engineers, Security Team