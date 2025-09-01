from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.user import User, db
from models.role import Role, Permission
from models.audit import AuditLog
from rbac import require_role, RBACManager
from validation.schemas import UserCreate, RoleCreate, PermissionCreate
from utils import handle_errors, success_response, error_response
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# ============= User Management =============

@admin_bp.route('/users', methods=['GET'])
@login_required
@require_role('admin')
@handle_errors
def list_users():
    """List all users"""
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users],
        'count': len(users)
    }), 200

@admin_bp.route('/users', methods=['POST'])
@login_required
@require_role('admin')
@handle_errors
def create_user():
    """Create a new user"""
    data = request.get_json()
    user_data = UserCreate(**data)
    
    # Check if user exists
    if User.query.filter_by(username=user_data.username).first():
        return error_response('Username already exists', 400)
    
    if User.query.filter_by(email=user_data.email).first():
        return error_response('Email already exists', 400)
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        department=user_data.department,
        phone_number=user_data.phone_number
    )
    user.set_password(user_data.password)
    
    db.session.add(user)
    db.session.commit()
    
    # Log the action
    AuditLog.log_action(
        user_id=current_user.id,
        action='admin_create_user',
        resource_type='user',
        resource_id=user.id
    )
    db.session.commit()
    
    return success_response('User created successfully',
                          {'user': user.to_dict()}, 201)

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@require_role('admin')
@handle_errors
def update_user(user_id):
    """Update a user"""
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404)
    
    data = request.get_json()
    old_values = {}
    
    # Update fields
    for field, value in data.items():
        if hasattr(user, field) and value is not None:
            old_values[field] = getattr(user, field)
            setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Log the action
    AuditLog.log_action(
        user_id=current_user.id,
        action='admin_update_user',
        resource_type='user',
        resource_id=user_id,
        old_values=old_values,
        new_values=data
    )
    db.session.commit()
    
    return success_response('User updated successfully',
                          {'user': user.to_dict()})

@admin_bp.route('/users/<int:user_id>/roles', methods=['POST'])
@login_required
@require_role('admin')
@handle_errors
def assign_role_to_user(user_id):
    """Assign a role to a user"""
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404)
    
    data = request.get_json()
    role_id = data.get('role_id')
    
    role = Role.query.get(role_id)
    if not role:
        return error_response('Role not found', 404)
    
    success = RBACManager.assign_role_to_user(user, role)
    
    # Log the action
    AuditLog.log_action(
        user_id=current_user.id,
        action='assign_role',
        resource_type='user',
        resource_id=user_id,
        details={'role_id': role_id, 'role_name': role.name}
    )
    db.session.commit()
    
    if success:
        return success_response('Role assigned successfully')
    
    return error_response('Failed to assign role', 400)

@admin_bp.route('/users/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@login_required
@require_role('admin')
@handle_errors
def remove_role_from_user(user_id, role_id):
    """Remove a role from a user"""
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404)
    
    role = Role.query.get(role_id)
    if not role:
        return error_response('Role not found', 404)
    
    success = RBACManager.remove_role_from_user(user, role)
    
    # Log the action
    AuditLog.log_action(
        user_id=current_user.id,
        action='remove_role',
        resource_type='user',
        resource_id=user_id,
        details={'role_id': role_id, 'role_name': role.name}
    )
    db.session.commit()
    
    if success:
        return success_response('Role removed successfully')
    
    return error_response('Failed to remove role', 400)

# ============= Role Management =============

@admin_bp.route('/roles', methods=['GET'])
@login_required
@require_role('admin')
@handle_errors
def list_roles():
    """List all roles"""
    roles = Role.query.all()
    return jsonify({
        'roles': [role.to_dict() for role in roles],
        'count': len(roles)
    }), 200

