# Real-time Chat API

The Real-time Chat API provides seamless communication between customers and staff throughout the service delivery process using WebSocket connections powered by Socket.IO.

## Overview

The chat system enables:
- Real-time messaging between customers and assigned staff
- File and image sharing
- Message read receipts and typing indicators
- Message history and search
- Push notifications
- Mobile app support

## Connection

### WebSocket Connection

```javascript
import io from 'socket.io-client';

const socket = io('wss://api.gmservices.com/chat', {
  auth: {
    token: 'your_jwt_token'
  },
  transports: ['websocket', 'polling']
});
```

### Authentication

Include JWT token in connection headers:

```javascript
const socket = io('wss://api.gmservices.com/chat', {
  auth: {
    token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    user_id: 123,
    user_type: 'customer' // or 'staff', 'admin'
  }
});
```

## Chat Rooms

### Join Service Chat Room

Each service request automatically creates a private chat room between customer and assigned staff.

```javascript
// Join service request chat room
socket.emit('join_room', {
  room_id: 'service_789',
  service_request_id: 789
});

// Confirmation
socket.on('room_joined', (data) => {
  console.log(`Joined room: ${data.room_id}`);
  console.log(`Participants: ${data.participants.length}`);
});
```

### Room Types

| Room Type | Format | Description |
|-----------|--------|-------------|
| Service Request | `service_{id}` | Customer ↔ Staff communication |
| Support | `support_{id}` | Customer ↔ Support team |
| Internal | `internal_{dept}` | Staff ↔ Staff communication |
| Broadcast | `broadcast_all` | System announcements |

## Messaging

### Send Message

```javascript
socket.emit('send_message', {
  room_id: 'service_789',
  message: 'Hello, I have a question about my service request',
  message_type: 'text',
  metadata: {
    service_request_id: 789,
    priority: 'normal'
  }
});
```

### Message Types

| Type | Description | Example |
|------|-------------|---------|
| `text` | Plain text message | "Hello, how can I help?" |
| `image` | Image attachment | Car damage photo |
| `file` | File attachment | Service document |
| `location` | GPS coordinates | Service location |
| `status_update` | Service status change | "Service completed" |
| `system` | Automated message | "Staff assigned" |

### Receive Messages

```javascript
socket.on('new_message', (data) => {
  console.log('New message:', data);
  /*
  {
    id: 'msg_abc123',
    room_id: 'service_789',
    sender: {
      id: 456,
      name: 'Mike Johnson',
      type: 'staff',
      avatar: 'https://cdn.gmservices.com/avatars/456.jpg'
    },
    message: 'I'll be there in 15 minutes',
    message_type: 'text',
    timestamp: '2024-01-15T14:30:00Z',
    read_by: [],
    attachments: []
  }
  */
});
```

## File Sharing

### Upload File

```http
POST /api/v1/chat/upload
```

### Request Body (multipart/form-data)

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('room_id', 'service_789');
formData.append('description', 'Vehicle damage photo');

fetch('/api/v1/chat/upload', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your_jwt_token'
  },
  body: formData
});
```

### Response

```json
{
  "success": true,
  "data": {
    "file_id": "file_abc123",
    "filename": "damage_photo.jpg",
    "file_size": 2048576,
    "file_type": "image/jpeg",
    "url": "https://cdn.gmservices.com/chat/files/abc123.jpg",
    "thumbnail_url": "https://cdn.gmservices.com/chat/thumbs/abc123.jpg",
    "expires_at": "2024-01-22T14:30:00Z"
  }
}
```

### Send File Message

```javascript
socket.emit('send_message', {
  room_id: 'service_789',
  message: 'Here's the damage photo',
  message_type: 'image',
  attachments: [{
    file_id: 'file_abc123',
    filename: 'damage_photo.jpg',
    url: 'https://cdn.gmservices.com/chat/files/abc123.jpg',
    thumbnail_url: 'https://cdn.gmservices.com/chat/thumbs/abc123.jpg'
  }]
});
```

## Real-time Features

### Typing Indicators

```javascript
// Send typing indicator
socket.emit('typing_start', {
  room_id: 'service_789'
});

