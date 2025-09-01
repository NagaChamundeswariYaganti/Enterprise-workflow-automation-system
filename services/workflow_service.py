from models.request import Request, ApprovalHistory
from models.user import User, db
from models.audit import AuditLog
from datetime import datetime
from typing import Optional, List, Dict

class WorkflowService:
    """Service for managing workflow operations"""
    
    @staticmethod
    def create_request(requester_id: int, **kwargs) -> Request:
        """
        Create a new request
        
        Args:
            requester_id: ID of the user creating the request
            **kwargs: Additional request parameters
        
        Returns:
            Request: Created request object
        """
        request = Request(
            requester_id=requester_id,
            **kwargs
        )
        
        # Set submission time
        request.submitted_at = datetime.utcnow()
        request.status = 'pending'
        
        db.session.add(request)
        db.session.commit()
        
        # Log the action
        AuditLog.log_action(
            user_id=requester_id,
            action='create_request',
            resource_type='request',
            resource_id=request.id,
            details={'title': request.title, 'type': request.request_type}
        )
        db.session.commit()
        
        return request
    
    @staticmethod
    def update_request(request_id: int, user_id: int, **kwargs) -> Optional[Request]:
        """
        Update an existing request
        
        Args:
            request_id: ID of the request to update
            user_id: ID of the user performing the update
            **kwargs: Fields to update
        
        Returns:
            Request: Updated request object or None
        """
        request = Request.query.get(request_id)
        if not request:
            return None
        
        # Store old values for audit
        old_values = {k: getattr(request, k) for k in kwargs.keys() if hasattr(request, k)}
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(request, key):
                setattr(request, key, value)
        
        request.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log the action
        AuditLog.log_action(
            user_id=user_id,
            action='update_request',
            resource_type='request',
            resource_id=request_id,
            old_values=old_values,
            new_values=kwargs
        )
        db.session.commit()
        
        return request
    
    @staticmethod
    def process_approval(request_id: int, approver_id: int, action: str, 
                        comments: Optional[str] = None) -> Dict:
        """
        Process an approval action on a request
        
        Args:
            request_id: ID of the request
            approver_id: ID of the approver
            action: Action to take (approve, reject, request_more_info)
            comments: Optional comments
        
        Returns:
            dict: Result of the approval action
        """
        request = Request.query.get(request_id)
        if not request:
            return {'success': False, 'error': 'Request not found'}
        
        approver = User.query.get(approver_id)
        if not approver:
            return {'success': False, 'error': 'Approver not found'}
        
        # Check if user can approve
        if not request.can_approve(approver):
            return {'success': False, 'error': 'User cannot approve this request'}
        
        # Create approval history entry
        approval = ApprovalHistory(
            request_id=request_id,
            approver_id=approver_id,
            action=action,
            approval_level=request.current_approval_level,
            comments=comments
        )
        db.session.add(approval)
        
        # Process based on action
        if action == 'approve':
            request.advance_approval_level()
            if request.status == 'approved':
                message = 'Request fully approved'
            else:
                request.status = 'in_progress'
                message = f'Approval level {request.current_approval_level} completed'
        
        elif action == 'reject':
            request.reject_request()
            message = 'Request rejected'
        
        elif action == 'request_more_info':
            request.status = 'pending'
            message = 'More information requested'
        
        else:
            return {'success': False, 'error': 'Invalid action'}
        
        db.session.commit()
        
        # Log the action
        AuditLog.log_action(
            user_id=approver_id,
            action=f'{action}_request',
            resource_type='request',
            resource_id=request_id,
            details={'comments': comments}
        )
        db.session.commit()
        
        return {
            'success': True,
            'message': message,
            'request_status': request.status,
            'current_level': request.current_approval_level
        }
    
    @staticmethod
    def get_pending_approvals(user_id: int) -> List[Request]:
        """
        Get all requests pending approval by a specific user
        
        Args:
            user_id: ID of the user
        
        Returns:
            List[Request]: List of pending requests
        """
        user = User.query.get(user_id)
        if not user:
            return []
        
        # Get all pending or in_progress requests
        requests = Request.query.filter(
            Request.status.in_(['pending', 'in_progress'])
        ).all()
        
        # Filter by those the user can approve
        pending = [req for req in requests if req.can_approve(user)]
        
        return pending
    
    @staticmethod
    def get_user_requests(user_id: int, status: Optional[str] = None) -> List[Request]:
        """
        Get all requests created by a user
        
        Args:
            user_id: ID of the user
            status: Optional status filter
        
        Returns:
            List[Request]: List of requests
        """
        query = Request.query.filter_by(requester_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Request.created_at.desc()).all()
    
    @staticmethod
    def assign_request(request_id: int, assignee_id: int, assigner_id: int) -> Dict:
        """
        Assign a request to a user
        
        Args:
            request_id: ID of the request
            assignee_id: ID of the user to assign to
            assigner_id: ID of the user performing the assignment
        
        Returns:
            dict: Result of the assignment
        """
        request = Request.query.get(request_id)
        if not request:
            return {'success': False, 'error': 'Request not found'}
        
        assignee = User.query.get(assignee_id)
        if not assignee:
            return {'success': False, 'error': 'Assignee not found'}
        
        old_assignee_id = request.assigned_to_id
        request.assigned_to_id = assignee_id
        request.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log the action
        AuditLog.log_action(
            user_id=assigner_id,
            action='assign_request',
            resource_type='request',
            resource_id=request_id,
            old_values={'assigned_to_id': old_assignee_id},
            new_values={'assigned_to_id': assignee_id}
        )
        db.session.commit()
        
        return {'success': True, 'message': 'Request assigned successfully'}
    
    @staticmethod
    def cancel_request(request_id: int, user_id: int, reason: Optional[str] = None) -> Dict:
        """
        Cancel a request
        
        Args:
            request_id: ID of the request
            user_id: ID of the user cancelling
            reason: Optional cancellation reason
        
        Returns:
            dict: Result of the cancellation
        """
        request = Request.query.get(request_id)
        if not request:
            return {'success': False, 'error': 'Request not found'}
        
        # Only requester can cancel their own request
        if request.requester_id != user_id:
            user = User.query.get(user_id)
            if not user or not user.has_permission('cancel_any_request'):
                return {'success': False, 'error': 'Not authorized to cancel this request'}
        
        request.status = 'cancelled'
        request.updated_at = datetime.utcnow()
        request.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log the action
        AuditLog.log_action(
            user_id=user_id,
            action='cancel_request',
            resource_type='request',
            resource_id=request_id,
            details={'reason': reason}
        )
        db.session.commit()
        
        return {'success': True, 'message': 'Request cancelled successfully'}
