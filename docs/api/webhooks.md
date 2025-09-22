# Webhook Integration Guide

Webhooks allow your application to receive real-time notifications when events occur in the GM Services platform. This guide covers setup, security, and handling of webhook events.

## Overview

GM Services sends HTTP POST requests to your configured webhook endpoints when specific events occur, such as:
- Service request status changes
- Payment processing events
- User account modifications
- Chat message events
- System notifications

## Webhook Configuration

### Setup Webhook Endpoint

```http
POST /api/v1/webhooks
```

### Request Body

```json
{
  "url": "https://your-app.com/webhooks/gmservices",
  "events": [
    "service_request.created",
    "service_request.status_updated",
    "payment.succeeded",
    "payment.failed",
    "chat.message_sent"
  ],
  "description": "Production webhook for service updates",
  "secret": "your_webhook_secret_key",
  "active": true,
  "headers": {
    "X-Custom-Header": "your-custom-value"
  },
  "retry_config": {
    "max_retries": 3,
    "retry_delay": 5000,
    "backoff_multiplier": 2
  }
}
```

### Response

```json
{
  "success": true,
  "data": {
    "webhook_id": "wh_abc123xyz",
    "url": "https://your-app.com/webhooks/gmservices",
    "secret": "whsec_abc123...",
    "events": [
      "service_request.created",
      "service_request.status_updated",
      "payment.succeeded",
      "payment.failed",
      "chat.message_sent"
    ],
    "active": true,
    "created_at": "2024-01-15T14:30:00Z",
    "last_delivery_at": null,
    "delivery_success_rate": 0.0
  }
}
```

## Available Events

### Service Request Events

| Event | Description | Trigger |
|-------|-------------|---------|
| `service_request.created` | New service request submitted | Customer creates request |
| `service_request.confirmed` | Service request confirmed | Staff confirms request |
| `service_request.status_updated` | Status changed | Any status change |
| `service_request.assigned` | Staff member assigned | Staff assignment |
| `service_request.completed` | Service completed | Service marked complete |
| `service_request.cancelled` | Service cancelled | Cancellation by customer/staff |
| `service_request.scheduled` | Service scheduled | Appointment set |

### Payment Events

| Event | Description | Trigger |
|-------|-------------|---------|
| `payment.created` | Payment intent created | Payment process started |
| `payment.succeeded` | Payment completed | Successful payment |
| `payment.failed` | Payment failed | Payment attempt failed |
| `payment.refunded` | Payment refunded | Refund processed |
| `payment.dispute_created` | Chargeback initiated | Customer disputes payment |

### User Events

| Event | Description | Trigger |
|-------|-------------|---------|
| `user.created` | New user registered | Account creation |
| `user.updated` | User profile updated | Profile changes |
| `user.verified` | Email/phone verified | Verification complete |
| `user.deactivated` | Account deactivated | Account suspension |

### Chat Events

| Event | Description | Trigger |
|-------|-------------|---------|
| `chat.message_sent` | New message sent | Message in chat |
| `chat.room_created` | Chat room created | New conversation |
| `chat.file_shared` | File uploaded | File attachment |

### System Events

| Event | Description | Trigger |
|-------|-------------|---------|
| `system.maintenance_start` | Maintenance mode started | Scheduled maintenance |
| `system.maintenance_end` | Maintenance mode ended | Maintenance complete |
| `system.alert` | System alert triggered | Critical system event |

## Webhook Payload Structure

### Standard Payload Format

```json
{
  "event": "service_request.status_updated",
  "event_id": "evt_abc123xyz",
  "webhook_id": "wh_abc123xyz",
  "timestamp": "2024-01-15T14:30:00Z",
  "api_version": "v1",
  "data": {
    "object": "service_request",
    "id": 789,
    "reference_number": "SR-2024-789",
    "previous_attributes": {
      "status": "confirmed"
    },
    "current_attributes": {
      "status": "in_progress",
      "assigned_staff_id": 456,
      "estimated_completion": "2024-01-15T17:00:00Z"
    }
  },
  "metadata": {
    "source": "staff_app",
    "user_agent": "GM Services Staff App v1.2.0",
    "ip_address": "192.168.1.100"
  }
}
```

## Event Payload Examples

### Service Request Created

```json
{
  "event": "service_request.created",
  "event_id": "evt_abc123xyz",
  "webhook_id": "wh_abc123xyz",
  "timestamp": "2024-01-15T14:30:00Z",
  "data": {
    "object": "service_request",
    "id": 789,
    "reference_number": "SR-2024-789",
    "service": {
      "id": 1,
      "name": "Premium Car Maintenance",
      "category": "automotive"
    },
    "customer": {
      "id": 123,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890"
    },
    "status": "pending",
    "priority": "normal",
    "description": "Need urgent car maintenance",
    "location": {
      "address": "123 Main St",
      "city": "New York",
      "state": "NY",
      "zip_code": "10001"
    },
    "pricing": {
      "base_price": 299.99,
      "tax": 26.39,
      "total": 326.38,
      "currency": "USD"
    },
    "preferred_schedule": {
      "date": "2024-01-16",
      "time": "09:00"
    },
    "created_at": "2024-01-15T14:30:00Z"
  }
}
```

