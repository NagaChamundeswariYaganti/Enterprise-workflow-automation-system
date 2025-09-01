# Setup Instructions

Follow these steps to get the Enterprise Workflow Automation system running on your local machine.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Database Setup](#database-setup)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Initial Setup](#initial-setup)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
- **pip**: Python package installer (included with Python)
- **Git**: [Download Git](https://git-scm.com/downloads)
- **PostgreSQL** (for production) or **SQLite** (for development)

### Optional
- **Docker & Docker Compose**: For containerized deployment
- **Postman**: For API testing

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/workflow-automation.git
cd workflow-automation
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages:
- Flask (web framework)
- SQLAlchemy (ORM)
- Flask-Login (authentication)
- Pydantic (validation)
- Google API libraries
- And more...

## Database Setup

### Option 1: SQLite (Development)

SQLite is used by default and requires no setup. The database file will be created automatically.

### Option 2: PostgreSQL (Production)

**Install PostgreSQL:**

**Windows:**
- Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- Run installer and follow prompts

**Linux:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**Mac:**
```bash
brew install postgresql
brew services start postgresql
```

**Create Database:**
```bash
# Access PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE workflow_db;
CREATE USER workflow_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE workflow_db TO workflow_user;
\q
```

## Configuration

### 1. Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### 2. Edit `.env` File

**Windows:** Use Notepad or any text editor
**Linux/Mac:** Use nano, vim, or any text editor

```bash
notepad .env  # Windows
nano .env     # Linux/Mac
```

### 3. Configure Environment Variables

**Minimum Configuration (Development):**
```env
# Flask
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development

# Database (SQLite - default)
DATABASE_URL=sqlite:///workflow.db
```

**Full Configuration (Production):**
```env
# Flask
SECRET_KEY=generate-a-secure-random-string-here
FLASK_ENV=production

# Database (PostgreSQL)
DATABASE_URL=postgresql://workflow_user:your_password@localhost:5432/workflow_db

# Google Workspace (Optional)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/oauth2callback
GOOGLE_CREDENTIALS_FILE=credentials.json

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Application Settings
ADMIN_EMAIL=admin@example.com
MAX_APPROVAL_LEVELS=5
SESSION_TIMEOUT=3600
```

### Generate Secure Secret Key

**Python:**
```python
import secrets
print(secrets.token_hex(32))
```

**Or use online generator:** [randomkeygen.com](https://randomkeygen.com/)

## Running the Application

### 1. Initialize Database

```bash
python app.py
```

This will:
- Create all database tables
- Create default roles (admin, manager, employee)
- Create default permissions
- Display initialization summary

You should see:
```
Database initialized successfully!
Permissions created: 12
Roles created: 3
```

### 2. Start the Server

The server starts automatically. You should see:
```
* Running on http://0.0.0.0:5000
* Debugger is active!
```

### 3. Verify Installation

Open your browser or use curl:
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{"status": "healthy"}
```

## Initial Setup

### 1. Create Admin User

**Method 1: Register via API**
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "AdminPass123",
    "first_name": "System",
    "last_name": "Administrator"
  }'
```

**Method 2: Python Shell**
```python
from app import create_app
from models.user import User, db

app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@example.com',
        first_name='System',
        last_name='Administrator'
    )
    admin.set_password('AdminPass123')
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user created with ID: {admin.id}")
```

### 2. Assign Admin Role

```python
from app import create_app
from models.user import User, db
from models.role import Role

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    admin_role = Role.query.filter_by(name='admin').first()
    
    if user and admin_role:
        user.roles.append(admin_role)
        db.session.commit()
        print("Admin role assigned successfully!")
```

### 3. Test Login

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "AdminPass123"
  }'
```

## Testing

### Run Unit Tests

```bash
# Install pytest (if not already installed)
pip install pytest pytest-cov

# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

### Manual API Testing

Use Postman or curl to test endpoints. See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for details.

## Troubleshooting

### Common Issues

#### 1. Module Not Found Error
```
ModuleNotFoundError: No module named 'flask'
```
**Solution:** Ensure virtual environment is activated and dependencies are installed
```bash
# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. Database Connection Error
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```
**Solution:** Check PostgreSQL is running and credentials are correct
```bash
# Check PostgreSQL status
# Windows: Check Services
# Linux: sudo systemctl status postgresql
# Mac: brew services list

# Verify credentials in .env file
DATABASE_URL=postgresql://workflow_user:your_password@localhost:5432/workflow_db
```

#### 3. Port Already in Use
```
OSError: [Errno 98] Address already in use
```
**Solution:** Kill process using port 5000 or use different port
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9

# Or change port in app.py
app.run(port=5001)
```

#### 4. Permission Denied
```
PermissionError: [Errno 13] Permission denied
```
**Solution:** Run with appropriate permissions or change file permissions
```bash
# Linux/Mac
chmod +x app.py
sudo python app.py  # Not recommended

# Better: Fix file permissions
chmod -R 755 /path/to/project
```

#### 5. Google OAuth Errors
```
google.auth.exceptions.RefreshError
```
**Solution:** 
- Verify `credentials.json` exists
- Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in `.env`
- Ensure redirect URI matches Google Console configuration

### Getting Help

1. Check [GitHub Issues](https://github.com/yourusername/workflow-automation/issues)
2. Review [API Documentation](API_DOCUMENTATION.md)
3. Check logs in console output
4. Enable debug mode: `FLASK_ENV=development` in `.env`

### Debug Mode

Enable detailed error messages:

```python
# In app.py
app.run(debug=True)
```

### Logging

View application logs:

```bash
# Console output shows all logs in development
# For production, configure logging:

import logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)
```

## Docker Deployment (Alternative)

If you prefer Docker:

### 1. Build and Run

```bash
docker-compose up -d
```

### 2. Check Status

```bash
docker-compose ps
```

### 3. View Logs

```bash
docker-compose logs -f
```

### 4. Stop Services

```bash
docker-compose down
```

## Next Steps

Once everything is running:

1. ✅ Read [README.md](README.md) for feature overview
2. ✅ Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
3. ✅ Review [PROJECT_GUIDE.md](PROJECT_GUIDE.md) for architecture
4. ✅ Create test users and requests
5. ✅ Explore the API endpoints
6. ✅ Customize for your needs

## Production Deployment

For production deployment:

1. Set `FLASK_ENV=production` in `.env`
2. Use PostgreSQL (not SQLite)
3. Generate strong `SECRET_KEY`
4. Use WSGI server (Gunicorn/uWSGI)
5. Set up HTTPS/SSL
6. Configure reverse proxy (Nginx/Apache)
7. Set up monitoring and logging
8. Regular database backups
9. Environment-specific configuration

See [README.md#deployment](README.md#deployment) for detailed production setup.

---

**Congratulations! Your Enterprise Workflow Automation System is ready to use!** 🎉
