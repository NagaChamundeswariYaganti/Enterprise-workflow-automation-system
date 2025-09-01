from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    """Request priority levels"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'

class RequestStatus(str, Enum):
    """Request status options"""
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class RequestCreate(BaseModel):
    """Validation schema for creating a request"""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    request_type: str = Field(..., min_length=1, max_length=50)
    priority: Priority = Priority.MEDIUM
    amount: Optional[float] = Field(None, ge=0)
    currency: str = Field('USD', min_length=3, max_length=3)
    required_approval_levels: int = Field(1, ge=1, le=5)
    metadata: Optional[Dict[str, Any]] = None
    attachments: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('request_type')
    def request_type_must_be_valid(cls, v):
        valid_types = ['purchase', 'access', 'leave', 'expense', 'travel', 'other']
        if v.lower() not in valid_types:
            raise ValueError(f'Request type must be one of {valid_types}')
        return v.lower()
    
    @validator('amount')
    def validate_amount(cls, v, values):
        if v is not None and v < 0:
            raise ValueError('Amount must be non-negative')
        return v
    
    class Config:
        use_enum_values = True

class RequestUpdate(BaseModel):
    """Validation schema for updating a request"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[RequestStatus] = None
    assigned_to_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    attachments: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    
    class Config:
        use_enum_values = True

class ApprovalAction(BaseModel):
    """Validation schema for approval actions"""
    action: str = Field(..., pattern='^(approve|reject|request_more_info)$')
    comments: Optional[str] = Field(None, max_length=1000)
    
    @validator('action')
    def validate_action(cls, v):
        valid_actions = ['approve', 'reject', 'request_more_info']
        if v not in valid_actions:
            raise ValueError(f'Action must be one of {valid_actions}')
        return v

class UserCreate(BaseModel):
    """Validation schema for creating a user"""
    username: str = Field(..., min_length=3, max_length=80)
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v.lower()
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    """Validation schema for updating a user"""
    email: Optional[str] = Field(None, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None

class RoleCreate(BaseModel):
    """Validation schema for creating a role"""
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    level: int = Field(0, ge=0, le=10)
    can_approve: bool = False
    approval_limit: Optional[float] = Field(None, ge=0)
    
    @validator('name')
    def name_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').replace(' ', '').isalnum():
            raise ValueError('Role name must be alphanumeric')
        return v.lower()

class PermissionCreate(BaseModel):
    """Validation schema for creating a permission"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    resource: str = Field(..., max_length=50)
    action: str = Field(..., pattern='^(create|read|update|delete|approve|manage)$')
    
    @validator('name')
    def name_format(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Permission name must be alphanumeric')
        return v.lower()
