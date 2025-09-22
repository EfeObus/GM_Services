"""
Chat Utilities
Helper functions for chat functionality
"""
from models.chat import ChatRoom, ChatMessage
from models.user import User
from database import db
from datetime import datetime

def create_chat_room(customer_id, staff_id=None, room_type='support', service_request_id=None):
    """Create a new chat room"""
    chat_room = ChatRoom(
        customer_id=customer_id,
        staff_id=staff_id,
        room_type=room_type,
        service_request_id=service_request_id
    )
    
    db.session.add(chat_room)
    db.session.commit()
    
    return chat_room

def assign_staff_to_room(room_id, staff_id):
    """Assign staff member to a chat room"""
    chat_room = ChatRoom.query.get(room_id)
    if chat_room and not chat_room.staff_id:
        staff_member = User.query.get(staff_id)
        if staff_member and staff_member.is_staff():
            chat_room.staff_id = staff_id
            db.session.commit()
            return True
    return False

def get_user_active_rooms(user_id):
    """Get all active chat rooms for a user"""
    user = User.query.get(user_id)
    if not user:
        return []
    
    if user.is_customer():
        rooms = ChatRoom.query.filter_by(
            customer_id=user_id,
            status='active'
        ).order_by(ChatRoom.last_activity.desc()).all()
    
    elif user.is_staff() or user.is_admin():
        if user.is_admin():
            rooms = ChatRoom.query.filter_by(
                status='active'
            ).order_by(ChatRoom.last_activity.desc()).all()
        else:
            rooms = ChatRoom.query.filter_by(
                staff_id=user_id,
                status='active'
            ).order_by(ChatRoom.last_activity.desc()).all()
    
    else:
        rooms = []
    
    return rooms

def get_room_messages(room_id, limit=50, offset=0):
    """Get messages from a chat room"""
    messages = ChatMessage.query.filter_by(
        room_id=room_id,
        is_deleted=False
    ).order_by(
        ChatMessage.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    # Return in chronological order (oldest first)
    return list(reversed(messages))

def send_system_message(room_id, message_text):
    """Send a system message to a chat room"""
    system_message = ChatMessage(
        room_id=room_id,
        sender_id=None,  # System messages have no sender
        message=message_text,
        message_type='system'
    )
    
    db.session.add(system_message)
    db.session.commit()
    
    return system_message

def close_chat_room(room_id, closed_by_user_id):
    """Close a chat room"""
    chat_room = ChatRoom.query.get(room_id)
    if chat_room:
        chat_room.status = 'closed'
        chat_room.closed_at = datetime.utcnow()
        
        # Send system message about room closure
        closer = User.query.get(closed_by_user_id)
        if closer:
            send_system_message(
                room_id, 
                f"Chat room closed by {closer.full_name}"
            )
        
        db.session.commit()
        return True
    
    return False

def get_unassigned_support_rooms():
    """Get support rooms that don't have staff assigned"""
    return ChatRoom.query.filter_by(
        room_type='support',
        staff_id=None,
        status='active'
    ).order_by(ChatRoom.created_at.asc()).all()

def get_chat_statistics(user_id=None, date_from=None, date_to=None):
    """Get chat statistics"""
    query = ChatMessage.query
    
    if user_id:
        query = query.filter_by(sender_id=user_id)
    
    if date_from:
        query = query.filter(ChatMessage.created_at >= date_from)
    
    if date_to:
        query = query.filter(ChatMessage.created_at <= date_to)
    
    total_messages = query.count()
    
    # Get room statistics
    room_query = ChatRoom.query
    if date_from:
        room_query = room_query.filter(ChatRoom.created_at >= date_from)
    if date_to:
        room_query = room_query.filter(ChatRoom.created_at <= date_to)
    
    total_rooms = room_query.count()
    active_rooms = room_query.filter_by(status='active').count()
    closed_rooms = room_query.filter_by(status='closed').count()
    
    return {
        'total_messages': total_messages,
        'total_rooms': total_rooms,
        'active_rooms': active_rooms,
        'closed_rooms': closed_rooms
    }

def search_messages(query, room_id=None, user_id=None, limit=50):
    """Search messages by content"""
    search_query = ChatMessage.query.filter(
        ChatMessage.message.contains(query),
        ChatMessage.is_deleted == False
    )
    
    if room_id:
        search_query = search_query.filter_by(room_id=room_id)
    
    if user_id:
        search_query = search_query.filter_by(sender_id=user_id)
    
    return search_query.order_by(
        ChatMessage.created_at.desc()
    ).limit(limit).all()

def export_chat_history(room_id, format='json'):
    """Export chat history for a room"""
    chat_room = ChatRoom.query.get(room_id)
    if not chat_room:
        return None
    
    messages = ChatMessage.query.filter_by(
        room_id=room_id,
        is_deleted=False
    ).order_by(ChatMessage.created_at.asc()).all()
    
    if format == 'json':
        return {
            'room': chat_room.to_dict(),
            'messages': [msg.to_dict() for msg in messages],
            'exported_at': datetime.utcnow().isoformat()
        }
    
    elif format == 'txt':
        lines = [
            f"Chat History - {chat_room.name or 'Support Chat'}",
            f"Exported: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Room ID: {room_id}",
            "-" * 50
        ]
        
        for msg in messages:
            timestamp = msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
            sender_name = msg.sender.full_name if msg.sender else 'System'
            lines.append(f"[{timestamp}] {sender_name}: {msg.message}")
        
        return '\n'.join(lines)
    
    return None