// Stop typing
socket.emit('typing_stop', {
  room_id: 'service_789'
});

// Receive typing indicators
socket.on('user_typing', (data) => {
  console.log(`${data.user.name} is typing...`);
});

socket.on('user_stopped_typing', (data) => {
  console.log(`${data.user.name} stopped typing`);
});
```

### Message Read Receipts

```javascript
// Mark message as read
socket.emit('mark_read', {
  room_id: 'service_789',
  message_id: 'msg_abc123'
});

// Receive read receipt
socket.on('message_read', (data) => {
  console.log(`Message ${data.message_id} read by ${data.user.name}`);
});
```

### Online Status

```javascript
// User comes online
socket.on('user_online', (data) => {
  console.log(`${data.user.name} is now online`);
});

// User goes offline
socket.on('user_offline', (data) => {
  console.log(`${data.user.name} is now offline`);
  console.log(`Last seen: ${data.last_seen}`);
});

// Get online users in room
socket.emit('get_online_users', {
  room_id: 'service_789'
});

socket.on('online_users', (data) => {
  console.log('Online users:', data.users);
});
```

## Chat History

### Get Message History

```http
GET /api/v1/chat/rooms/{room_id}/messages
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number (default: 1) |
| `per_page` | integer | Messages per page (default: 50, max: 100) |
| `before` | string | Get messages before this timestamp |
| `after` | string | Get messages after this timestamp |
| `search` | string | Search in message content |
| `message_type` | string | Filter by message type |

### Example Request

```bash
curl -H "Authorization: Bearer TOKEN" \
     "https://api.gmservices.com/v1/chat/rooms/service_789/messages?page=1&per_page=20"
```

### Response

```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "msg_abc123",
        "sender": {
          "id": 123,
          "name": "John Doe",
          "type": "customer",
          "avatar": "https://cdn.gmservices.com/avatars/123.jpg"
        },
        "message": "Hello, I need help with my car service",
        "message_type": "text",
        "timestamp": "2024-01-15T14:30:00Z",
        "edited_at": null,
        "read_by": [
          {
            "user_id": 456,
            "read_at": "2024-01-15T14:31:00Z"
          }
        ],
        "attachments": [],
        "metadata": {
          "service_request_id": 789
        }
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 45,
      "pages": 3,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### Search Messages

```http
GET /api/v1/chat/search
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query |
| `room_ids` | array | Limit search to specific rooms |
| `date_from` | string | Search from date |
| `date_to` | string | Search to date |
| `sender_id` | integer | Filter by sender |

### Example Request

```bash
curl -H "Authorization: Bearer TOKEN" \
     "https://api.gmservices.com/v1/chat/search?q=brake%20service&room_ids=service_789"
```

## Chat Analytics

### Get Chat Statistics

```http
GET /api/v1/chat/analytics
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `date_from` | string | Start date (ISO 8601) |
| `date_to` | string | End date (ISO 8601) |
| `room_type` | string | Filter by room type |
| `service_category` | string | Filter by service category |

### Response

```json
{
  "success": true,
  "data": {
    "total_messages": 12450,
    "total_rooms": 234,
    "active_rooms": 45,
    "average_response_time": {
      "staff": "00:05:30",
      "customer": "00:12:15"
    },
    "message_types": {
      "text": 85.2,
      "image": 8.7,
      "file": 4.1,
      "system": 2.0
    },
    "peak_hours": [
      { "hour": 9, "message_count": 1250 },
      { "hour": 14, "message_count": 1180 },
      { "hour": 16, "message_count": 980 }
    ],
    "satisfaction_scores": {
      "average": 4.7,
      "total_ratings": 156
    }
  }
}
```

## Moderation

### Message Moderation

```javascript
// Flag inappropriate message
socket.emit('flag_message', {
  message_id: 'msg_abc123',
  reason: 'inappropriate_language',
  description: 'Contains offensive language'
});

