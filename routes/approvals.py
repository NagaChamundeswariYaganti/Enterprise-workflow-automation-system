from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.workflow_service import WorkflowService
from rbac import require_permission
from validation.schemas import ApprovalAction
from utils import handle_errors, success_response, error_response

approvals_bp = Blueprint('approvals', __name__)

@approvals_bp.route('/pending', methods=['GET'])
@login_required
@require_permission('approve_request')
@handle_errors
def get_pending_approvals():
    """Get all requests pending approval by current user"""
    pending_requests = WorkflowService.get_pending_approvals(current_user.id)
    
    return jsonify({
        'pending_approvals': [req.to_dict() for req in pending_requests],
        'count': len(pending_requests)
    }), 200

@approvals_bp.route('/<int:request_id>/process', methods=['POST'])
@login_required
@require_permission('approve_request')
@handle_errors
def process_approval(request_id):
    """Process an approval action (approve/reject/request_more_info)"""
    data = request.get_json()
    approval_data = ApprovalAction(**data)
    
    result = WorkflowService.process_approval(
        request_id,
        current_user.id,
        approval_data.action,
        approval_data.comments
    )
    
    if not result['success']:
        return error_response(result['error'], 400)
    
    return jsonify(result), 200

@approvals_bp.route('/<int:request_id>/approve', methods=['POST'])
@login_required
@require_permission('approve_request')
@handle_errors
def approve_request(request_id):
    """Approve a request"""
    data = request.get_json() or {}
    comments = data.get('comments')
    
    result = WorkflowService.process_approval(
        request_id,
        current_user.id,
        'approve',
        comments
    )
    
    if not result['success']:
        return error_response(result['error'], 400)
    
    return jsonify(result), 200

@approvals_bp.route('/<int:request_id>/reject', methods=['POST'])
@login_required
@require_permission('approve_request')
@handle_errors
def reject_request(request_id):
    """Reject a request"""
    data = request.get_json() or {}
    comments = data.get('comments')
    
    result = WorkflowService.process_approval(
        request_id,
        current_user.id,
        'reject',
        comments
    )
    
    if not result['success']:
        return error_response(result['error'], 400)
    
    return jsonify(result), 200

@approvals_bp.route('/<int:request_id>/request-info', methods=['POST'])
@login_required
@require_permission('approve_request')
@handle_errors
def request_more_info(request_id):
    """Request more information"""
    data = request.get_json() or {}
    comments = data.get('comments', 'More information required')
    
    result = WorkflowService.process_approval(
        request_id,
        current_user.id,
        'request_more_info',
        comments
    )
    
    if not result['success']:
        return error_response(result['error'], 400)
    
    return jsonify(result), 200

@approvals_bp.route('/my-history', methods=['GET'])
@login_required
@handle_errors
def get_my_approvals():
    """Get approval history for current user"""
    from models.request import ApprovalHistory
    
    history = ApprovalHistory.query.filter_by(
        approver_id=current_user.id
    ).order_by(ApprovalHistory.created_at.desc()).limit(50).all()
    
    return jsonify({
        'approvals': [approval.to_dict() for approval in history],
        'count': len(history)
    }), 200
