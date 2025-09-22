# Service Management API

The Service Management API allows you to interact with the GM Services platform's comprehensive service catalog, submit service requests, and track their progress.

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/services` | List all available services |
| GET | `/services/{id}` | Get service details |
| POST | `/service-requests` | Create a service request |
| GET | `/service-requests` | List user's service requests |
| GET | `/service-requests/{id}` | Get service request details |
| PUT | `/service-requests/{id}` | Update service request |
| DELETE | `/service-requests/{id}` | Cancel service request |

## Service Categories

| Category | Description | Example Services |
|----------|-------------|------------------|
| `automotive` | Vehicle sales and services | Car dealership, maintenance, repairs |
| `loans` | Financial lending services | Personal loans, business loans, auto loans |
| `gadgets` | Electronics and technology | Smartphones, laptops, accessories |
| `hotel` | Hospitality services | Accommodation, event management |
| `logistics` | Shipping and delivery | Express delivery, international shipping |
| `rental` | Equipment and vehicle rental | Car rental, equipment rental |
| `car_service` | Automotive maintenance | Oil change, brake service, diagnostics |
| `paperwork` | Documentation services | Vehicle registration, license plates |
| `jewelry` | Luxury jewelry and accessories | Fine jewelry, custom designs |
| `creative` | Design and creative services | Graphic design, logo creation |
| `web_design` | Web development | Website creation, mobile apps |

## Get All Services

```http
GET /api/v1/services
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Filter by service category |
| `featured` | boolean | Show only featured services |
| `search` | string | Search by name or description |
| `page` | integer | Page number (default: 1) |
| `per_page` | integer | Items per page (default: 20, max: 100) |
| `sort_by` | string | Sort field (name, price, created_at) |
| `sort_order` | string | Sort order (asc, desc) |

### Example Request

```bash
curl -H "Authorization: Bearer TOKEN" \
     "https://api.gmservices.com/v1/services?category=automotive&featured=true"
```

### Example Response

```json
{
  "success": true,
  "data": {
    "services": [
      {
        "id": 1,
        "name": "Premium Car Maintenance",
        "slug": "premium-car-maintenance",
        "category": "automotive",
        "price": 299.99,
        "currency": "USD",
        "description": "Complete professional car maintenance service",
        "short_description": "Oil change, brake check, engine diagnostic",
        "features": [
          "Oil Change",
          "Brake Inspection",
          "Engine Diagnostic",
          "Tire Rotation",
          "Fluid Top-up"
        ],
        "duration": "2-3 hours",
        "location": "Service center or mobile",
        "requirements": [
          "Vehicle registration",
          "Service history (if available)"
        ],
        "is_featured": true,
        "is_active": true,
        "images": [
          "https://cdn.gmservices.com/services/car-maintenance-1.jpg"
        ],
        "rating": {
          "average": 4.8,
          "count": 156
        },
        "availability": {
          "next_available": "2024-01-15T09:00:00Z",
          "booking_slots": ["09:00", "13:00", "15:30"]
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-10T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

## Get Service Details

```http
GET /api/v1/services/{service_id}
```

### Example Request

```bash
curl -H "Authorization: Bearer TOKEN" \
     https://api.gmservices.com/v1/services/1
```

### Example Response

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Premium Car Maintenance",
    "slug": "premium-car-maintenance",
    "category": "automotive",
    "price": 299.99,
    "currency": "USD",
    "description": "Our premium car maintenance service provides comprehensive care for your vehicle...",
    "detailed_description": "This service includes a thorough inspection of all major systems...",
    "features": [
      "Oil Change",
      "Brake Inspection",
      "Engine Diagnostic"
    ],
    "requirements": [
      "Vehicle registration",
      "Service history"
    ],
    "duration": "2-3 hours",
    "location": "Service center or mobile",
    "staff_assigned": {
      "id": 15,
      "name": "Mike Johnson",
      "specialization": "Automotive Technician",
      "rating": 4.9,
      "experience_years": 8
    },
    "reviews": {
      "average_rating": 4.8,
      "total_reviews": 156,
      "recent_reviews": [
        {
          "id": 1,
          "rating": 5,
          "comment": "Excellent service, very professional",
          "customer_name": "John D.",
          "date": "2024-01-05T00:00:00Z"
        }
      ]
    },
    "pricing_tiers": [
      {
        "name": "Basic",
        "price": 199.99,
        "features": ["Oil Change", "Basic Inspection"]
      },
      {
        "name": "Premium",
        "price": 299.99,
        "features": ["Oil Change", "Brake Check", "Engine Diagnostic"]
      }
    ],
    "add_ons": [
      {
        "name": "Tire Rotation",
        "price": 29.99,
        "description": "Professional tire rotation service"
      }
    ]
  }
}
```

## Create Service Request

```http
POST /api/v1/service-requests
```

### Request Body

```json
{
  "service_id": 1,
  "description": "Need urgent car maintenance for my Toyota Camry",
  "preferred_date": "2024-01-15",
  "preferred_time": "09:00",
  "location": {
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "country": "US"
  },
  "contact_info": {
    "phone": "+1234567890",
    "email": "customer@example.com",
    "preferred_contact_method": "phone"
  },
  "vehicle_info": {
    "make": "Toyota",
    "model": "Camry",
    "year": 2020,
    "vin": "1234567890ABCDEFG",
    "mileage": 25000,
    "license_plate": "ABC123"
  },
  "additional_notes": "Car makes strange noise when braking",
  "priority": "normal",
  "attachments": [
    {
      "name": "vehicle_photo.jpg",
      "url": "https://uploads.gmservices.com/temp/abc123.jpg",
      "type": "image"
    }
  ],
  "pricing_tier": "premium",
  "add_ons": ["tire_rotation"],
  "insurance_info": {
    "provider": "State Farm",
    "policy_number": "SF123456789",
    "coverage_type": "comprehensive"
  }
}
```

