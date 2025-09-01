# Enterprise Workflow Automation & RBAC System - Implementation Guide

## Project Overview

This guide will help you build a structured workflow system for request intake, validation, and multi-party approval routing with role-based access control (RBAC).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend/API Layer                       │
│              (Flask Routes, Authentication)                  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Business Logic                          │
│        (Workflow Service, RBAC Manager, Validators)          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Data Access Layer                       │
│                   (SQLAlchemy Models)                        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                         Database                             │
│              (PostgreSQL/SQLite + Audit Logs)                │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
Automation/
├── models/              # Database models
│   ├── __init__.py
│   ├── user.py         # User model with authentication
│   ├── role.py         # Role & Permission models
│   ├── request.py      # Request & ApprovalHistory models
│   └── audit.py        # Audit log model
├── services/           # Business logic
│   ├── workflow_service.py
│   ├── google_workspace_service.py
│   └── notification_service.py
├── rbac/               # Access control logic
│   └── __init__.py     # Decorators and RBAC manager
├── validation/         # Input validation
│   └── schemas.py      # Pydantic schemas
├── routes/             # API endpoints
│   ├── auth.py
│   ├── requests.py
│   ├── admin.py
│   └── approvals.py
├── config.py           # Configuration
├── app.py              # Main application
├── requirements.txt    # Dependencies
└── .env                # Environment variables
```

## Step-by-Step Implementation Guide

### Phase 1: Setup and Database Models (2-3 hours)

#### 1.1 Environment Setup

**Install dependencies:**
```bash
python -m venv venv
venv\Scripts\activate
pip install flask flask-sqlalchemy flask-login python-dotenv pydantic
pip install google-auth google-auth-oauthlib google-api-python-client
pip install bcrypt psycopg2-binary
```

**Create `.env` file:**
```env
DATABASE_URL=sqlite:///workflow.db
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

#### 1.2 Create User Model (`models/user.py`)

**Key Components:**
- User authentication (password hashing with bcrypt)
- Many-to-many relationship with roles
- Google Workspace integration fields
- Profile information
- Active/inactive status tracking

**Important Methods:**
- `set_password()` - Hash passwords
- `check_password()` - Verify passwords
- `has_role()` - Check user roles
- `has_permission()` - Check permissions through roles

**Database Fields:**
```python
- id (Primary Key)
- username (unique, indexed)
- email (unique, indexed)
- password_hash
- first_name, last_name, department
- google_id, google_access_token, google_refresh_token
- is_active, is_verified
- created_at, updated_at, last_login
```

#### 1.3 Create Role and Permission Models (`models/role.py`)

**Role Model:**
- Hierarchical role structure with levels
- Approval authority configuration
- Many-to-many relationship with permissions
- Approval limits for financial workflows

**Permission Model:**
- Resource-based permissions (create, read, update, delete, approve)
- Granular access control
- Pattern: `{action}_{resource}` (e.g., "create_request", "approve_request")

**Common Permissions:**
```python
- create_request, read_request, update_request, delete_request
- approve_request, reject_request
- manage_users, manage_roles
- view_audit_logs, export_reports
```

#### 1.4 Create Request Model (`models/request.py`)

**Request Model:**
- Title, description, request type
- Status workflow (pending → in_progress → approved/rejected)
- Multi-level approval tracking
- Financial information (amount, currency)
- Priority levels (low, medium, high, urgent)
- Metadata JSON field for flexibility

**ApprovalHistory Model:**
- Track each approval action
- Store approver, action, level, comments
- Timestamp for audit trail

**Status Flow:**
```
pending → in_progress → approved
           ↓
        rejected
```

#### 1.5 Create Audit Log Model (`models/audit.py`)

**Purpose:** Complete system traceability

**Track:**
- User actions (who did what)
- Resource changes (before/after values)
- API requests (endpoint, method, status)
- IP address and user agent
- Timestamps

**Use Cases:**
- Compliance requirements
- Security investigations
- Change tracking
- Performance monitoring

### Phase 2: Business Logic & Validation (3-4 hours)

#### 2.1 Input Validation (`validation/schemas.py`)

Use **Pydantic** for robust validation:

**RequestCreate Schema:**
```python
- title: 3-200 characters
- request_type: predefined list
- amount: non-negative float
- priority: enum (low, medium, high, urgent)
- required_approval_levels: 1-5
- Custom validators for business rules
```

**UserCreate Schema:**
```python
- username: alphanumeric + underscores
- email: valid email format
- password: 8+ chars, uppercase, lowercase, digit
- Custom validators for security
```

**Benefits:**
- Automatic validation before database operations
- Clear error messages
- Type safety
- Reusable schemas

#### 2.2 Workflow Service (`services/workflow_service.py`)

**Core Functions:**

**1. create_request()**
- Validate requester exists
- Set initial status to 'pending'
- Log creation in audit trail
- Return created request

