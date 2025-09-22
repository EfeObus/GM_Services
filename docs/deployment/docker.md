# Docker Deployment Guide

This guide covers deploying GM Services using Docker and Docker Compose for development, staging, and production environments.

## Prerequisites

- Docker 20.10+ installed
- Docker Compose v2.0+ installed
- 8GB+ RAM recommended
- 20GB+ disk space
- PostgreSQL 13+ (if not using containerized database)

## Quick Start

### Development Environment

```bash
# Clone the repository
git clone https://github.com/your-org/gm-services.git
cd gm-services

# Copy environment file
cp .env.example .env

# Edit environment variables
nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Access the application
open http://localhost:5000
```

## Docker Configuration

### Dockerfile

The application uses a multi-stage Dockerfile for optimized builds:

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### Docker Compose Configuration

#### docker-compose.yml (Development)

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
      - DATABASE_URL=postgresql://gmservices:password@db:5432/gmservices_dev
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - PAYPAL_CLIENT_ID=${PAYPAL_CLIENT_ID}
      - PAYSTACK_SECRET_KEY=${PAYSTACK_SECRET_KEY}
    volumes:
      - .:/app
      - /app/__pycache__
      - /app/instance
    depends_on:
      - db
      - redis
    networks:
      - gmservices-network
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=gmservices_dev
      - POSTGRES_USER=gmservices
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - gmservices-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - gmservices-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./static:/var/www/static:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    networks:
      - gmservices-network
    restart: unless-stopped

  worker:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://gmservices:password@db:5432/gmservices_dev
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    networks:
      - gmservices-network
    restart: unless-stopped

  scheduler:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A app.celery beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://gmservices:password@db:5432/gmservices_dev
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    networks:
      - gmservices-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  gmservices-network:
    driver: bridge
```

#### docker-compose.prod.yml (Production)

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - PAYPAL_CLIENT_ID=${PAYPAL_CLIENT_ID}
      - PAYSTACK_SECRET_KEY=${PAYSTACK_SECRET_KEY}
      - MAIL_SERVER=${MAIL_SERVER}
      - MAIL_USERNAME=${MAIL_USERNAME}
      - MAIL_PASSWORD=${MAIL_PASSWORD}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - S3_BUCKET=${S3_BUCKET}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
    networks:
      - gmservices-network
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_volume:/var/www/static:ro
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    networks:
      - gmservices-network
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"

  worker:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A app.celery worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    networks:
      - gmservices-network

volumes:
  static_volume:

networks:
  gmservices-network:
    external: true
```

## Environment Configuration

### .env File

```bash
# Application
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DEBUG=False
TESTING=False

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/gmservices
DATABASE_POOL_SIZE=20
DATABASE_POOL_OVERFLOW=30

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Payment Processing
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_MODE=live

PAYSTACK_PUBLIC_KEY=pk_live_...
PAYSTACK_SECRET_KEY=sk_live_...

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@gmservices.com

# File Storage (AWS S3)
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET=gmservices-uploads
S3_LOCATION=https://gmservices-uploads.s3.amazonaws.com/

# Social Authentication
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
NEW_RELIC_LICENSE_KEY=your_new_relic_key
DATADOG_API_KEY=your_datadog_api_key

# Security
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
RATE_LIMIT_STORAGE_URL=redis://localhost:6379/3

# Chat/WebSocket
SOCKETIO_ASYNC_MODE=redis
SOCKETIO_LOGGER=True
SOCKETIO_ENGINEIO_LOGGER=True
```

## Nginx Configuration

### nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:5000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    server {
        listen 80;
        server_name gmservices.com www.gmservices.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name gmservices.com www.gmservices.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # WebSocket connections
        location /socket.io/ {
            proxy_pass http://app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_buffering off;
        }

        # Login rate limiting
        location /auth/login {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Application
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # Health check
        location /health {
            access_log off;
            proxy_pass http://app;
            proxy_set_header Host $host;
        }
    }
}
```

## Database Setup

### PostgreSQL Initialization

Create `init-scripts/01-init-db.sql`:

```sql
-- Create databases
CREATE DATABASE gmservices_dev;
CREATE DATABASE gmservices_test;
CREATE DATABASE gmservices_prod;

-- Create users
CREATE USER gmservices_app WITH ENCRYPTED PASSWORD 'app_password';
CREATE USER gmservices_readonly WITH ENCRYPTED PASSWORD 'readonly_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE gmservices_dev TO gmservices_app;
GRANT ALL PRIVILEGES ON DATABASE gmservices_test TO gmservices_app;
GRANT ALL PRIVILEGES ON DATABASE gmservices_prod TO gmservices_app;