### Example Response

```json
{
  "success": true,
  "data": {
    "id": 789,
    "reference_number": "SR-2024-789",
    "service": {
      "id": 1,
      "name": "Premium Car Maintenance",
      "category": "automotive"
    },
    "status": "pending",
    "priority": "normal",
    "description": "Need urgent car maintenance for my Toyota Camry",
    "customer": {
      "id": 123,
      "name": "John Doe",
      "email": "customer@example.com"
    },
    "pricing": {
      "base_price": 299.99,
      "add_ons": 29.99,
      "tax": 26.39,
      "total": 356.37,
      "currency": "USD"
    },
    "schedule": {
      "preferred_date": "2024-01-15",
      "preferred_time": "09:00",
      "estimated_duration": "2-3 hours",
      "scheduled_date": null,
      "actual_start": null,
      "actual_end": null
    },
    "location": {
      "address": "123 Main St",
      "city": "New York",
      "state": "NY",
      "zip_code": "10001",
      "coordinates": {
        "lat": 40.7128,
        "lng": -74.0060
      }
    },
    "assigned_staff": null,
    "tracking_url": "https://gmservices.com/track/SR-2024-789",
    "chat_room_id": "room_789",
    "estimated_completion": null,
    "created_at": "2024-01-10T14:30:00Z",
    "updated_at": "2024-01-10T14:30:00Z"
  }
}
```

## Get Service Requests

```http
GET /api/v1/service-requests
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status (pending, confirmed, in_progress, completed, cancelled) |
| `category` | string | Filter by service category |
| `date_from` | string | Filter from date (ISO 8601) |
| `date_to` | string | Filter to date (ISO 8601) |
| `page` | integer | Page number |
| `per_page` | integer | Items per page |

### Example Request

```bash
curl -H "Authorization: Bearer TOKEN" \
     "https://api.gmservices.com/v1/service-requests?status=in_progress"
```

## Update Service Request

```http
PUT /api/v1/service-requests/{request_id}
```

### Request Body (Customer Updates)

```json
{
  "description": "Updated description",
  "preferred_date": "2024-01-16",
  "additional_notes": "Please call before arriving",
  "contact_info": {
    "phone": "+1987654321"
  }
}
```

### Request Body (Staff Updates)

```json
{
  "status": "in_progress",
  "staff_notes": "Started diagnostic process",
  "estimated_completion": "2024-01-15T17:00:00Z",
  "actual_start": "2024-01-15T09:15:00Z",
  "progress_percentage": 25,
  "next_steps": "Waiting for parts delivery"
}
```

## Service Request Status Flow

```
pending → confirmed → in_progress → completed
   ↓           ↓            ↓
cancelled   cancelled   cancelled
```

### Status Descriptions

- **pending**: Request submitted, waiting for confirmation
- **confirmed**: Request confirmed, scheduled for service
- **in_progress**: Service work has begun
- **completed**: Service work finished successfully
- **cancelled**: Request cancelled by customer or staff

## Webhooks

Subscribe to service request events:

- `service_request.created`
- `service_request.confirmed`
- `service_request.status_updated`
- `service_request.completed`
- `service_request.cancelled`

## Error Handling

### Common Errors

| Error Code | Description | Solution |
|------------|-------------|----------|
| `SERVICE_NOT_FOUND` | Service ID doesn't exist | Check service ID |
| `SERVICE_UNAVAILABLE` | Service not currently available | Try different date |
| `INVALID_LOCATION` | Location outside service area | Check service coverage |
| `MISSING_VEHICLE_INFO` | Vehicle information required | Provide vehicle details |
| `SCHEDULING_CONFLICT` | Requested time slot unavailable | Choose different time |

### Example Error Response

```json
{
  "success": false,
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "The requested service is not available on the selected date",
    "details": {
      "service_id": 1,
      "requested_date": "2024-01-15",
      "next_available": "2024-01-17"
    }
  }
}
```

## Code Examples

### Python SDK

```python
from gmservices import GMServicesClient

client = GMServicesClient(api_key='your_api_key')

# Get services
services = client.services.list(category='automotive')

# Create service request
request = client.service_requests.create(
    service_id=1,
    description='Need car maintenance',
    preferred_date='2024-01-15',
    location={
        'address': '123 Main St',
        'city': 'New York',
        'state': 'NY'
    }
)

print(f"Service request created: {request.reference_number}")
```

### JavaScript SDK

```javascript
const GMServices = require('gmservices-js');

const client = new GMServices({ apiKey: 'your_api_key' });

// Get services
const services = await client.services.list({
  category: 'automotive'
});

// Create service request
const request = await client.serviceRequests.create({
  serviceId: 1,
  description: 'Need car maintenance',
  preferredDate: '2024-01-15',
  location: {
    address: '123 Main St',
    city: 'New York',
    state: 'NY'
  }
});

console.log(`Service request created: ${request.referenceNumber}`);
```

## Related Documentation

- [Payment Processing API](payments.md)
- [Real-time Chat API](chat.md)
- [Webhook Integration](webhooks.md)
- [Authentication Guide](authentication.md)