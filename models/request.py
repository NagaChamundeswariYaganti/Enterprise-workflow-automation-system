from datetime import datetime
from models.user import db
import json

class Request(db.Model):
    """Request model for workflow automation"""
    __tablename__ = 'requests'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Request Information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    request_type = db.Column(db.String(50), nullable=False)  # e.g., 'purchase', 'access', 'leave'
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    
    # Financial Information (if applicable)
    amount = db.Column(db.Float)
    currency = db.Column(db.String(3), default='USD')
    
    # Status Tracking
    status = db.Column(db.String(20), default='pending', index=True)
    current_approval_level = db.Column(db.Integer, default=0)
    required_approval_levels = db.Column(db.Integer, default=1)
    
    # User References
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Additional Data
    metadata = db.Column(db.Text)  # JSON field for flexible data storage
    attachments = db.Column(db.Text)  # JSON array of attachment URLs/paths
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    
    # Relationships
    approvals = db.relationship('ApprovalHistory', backref='request', lazy=True,
                               cascade='all, delete-orphan')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])
    
    def set_metadata(self, data):
        """Store additional metadata as JSON"""
        self.metadata = json.dumps(data)
    
    def get_metadata(self):
        """Retrieve metadata from JSON"""
        return json.loads(self.metadata) if self.metadata else {}
    
    def set_attachments(self, attachments_list):
        """Store attachments as JSON"""
        self.attachments = json.dumps(attachments_list)
    
    def get_attachments(self):
        """Retrieve attachments from JSON"""
        return json.loads(self.attachments) if self.attachments else []
    
    def can_approve(self, user):
        """Check if a user can approve this request"""
        # Check if user has approval permissions
        if not user.has_permission('approve_request'):
            return False
        
        # Check if request is in pending status
        if self.status not in ['pending', 'in_progress']:
            return False
        
        # Additional business logic can be added here
        # e.g., approval based on amount, department, role level
        
        return True
    
    def advance_approval_level(self):
        """Move to next approval level"""
        self.current_approval_level += 1
        if self.current_approval_level >= self.required_approval_levels:
            self.status = 'approved'
            self.completed_at = datetime.utcnow()
    
    def reject_request(self):
        """Reject the request"""
        self.status = 'rejected'
        self.completed_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert request to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'request_type': self.request_type,
            'priority': self.priority,
            'status': self.status,
            'amount': self.amount,
            'currency': self.currency,
            'current_approval_level': self.current_approval_level,
            'required_approval_levels': self.required_approval_levels,
            'requester': self.requester.to_dict() if self.requester else None,
            'assigned_to': self.assigned_to.to_dict() if self.assigned_to else None,
            'metadata': self.get_metadata(),
            'attachments': self.get_attachments(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<Request {self.id}: {self.title}>'

class ApprovalHistory(db.Model):
    """Track approval history for requests"""
    __tablename__ = 'approval_history'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # References
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Approval Details
    action = db.Column(db.String(20), nullable=False)  # 'approve', 'reject', 'request_more_info'
    approval_level = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert approval history to dictionary"""
        return {
            'id': self.id,
            'request_id': self.request_id,
            'approver': self.approver.to_dict() if self.approver else None,
            'action': self.action,
            'approval_level': self.approval_level,
            'comments': self.comments,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ApprovalHistory {self.id}: {self.action} by {self.approver_id}>'
