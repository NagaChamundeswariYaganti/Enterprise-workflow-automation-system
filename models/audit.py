from datetime import datetime
from models.user import db
import json

class AuditLog(db.Model):
    """Audit log for system traceability and compliance"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # User and Action
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False, index=True)
    resource_type = db.Column(db.String(50), index=True)  # e.g., 'request', 'user', 'role'
    resource_id = db.Column(db.Integer, index=True)
    
    # Request Details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    endpoint = db.Column(db.String(255))
    method = db.Column(db.String(10))  # GET, POST, PUT, DELETE
    
    # Status and Response
    status_code = db.Column(db.Integer)
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    
    # Additional Data
    details = db.Column(db.Text)  # JSON field for additional information
    old_values = db.Column(db.Text)  # JSON field for tracking changes
    new_values = db.Column(db.Text)  # JSON field for tracking changes
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def set_details(self, data):
        """Store additional details as JSON"""
        self.details = json.dumps(data)
    
    def get_details(self):
        """Retrieve details from JSON"""
        return json.loads(self.details) if self.details else {}
    
    def set_old_values(self, data):
        """Store old values as JSON"""
        self.old_values = json.dumps(data)
    
    def get_old_values(self):
        """Retrieve old values from JSON"""
        return json.loads(self.old_values) if self.old_values else {}
    
    def set_new_values(self, data):
        """Store new values as JSON"""
        self.new_values = json.dumps(data)
    
    def get_new_values(self):
        """Retrieve new values from JSON"""
        return json.loads(self.new_values) if self.new_values else {}
    
    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'user': self.user.to_dict() if self.user else None,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'ip_address': self.ip_address,
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'success': self.success,
            'error_message': self.error_message,
            'details': self.get_details(),
            'old_values': self.get_old_values(),
            'new_values': self.get_new_values(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def log_action(cls, user_id, action, resource_type=None, resource_id=None, 
                   details=None, success=True, error_message=None, 
                   old_values=None, new_values=None):
        """Convenience method to create an audit log entry"""
        log = cls(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            success=success,
            error_message=error_message
        )
        
        if details:
            log.set_details(details)
        if old_values:
            log.set_old_values(old_values)
        if new_values:
            log.set_new_values(new_values)
        
        db.session.add(log)
        return log
    
    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action}>'
