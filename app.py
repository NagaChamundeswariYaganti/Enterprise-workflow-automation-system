from flask import Flask, jsonify
from flask_login import LoginManager
from models.user import db, User
from models.role import Role, Permission
from config import config
import os

# Import blueprints
from routes.auth import auth_bp
from routes.requests import requests_bp
from routes.approvals import approvals_bp
from routes.admin import admin_bp

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(requests_bp, url_prefix='/requests')
    app.register_blueprint(approvals_bp, url_prefix='/approvals')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Enterprise Workflow Automation API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/auth',
                'requests': '/requests',
                'approvals': '/approvals',
                'admin': '/admin'
            }
        }), 200
    
    # Health check
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

def init_db(app):
    """Initialize database with tables and seed data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default permissions
        permissions_data = [
            ('create_request', 'Create a new request', 'request', 'create'),
            ('read_request', 'View own requests', 'request', 'read'),
            ('update_request', 'Update own requests', 'request', 'update'),
            ('delete_request', 'Delete own requests', 'request', 'delete'),
            ('approve_request', 'Approve requests', 'request', 'approve'),
            ('view_all_requests', 'View all requests in system', 'request', 'read'),
            ('update_any_request', 'Update any request', 'request', 'update'),
            ('assign_request', 'Assign requests to users', 'request', 'manage'),
            ('cancel_any_request', 'Cancel any request', 'request', 'manage'),
            ('manage_users', 'Manage users', 'user', 'manage'),
            ('manage_roles', 'Manage roles', 'role', 'manage'),
            ('view_audit_logs', 'View audit logs', 'audit', 'read'),
        ]
        
        for perm_name, perm_desc, resource, action in permissions_data:
            if not Permission.query.filter_by(name=perm_name).first():
                permission = Permission(
                    name=perm_name,
                    description=perm_desc,
                    resource=resource,
                    action=action
                )
                db.session.add(permission)
        
        db.session.commit()
        
        # Create default roles
        # Admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(
                name='admin',
                description='System administrator with full access',
                level=10,
                can_approve=True
            )
            db.session.add(admin_role)
            db.session.commit()
            
            # Assign all permissions to admin
            all_permissions = Permission.query.all()
            for perm in all_permissions:
                admin_role.permissions.append(perm)
            db.session.commit()
        
        # Manager role
        manager_role = Role.query.filter_by(name='manager').first()
        if not manager_role:
            manager_role = Role(
                name='manager',
                description='Manager with approval authority',
                level=5,
                can_approve=True,
                approval_limit=10000.0
            )
            db.session.add(manager_role)
            db.session.commit()
            
            # Assign manager permissions
            manager_perms = ['approve_request', 'view_all_requests', 'assign_request', 
                           'create_request', 'read_request', 'update_request']
            for perm_name in manager_perms:
                perm = Permission.query.filter_by(name=perm_name).first()
                if perm:
                    manager_role.permissions.append(perm)
            db.session.commit()
        
        # Employee role
        employee_role = Role.query.filter_by(name='employee').first()
        if not employee_role:
            employee_role = Role(
                name='employee',
                description='Regular employee',
                level=1,
                can_approve=False
            )
            db.session.add(employee_role)
            db.session.commit()
            
            # Assign employee permissions
            employee_perms = ['create_request', 'read_request', 'update_request', 'delete_request']
            for perm_name in employee_perms:
                perm = Permission.query.filter_by(name=perm_name).first()
                if perm:
                    employee_role.permissions.append(perm)
            db.session.commit()
        
        print("Database initialized successfully!")
        print(f"Permissions created: {Permission.query.count()}")
        print(f"Roles created: {Role.query.count()}")

if __name__ == '__main__':
    # Create app
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    # Initialize database
    init_db(app)
    
    # Run app
    app.run(host='0.0.0.0', port=5000, debug=True)
