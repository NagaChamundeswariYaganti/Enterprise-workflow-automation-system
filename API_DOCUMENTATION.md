# API Documentation

## Base URL
```
http://localhost:5000
```

## Authentication

All authenticated endpoints require a valid session cookie obtained through the login endpoint.

## Response Format

### Success Response
```json
{
  "message": "Success message",
  "data": { }
}
```

### Error Response
```json
{
  "error": "Error message",
  "details": [ ]  // Optional validation errors
}
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error |

---

## Authentication Endpoints

### Register User
Register a new user account.

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "department": "Engineering",
  "phone_number": "+1234567890"
}
```

**Validation Rules:**
- `username`: 3-80 characters, alphanumeric with underscores/hyphens
- `email`: Valid email format
- `password`: Minimum 8 characters, must contain uppercase, lowercase, and digit
- `first_name`, `last_name`: Optional, max 50 characters
- `department`: Optional, max 100 characters
- `phone_number`: Optional, max 20 characters

**Response:** `201 Created`
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "department": "Engineering",
    "is_active": true,
    "roles": [],
    "created_at": "2025-12-23T10:00:00"
  }
}
```

### Login
Authenticate and create a session.

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "roles": ["employee"]
  }
}
```

**Session Cookie:** Set in response headers

### Logout
End current session.

**Endpoint:** `POST /auth/logout`

**Auth Required:** Yes

**Response:** `200 OK`
```json
{
  "message": "Logout successful"
}
```

### Get Profile
Get current user profile.

**Endpoint:** `GET /auth/profile`

**Auth Required:** Yes

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "department": "Engineering",
  "roles": ["employee", "manager"],
  "created_at": "2025-12-23T10:00:00",
  "last_login": "2025-12-23T14:30:00"
}
```

### Update Profile
Update current user profile.

**Endpoint:** `PUT /auth/profile`

**Auth Required:** Yes

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "department": "Product",
  "phone_number": "+1234567890"
}
```

**Response:** `200 OK`
```json
{
  "message": "Profile updated successfully",
  "user": { /* updated user object */ }
}
```

### Change Password
Change user password.

**Endpoint:** `POST /auth/change-password`

**Auth Required:** Yes

**Request Body:**
```json
{
  "current_password": "OldPassword123",
  "new_password": "NewPassword456"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password changed successfully"
}
```

---

## Request Management Endpoints

### Create Request
Create a new workflow request.

**Endpoint:** `POST /requests`

**Auth Required:** Yes

**Permission Required:** `create_request`

**Request Body:**
```json
{
  "title": "Purchase Office Supplies",
  "description": "Need keyboards, mice, and monitors",
  "request_type": "purchase",
  "priority": "medium",
  "amount": 1500.00,
  "currency": "USD",
  "required_approval_levels": 2,
  "metadata": {
    "department": "Engineering",
    "budget_code": "ENG-2025-Q4"
  },
  "attachments": ["quote.pdf", "specifications.doc"],
  "due_date": "2025-12-31T23:59:59"
}
```

**Request Types:** `purchase`, `access`, `leave`, `expense`, `travel`, `other`

**Priority Levels:** `low`, `medium`, `high`, `urgent`

**Response:** `201 Created`
```json
{
  "message": "Request created successfully",
  "request": {
    "id": 1,
    "title": "Purchase Office Supplies",
    "request_type": "purchase",
    "status": "pending",
    "priority": "medium",
    "amount": 1500.00,
    "currency": "USD",
    "current_approval_level": 0,
    "required_approval_levels": 2,
    "requester": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com"
    },
    "created_at": "2025-12-23T15:00:00"
  }
}
```

### List Requests
Get list of requests.

**Endpoint:** `GET /requests?status=pending`

**Auth Required:** Yes

**Permission Required:** `read_request`

**Query Parameters:**
- `status` (optional): Filter by status (`pending`, `in_progress`, `approved`, `rejected`, `completed`, `cancelled`)

**Response:** `200 OK`
```json
{
  "requests": [
    {
      "id": 1,
      "title": "Purchase Office Supplies",
      "status": "pending",
      "priority": "medium",
      "created_at": "2025-12-23T15:00:00"
    }
  ],
  "count": 1
}
```

