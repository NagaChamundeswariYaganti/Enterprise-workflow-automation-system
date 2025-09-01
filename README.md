# Enterprise Workflow Automation & RBAC System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A professional-grade workflow automation system with Role-Based Access Control (RBAC), multi-party approval routing, comprehensive audit logging, and Google Workspace integration.

## 🚀 Features

### Core Functionality
- **📝 Request Management**: Create, update, track, and manage workflow requests
- **✅ Multi-Level Approval**: Configurable approval workflows with multiple authorization levels
- **🔐 Role-Based Access Control (RBAC)**: Fine-grained permissions and role hierarchy
- **📊 Audit Trail**: Complete system traceability with detailed logging
- **🔔 Notifications**: Email notifications for request updates and approvals
- **🔗 Google Workspace Integration**: OAuth2, Gmail, Calendar, and Drive APIs

### Security & Compliance
- **Password Security**: Bcrypt password hashing
- **Session Management**: Secure authentication with Flask-Login
- **Permission Checks**: Decorator-based access control
- **Audit Logging**: Track all user actions and system changes
- **Input Validation**: Pydantic schemas for data integrity

### Technical Highlights
- **RESTful API**: Clean, documented API endpoints
- **Database Agnostic**: SQLAlchemy ORM (PostgreSQL/SQLite)
- **Docker Support**: Containerized deployment ready
- **Modular Architecture**: Separation of concerns (MVC pattern)
- **Test Coverage**: Unit tests for critical components

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Testing](#testing)
- [Contributing](#contributing)

## 🛠️ Installation

### Prerequisites
- Python 3.11 or higher
- PostgreSQL (for production) or SQLite (for development)
- Git

### Local Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd workflow-automation
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python app.py
```

The application will create all necessary tables and seed initial data (roles, permissions).

## 🚀 Quick Start

### Start the Development Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Create Your First Admin User

```bash
# Using curl or Postman
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "SecurePassword123",
    "first_name": "Admin",
    "last_name": "User"
  }'
```

### Assign Admin Role

```python
# Using Python shell
from app import create_app
from models.user import User, db
from models.role import Role

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    admin_role = Role.query.filter_by(name='admin').first()
    user.roles.append(admin_role)
    db.session.commit()
```

### Login

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "SecurePassword123"
  }'
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│              (Web UI, Mobile App, CLI, etc.)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (Flask)                       │
│  ┌──────────┬───────────┬────────────┬──────────────────┐  │
│  │   Auth   │ Requests  │ Approvals  │  Admin Routes    │  │
│  └──────────┴───────────┴────────────┴──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                       │
│  ┌──────────────┬─────────────────┬────────────────────┐   │
│  │   Workflow   │  RBAC Manager   │   Validators       │   │
│  │   Service    │                 │   (Pydantic)       │   │
│  └──────────────┴─────────────────┴────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Access Layer                         │
│  ┌──────────┬───────────┬────────────┬──────────────────┐  │
│  │   User   │   Role    │  Request   │  Audit Log       │  │
│  │  Model   │  Model    │  Model     │  Model           │  │
│  └──────────┴───────────┴────────────┴──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         Database                             │
│                  (PostgreSQL / SQLite)                       │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
Automation/
├── models/              # Database models
│   ├── user.py         # User authentication & profile
│   ├── role.py         # Roles & permissions
│   ├── request.py      # Requests & approval history
│   └── audit.py        # Audit logging
├── services/           # Business logic
│   ├── workflow_service.py
│   ├── google_workspace_service.py
│   └── notification_service.py
├── routes/             # API endpoints
│   ├── auth.py         # Authentication
│   ├── requests.py     # Request management
│   ├── approvals.py    # Approval processing
│   └── admin.py        # Admin operations
├── rbac/               # Access control
│   └── __init__.py     # Decorators & RBAC manager
├── validation/         # Input validation
│   └── schemas.py      # Pydantic schemas
├── tests/              # Unit tests
│   └── test_workflow.py
├── app.py              # Application entry point
├── config.py           # Configuration
├── requirements.txt    # Dependencies
├── Dockerfile          # Docker image
├── docker-compose.yml  # Docker orchestration
└── .env.example        # Environment template
```

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | User login | No |
| POST | `/auth/logout` | User logout | Yes |
| GET | `/auth/profile` | Get current user | Yes |
| PUT | `/auth/profile` | Update profile | Yes |
| POST | `/auth/change-password` | Change password | Yes |

### Request Endpoints

| Method | Endpoint | Description | Permission Required |
|--------|----------|-------------|---------------------|
| POST | `/requests` | Create request | `create_request` |
| GET | `/requests` | List requests | `read_request` |
| GET | `/requests/<id>` | Get request details | `read_request` |
| PUT | `/requests/<id>` | Update request | `update_request` |
| DELETE | `/requests/<id>` | Cancel request | `delete_request` |
| GET | `/requests/<id>/history` | Get approval history | `read_request` |
| POST | `/requests/<id>/assign` | Assign request | `assign_request` |

### Approval Endpoints

| Method | Endpoint | Description | Permission Required |
|--------|----------|-------------|---------------------|
| GET | `/approvals/pending` | Get pending approvals | `approve_request` |
| POST | `/approvals/<id>/process` | Process approval | `approve_request` |
| POST | `/approvals/<id>/approve` | Approve request | `approve_request` |
| POST | `/approvals/<id>/reject` | Reject request | `approve_request` |
| POST | `/approvals/<id>/request-info` | Request more info | `approve_request` |

### Admin Endpoints

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/admin/users` | List all users | Admin |
| POST | `/admin/users` | Create user | Admin |
| PUT | `/admin/users/<id>` | Update user | Admin |
| POST | `/admin/users/<id>/roles` | Assign role | Admin |
| DELETE | `/admin/users/<id>/roles/<role_id>` | Remove role | Admin |
| GET | `/admin/roles` | List all roles | Admin |
| POST | `/admin/roles` | Create role | Admin |
| POST | `/admin/roles/<id>/permissions` | Assign permission | Admin |
| GET | `/admin/permissions` | List permissions | Admin |
| POST | `/admin/permissions` | Create permission | Admin |
| GET | `/admin/audit-logs` | View audit logs | Admin |

## 💡 Usage Examples

### Create a Request

```python
import requests

# Login first
login_response = requests.post('http://localhost:5000/auth/login', json={
    'username': 'employee',
    'password': 'Password123'
})

# Create request
response = requests.post('http://localhost:5000/requests', json={
    'title': 'Purchase Office Supplies',
    'description': 'Need new keyboards and mice for the team',
    'request_type': 'purchase',
    'priority': 'medium',
    'amount': 500.00,
    'currency': 'USD',
    'required_approval_levels': 2
}, cookies=login_response.cookies)

print(response.json())
```

### Approve a Request

```python
# Login as manager
login_response = requests.post('http://localhost:5000/auth/login', json={
    'username': 'manager',
    'password': 'Password123'
})

# Approve request
response = requests.post('http://localhost:5000/approvals/1/approve', json={
    'comments': 'Approved - budget available'
}, cookies=login_response.cookies)

print(response.json())
```

### Get Pending Approvals

```python
response = requests.get('http://localhost:5000/approvals/pending',
                       cookies=login_response.cookies)

print(response.json())
```

## ⚙️ Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/workflow_db

# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Google Workspace (Optional)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/oauth2callback

# Email Notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
```

### Default Roles & Permissions

The system initializes with three default roles:

**Admin** (Level 10)
- Full system access
- All permissions

**Manager** (Level 5)
- Approve requests
- View all requests
- Assign requests
- Create/update own requests

**Employee** (Level 1)
- Create requests
- View own requests
- Update own requests
- Delete own requests

## 🐳 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Deployment

1. **Set up PostgreSQL database**
2. **Configure production environment variables**
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Initialize database**: `python app.py`
5. **Use production WSGI server** (Gunicorn):

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Production Checklist

- [ ] Use strong `SECRET_KEY`
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HTTPS/SSL
- [ ] Configure proper CORS if needed
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Use environment-specific configs
- [ ] Set up Google OAuth2 credentials (if using)
- [ ] Configure email service
- [ ] Review and adjust permissions

## 🧪 Testing

### Run Unit Tests

```bash
python -m pytest tests/

# With coverage
python -m pytest tests/ --cov=.
```

### Manual API Testing

Use the included Postman collection or test with curl:

```bash
# Health check
curl http://localhost:5000/health

# Register user
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"Test123456"}'
```

## 🎯 Key Features Showcase

### 1. Multi-Level Approval Workflow

Requests can require multiple approval levels, automatically routing to appropriate approvers:

```python
request = {
    'title': 'Capital Equipment Purchase',
    'amount': 50000.00,
    'required_approval_levels': 3  # Department Manager → Director → CFO
}
```

### 2. Comprehensive Audit Trail

Every action is logged with full context:
- Who performed the action
- What changed (before/after values)
- When it happened
- Where (IP address, endpoint)
- Why (success/failure)

### 3. Fine-Grained RBAC

Permissions are resource-action based:
- `create_request`, `read_request`, `update_request`, `delete_request`
- `approve_request`, `assign_request`
- `manage_users`, `manage_roles`
- `view_audit_logs`

### 4. Google Workspace Integration

- OAuth2 authentication
- Send emails via Gmail API
- Create calendar events for approvals
- Store attachments in Google Drive

## 📈 Future Enhancements

- [ ] Web frontend (React/Vue)
- [ ] Advanced reporting and analytics
- [ ] Webhook notifications
- [ ] Request templates
- [ ] File attachment support
- [ ] Mobile app (React Native)
- [ ] Real-time notifications (WebSockets)
- [ ] Advanced search and filtering
- [ ] Export to PDF/Excel
- [ ] Integration with other services (Slack, Teams, etc.)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**[Your Name]**
- GitHub: [@your-github-username](https://github.com/your-github-username)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/your-profile)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

If you have any questions or need help, please open an issue or contact me directly.

---

⭐ **If you find this project useful, please consider giving it a star!** ⭐
