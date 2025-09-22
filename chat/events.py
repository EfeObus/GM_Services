"""
Chat Events Handler
Real-time chat functionality using Flask-SocketIO
"""
from flask_socketio import emit, join_room, leave_room, close_room
from flask_login import current_user
from models.chat import ChatRoom, ChatMessage
from models.user import User
from database import db
from datetime import datetime
import json

def register_chat_events(socketio):
    """Register all chat-related SocketIO events"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        if current_user.is_authenticated:
            print(f'User {current_user.full_name} connected to chat')
            emit('status', {'msg': f'{current_user.first_name} has connected'})
        else:
            print('Anonymous user connected')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        if current_user.is_authenticated:
            print(f'User {current_user.full_name} disconnected from chat')
    
    @socketio.on('join_room')
    def handle_join_room(data):
        """Handle user joining a chat room"""
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        room_id = data.get('room_id')
        if not room_id:
            emit('error', {'message': 'Room ID required'})
            return
        
        # Verify user has access to this room
        chat_room = ChatRoom.query.get(room_id)
        if not chat_room:
            emit('error', {'message': 'Room not found'})
            return
        
        # Check if user is participant in this room
        if (current_user.id != chat_room.customer_id and 
            current_user.id != chat_room.staff_id and 
            not current_user.is_admin()):
            emit('error', {'message': 'Access denied'})
            return
        
        join_room(str(room_id))
        
        # Mark messages as read for this user
        chat_room.mark_messages_as_read(current_user.id)
        
        # Get recent messages
        messages = ChatMessage.query.filter_by(
            room_id=room_id,
            is_deleted=False
        ).order_by(ChatMessage.created_at.desc()).limit(50).all()
        
        # Reverse to show oldest first
        messages.reverse()
        
        message_data = [msg.to_dict() for msg in messages]
        
        emit('joined_room', {
            'room_id': room_id,
            'room_name': chat_room.name or f'Chat with {chat_room.customer.full_name if current_user.id == chat_room.staff_id else chat_room.staff_member.full_name if chat_room.staff_member else "Support"}',
            'messages': message_data
        })
        
        # Notify other participants
        emit('user_joined', {
            'user_name': current_user.full_name,
            'user_role': current_user.role
        }, room=str(room_id), include_self=False)
    
    @socketio.on('leave_room')
    def handle_leave_room(data):
        """Handle user leaving a chat room"""
        if not current_user.is_authenticated:
            return
        
        room_id = data.get('room_id')
        if room_id:
            leave_room(str(room_id))
            emit('user_left', {
                'user_name': current_user.full_name,
                'user_role': current_user.role
            }, room=str(room_id))
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle sending a message"""
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        room_id = data.get('room_id')
        message_text = data.get('message', '').strip()
        message_type = data.get('message_type', 'text')
        reply_to_id = data.get('reply_to_message_id')
        
        if not room_id or not message_text:
            emit('error', {'message': 'Room ID and message are required'})
            return
        
        # Verify room access
        chat_room = ChatRoom.query.get(room_id)
        if not chat_room:
            emit('error', {'message': 'Room not found'})
            return
        
        if (current_user.id != chat_room.customer_id and 
            current_user.id != chat_room.staff_id and 
            not current_user.is_admin()):
            emit('error', {'message': 'Access denied'})
            return
        
        # Create new message
        new_message = ChatMessage(
            room_id=room_id,
            sender_id=current_user.id,
            message=message_text,
            message_type=message_type,
            reply_to_message_id=reply_to_id
        )
        
        try:
            db.session.add(new_message)
            
            # Update room last activity
            chat_room.last_activity = datetime.utcnow()
            
            db.session.commit()
            
            # Emit message to all room participants
            message_data = new_message.to_dict()
            emit('new_message', message_data, room=str(room_id))
            
            # Send notification to offline participants
            send_message_notification(chat_room, new_message)
            
        except Exception as e:
            db.session.rollback()
            emit('error', {'message': 'Failed to send message'})
            print(f'Error sending message: {e}')
    
    @socketio.on('typing')
    def handle_typing(data):
        """Handle typing indicators"""
        if not current_user.is_authenticated:
            return
        
        room_id = data.get('room_id')
        is_typing = data.get('is_typing', False)
        
        if room_id:
            emit('user_typing', {
                'user_name': current_user.full_name,
                'user_id': current_user.id,
                'is_typing': is_typing
            }, room=str(room_id), include_self=False)
    
    @socketio.on('mark_messages_read')
    def handle_mark_messages_read(data):
        """Handle marking messages as read"""
        if not current_user.is_authenticated:
            return
        
        room_id = data.get('room_id')
        if not room_id:
            return
        
        chat_room = ChatRoom.query.get(room_id)
        if chat_room:
            chat_room.mark_messages_as_read(current_user.id)
            
            # Notify other participants that messages were read
            emit('messages_read', {
                'user_id': current_user.id,
                'room_id': room_id
            }, room=str(room_id), include_self=False)
    
    @socketio.on('edit_message')
    def handle_edit_message(data):
        """Handle message editing"""
        if not current_user.is_authenticated:
            return
        
        message_id = data.get('message_id')
        new_text = data.get('new_message', '').strip()
        
        if not message_id or not new_text:
            emit('error', {'message': 'Message ID and new text are required'})
            return
        
        message = ChatMessage.query.get(message_id)
        if not message:
            emit('error', {'message': 'Message not found'})
            return
        
        # Only sender can edit their own messages
        if message.sender_id != current_user.id:
            emit('error', {'message': 'You can only edit your own messages'})
            return
        
        # Don't allow editing messages older than 10 minutes
        time_diff = datetime.utcnow() - message.created_at
        if time_diff.total_seconds() > 600:  # 10 minutes
            emit('error', {'message': 'Cannot edit messages older than 10 minutes'})
            return
        
        try:
            message.edit_message(new_text)
            
            # Emit updated message to room
            emit('message_edited', {
                'message_id': message_id,
                'new_message': new_text,
                'is_edited': True,
                'updated_at': message.updated_at.isoformat()
            }, room=str(message.room_id))
            
        except Exception as e:
            emit('error', {'message': 'Failed to edit message'})
            print(f'Error editing message: {e}')
    
    @socketio.on('delete_message')
    def handle_delete_message(data):
        """Handle message deletion"""
        if not current_user.is_authenticated:
            return
        
        message_id = data.get('message_id')
        
        if not message_id:
            emit('error', {'message': 'Message ID required'})
            return
        
        message = ChatMessage.query.get(message_id)
        if not message:
            emit('error', {'message': 'Message not found'})
            return
        
        # Only sender or admin can delete messages
        if message.sender_id != current_user.id and not current_user.is_admin():
            emit('error', {'message': 'You can only delete your own messages'})
            return
        
        try:
            message.delete_message()
            
            # Emit deletion to room
            emit('message_deleted', {
                'message_id': message_id,
                'deleted_by': current_user.full_name
            }, room=str(message.room_id))
            
        except Exception as e:
            emit('error', {'message': 'Failed to delete message'})
            print(f'Error deleting message: {e}')
    
    @socketio.on('get_user_rooms')
    def handle_get_user_rooms(data):
        """Get list of user's chat rooms"""
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        if current_user.is_customer():
            # Customer sees their own rooms
            rooms = ChatRoom.query.filter_by(
                customer_id=current_user.id,
                status='active'
            ).order_by(ChatRoom.last_activity.desc()).all()
        
        elif current_user.is_staff() or current_user.is_admin():
            # Staff sees assigned rooms or all rooms for admin
            if current_user.is_admin():
                rooms = ChatRoom.query.filter_by(
                    status='active'
                ).order_by(ChatRoom.last_activity.desc()).all()
            else:
                rooms = ChatRoom.query.filter_by(
                    staff_id=current_user.id,
                    status='active'
                ).order_by(ChatRoom.last_activity.desc()).all()
        
        room_data = []
        for room in rooms:
            last_message = room.get_last_message()
            unread_count = room.get_unread_count(current_user.id)
            
            room_info = {
                'id': room.id,
                'name': room.name or f'Chat with {room.customer.full_name if current_user.id == room.staff_id else room.staff_member.full_name if room.staff_member else "Support"}',
                'last_message': last_message.to_dict() if last_message else None,
                'unread_count': unread_count,
                'last_activity': room.last_activity.isoformat() if room.last_activity else None,
                'participants': [p.to_dict() for p in room.get_participants()]
            }
            room_data.append(room_info)
        
        emit('user_rooms', {'rooms': room_data})
    
    @socketio.on('create_support_room')
    def handle_create_support_room(data):
        """Create a new support chat room"""
        if not current_user.is_authenticated or not current_user.is_customer():
            emit('error', {'message': 'Only customers can create support rooms'})
            return
        
        service_request_id = data.get('service_request_id')
        
        # Check if user already has an active support room
        existing_room = ChatRoom.query.filter_by(
            customer_id=current_user.id,
            room_type='support',
            status='active',
            service_request_id=service_request_id
        ).first()
        
        if existing_room:
            emit('room_created', {'room_id': existing_room.id})
            return
        
        # Create new support room
        new_room = ChatRoom(
            customer_id=current_user.id,
            room_type='support',
            service_request_id=service_request_id,
            name=f'Support Chat - {current_user.full_name}'
        )
        
        try:
            db.session.add(new_room)
            db.session.commit()
            
            emit('room_created', {'room_id': new_room.id})
            
            # Notify available staff about new support request
            notify_staff_new_support_room(new_room)
            
        except Exception as e:
            db.session.rollback()
            emit('error', {'message': 'Failed to create support room'})
            print(f'Error creating support room: {e}')

def send_message_notification(chat_room, message):
    """Send notification for new message to offline participants"""
    # This would integrate with your notification system
    # For now, just print the notification
    print(f'New message notification: {message.sender.full_name} sent a message in room {chat_room.id}')

def notify_staff_new_support_room(chat_room):
    """Notify available staff about new support room"""
    # This would notify staff members about new support requests
    print(f'New support room created: {chat_room.id} by {chat_room.customer.full_name}')