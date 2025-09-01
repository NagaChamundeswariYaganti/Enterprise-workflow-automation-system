import unittest
from app import create_app, init_db
from models.user import db, User
from models.role import Role, Permission
from models.request import Request
import json

class WorkflowTestCase(unittest.TestCase):
    """Test cases for workflow automation system"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create all tables
        db.create_all()
        
        # Create test permission
        self.permission = Permission(
            name='create_request',
            description='Create requests',
            resource='request',
            action='create'
        )
        db.session.add(self.permission)
        
        # Create test role
        self.role = Role(
            name='employee',
            description='Test role',
            level=1
        )
        db.session.add(self.role)
        self.role.permissions.append(self.permission)
        
        # Create test user
        self.user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.user.set_password('TestPassword123')
        self.user.roles.append(self.role)
        db.session.add(self.user)
        
        db.session.commit()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def login(self, username='testuser', password='TestPassword123'):
        """Helper method to login"""
        return self.client.post('/auth/login',
                               data=json.dumps({
                                   'username': username,
                                   'password': password
                               }),
                               content_type='application/json')
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post('/auth/register',
                                   data=json.dumps({
                                       'username': 'newuser',
                                       'email': 'newuser@example.com',
                                       'password': 'NewPassword123',
                                       'first_name': 'New',
                                       'last_name': 'User'
                                   }),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'newuser')
    
    def test_user_login(self):
        """Test user login"""
        response = self.login()
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Login successful')
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = self.login(username='testuser', password='wrongpassword')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertNotEqual(user.password_hash, 'TestPassword123')
        self.assertTrue(user.check_password('TestPassword123'))
    
    def test_user_has_role(self):
        """Test user role checking"""
        user = User.query.filter_by(username='testuser').first()
        self.assertTrue(user.has_role('employee'))
        self.assertFalse(user.has_role('admin'))
    
    def test_user_has_permission(self):
        """Test user permission checking"""
        user = User.query.filter_by(username='testuser').first()
        self.assertTrue(user.has_permission('create_request'))
        self.assertFalse(user.has_permission('manage_users'))

class RequestWorkflowTestCase(unittest.TestCase):
    """Test cases for request workflow"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create permissions
        create_perm = Permission(name='create_request', resource='request', action='create')
        approve_perm = Permission(name='approve_request', resource='request', action='approve')
        db.session.add_all([create_perm, approve_perm])
        
        # Create roles
        employee_role = Role(name='employee', level=1)
        manager_role = Role(name='manager', level=5, can_approve=True)
        employee_role.permissions.append(create_perm)
        manager_role.permissions.extend([create_perm, approve_perm])
        db.session.add_all([employee_role, manager_role])
        
        # Create users
        self.employee = User(username='employee', email='employee@example.com')
        self.employee.set_password('Password123')
        self.employee.roles.append(employee_role)
        
        self.manager = User(username='manager', email='manager@example.com')
        self.manager.set_password('Password123')
        self.manager.roles.append(manager_role)
        
        db.session.add_all([self.employee, self.manager])
        db.session.commit()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_request_creation(self):
        """Test creating a new request"""
        # Login as employee
        self.client.post('/auth/login',
                        data=json.dumps({
                            'username': 'employee',
                            'password': 'Password123'
                        }),
                        content_type='application/json')
        
        # Create request
        response = self.client.post('/requests',
                                   data=json.dumps({
                                       'title': 'Test Request',
                                       'description': 'Test description',
                                       'request_type': 'purchase',
                                       'priority': 'medium',
                                       'amount': 100.0
                                   }),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('request', data)
        self.assertEqual(data['request']['title'], 'Test Request')
        self.assertEqual(data['request']['status'], 'pending')
    
    def test_approval_workflow(self):
        """Test request approval workflow"""
        # Create request
        request = Request(
            title='Test Request',
            description='Test',
            request_type='purchase',
            requester_id=self.employee.id,
            status='pending',
            required_approval_levels=1
        )
        db.session.add(request)
        db.session.commit()
        request_id = request.id
        
        # Login as manager
        self.client.post('/auth/login',
                        data=json.dumps({
                            'username': 'manager',
                            'password': 'Password123'
                        }),
                        content_type='application/json')
        
        # Approve request
        response = self.client.post(f'/approvals/{request_id}/approve',
                                   data=json.dumps({
                                       'comments': 'Approved'
                                   }),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify request is approved
        request = Request.query.get(request_id)
        self.assertEqual(request.status, 'approved')

if __name__ == '__main__':
    unittest.main()