### Get Request Details
Get detailed information about a specific request.

**Endpoint:** `GET /requests/{id}`

**Auth Required:** Yes

**Permission Required:** `read_request`

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Purchase Office Supplies",
  "description": "Need keyboards, mice, and monitors",
  "request_type": "purchase",
  "status": "pending",
  "priority": "medium",
  "amount": 1500.00,
  "currency": "USD",
  "current_approval_level": 0,
  "required_approval_levels": 2,
  "requester": { /* user object */ },
  "assigned_to": { /* user object or null */ },
  "metadata": { /* custom metadata */ },
  "attachments": ["quote.pdf"],
  "created_at": "2025-12-23T15:00:00",
  "updated_at": "2025-12-23T15:00:00",
  "due_date": "2025-12-31T23:59:59"
}
```

### Update Request
Update an existing request.

**Endpoint:** `PUT /requests/{id}`

**Auth Required:** Yes

**Permission Required:** `update_request` (own) or `update_any_request` (any)

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "priority": "high",
  "due_date": "2026-01-15T23:59:59"
}
```

**Response:** `200 OK`
```json
{
  "message": "Request updated successfully",
  "request": { /* updated request object */ }
}
```

### Cancel Request
Cancel a request.

**Endpoint:** `DELETE /requests/{id}?reason=No+longer+needed`

**Auth Required:** Yes

**Permission Required:** Own requester or `cancel_any_request`

**Query Parameters:**
- `reason` (optional): Cancellation reason

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Request cancelled successfully"
}
```

### Get Approval History
Get approval history for a request.

**Endpoint:** `GET /requests/{id}/history`

**Auth Required:** Yes

**Response:** `200 OK`
```json
{
  "request_id": 1,
  "history": [
    {
      "id": 1,
      "approver": {
        "id": 2,
        "username": "manager1",
        "email": "manager1@example.com"
      },
      "action": "approve",
      "approval_level": 0,
      "comments": "Approved - budget available",
      "created_at": "2025-12-23T16:00:00"
    }
  ]
}
```

### Assign Request
Assign a request to a user.

**Endpoint:** `POST /requests/{id}/assign`

**Auth Required:** Yes

**Permission Required:** `assign_request`

**Request Body:**
```json
{
  "assignee_id": 3
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Request assigned successfully"
}
```

---

## Approval Endpoints

### Get Pending Approvals
Get all requests pending approval by current user.

**Endpoint:** `GET /approvals/pending`

**Auth Required:** Yes

**Permission Required:** `approve_request`

**Response:** `200 OK`
```json
{
  "pending_approvals": [
    {
      "id": 1,
      "title": "Purchase Office Supplies",
      "requester": { /* user object */ },
      "amount": 1500.00,
      "priority": "medium",
      "created_at": "2025-12-23T15:00:00"
    }
  ],
  "count": 1
}
```

### Process Approval
Process an approval action.

**Endpoint:** `POST /approvals/{request_id}/process`

**Auth Required:** Yes

**Permission Required:** `approve_request`

**Request Body:**
```json
{
  "action": "approve",
  "comments": "Approved - within budget"
}
```

**Actions:** `approve`, `reject`, `request_more_info`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Approval level 1 completed",
  "request_status": "in_progress",
  "current_level": 1
}
```

### Approve Request
Convenience endpoint to approve a request.

**Endpoint:** `POST /approvals/{request_id}/approve`

**Auth Required:** Yes

**Permission Required:** `approve_request`

**Request Body:**
```json
{
  "comments": "Approved"
}
```

**Response:** `200 OK`

### Reject Request
Convenience endpoint to reject a request.

**Endpoint:** `POST /approvals/{request_id}/reject`

**Auth Required:** Yes

**Permission Required:** `approve_request`

**Request Body:**
```json
{
  "comments": "Budget not available"
}
```

**Response:** `200 OK`

### Request More Information
Request additional information from requester.

**Endpoint:** `POST /approvals/{request_id}/request-info`

**Auth Required:** Yes

**Permission Required:** `approve_request`

**Request Body:**
```json
{
  "comments": "Please provide detailed specifications"
}
```

**Response:** `200 OK`

