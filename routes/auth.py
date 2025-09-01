from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User, db
from models.audit import AuditLog
from validation.schemas import UserCreate, UserUpdate
from utils import handle_errors, success_response, error_response
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@handle_errors
def register():
    """Register a new user"""
    data = request.get_json()
    user_data = UserCreate(**data)
    
    # Check if user already exists
    if User.query.filter_by(username=user_data.username).first():
        return error_response('Username already exists')
    if User.query.filter_by(email=user_data.email).first():
        return error_response('Email already exists')
    
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
    AuditLog.log_action(user_id=user.id, action='register', 
                       resource_type='user', resource_id=user.id)
    db.session.commit()
    
    return success_response('User registered successfully', 
                          {'user': user.to_dict()}, 201)

@auth_bp.route('/login', methods=['POST'])
@handle_errors
def login():
    """User login"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return error_response('Username and password required')
    
    # Find and validate user
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return error_response('Invalid username or password', 401)
    if not user.is_active:
        return error_response('Account is inactive', 403)
    
    # Log in user
    login_user(user)
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Log the action
    AuditLog.log_action(user_id=user.id, action='login',
                       resource_type='user', resource_id=user.id)
    db.session.commit()
    
    return success_response('Login successful', {'user': user.to_dict()})

@auth_bp.route('/logout', methods=['POST'])
@login_required
@handle_errors
def logout():
    """User logout"""
    user_id = current_user.id
    AuditLog.log_action(user_id=user_id, action='logout',
                       resource_type='user', resource_id=user_id)
    db.session.commit()
    logout_user()
    return success_response('Logout successful')

@auth_bp.route('/profile', methods=['GET'])
@login_required
@handle_errors
def get_profile():
    """Get current user profile"""
    return jsonify({'user': current_user.to_dict()}), 200

@auth_bp.route('/profile', methods=['PUT'])
@login_required
@handle_errors
def update_profile():
    """Update current user profile"""
    data = request.get_json()
    update_data = UserUpdate(**data)
    
    # Update fields and track changes
    old_values = {}
    for field, value in update_data.dict(exclude_unset=True).items():
        if hasattr(current_user, field) and value is not None:
            old_values[field] = getattr(current_user, field)
            setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Log the action
    AuditLog.log_action(user_id=current_user.id, action='update_profile',
                       resource_type='user', resource_id=current_user.id,
                       old_values=old_values, 
                       new_values=update_data.dict(exclude_unset=True))
    db.session.commit()
    
    return success_response('Profile updated successfully',
                          {'user': current_user.to_dict()})

@auth_bp.route('/change-password', methods=['POST'])
@login_required
@handle_errors
def change_password():
    """Change user password"""
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return error_response('Current and new password required')
    if not current_user.check_password(current_password):
        return error_response('Current password is incorrect', 401)
    if len(new_password) < 8:
        return error_response('Password must be at least 8 characters')
    
    # Set new password
    current_user.set_password(new_password)
    current_user.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Log the action
    AuditLog.log_action(user_id=current_user.id, action='change_password',
                       resource_type='user', resource_id=current_user.id)
    db.session.commit()
    
    return success_response('Password changed successfully')
