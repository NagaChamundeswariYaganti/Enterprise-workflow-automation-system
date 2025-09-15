# Enterprise Workflow Automation & RBAC System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready workflow automation system with Role-Based Access Control (RBAC), multi-level approvals, Google Workspace integration, and comprehensive audit logging.

## Features

- **Request Management**: Create, update, track, and manage workflow requests
- **Multi-Level Approval**: Configurable approval workflows with multiple authorization levels
- **Role-Based Access Control**: Fine-grained permissions and role hierarchy
- **Audit Trail**: Complete system traceability with detailed logging
- **Notifications**: Email notifications for request updates and approvals
- **Google Workspace Integration**: OAuth2, Gmail, Calendar, and Drive APIs

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL (production) or SQLite (development)

### Setup

```bash
# Clone repository
git clone <your-repo-url>
cd workflow-automation

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python app.py
```

## Quick Start

```bash
# Start development server
python app.py

# API available at http://localhost:5000
```

### Create Admin User

```python
from app import create_app
from models.user import User, db
from models.role import Role

app = create_app()
with app.app_context():
    # Register user via API first, then:
    user = User.query.filter_by(username='admin').first()
    admin_role = Role.query.filter_by(name='admin').first()
    user.roles.append(admin_role)
    db.session.commit()
```

## API Documentation

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | User login | No |
| POST | `/auth/logout` | User logout | Yes |
| GET | `/auth/profile` | Get current user | Yes |
| PUT | `/auth/profile` | Update profile | Yes |
| POST | `/auth/change-password` | Change password | Yes |

### Requests

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| POST | `/requests` | Create request | `create_request` |
| GET | `/requests` | List requests | `read_request` |
| GET | `/requests/<id>` | Get request details | `read_request` |
| PUT | `/requests/<id>` | Update request | `update_request` |
| DELETE | `/requests/<id>` | Cancel request | `delete_request` |
| GET | `/requests/<id>/history` | Get approval history | `read_request` |

### Approvals

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/approvals/pending` | Get pending approvals | `approve_request` |
| POST | `/approvals/<id>/approve` | Approve request | `approve_request` |
| POST | `/approvals/<id>/reject` | Reject request | `approve_request` |

### Admin

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | `/admin/users` | List all users | Admin |
| POST | `/admin/users` | Create user | Admin |
| PUT | `/admin/users/<id>` | Update user | Admin |
| POST | `/admin/users/<id>/roles` | Assign role | Admin |
| GET | `/admin/roles` | List all roles | Admin |
| GET | `/admin/audit-logs` | View audit logs | Admin |

## Usage Examples

### Create Request

```python
import requests

# Login
response = requests.post('http://localhost:5000/auth/login', json={
    'username': 'user',
    'password': 'password'
})

# Create request
response = requests.post('http://localhost:5000/requests', json={
    'title': 'Purchase Request',
    'description': 'Need office supplies',
    'request_type': 'purchase',
    'priority': 'medium',
    'amount': 500.00,
    'required_approval_levels': 2
}, cookies=response.cookies)
```

### Approve Request

```python
response = requests.post('http://localhost:5000/approvals/1/approve', json={
    'comments': 'Approved'
}, cookies=login_response.cookies)
```

## Configuration

Create `.env` file:

```env
DATABASE_URL=sqlite:///workflow.db
SECRET_KEY=your-secret-key
FLASK_ENV=development

# Google Workspace (Optional)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# Email (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-password
```

## Deployment

### Docker

```bash
docker-compose up -d
```

### Production

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Testing

```bash
pytest tests/
```

## Architecture

```
┌─────────────────┐
│   API Routes    │
└────────┬────────┘
         │
┌────────▼────────┐
│   Services      │
└────────┬────────┘
         │
┌────────▼────────┐
│   Models        │
└────────┬────────┘
         │
┌────────▼────────┐
│   Database      │
└─────────────────┘
```

## Project Structure

```
Automation/
├── models/              # Database models
├── services/           # Business logic
├── routes/             # API endpoints
├── rbac/               # Access control
├── validation/         # Input validation
├── tests/              # Unit tests
├── app.py              # Application entry point
├── config.py           # Configuration
└── requirements.txt    # Dependencies
```

## License

MIT License - see LICENSE file

## Contributing

See CONTRIBUTING.md