---

## Admin Endpoints

All admin endpoints require the `admin` role.

### List Users
Get all users in the system.

**Endpoint:** `GET /admin/users`

**Auth Required:** Yes

**Role Required:** `admin`

**Response:** `200 OK`
```json
{
  "users": [ /* array of user objects */ ],
  "count": 10
}
```

### Create User (Admin)
Create a new user as admin.

**Endpoint:** `POST /admin/users`

**Auth Required:** Yes

**Role Required:** `admin`

**Request Body:** Same as `/auth/register`

**Response:** `201 Created`

### Update User
Update any user.

**Endpoint:** `PUT /admin/users/{id}`

**Auth Required:** Yes

**Role Required:** `admin`

**Request Body:**
```json
{
  "first_name": "Updated",
  "is_active": false
}
```

**Response:** `200 OK`

### Assign Role to User
Assign a role to a user.

**Endpoint:** `POST /admin/users/{user_id}/roles`

**Auth Required:** Yes

**Role Required:** `admin`

**Request Body:**
```json
{
  "role_id": 2
}
```

**Response:** `200 OK`
```json
{
  "message": "Role manager assigned to johndoe",
  "user": { /* updated user object */ }
}
```

### Remove Role from User
Remove a role from a user.

**Endpoint:** `DELETE /admin/users/{user_id}/roles/{role_id}`

**Auth Required:** Yes

**Role Required:** `admin`

**Response:** `200 OK`

### List Roles
Get all roles.

**Endpoint:** `GET /admin/roles`

**Auth Required:** Yes

**Role Required:** `admin`

**Response:** `200 OK`
```json
{
  "roles": [
    {
      "id": 1,
      "name": "admin",
      "description": "System administrator",
      "level": 10,
      "can_approve": true,
      "permissions": ["manage_users", "manage_roles", ...]
    }
  ],
  "count": 3
}
```

### Create Role
Create a new role.

**Endpoint:** `POST /admin/roles`

**Auth Required:** Yes

**Role Required:** `admin`

**Request Body:**
```json
{
  "name": "director",
  "description": "Department director",
  "level": 7,
  "can_approve": true,
  "approval_limit": 50000.00
}
```

**Response:** `201 Created`

### Assign Permission to Role
Assign a permission to a role.

**Endpoint:** `POST /admin/roles/{role_id}/permissions`

**Auth Required:** Yes

**Role Required:** `admin`

**Request Body:**
```json
{
  "permission_id": 5
}
```

**Response:** `200 OK`

### List Permissions
Get all permissions.

**Endpoint:** `GET /admin/permissions`

**Auth Required:** Yes

**Role Required:** `admin`

**Response:** `200 OK`
```json
{
  "permissions": [
    {
      "id": 1,
      "name": "create_request",
      "description": "Create a new request",
      "resource": "request",
      "action": "create"
    }
  ],
  "count": 12
}
```

### Create Permission
Create a new permission.

**Endpoint:** `POST /admin/permissions`

**Auth Required:** Yes

**Role Required:** `admin`

**Request Body:**
```json
{
  "name": "export_reports",
  "description": "Export system reports",
  "resource": "report",
  "action": "read"
}
```

**Response:** `201 Created`

### Get Audit Logs
View system audit logs.

**Endpoint:** `GET /admin/audit-logs?user_id=1&action=login&limit=50`

**Auth Required:** Yes

**Role Required:** `admin`

**Query Parameters:**
- `user_id` (optional): Filter by user
- `action` (optional): Filter by action
- `resource_type` (optional): Filter by resource type
- `limit` (optional): Max results (default: 100)

**Response:** `200 OK`
```json
{
  "audit_logs": [
    {
      "id": 1,
      "user": { /* user object */ },
      "action": "login",
      "resource_type": "user",
      "resource_id": 1,
      "ip_address": "192.168.1.100",
      "endpoint": "/auth/login",
      "method": "POST",
      "success": true,
      "created_at": "2025-12-23T14:30:00"
    }
  ],
  "count": 1
}
```

---

## Webhooks (Future)

Coming soon: Webhook notifications for request events.

## Rate Limiting (Future)

Coming soon: API rate limiting configuration.