GRANT CONNECT ON DATABASE gmservices_prod TO gmservices_readonly;

-- Extensions
\c gmservices_dev;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

\c gmservices_test;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

\c gmservices_prod;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
```

### Database Migration

```bash
# Initialize database
docker-compose exec app flask db init

# Create migration
docker-compose exec app flask db migrate -m "Initial migration"

# Apply migration
docker-compose exec app flask db upgrade

# Create admin user
docker-compose exec app python create_admin.py
```

## Deployment Commands

### Development

```bash
# Build and start services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Execute commands in container
docker-compose exec app flask shell
docker-compose exec app flask db upgrade
docker-compose exec app python create_admin.py

# Stop services
docker-compose down

# Reset everything
docker-compose down -v
docker system prune -f
```

### Production

```bash
# Deploy to production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale app=3 --scale worker=2

# Rolling update
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --no-deps app

# View production logs
docker-compose -f docker-compose.prod.yml logs -f app
```

## Monitoring and Health Checks

### Health Check Endpoint

The application includes a health check endpoint at `/health`:

```python
@app.route('/health')
def health_check():
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check Redis connection
        redis_client.ping()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': app.config.get('VERSION', '1.0.0'),
            'services': {
                'database': 'healthy',
                'redis': 'healthy'
            }
        }, 200
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, 503
```

### Docker Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
```

### Monitoring with Docker

```bash
# Check container health
docker-compose ps

# Monitor resource usage
docker stats

# Check logs
docker-compose logs -f --tail=100 app

# Execute health check manually
docker-compose exec app curl -f http://localhost:5000/health
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec db pg_dump -U gmservices gmservices_prod > backup.sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U gmservices gmservices_prod > ${BACKUP_DIR}/backup_${DATE}.sql
gzip ${BACKUP_DIR}/backup_${DATE}.sql

# Keep only last 7 days of backups
find ${BACKUP_DIR} -name "backup_*.sql.gz" -mtime +7 -delete
```

### Volume Backup

```bash
# Backup PostgreSQL data
docker run --rm -v gm-services_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data

# Backup Redis data
docker run --rm -v gm-services_redis_data:/data -v $(pwd):/backup ubuntu tar czf /backup/redis_backup.tar.gz /data

# Restore PostgreSQL data
docker run --rm -v gm-services_postgres_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/postgres_backup.tar.gz -C /
```

## Security Considerations

### Container Security

```dockerfile
# Use non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Read-only filesystem
docker run --read-only --tmpfs /tmp --tmpfs /var/run --tmpfs /var/lock gmservices:latest

# Security scanning
docker scan gmservices:latest
```

### Secrets Management

```yaml
# Use Docker secrets in production
services:
  app:
    secrets:
      - db_password
      - stripe_secret_key
    environment:
      - DATABASE_PASSWORD_FILE=/run/secrets/db_password
      - STRIPE_SECRET_KEY_FILE=/run/secrets/stripe_secret_key

secrets:
  db_password:
    external: true
  stripe_secret_key:
    external: true
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find process using port
   lsof -i :5000
   
   # Kill process
   kill -9 <PID>
   ```

2. **Database connection failed**
   ```bash
   # Check database logs
   docker-compose logs db
   
   # Connect to database
   docker-compose exec db psql -U gmservices -d gmservices_dev
   ```

3. **Out of memory**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase memory limits in docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 2G
   ```

4. **SSL certificate issues**
   ```bash
   # Generate self-signed certificate
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout ssl/key.pem -out ssl/cert.pem
   ```

### Debugging

```bash
# Enter container shell
docker-compose exec app bash

# Debug with Python
docker-compose exec app python -c "import app; print(app.config)"

# View environment variables
docker-compose exec app env

# Check network connectivity
docker-compose exec app ping db
docker-compose exec app nc -zv redis 6379
```

## Performance Optimization

### Resource Limits

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Caching

```yaml
# Add Redis caching layer
services:
  redis-cache:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### Database Optimization

```yaml
# PostgreSQL performance tuning
services:
  db:
    image: postgres:15-alpine
    command: postgres -c shared_preload_libraries=pg_stat_statements -c max_connections=200 -c shared_buffers=256MB
```

## Related Documentation

- [Cloud Platform Deployment](cloud-platforms.md)
- [Environment Configuration](configuration.md)
- [Monitoring and Logging](monitoring.md)
- [Security Best Practices](../developer/security.md)