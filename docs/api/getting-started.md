# API Documentation - Getting Started

## Overview

The GM Services API is a RESTful web service that allows developers to integrate with our comprehensive multi-service platform. The API provides programmatic access to all platform features including user management, service requests, payments, and real-time communication.

## Base URLs

- **Production**: `https://api.gmservices.com/v1/`
- **Staging**: `https://staging-api.gmservices.com/v1/`
- **Development**: `http://localhost:5000/api/v1/`

## Authentication

### JWT Bearer Token (Recommended)

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     https://api.gmservices.com/v1/services
```

### API Key Authentication

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     https://api.gmservices.com/v1/services
```

### Getting an Access Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 3600,
  "user": {
    "id": 123,
    "email": "user@example.com",
    "role": "customer"
  }
}
```

## Rate Limiting

- **Free Tier**: 100 requests/hour
- **Basic Plan**: 1,000 requests/hour
- **Premium Plan**: 10,000 requests/hour
- **Enterprise**: Custom limits

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1641811200
```

## Response Format

All API responses follow a consistent format:

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request parameters are invalid",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |

## Pagination

List endpoints support pagination:

```http
GET /api/v1/services?page=2&per_page=20
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": true
  }
}
```

## Quick Examples

### Get All Services
```bash
curl -H "Authorization: Bearer TOKEN" \
     https://api.gmservices.com/v1/services
```

### Create Service Request
```bash
curl -X POST \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "service_id": 1,
       "description": "Need car maintenance",
       "preferred_date": "2024-01-15"
     }' \
     https://api.gmservices.com/v1/service-requests
```

### Process Payment
```bash
curl -X POST \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "amount": 29999,
       "currency": "usd",
       "service_request_id": 789
     }' \
     https://api.gmservices.com/v1/payments/intents
```

## SDK Libraries

- **Python**: `pip install gmservices-python`
- **JavaScript/Node.js**: `npm install gmservices-js`
- **PHP**: `composer require gmservices/gmservices-php`
- **Ruby**: `gem install gmservices`

## Next Steps

- [Authentication Guide](authentication.md)
- [Service Management API](services.md)
- [Payment Processing API](payments.md)
- [Real-time Chat API](chat.md)
- [Webhook Integration](webhooks.md)

## Support

- **API Support**: [api-support@gmservices.com](mailto:api-support@gmservices.com)
- **Documentation Issues**: [GitHub Issues](https://github.com/gmservices/gm-services/issues)
- **Community Forum**: [community.gmservices.com](https://community.gmservices.com)