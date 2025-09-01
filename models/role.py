from models.user import db
from datetime import datetime

# Association table for role-permission many-to-many relationship
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

class Role(db.Model):
    """Role model for role-based access control"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200))
    level = db.Column(db.Integer, default=1)  # Hierarchy level for approval workflow
    can_approve = db.Column(db.Boolean, default=False)
    approval_limit = db.Column(db.Float, default=0.0)  # Maximum amount they can approve
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    permissions = db.relationship('Permission', secondary=role_permissions, lazy='subquery',
                                 backref=db.backref('roles', lazy=True))
    
    def to_dict(self):
        """Convert role to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'level': self.level,
            'can_approve': self.can_approve,
            'approval_limit': self.approval_limit,
            'permissions': [perm.name for perm in self.permissions],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Role {self.name}>'

class Permission(db.Model):
    """Permission model for fine-grained access control"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200))
    resource = db.Column(db.String(50))  # e.g., 'request', 'user', 'role'
    action = db.Column(db.String(50))    # e.g., 'create', 'read', 'update', 'delete'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert permission to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'resource': self.resource,
            'action': self.action,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Permission {self.name}>'
