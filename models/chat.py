"""
Chat Models
Handles real-time chat functionality between customers and staff
"""
from database import db
from datetime import datetime

class ChatRoom(db.Model):
    """Chat room model for organizing conversations"""
    
    __tablename__ = 'chat_rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Room Information
    name = db.Column(db.String(200))
    room_type = db.Column(db.String(50), default='support')  # support, general, service_specific
    
    # Participants
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    
    # Room Status
    status = db.Column(db.String(20), default='active')  # active, closed, archived
    is_private = db.Column(db.Boolean, default=True)
    
    # Related Service Request (if applicable)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id'))
    
    # Room Settings
    allow_file_upload = db.Column(db.Boolean, default=True)
    max_participants = db.Column(db.Integer, default=2)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='room', lazy='dynamic', 
                             cascade='all, delete-orphan')
    customer = db.relationship('User', foreign_keys=[customer_id], backref='customer_chat_rooms')
    staff_member = db.relationship('User', foreign_keys=[staff_id], backref='staff_chat_rooms')
    service_request = db.relationship('ServiceRequest', backref='chat_room')
    
    def __repr__(self):
        return f'<ChatRoom {self.id}: {self.name or "Support Chat"}>'
    
    def get_last_message(self):
        """Get the last message in the room"""
        return self.messages.order_by(ChatMessage.created_at.desc()).first()
    
    def get_unread_count(self, user_id):
        """Get unread message count for a specific user"""
        return self.messages.filter(
            ChatMessage.sender_id != user_id,
            ChatMessage.is_read == False
        ).count()
    
    def mark_messages_as_read(self, user_id):
        """Mark all messages as read for a specific user"""
        unread_messages = self.messages.filter(
            ChatMessage.sender_id != user_id,
            ChatMessage.is_read == False
        ).all()
        
        for message in unread_messages:
            message.is_read = True
        
        db.session.commit()
    
    def get_participants(self):
        """Get list of participants"""
        participants = []
        if self.customer:
            participants.append(self.customer)
        if self.staff_member:
            participants.append(self.staff_member)
        return participants
    
    def to_dict(self):
        """Convert chat room to dictionary"""
        last_message = self.get_last_message()
        return {
            'id': self.id,
            'name': self.name,
            'room_type': self.room_type,
            'customer_id': self.customer_id,
            'staff_id': self.staff_id,
            'customer_name': self.customer.full_name if self.customer else None,
            'staff_name': self.staff_member.full_name if self.staff_member else None,
            'status': self.status,
            'service_request_id': self.service_request_id,
            'last_message': last_message.to_dict() if last_message else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }

class ChatMessage(db.Model):
    """Chat message model"""
    
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Message Information
    room_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Message Content
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, file, system
    
    # File Attachments
    file_url = db.Column(db.String(255))
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)  # Size in bytes
    file_type = db.Column(db.String(50))
    
    # Message Status
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    is_edited = db.Column(db.Boolean, default=False, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    # Reply Information
    reply_to_message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    
    # Relationships
    reply_to = db.relationship('ChatMessage', remote_side=[id], backref='replies')
    
    def __repr__(self):
        return f'<ChatMessage {self.id}: {self.message[:50]}...>'
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            db.session.commit()
    
    def edit_message(self, new_message):
        """Edit message content"""
        self.message = new_message
        self.is_edited = True
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def delete_message(self):
        """Soft delete message"""
        self.is_deleted = True
        self.message = "[Message deleted]"
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def get_time_ago(self):
        """Get human-readable time since message was sent"""
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'room_id': self.room_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.full_name if self.sender else None,
            'sender_role': self.sender.role if self.sender else None,
            'message': self.message,
            'message_type': self.message_type,
            'file_url': self.file_url,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'is_read': self.is_read,
            'is_edited': self.is_edited,
            'is_deleted': self.is_deleted,
            'reply_to_message_id': self.reply_to_message_id,
            'reply_to_message': self.reply_to.message[:100] if self.reply_to and not self.reply_to.is_deleted else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'time_ago': self.get_time_ago()
        }