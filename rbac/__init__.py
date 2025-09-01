from functools import wraps
from flask import request, jsonify, g
from flask_login import current_user
from models.audit import AuditLog
from models.user import db

def require_permission(permission_name):
    """
    Decorator to check if user has a specific permission
    Usage: @require_permission('create_request')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not current_user.has_permission(permission_name):
                AuditLog.log_action(
                    user_id=current_user.id,
                    action=f'permission_denied:{permission_name}',
                    success=False,
                    error_message='Insufficient permissions'
                )
                db.session.commit()
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_role(role_name):
    """
    Decorator to check if user has a specific role
    Usage: @require_role('admin')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not current_user.has_role(role_name):
                AuditLog.log_action(
                    user_id=current_user.id,
                    action=f'role_check_failed:{role_name}',
                    success=False,
                    error_message='Required role not found'
                )
                db.session.commit()
                return jsonify({'error': 'Required role not found'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_resource_access(user, resource_type, resource_id, action='read'):
    """
    Check if user has access to a specific resource
    
    Args:
        user: User object
        resource_type: Type of resource (e.g., 'request', 'report')
        resource_id: ID of the resource
        action: Action to perform (read, write, delete)
    
    Returns:
        bool: True if user has access, False otherwise
    """
    # Check general permission
    permission_name = f'{action}_{resource_type}'
    if user.has_permission(permission_name):
        return True
    
    # Resource-specific access checks
    if resource_type == 'request':
        from models.request import Request
        resource = Request.query.get(resource_id)
        if resource:
            # User is the requester
            if resource.requester_id == user.id:
                return True
            # User is assigned to the request
            if resource.assigned_to_id == user.id:
                return True
            # User is an approver in the history
            if any(approval.approver_id == user.id for approval in resource.approvals):
                return True
    
    return False

def audit_action(action, resource_type=None, resource_id=None):
    """
    Decorator to automatically log actions in audit trail
    Usage: @audit_action('create_request', 'request')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the function
            result = f(*args, **kwargs)
            
            # Log the action
            if current_user.is_authenticated:
                try:
                    # Determine resource_id from kwargs or result
                    res_id = resource_id
                    if res_id is None and isinstance(result, tuple):
                        # Try to extract from response
                        response_data = result[0].get_json() if hasattr(result[0], 'get_json') else None
                        if response_data and 'id' in response_data:
                            res_id = response_data['id']
                    
                    AuditLog.log_action(
                        user_id=current_user.id,
                        action=action,
                        resource_type=resource_type,
                        resource_id=res_id,
                        details={
                            'endpoint': request.endpoint,
                            'method': request.method,
                            'args': str(args),
                            'kwargs': str(kwargs)
                        }
                    )
                    db.session.commit()
                except Exception as e:
                    # Don't fail the request if audit logging fails
                    print(f"Audit logging failed: {str(e)}")
            
            return result
        return decorated_function
    return decorator

class RBACManager:
    """Central manager for RBAC operations"""
    
    @staticmethod
    def assign_role_to_user(user, role):
        """Assign a role to a user"""
        if role not in user.roles:
            user.roles.append(role)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def remove_role_from_user(user, role):
        """Remove a role from a user"""
        if role in user.roles:
            user.roles.remove(role)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def assign_permission_to_role(role, permission):
        """Assign a permission to a role"""
        if permission not in role.permissions:
            role.permissions.append(permission)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def remove_permission_from_role(role, permission):
        """Remove a permission from a role"""
        if permission in role.permissions:
            role.permissions.remove(permission)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_user_permissions(user):
        """Get all permissions for a user across all their roles"""
        permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(permission.name)
        return list(permissions)
    
    @staticmethod
    def get_users_with_permission(permission_name):
        """Get all users that have a specific permission"""
        from models.user import User
        from models.role import Permission
        
        permission = Permission.query.filter_by(name=permission_name).first()
        if not permission:
            return []
        
        users = []
        for role in permission.roles:
            users.extend(role.users)
        
        # Remove duplicates
        return list(set(users))