### Payment Succeeded

```json
{
  "event": "payment.succeeded",
  "event_id": "evt_pay123xyz",
  "webhook_id": "wh_abc123xyz",
  "timestamp": "2024-01-15T15:00:00Z",
  "data": {
    "object": "payment",
    "id": "pay_abc123xyz",
    "payment_intent_id": "pi_3L0XYZ123ABC",
    "amount": 32638,
    "currency": "USD",
    "status": "succeeded",
    "service_request": {
      "id": 789,
      "reference_number": "SR-2024-789"
    },
    "customer": {
      "id": 123,
      "name": "John Doe",
      "email": "john@example.com"
    },
    "payment_method": {
      "type": "card",
      "card": {
        "brand": "visa",
        "last4": "4242",
        "exp_month": 12,
        "exp_year": 2025
      }
    },
    "receipt_url": "https://pay.stripe.com/receipts/abc123",
    "created_at": "2024-01-15T15:00:00Z"
  }
}
```

### Chat Message Sent

```json
{
  "event": "chat.message_sent",
  "event_id": "evt_msg123xyz",
  "webhook_id": "wh_abc123xyz",
  "timestamp": "2024-01-15T16:30:00Z",
  "data": {
    "object": "chat_message",
    "id": "msg_abc123",
    "room_id": "service_789",
    "sender": {
      "id": 456,
      "name": "Mike Johnson",
      "type": "staff",
      "role": "automotive_technician"
    },
    "message": "I'm on my way to your location",
    "message_type": "text",
    "service_request": {
      "id": 789,
      "reference_number": "SR-2024-789"
    },
    "attachments": [],
    "created_at": "2024-01-15T16:30:00Z"
  }
}
```

## Security

### Webhook Signatures

Every webhook request includes a signature in the `X-GM-Signature` header for verification:

```
X-GM-Signature: sha256=5d41402abc4b2a76b9719d911017c592
```

### Verify Webhook Signature

#### Python Example

```python
import hmac
import hashlib
import json

def verify_webhook_signature(payload, signature, secret):
    """Verify webhook signature"""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Remove 'sha256=' prefix if present
    if signature.startswith('sha256='):
        signature = signature[7:]
    
    return hmac.compare_digest(expected_signature, signature)

# Example usage
def handle_webhook(request):
    payload = request.body.decode('utf-8')
    signature = request.headers.get('X-GM-Signature')
    secret = 'your_webhook_secret'
    
    if not verify_webhook_signature(payload, signature, secret):
        return {'error': 'Invalid signature'}, 401
    
    event_data = json.loads(payload)
    process_webhook_event(event_data)
    
    return {'success': True}, 200
```

#### Node.js Example

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload, 'utf8')
    .digest('hex');
  
  // Remove 'sha256=' prefix if present
  const cleanSignature = signature.startsWith('sha256=') 
    ? signature.slice(7) 
    : signature;
  
  return crypto.timingSafeEqual(
    Buffer.from(expectedSignature, 'hex'),
    Buffer.from(cleanSignature, 'hex')
  );
}

