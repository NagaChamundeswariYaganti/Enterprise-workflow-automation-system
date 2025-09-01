from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.request import Request
from models.user import db
from services.workflow_service import WorkflowService
from rbac import require_permission
from validation.schemas import RequestCreate, RequestUpdate
from utils import handle_errors, success_response, error_response

requests_bp = Blueprint('requests', __name__)

@requests_bp.route('', methods=['POST'])
@login_required
@require_permission('create_request')
@handle_errors
def create_request():
    """Create a new request"""
    data = request.get_json()
    request_data = RequestCreate(**data)
    
    new_request = WorkflowService.create_request(
        requester_id=current_user.id,
        **request_data.dict()
    )
    
    return success_response('Request created successfully',
                          {'request': new_request.to_dict()}, 201)

@requests_bp.route('', methods=['GET'])
@login_required
@handle_errors
def list_requests():
    """List requests based on user role"""
    status = request.args.get('status')
    
    # Get requests based on permissions
    if current_user.has_permission('view_all_requests'):
        query = Request.query
        if status:
            query = query.filter_by(status=status)
        requests_list = query.order_by(Request.created_at.desc()).all()
    else:
        requests_list = WorkflowService.get_user_requests(current_user.id, status)
    
    return jsonify({
        'requests': [req.to_dict() for req in requests_list],
        'count': len(requests_list)
    }), 200

@requests_bp.route('/<int:request_id>', methods=['GET'])
@login_required
@handle_errors
def get_request(request_id):
    """Get request details"""
    req = Request.query.get(request_id)
    if not req:
        return error_response('Request not found', 404)
    
    # Check access permissions
    if (req.requester_id != current_user.id and 
        not current_user.has_permission('view_all_requests')):
        return error_response('Access denied', 403)
    
    return jsonify(req.to_dict()), 200

@requests_bp.route('/<int:request_id>', methods=['PUT'])
@login_required
@require_permission('update_request')
@handle_errors
def update_request(request_id):
    """Update request details"""
    data = request.get_json()
    update_data = RequestUpdate(**data)
    
    req = Request.query.get(request_id)
    if not req:
        return error_response('Request not found', 404)
    
    # Check ownership or admin permission
    if (req.requester_id != current_user.id and 
        not current_user.has_permission('update_any_request')):
        return error_response('Access denied', 403)
    
    # Update request
    updated_request = WorkflowService.update_request(
        request_id,
        current_user.id,
        **update_data.dict(exclude_unset=True)
    )
    
    return success_response('Request updated successfully',
                          {'request': updated_request.to_dict()})

@requests_bp.route('/<int:request_id>', methods=['DELETE'])
@login_required
@handle_errors
def delete_request(request_id):
    """Cancel a request"""
    reason = request.args.get('reason')
    
    result = WorkflowService.cancel_request(
        request_id,
        current_user.id,
        reason
    )
    
    if not result['success']:
        return error_response(result['error'], 400)
    
    return jsonify(result), 200

@requests_bp.route('/<int:request_id>/history', methods=['GET'])
@login_required
@handle_errors
def get_approval_history(request_id):
    """Get approval history for a request"""
    req = Request.query.get(request_id)
    if not req:
        return error_response('Request not found', 404)
    
    # Check access
    if (req.requester_id != current_user.id and 
        not current_user.has_permission('view_all_requests')):
        return error_response('Access denied', 403)
    
    history = [approval.to_dict() for approval in req.approvals]
    
    return jsonify({
        'request_id': request_id,
        'history': history
    }), 200

@requests_bp.route('/<int:request_id>/assign', methods=['POST'])
@login_required
@require_permission('assign_request')
@handle_errors
def assign_request(request_id):
    """Assign a request to a user"""
    data = request.get_json()
    assignee_id = data.get('assignee_id')
    
    if not assignee_id:
        return error_response('assignee_id required', 400)
    
    result = WorkflowService.assign_request(
        request_id,
        assignee_id,
        current_user.id
    )
    
    if not result['success']:
        return error_response(result['error'], 400)
    
    return jsonify(result), 200
