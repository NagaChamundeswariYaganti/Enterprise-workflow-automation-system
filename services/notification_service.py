import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from config import Config

class NotificationService:
    """Service for sending notifications via email"""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = None, 
                 username: str = None, password: str = None):
        """
        Initialize notification service
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
        """
        self.smtp_server = smtp_server or Config.SMTP_SERVER
        self.smtp_port = smtp_port or Config.SMTP_PORT
        self.username = username or Config.SMTP_USERNAME
        self.password = password or Config.SMTP_PASSWORD
    
    def send_email(self, to: List[str], subject: str, body: str, 
                   html: bool = False) -> dict:
        """
        Send email notification
        
        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body
            html: Whether body is HTML
        
        Returns:
            dict: Result of email send
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = ', '.join(to)
            
            # Attach body
            mime_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, mime_type))
            
            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return {'success': True, 'message': 'Email sent successfully'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def notify_request_created(self, request, approvers: List[str]) -> dict:
        """
        Notify approvers when a new request is created
        
        Args:
            request: Request object
            approvers: List of approver email addresses
        
        Returns:
            dict: Result of notification
        """
        subject = f"New Request: {request.title}"
        body = f"""
        <html>
        <body>
            <h2>New Request Requires Your Approval</h2>
            <p><strong>Title:</strong> {request.title}</p>
            <p><strong>Type:</strong> {request.request_type}</p>
            <p><strong>Priority:</strong> {request.priority}</p>
            <p><strong>Requester:</strong> {request.requester.get_full_name()}</p>
            <p><strong>Description:</strong> {request.description or 'N/A'}</p>
            <p>Please log in to the system to review and approve this request.</p>
        </body>
        </html>
        """
        
        return self.send_email(approvers, subject, body, html=True)
    
    def notify_request_approved(self, request, level: int) -> dict:
        """
        Notify requester when request is approved
        
        Args:
            request: Request object
            level: Approval level completed
        
        Returns:
            dict: Result of notification
        """
        subject = f"Request Approved: {request.title}"
        
        if request.status == 'approved':
            status_msg = "fully approved and completed"
        else:
            status_msg = f"approved at level {level}"
        
        body = f"""
        <html>
        <body>
            <h2>Your Request Has Been {status_msg.title()}</h2>
            <p><strong>Title:</strong> {request.title}</p>
            <p><strong>Status:</strong> {status_msg}</p>
            <p><strong>Current Level:</strong> {request.current_approval_level} of {request.required_approval_levels}</p>
            <p>You will be notified of any further updates.</p>
        </body>
        </html>
        """
        
        return self.send_email([request.requester.email], subject, body, html=True)
    
    def notify_request_rejected(self, request, comments: Optional[str] = None) -> dict:
        """
        Notify requester when request is rejected
        
        Args:
            request: Request object
            comments: Rejection comments
        
        Returns:
            dict: Result of notification
        """
        subject = f"Request Rejected: {request.title}"
        body = f"""
        <html>
        <body>
            <h2>Your Request Has Been Rejected</h2>
            <p><strong>Title:</strong> {request.title}</p>
            <p><strong>Type:</strong> {request.request_type}</p>
            {f'<p><strong>Comments:</strong> {comments}</p>' if comments else ''}
            <p>Please contact the approver for more information.</p>
        </body>
        </html>
        """
        
        return self.send_email([request.requester.email], subject, body, html=True)
    
    def notify_more_info_requested(self, request, comments: Optional[str] = None) -> dict:
        """
        Notify requester when more information is requested
        
        Args:
            request: Request object
            comments: Comments about what info is needed
        
        Returns:
            dict: Result of notification
        """
        subject = f"More Information Needed: {request.title}"
        body = f"""
        <html>
        <body>
            <h2>Additional Information Required</h2>
            <p><strong>Title:</strong> {request.title}</p>
            <p><strong>Type:</strong> {request.request_type}</p>
            {f'<p><strong>Comments:</strong> {comments}</p>' if comments else ''}
            <p>Please log in to the system to provide the requested information.</p>
        </body>
        </html>
        """
        
        return self.send_email([request.requester.email], subject, body, html=True)