// Express.js middleware
app.post('/webhooks/gmservices', express.raw({type: 'application/json'}), (req, res) => {
  const payload = req.body.toString();
  const signature = req.headers['x-gm-signature'];
  const secret = process.env.WEBHOOK_SECRET;
  
  if (!verifyWebhookSignature(payload, signature, secret)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  const eventData = JSON.parse(payload);
  processWebhookEvent(eventData);
  
  res.json({ success: true });
});
```

### IP Whitelisting

GM Services webhooks are sent from these IP ranges:

```
Production:
- 52.89.214.238
- 54.187.174.169
- 54.187.205.235

Staging:
- 52.89.214.240
- 54.187.174.170
```

## Response Requirements

### Successful Response

Your webhook endpoint should return a `2xx` status code to indicate successful processing:

```json
{
  "success": true,
  "message": "Webhook processed successfully",
  "processed_at": "2024-01-15T14:30:15Z"
}
```

### Error Response

Return appropriate error codes for processing issues:

```json
{
  "success": false,
  "error": {
    "code": "PROCESSING_ERROR",
    "message": "Failed to update internal records",
    "details": "Database connection timeout"
  }
}
```

### Response Timeout

- Webhook endpoints must respond within **10 seconds**
- Responses taking longer will be considered failed
- Failed webhooks will be retried automatically

## Retry Logic

### Automatic Retries

Failed webhook deliveries are automatically retried with exponential backoff:

1. **Initial attempt**: Immediate
2. **Retry 1**: 5 seconds later
3. **Retry 2**: 25 seconds later (5 × 5)
4. **Retry 3**: 125 seconds later (25 × 5)

### Retry Conditions

Retries occur for:
- HTTP status codes: 5xx, 408, 429
- Network timeouts
- Connection errors

No retries for:
- HTTP status codes: 4xx (except 408, 429)
- Invalid webhook URL
- SSL certificate errors

### Manual Retry

```http
POST /api/v1/webhooks/{webhook_id}/retry/{event_id}
```

## Webhook Management

### List Webhooks

```http
GET /api/v1/webhooks
```

### Update Webhook

```http
PUT /api/v1/webhooks/{webhook_id}
```

```json
{
  "url": "https://your-app.com/webhooks/gmservices-v2",
  "events": [
    "service_request.created",
    "payment.succeeded"
  ],
  "active": true
}
```

### Delete Webhook

```http
DELETE /api/v1/webhooks/{webhook_id}
```

### Webhook Logs

```http
GET /api/v1/webhooks/{webhook_id}/deliveries
```

### Response

```json
{
  "success": true,
  "data": {
    "deliveries": [
      {
        "id": "del_abc123",
        "event_id": "evt_abc123xyz",
        "event_type": "service_request.created",
        "url": "https://your-app.com/webhooks/gmservices",
        "http_status": 200,
        "response_body": "{\"success\": true}",
        "response_time_ms": 150,
        "attempt_number": 1,
        "delivered_at": "2024-01-15T14:30:05Z",
        "error_message": null
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

## Testing Webhooks

### Webhook Testing Tool

```http
POST /api/v1/webhooks/test
```

```json
{
  "url": "https://your-app.com/webhooks/test",
  "event": "service_request.created",
  "secret": "your_webhook_secret"
}
```

### Local Testing with ngrok

```bash
# Install ngrok
npm install -g ngrok

# Expose local server
ngrok http 3000

# Use the HTTPS URL for webhook configuration
# https://abc123.ngrok.io/webhooks/gmservices
```

### Testing Framework Example

```python
import pytest
import json
from unittest.mock import patch
from your_app import webhook_handler

class TestWebhooks:
    def test_service_request_created(self):
        payload = {
            "event": "service_request.created",
            "data": {
                "object": "service_request",
                "id": 789,
                "status": "pending"
            }
        }
        
        with patch('your_app.process_service_request') as mock_process:
            result = webhook_handler(payload)
            assert result['success'] is True
            mock_process.assert_called_once_with(789)
    
    def test_invalid_signature(self):
        payload = json.dumps({"event": "test"})
        invalid_signature = "invalid_signature"
        
        result = webhook_handler(payload, invalid_signature)
        assert result['error'] == 'Invalid signature'
```

## Best Practices

### Idempotency

Implement idempotent processing to handle duplicate webhook deliveries:

```python
def process_webhook_event(event_data):
    event_id = event_data['event_id']
    
    # Check if event already processed
    if ProcessedEvent.objects.filter(event_id=event_id).exists():
        return {'success': True, 'message': 'Event already processed'}
    
    # Process event
    try:
        handle_event(event_data)
        
        # Mark as processed
        ProcessedEvent.objects.create(
            event_id=event_id,
            processed_at=timezone.now()
        )
        
        return {'success': True}
    except Exception as e:
        logger.error(f"Failed to process event {event_id}: {e}")
        return {'success': False, 'error': str(e)}
```

### Error Handling

```python
def webhook_handler(request):
    try:
        # Verify signature
        if not verify_signature(request):
            return JsonResponse({'error': 'Invalid signature'}, status=401)
        
        # Parse payload
        event_data = json.loads(request.body)
        
        # Process based on event type
        event_type = event_data['event']
        
        if event_type == 'service_request.created':
            handle_service_request_created(event_data)
        elif event_type == 'payment.succeeded':
            handle_payment_succeeded(event_data)
        else:
            logger.warning(f"Unhandled event type: {event_type}")
        
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JsonResponse({'error': 'Processing failed'}, status=500)
```

### Logging

```python
import logging

logger = logging.getLogger('webhooks')

def log_webhook_event(event_data, status, error=None):
    logger.info(
        "Webhook processed",
        extra={
            'event_id': event_data.get('event_id'),
            'event_type': event_data.get('event'),
            'status': status,
            'error': error,
            'timestamp': event_data.get('timestamp')
        }
    )
```

## Related Documentation

- [Authentication Guide](authentication.md)
- [Service Management API](services.md)
- [Payment Processing API](payments.md)
- [Error Handling](../developer/error-handling.md)