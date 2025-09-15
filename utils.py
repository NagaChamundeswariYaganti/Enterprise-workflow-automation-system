"""Utility functions and decorators"""
from flask import jsonify
from functools import wraps
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from models.user import db


def handle_errors(f):
    """Decorator to handle common errors in routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Database error'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return decorated_function


def success_response(message, data=None, status_code=200):
    """Standard success response format"""
    response = {'message': message}
    if data:
        response.update(data)
    return jsonify(response), status_code


def error_response(message, status_code=400, details=None):
    """Standard error response format"""
    response = {'error': message}
    if details:
        response['details'] = details
    return jsonify(response), status_code