// Admin response
socket.on('message_flagged', (data) => {
  console.log(`Message ${data.message_id} has been flagged`);
});
```

### Auto-moderation

The system automatically filters:
- Profanity and inappropriate language
- Spam and repetitive messages
- Suspicious links and attachments
- Personal information (phone numbers, emails)

## Push Notifications

### Configure Notifications

```javascript
// Register for push notifications
socket.emit('register_device', {
  device_token: 'fcm_token_abc123',
  platform: 'ios', // or 'android', 'web'
  app_version: '1.2.0'
});

// Notification preferences
socket.emit('update_notification_settings', {
  new_messages: true,
  service_updates: true,
  promotional: false,
  quiet_hours: {
    start: '22:00',
    end: '08:00',
    timezone: 'America/New_York'
  }
});
```

### Notification Types

| Type | Description | Example |
|------|-------------|---------|
| `new_message` | New chat message received | "Mike Johnson sent you a message" |
| `service_update` | Service status changed | "Your car service is complete" |
| `staff_assigned` | Staff member assigned | "Mike has been assigned to your request" |
| `payment_required` | Payment action needed | "Please complete payment for your service" |

## Error Handling

### Connection Errors

```javascript
socket.on('connect_error', (error) => {
  console.error('Connection failed:', error.message);
  // Implement retry logic
});

socket.on('disconnect', (reason) => {
  console.log('Disconnected:', reason);
  if (reason === 'io server disconnect') {
    // Server forcibly disconnected, reconnect
    socket.connect();
  }
});
```

### Message Errors

```javascript
socket.on('message_error', (error) => {
  console.error('Message failed:', error);
  /*
  {
    error_code: 'MESSAGE_TOO_LONG',
    message: 'Message exceeds maximum length',
    details: {
      max_length: 2000,
      current_length: 2543
    }
  }
  */
});
```

### Common Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| `ROOM_NOT_FOUND` | Chat room doesn't exist | Check room ID |
| `ACCESS_DENIED` | No permission to access room | Verify user permissions |
| `MESSAGE_TOO_LONG` | Message exceeds length limit | Reduce message length |
| `FILE_TOO_LARGE` | File exceeds size limit | Compress or use smaller file |
| `RATE_LIMITED` | Too many messages sent | Wait before sending next message |

## Code Examples

### React Chat Component

```jsx
import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

function ChatComponent({ roomId, userId, token }) {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    const newSocket = io('wss://api.gmservices.com/chat', {
      auth: { token, user_id: userId }
    });

    newSocket.emit('join_room', { room_id: roomId });

    newSocket.on('new_message', (message) => {
      setMessages(prev => [...prev, message]);
    });

    setSocket(newSocket);

    return () => newSocket.close();
  }, [roomId, userId, token]);

  const sendMessage = () => {
    if (socket && newMessage.trim()) {
      socket.emit('send_message', {
        room_id: roomId,
        message: newMessage,
        message_type: 'text'
      });
      setNewMessage('');
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id} className="message">
            <strong>{msg.sender.name}:</strong> {msg.message}
          </div>
        ))}
      </div>
      <div className="input-area">
        <input
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type a message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}
```

### Python Client

```python
import socketio

class ChatClient:
    def __init__(self, token, user_id):
        self.sio = socketio.Client()
        self.token = token
        self.user_id = user_id
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.sio.on('new_message')
        def on_message(data):
            print(f"New message from {data['sender']['name']}: {data['message']}")
        
        @self.sio.on('connect')
        def on_connect():
            print("Connected to chat server")
    
    def connect(self):
        self.sio.connect('wss://api.gmservices.com/chat', 
                        auth={'token': self.token, 'user_id': self.user_id})
    
    def join_room(self, room_id):
        self.sio.emit('join_room', {'room_id': room_id})
    
    def send_message(self, room_id, message):
        self.sio.emit('send_message', {
            'room_id': room_id,
            'message': message,
            'message_type': 'text'
        })

# Usage
client = ChatClient('your_jwt_token', 123)
client.connect()
client.join_room('service_789')
client.send_message('service_789', 'Hello from Python!')
```

## Related Documentation

- [Authentication Guide](authentication.md)
- [Service Management API](services.md)
- [Push Notifications Setup](../deployment/notifications.md)
- [WebSocket Configuration](../deployment/websockets.md)