@admin_bp.route('/roles', methods=['POST'])
@login_required
@require_role('admin')
@handle_errors
def create_role():
    """Create a new role"""
    data = request.get_json()
    role_data = RoleCreate(**data)
    
    # Check if role exists
    if Role.query.filter_by(name=role_data.name).first():
        return error_response('Role already exists', 400)
    
    role = Role(
        name=role_data.name,
        description=role_data.description,
        level=role_data.level,
        can_approve=role_data.can_approve,
        approval_limit=role_data.approval_limit
    )
    
    db.session.add(role)
    db.session.commit()
    
    # Log the action
    AuditLog.log_action(
        user_id=current_user.id,
        action='create_role',
        resource_type='role',
        resource_id=role.id
    )
    db.session.commit()
    
    return success_response('Role created successfully',
                          {'role': role.to_dict()}, 201)

@admin_bp.route('/roles/<int:role_id>/permissions', methods=['POST'])
@login_required
@require_role('admin')
@handle_errors
def assign_permission_to_role(role_id):
    """Assign a permission to a role"""
    role = Role.query.get(role_id)
    if not role:
        return error_response('Role not found', 404)
    
    data = request.get_json()
    permission_id = data.get('permission_id')
    
    permission = Permission.query.get(permission_id)
    if not permission:
        return error_response('Permission not found', 404)
    
    success = RBACManager.assign_permission_to_role(role, permission)
    
    # Log the action
    AuditLog.log_action(
        user_id=current_user.id,
        action='assign_permission',
        resource_type='role',
        resource_id=role_id,
        details={'permission_id': permission_id, 'permission_name': permission.name}
    )
    db.session.commit()
    
    if success:
        return success_response('Permission assigned successfully')
    
    return error_response('Failed to assign permission', 400)

# ============= Permission Management =============

@admin_bp.route('/permissions', methods=['GET'])
@login_required
@require_role('admin')
@handle_errors
def list_permissions():
    """List all permissions"""
    permissions = Permission.query.all()
    return jsonify({
        'permissions': [perm.to_dict() for perm in permissions],
        'count': len(permissions)
    }), 200

@admin_bp.route('/permissions', methods=['POST'])
@login_required
@require_role('admin')
@handle_errors
def create_permission():
    """Create a new permission"""
    data = request.get_json()
    perm_data = PermissionCreate(**data)
    
    # Check if permission exists
    if Permission.query.filter_by(name=perm_data.name).first():
        return error_response('Permission already exists', 400)
    
    permission = Permission(
        name=perm_data.name,
        description=perm_data.description,
        resource=perm_data.resource,
        action=perm_data.action
    )
    
    db.session.add(permission)
    db.session.commit()
    
    # Log the action
    AuditLog.log_action(
        user_id=current_user.id,
        action='create_permission',
        resource_type='permission',
        resource_id=permission.id
    )
    db.session.commit()
    
    return success_response('Permission created successfully',
                          {'permission': permission.to_dict()}, 201)

# ============= Audit Logs =============

@admin_bp.route('/audit-logs', methods=['GET'])
@login_required
@require_role('admin')
@handle_errors
def get_audit_logs():
    """Get audit logs with optional filters"""
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    resource_type = request.args.get('resource_type')
    limit = request.args.get('limit', 100, type=int)
    
    query = AuditLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if action:
        query = query.filter_by(action=action)
    if resource_type:
        query = query.filter_by(resource_type=resource_type)
    
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'audit_logs': [log.to_dict() for log in logs],
        'count': len(logs)
    }), 200

# ============= Statistics =============

@admin_bp.route('/statistics', methods=['GET'])
@login_required
@require_role('admin')
@handle_errors
def get_statistics():
    """Get system statistics"""
    from models.request import Request
    
    total_users = User.query.count()
    total_requests = Request.query.count()
    pending_requests = Request.query.filter_by(status='pending').count()
    approved_requests = Request.query.filter_by(status='approved').count()
    rejected_requests = Request.query.filter_by(status='rejected').count()
    
    return jsonify({
        'users': total_users,
        'requests': {
            'total': total_requests,
            'pending': pending_requests,
            'approved': approved_requests,
            'rejected': rejected_requests
        }
    }), 200