**2. process_approval()**
- Verify approver has permission
- Check current approval level
- Create approval history entry
- Advance workflow or finalize
- Send notifications
- Log action

**3. get_pending_approvals(user_id)**
- Filter requests by status
- Check approval permissions
- Return requests user can approve

**4. assign_request()**
- Assign to team member
- Update status
- Notify assignee
- Log assignment

**Workflow Logic:**
```python
if action == 'approve':
    current_level += 1
    if current_level >= required_levels:
        status = 'approved'
    else:
        status = 'in_progress'
elif action == 'reject':
    status = 'rejected'
```

#### 2.3 RBAC Manager (`rbac/__init__.py`)

**Decorators:**

**@require_permission('permission_name')**
```python
@require_permission('create_request')
def create_request_endpoint():
    # Only users with 'create_request' permission can access
```

**@require_role('role_name')**
```python
@require_role('admin')
def admin_dashboard():
    # Only admins can access
```

**@audit_action('action_name')**
```python
@audit_action('delete_user', 'user')
def delete_user(user_id):
    # Automatically logs action in audit trail
```

**RBACManager Class:**
- assign_role_to_user()
- remove_role_from_user()
- assign_permission_to_role()
- get_user_permissions()
- get_users_with_permission()

### Phase 3: Google Workspace Integration (2-3 hours)

#### 3.1 OAuth2 Setup

**1. Create Google Cloud Project:**
- Go to console.cloud.google.com
- Create new project
- Enable APIs: Gmail, Calendar, Drive, OAuth2
- Create OAuth2 credentials
- Download credentials.json

**2. Configure Scopes:**
```python
SCOPES = [
    'userinfo.email',
    'userinfo.profile',
    'gmail.send',
    'calendar',
    'drive.file'
]
```

#### 3.2 Google Workspace Service (`services/google_workspace_service.py`)

**Key Methods:**

**1. get_authorization_url()**
- Generate OAuth2 URL
- User clicks to authorize
- Redirect back with code

**2. exchange_code_for_tokens()**
- Exchange code for access/refresh tokens
- Store in user model
- Use for API calls

**3. send_email()**
- Send notifications via Gmail API
- HTML or plain text
- Approval requests, status updates

**4. create_calendar_event()**
- Schedule approval meetings
- Add attendees automatically
- Send invitations

**5. upload_to_drive()**
- Store request attachments
- Organize in folders
- Share with approvers

**Workflow Integration:**
```python
# When request created
send_email(approvers, "New request needs approval")

# When approved
create_calendar_event("Approved - Implementation starts")

# Store documents
upload_to_drive(request_attachments, request_folder)
```

### Phase 4: API Routes & Application (3-4 hours)

#### 4.1 Authentication Routes (`routes/auth.py`)

**Endpoints:**
- POST `/auth/register` - User registration
- POST `/auth/login` - Login with password
- POST `/auth/logout` - Logout
- GET `/auth/google` - Google OAuth2 start
- GET `/auth/google/callback` - OAuth2 callback
- GET `/auth/profile` - Get current user
- PUT `/auth/profile` - Update profile

#### 4.2 Request Routes (`routes/requests.py`)

**Endpoints:**
- POST `/requests` - Create request
- GET `/requests` - List all requests (filtered by user)
- GET `/requests/{id}` - Get request details
- PUT `/requests/{id}` - Update request
- DELETE `/requests/{id}` - Cancel request
- GET `/requests/{id}/history` - Get approval history

#### 4.3 Approval Routes (`routes/approvals.py`)

**Endpoints:**
- GET `/approvals/pending` - Get pending approvals
- POST `/approvals/{request_id}/approve` - Approve request
- POST `/approvals/{request_id}/reject` - Reject request
- POST `/approvals/{request_id}/request-info` - Request more info

#### 4.4 Admin Routes (`routes/admin.py`)

**Endpoints:**
- GET `/admin/users` - List users
- POST `/admin/users` - Create user
- PUT `/admin/users/{id}` - Update user
- POST `/admin/users/{id}/roles` - Assign role
- GET `/admin/roles` - List roles
- POST `/admin/roles` - Create role
- POST `/admin/roles/{id}/permissions` - Assign permission
- GET `/admin/audit-logs` - View audit logs
- GET `/admin/reports` - Generate reports

#### 4.5 Main Application (`app.py`)

**Setup:**
```python
from flask import Flask
from flask_login import LoginManager
from models.user import db
from config import config

app = Flask(__name__)
app.config.from_object(config['development'])

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(requests_bp, url_prefix='/requests')
app.register_blueprint(approvals_bp, url_prefix='/approvals')
app.register_blueprint(admin_bp, url_prefix='/admin')

# Create tables
with app.app_context():
    db.create_all()
```

### Phase 5: Data Consistency & Traceability (1-2 hours)

#### 5.1 Database Transactions

**Use transaction management:**
```python
from sqlalchemy import exc

try:
    # Multiple operations
    db.session.add(request)
    db.session.add(approval)
    db.session.commit()
except exc.SQLAlchemyError:
    db.session.rollback()
    raise
```

