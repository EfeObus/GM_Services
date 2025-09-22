# Payment Processing API

The Payment Processing API handles all financial transactions within the GM Services platform, supporting multiple payment methods and currencies for global operations.

## Supported Payment Methods

| Provider | Payment Types | Currencies | Regions |
|----------|---------------|------------|---------|
| **Stripe** | Cards, Bank Transfers, Digital Wallets | 135+ currencies | Global |
| **PayPal** | PayPal, Credit Cards, Buy Now Pay Later | 100+ currencies | Global |
| **Paystack** | Cards, Bank Transfers, USSD, QR Codes | NGN, USD, GHS, ZAR | Africa |

## Payment Flow

```
1. Create Payment Intent → 2. Process Payment → 3. Confirm Payment → 4. Handle Webhook
```

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/payments/intent` | Create payment intent |
| GET | `/payments/{id}` | Get payment details |
| POST | `/payments/{id}/confirm` | Confirm payment |
| POST | `/payments/{id}/refund` | Process refund |
| GET | `/payments` | List payments |
| POST | `/payments/methods` | Add payment method |
| GET | `/payment-methods` | List saved payment methods |

## Create Payment Intent

Creates a payment intent for a service request or purchase.

```http
POST /api/v1/payments/intent
```

### Request Body

```json
{
  "amount": 29999,
  "currency": "USD",
  "service_request_id": 789,
  "payment_method": "stripe",
  "customer_id": 123,
  "description": "Premium Car Maintenance Service",
  "metadata": {
    "service_category": "automotive",
    "reference_number": "SR-2024-789",
    "location": "New York, NY"
  },
  "billing_address": {
    "line1": "123 Main Street",
    "line2": "Apt 4B",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US"
  },
  "shipping_address": {
    "line1": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US"
  },
  "payment_settings": {
    "capture_method": "automatic",
    "confirmation_method": "automatic",
    "setup_future_usage": "off_session"
  },
  "fees": {
    "platform_fee": 500,
    "processing_fee": 299,
    "tax": 2639
  }
}
```

### Response

```json
{
  "success": true,
  "data": {
    "payment_intent_id": "pi_3L0XYZ123ABC",
    "client_secret": "pi_3L0XYZ123ABC_secret_abc123",
    "amount": 29999,
    "currency": "USD",
    "status": "requires_payment_method",
    "payment_methods": ["card", "bank_transfer", "digital_wallet"],
    "expires_at": "2024-01-15T15:30:00Z",
    "next_action": {
      "type": "redirect_to_url",
      "redirect": {
        "url": "https://checkout.stripe.com/pay/cs_test_abc123"
      }
    }
  }
}
```

## Process Payment

Process payment using saved payment method or new payment details.

```http
POST /api/v1/payments/process
```

### Request Body (Credit Card)

```json
{
  "payment_intent_id": "pi_3L0XYZ123ABC",
  "payment_method": {
    "type": "card",
    "card": {
      "number": "4242424242424242",
      "exp_month": 12,
      "exp_year": 2025,
      "cvc": "123"
    },
    "billing_details": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "address": {
        "line1": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "US"
      }
    }
  },
  "save_payment_method": true,
  "return_url": "https://gmservices.com/payment/complete"
}
```

### Request Body (PayPal)

```json
{
  "payment_intent_id": "pi_3L0XYZ123ABC",
  "payment_method": {
    "type": "paypal",
    "paypal": {
      "return_url": "https://gmservices.com/payment/success",
      "cancel_url": "https://gmservices.com/payment/cancel"
    }
  }
}
```

### Request Body (Bank Transfer - Paystack)

```json
{
  "payment_intent_id": "pi_3L0XYZ123ABC",
  "payment_method": {
    "type": "bank_transfer",
    "bank": {
      "account_number": "1234567890",
      "bank_code": "058",
      "account_name": "John Doe"
    }
  }
}
```

### Response

```json
{
  "success": true,
  "data": {
    "payment_id": "pay_abc123xyz",
    "status": "succeeded",
    "amount": 29999,
    "currency": "USD",
    "payment_method": {
      "id": "pm_abc123",
      "type": "card",
      "card": {
        "brand": "visa",
        "last4": "4242",
        "exp_month": 12,
        "exp_year": 2025
      }
    },
    "receipt_url": "https://pay.stripe.com/receipts/abc123",
    "transaction_id": "txn_abc123xyz",
    "created_at": "2024-01-15T14:30:00Z"
  }
}
```

## Get Payment Details

```http
GET /api/v1/payments/{payment_id}
```

### Response

```json
{
  "success": true,
  "data": {
    "id": "pay_abc123xyz",
    "payment_intent_id": "pi_3L0XYZ123ABC",
    "amount": 29999,
    "currency": "USD",
    "status": "succeeded",
    "description": "Premium Car Maintenance Service",
    "service_request": {
      "id": 789,
      "reference_number": "SR-2024-789",
      "service_name": "Premium Car Maintenance"
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
        "last4": "4242"
      }
    },
    "fees": {
      "platform_fee": 500,
      "processing_fee": 299,
      "tax": 2639,
      "total_fees": 3438
    },
    "net_amount": 26561,
    "receipt_url": "https://pay.stripe.com/receipts/abc123",
    "refunds": [],
    "metadata": {
      "service_category": "automotive",
      "location": "New York, NY"
    },
    "created_at": "2024-01-15T14:30:00Z",
    "updated_at": "2024-01-15T14:30:15Z"
  }
}
```

## Process Refund

```http
POST /api/v1/payments/{payment_id}/refund
```

### Request Body

```json
{
  "amount": 29999,
  "reason": "requested_by_customer",
  "description": "Customer cancelled service",
  "refund_application_fee": false,
  "metadata": {
    "cancelled_by": "customer",
    "reason_code": "service_unavailable"
  }
}
```

### Response

```json
{
  "success": true,
  "data": {
    "refund_id": "re_abc123xyz",
    "payment_id": "pay_abc123xyz",
    "amount": 29999,
    "currency": "USD",
    "status": "succeeded",
    "reason": "requested_by_customer",
    "receipt_number": "1234-5678",
    "created_at": "2024-01-15T16:00:00Z",
    "estimated_arrival": "2024-01-20T00:00:00Z"
  }
}
```

## Payment Methods Management

### Add Payment Method

```http
POST /api/v1/payment-methods
```

### Request Body

```json
{
  "type": "card",
  "card": {
    "number": "4242424242424242",
    "exp_month": 12,
    "exp_year": 2025,
    "cvc": "123"
  },
  "billing_details": {
    "name": "John Doe",
    "email": "john@example.com",
    "address": {
      "line1": "123 Main Street",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "US"
    }
  },
  "set_as_default": true
}
```

### List Payment Methods

```http
GET /api/v1/payment-methods
```

### Response

```json
{
  "success": true,
  "data": {
    "payment_methods": [
      {
        "id": "pm_abc123",
        "type": "card",
        "card": {
          "brand": "visa",
          "last4": "4242",
          "exp_month": 12,
          "exp_year": 2025,
          "country": "US"
        },
        "billing_details": {
          "name": "John Doe",
          "email": "john@example.com"
        },
        "is_default": true,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

## Multi-Currency Support

### Supported Currencies

```json
{
  "currencies": {
    "USD": {
      "name": "US Dollar",
      "symbol": "$",
      "decimal_places": 2,
      "supported_methods": ["stripe", "paypal"]
    },
    "EUR": {
      "name": "Euro",
      "symbol": "€", 
      "decimal_places": 2,
      "supported_methods": ["stripe", "paypal"]
    },
    "GBP": {
      "name": "British Pound",
      "symbol": "£",
      "decimal_places": 2,
      "supported_methods": ["stripe", "paypal"]
    },
    "NGN": {
      "name": "Nigerian Naira",
      "symbol": "₦",
      "decimal_places": 2,
      "supported_methods": ["paystack"]
    },
    "GHS": {
      "name": "Ghanaian Cedi",
      "symbol": "₵",
      "decimal_places": 2,
      "supported_methods": ["paystack"]
    }
  }
}
```

### Currency Conversion

```http
GET /api/v1/payments/exchange-rates?from=USD&to=EUR,GBP,NGN
```

### Response

```json
{
  "success": true,
  "data": {
    "base_currency": "USD",
    "rates": {
      "EUR": 0.8234,
      "GBP": 0.7891,
      "NGN": 461.25
    },
    "updated_at": "2024-01-15T14:00:00Z"
  }
}
```

## Payment Analytics

### Get Payment Statistics

```http
GET /api/v1/payments/analytics
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `date_from` | string | Start date (ISO 8601) |
| `date_to` | string | End date (ISO 8601) |
| `currency` | string | Filter by currency |
| `payment_method` | string | Filter by payment method |
| `service_category` | string | Filter by service category |

### Response

```json
{
  "success": true,
  "data": {
    "total_revenue": {
      "amount": 1250000,
      "currency": "USD",
      "formatted": "$12,500.00"
    },
    "transaction_count": 425,
    "average_transaction": {
      "amount": 29412,
      "formatted": "$294.12"
    },
    "payment_methods": {
      "card": 68.2,
      "paypal": 23.1,
      "bank_transfer": 8.7
    },
    "top_services": [
      {
        "category": "automotive",
        "revenue": 450000,
        "percentage": 36.0
      },
      {
        "category": "loans",
        "revenue": 325000,
        "percentage": 26.0
      }
    ],
    "refund_rate": 2.1,
    "success_rate": 97.8
  }
}
```

## Webhooks

### Webhook Events

| Event | Description |
|-------|-------------|
| `payment.created` | Payment intent created |
| `payment.succeeded` | Payment completed successfully |
| `payment.failed` | Payment failed |
| `payment.refunded` | Payment refunded |
| `payment_method.attached` | Payment method added |

### Webhook Payload Example

```json
{
  "event": "payment.succeeded",
  "data": {
    "payment_id": "pay_abc123xyz",
    "amount": 29999,
    "currency": "USD",
    "service_request_id": 789,
    "customer_id": 123,
    "payment_method": "card",
    "created_at": "2024-01-15T14:30:00Z"
  },
  "webhook_id": "wh_abc123",
  "created": "2024-01-15T14:30:01Z"
}
```

## Testing

### Test Payment Methods

| Card Number | Description | Expected Result |
|-------------|-------------|-----------------|
| `4242424242424242` | Visa | Successful payment |
| `4000000000000002` | Visa | Card declined |
| `4000000000009995` | Visa | Insufficient funds |
| `4000000000000069` | Visa | Expired card |
| `4000000000000127` | Visa | Incorrect CVC |

### Test Mode

All test transactions use the `test_` prefix and don't charge real money.

```bash
# Test API endpoint
https://api-test.gmservices.com/v1/payments/intent

# Test API key
Bearer test_sk_abc123xyz...
```

## Security Features

### PCI Compliance
- PCI DSS Level 1 compliant infrastructure
- Tokenized payment data storage
- Encrypted data transmission
- Regular security audits

### Fraud Prevention
- Machine learning fraud detection
- 3D Secure authentication
- Address verification (AVS)
- CVV verification
- Risk scoring algorithms

### Data Protection
- Payment data never stored on GM Services servers
- Secure tokenization for stored payment methods
- End-to-end encryption
- GDPR compliant data handling

## Error Handling

### Common Payment Errors

| Error Code | Description | Suggested Action |
|------------|-------------|------------------|
| `CARD_DECLINED` | Card was declined by bank | Try different payment method |
| `INSUFFICIENT_FUNDS` | Not enough funds available | Check account balance |
| `EXPIRED_CARD` | Card has expired | Update card details |
| `INCORRECT_CVC` | CVC code is incorrect | Verify CVC code |
| `PROCESSING_ERROR` | Payment processor error | Retry payment |
| `CURRENCY_NOT_SUPPORTED` | Currency not supported | Use supported currency |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "CARD_DECLINED",
    "message": "Your card was declined",
    "details": {
      "decline_code": "generic_decline",
      "payment_intent_id": "pi_3L0XYZ123ABC"
    },
    "suggested_actions": [
      "Try a different payment method",
      "Contact your bank"
    ]
  }
}
```

## Code Examples

### Python

```python
import gmservices

client = gmservices.Client(api_key='your_api_key')

# Create payment intent
payment = client.payments.create_intent(
    amount=29999,
    currency='USD',
    service_request_id=789,
    payment_method='stripe'
)

# Process payment
result = client.payments.process(
    payment_intent_id=payment.payment_intent_id,
    payment_method={
        'type': 'card',
        'card': {
            'number': '4242424242424242',
            'exp_month': 12,
            'exp_year': 2025,
            'cvc': '123'
        }
    }
)

print(f"Payment status: {result.status}")
```

### JavaScript

```javascript
const gmservices = require('gmservices');

const client = new gmservices.Client({ apiKey: 'your_api_key' });

// Create payment intent
const payment = await client.payments.createIntent({
  amount: 29999,
  currency: 'USD',
  serviceRequestId: 789,
  paymentMethod: 'stripe'
});

// Process payment
const result = await client.payments.process({
  paymentIntentId: payment.paymentIntentId,
  paymentMethod: {
    type: 'card',
    card: {
      number: '4242424242424242',
      expMonth: 12,
      expYear: 2025,
      cvc: '123'
    }
  }
});

console.log(`Payment status: ${result.status}`);
```

## Related Documentation

- [Service Management API](services.md)
- [Webhook Configuration](webhooks.md)
- [Authentication Guide](authentication.md)
- [Error Handling](../developer/error-handling.md)