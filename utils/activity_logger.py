"""
Activity Logging Utilities
Helper functions for logging user activities and system events
"""
from database import db
from models.activity_tracking import ActivityLog, UserRegistration, StaffOnboarding, UsageStatistics, LoginSession
from flask import request, current_app
from datetime import datetime, date
import json
import uuid

class ActivityLogger:
    """
    Centralized activity logging service
    """
    
    @staticmethod
    def log_activity(
        user_id=None,
        performed_by_id=None,
        activity_type='general',
        action='unknown',
        description=None,
        category='system',
        metadata=None,
        success=True,
        error_message=None,
        duration_ms=None
    ):
        """
        Log any user or system activity
        """
        try:
            # Capture request information if available
            ip_address = None
            user_agent = None
            request_method = None
            request_url = None
            
            if request:
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent')
                request_method = request.method
                request_url = request.url
            
            activity_log = ActivityLog(
                user_id=user_id,
                performed_by_id=performed_by_id,
                activity_type=activity_type,
                action=action,
                description=description,
                category=category,
                ip_address=ip_address,
                user_agent=user_agent,
                request_method=request_method,
                request_url=request_url,
                additional_data=metadata,
                success=success,
                error_message=error_message,
                duration_ms=duration_ms
            )
            
            db.session.add(activity_log)
            db.session.commit()
            
            return activity_log
            
        except Exception as e:
            current_app.logger.error(f"Failed to log activity: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def log_user_registration(
        user_id,
        registration_method='email',
        registration_source='web',
        oauth_provider=None,
        oauth_id=None,
        additional_data=None
    ):
        """
        Log user registration with detailed tracking
        """
        try:
            # Log the general activity
            ActivityLogger.log_activity(
                user_id=user_id,
                activity_type='registration',
                action='user_registered',
                description=f'User registered via {registration_method}',
                category='auth',
                metadata={
                    'registration_method': registration_method,
                    'oauth_provider': oauth_provider,
                    'registration_source': registration_source
                }
            )
            
            # Create detailed registration record
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            referrer_url = request.referrer if request else None
            
            registration_record = UserRegistration(
                user_id=user_id,
                registration_method=registration_method,
                registration_source=registration_source,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer_url=referrer_url,
                oauth_provider=oauth_provider,
                oauth_id=oauth_id,
                registration_data=additional_data
            )
            
            db.session.add(registration_record)
            db.session.commit()
            
            # Update daily statistics
            ActivityLogger._update_usage_stats('new_registrations', 1)
            
            return registration_record
            
        except Exception as e:
            current_app.logger.error(f"Failed to log user registration: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def log_staff_onboarding(
        staff_user_id,
        onboarded_by_id,
        department=None,
        position=None,
        employee_id=None,
        permissions=None,
        notes=None
    ):
        """
        Log staff onboarding process
        """
        try:
            # Log the general activity
            ActivityLogger.log_activity(
                user_id=staff_user_id,
                performed_by_id=onboarded_by_id,
                activity_type='staff_onboarding',
                action='staff_onboarded',
                description=f'New staff member onboarded to {department}',
                category='user_management',
                metadata={
                    'department': department,
                    'position': position,
                    'employee_id': employee_id
                }
            )
            
            # Create detailed onboarding record
            onboarding_record = StaffOnboarding(
                staff_user_id=staff_user_id,
                onboarded_by_id=onboarded_by_id,
                department=department,
                position=position,
                employee_id=employee_id,
                status='completed',
                onboarding_stage='account_created',
                permissions_assigned=permissions,
                onboarding_notes=notes,
                completion_date=datetime.utcnow()
            )
            
            db.session.add(onboarding_record)
            db.session.commit()
            
            return onboarding_record
            
        except Exception as e:
            current_app.logger.error(f"Failed to log staff onboarding: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def log_login(user_id, login_method='password', session_id=None):
        """
        Log user login and create session tracking
        """
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Log the general activity
            ActivityLogger.log_activity(
                user_id=user_id,
                activity_type='authentication',
                action='login',
                description=f'User logged in via {login_method}',
                category='auth',
                metadata={'login_method': login_method}
            )
            
            # Create login session record
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            
            login_session = LoginSession(
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                login_method=login_method
            )
            
            db.session.add(login_session)
            db.session.commit()
            
            # Update daily statistics
            ActivityLogger._update_usage_stats('total_logins', 1)
            
            return login_session
            
        except Exception as e:
            current_app.logger.error(f"Failed to log login: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def log_logout(user_id, session_id=None, logout_reason='manual'):
        """
        Log user logout and update session
        """
        try:
            # Log the general activity
            ActivityLogger.log_activity(
                user_id=user_id,
                activity_type='authentication',
                action='logout',
                description=f'User logged out ({logout_reason})',
                category='auth',
                metadata={'logout_reason': logout_reason}
            )
            
            # Update session record
            if session_id:
                session = LoginSession.query.filter_by(
                    session_id=session_id,
                    user_id=user_id,
                    is_active=True
                ).first()
                
                if session:
                    session.logout_time = datetime.utcnow()
                    session.is_active = False
                    session.logout_reason = logout_reason
                    db.session.commit()
                    
                    return session
            
        except Exception as e:
            current_app.logger.error(f"Failed to log logout: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def log_user_action(
        user_id,
        action,
        description=None,
        category='user_action',
        target_user_id=None,
        metadata=None
    ):
        """
        Log general user actions for monitoring
        """
        return ActivityLogger.log_activity(
            user_id=user_id,
            activity_type='user_action',
            action=action,
            description=description,
            category=category,
            additional_data=metadata
        )
    
    @staticmethod
    def _update_usage_stats(metric, increment=1):
        """
        Update daily usage statistics
        """
        try:
            today = date.today()
            
            # Get or create today's stats
            stats = UsageStatistics.query.filter_by(date=today, hour=None).first()
            if not stats:
                stats = UsageStatistics(date=today)
                db.session.add(stats)
            
            # Update the specific metric
            current_value = getattr(stats, metric, 0) or 0
            setattr(stats, metric, current_value + increment)
            stats.updated_at = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Failed to update usage stats: {str(e)}")
            db.session.rollback()
    
    @staticmethod
    def get_user_activities(user_id, limit=50, activity_type=None, start_date=None, end_date=None):
        """
        Get user activity history
        """
        query = ActivityLog.query.filter_by(user_id=user_id)
        
        if activity_type:
            query = query.filter_by(activity_type=activity_type)
        
        if start_date:
            query = query.filter(ActivityLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(ActivityLog.timestamp <= end_date)
        
        return query.order_by(ActivityLog.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_staff_monitoring_data(staff_user_id, start_date=None, end_date=None):
        """
        Get data for staff monitoring dashboard
        """
        # Get users this staff member can monitor (their customers)
        from models.user import User
        
        if start_date is None:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get all user activities that this staff can monitor
        activities = ActivityLog.query.filter(
            ActivityLog.timestamp >= start_date
        )
        
        if end_date:
            activities = activities.filter(ActivityLog.timestamp <= end_date)
        
        return activities.order_by(ActivityLog.timestamp.desc()).all()
    
    @staticmethod
    def get_admin_monitoring_data(start_date=None, end_date=None):
        """
        Get comprehensive data for admin monitoring dashboard
        """
        if start_date is None:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        activities = ActivityLog.query.filter(
            ActivityLog.timestamp >= start_date
        )
        
        if end_date:
            activities = activities.filter(ActivityLog.timestamp <= end_date)
        
        return activities.order_by(ActivityLog.timestamp.desc()).all()