#### 5.2 Audit Trail Implementation

**Automatic Logging:**
- Use decorators for route-level logging
- Use model events for data changes
- Store before/after values
- Track all user actions

**Example:**
```python
@audit_action('create_request', 'request')
def create_request():
    # Automatically logged
    pass
```

#### 5.3 Validation Layers

**Three-Layer Validation:**
1. **Input Validation** (Pydantic schemas)
2. **Business Logic Validation** (Service layer)
3. **Database Constraints** (Model constraints)

**Example:**
```python
# Layer 1: Pydantic
schema = RequestCreate(**data)

# Layer 2: Business logic
if not user.has_permission('create_request'):
    raise PermissionError()

# Layer 3: Database
request = Request(**schema.dict())
db.session.add(request)
db.session.commit()
```

### Phase 6: Testing & Documentation (2-3 hours)

#### 6.1 Unit Tests

**Test Coverage:**
- Model methods
- Service functions
- RBAC logic
- Validation schemas

**Example Test:**
```python
def test_approval_workflow():
    request = create_test_request()
    assert request.status == 'pending'
    
    process_approval(request.id, approver.id, 'approve')
    assert request.status == 'in_progress'
```

#### 6.2 API Documentation

**Document Each Endpoint:**
- Request format
- Response format
- Required permissions
- Example calls

**Use Swagger/OpenAPI:**
```python
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
```

#### 6.3 Architecture Documentation

**Create Documentation:**
- System architecture diagram
- Database schema diagram
- Workflow diagrams
- Permission matrix
- Deployment guide

## Security Best Practices

### 1. Authentication & Authorization
- Hash all passwords with bcrypt
- Use secure session management
- Implement CSRF protection
- Rate limit login attempts

### 2. Input Validation
- Validate all user inputs
- Sanitize data before database operations
- Use parameterized queries (SQLAlchemy handles this)
- Validate file uploads

### 3. Access Control
- Implement principle of least privilege
- Verify permissions on every request
- Log all access attempts
- Implement role hierarchy

### 4. Data Protection
- Encrypt sensitive data at rest
- Use HTTPS in production
- Secure API keys and tokens
- Regular security audits

### 5. Audit & Monitoring
- Log all actions
- Monitor for suspicious activity
- Set up alerts for critical events
- Regular log reviews

## Deployment Checklist

### Pre-Production
- [ ] All tests passing
- [ ] Database migrations ready
- [ ] Environment variables configured
- [ ] Security review completed
- [ ] Documentation complete

### Production Setup
- [ ] Use PostgreSQL (not SQLite)
- [ ] Configure proper SECRET_KEY
- [ ] Set up HTTPS/SSL
- [ ] Configure email service (SMTP)
- [ ] Set up Google OAuth2 credentials
- [ ] Configure backup strategy
- [ ] Set up monitoring/logging
- [ ] Configure CORS if needed

### Post-Deployment
- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Verify email delivery
- [ ] Test Google integration
- [ ] User acceptance testing
- [ ] Create admin accounts
- [ ] Document operational procedures

## Common Pitfalls to Avoid

1. **Not Using Transactions**
   - Always wrap multiple operations in transactions
   - Handle rollback on errors

2. **Insufficient Permission Checks**
   - Check permissions at every access point
   - Don't rely only on frontend validation

3. **Poor Error Handling**
   - Return appropriate status codes
   - Don't expose internal errors to users
   - Log detailed errors for debugging

4. **Missing Audit Logs**
   - Log all state changes
   - Include context (who, what, when, where)

5. **Hardcoded Configuration**
   - Use environment variables
   - Different configs for dev/staging/prod

6. **Inadequate Testing**
   - Test permission boundaries
   - Test workflow edge cases
   - Test concurrent operations

## Performance Optimization

### Database
- Add indexes on frequently queried fields
- Use database query optimization
- Implement pagination for large result sets
- Cache frequently accessed data

### API
- Implement rate limiting
- Use connection pooling
- Minimize N+1 query problems
- Consider API response compression

### Google API
- Cache OAuth tokens
- Batch API requests when possible
- Handle rate limits gracefully
- Implement retry logic

## Next Steps

1. **Start with Phase 1** - Set up database models
2. **Test Each Component** - Before moving forward
3. **Build Incrementally** - Don't try to do everything at once
4. **Document As You Go** - Code comments and API docs
5. **Get Feedback Early** - Show stakeholders progress
6. **Iterate** - Refine based on testing and feedback

## Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Pydantic Documentation: https://docs.pydantic.dev/
- Google Workspace APIs: https://developers.google.com/workspace
- Flask-Login: https://flask-login.readthedocs.io/

## Support & Questions

As you build this system, remember:
- Break down complex problems into smaller pieces
- Test each component thoroughly
- Document your decisions
- Ask for help when stuck
- Iterate and improve continuously

Good luck with your implementation! 🚀
