from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Optional, Dict, List
import os

class GoogleWorkspaceService:
    """Service for integrating with Google Workspace APIs"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    def __init__(self, credentials_file: str = 'credentials.json'):
        """
        Initialize Google Workspace Service
        
        Args:
            credentials_file: Path to OAuth2 credentials file
        """
        self.credentials_file = credentials_file
    
    def get_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> str:
        """
        Get OAuth2 authorization URL
        
        Args:
            redirect_uri: Redirect URI after authorization
            state: Optional state parameter for security
        
        Returns:
            str: Authorization URL
        """
        flow = Flow.from_client_secrets_file(
            self.credentials_file,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        
        if state:
            flow.state = state
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return authorization_url
    
    def exchange_code_for_tokens(self, code: str, redirect_uri: str) -> Dict:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            code: Authorization code
            redirect_uri: Redirect URI used in authorization
        
        Returns:
            dict: Token information
        """
        flow = Flow.from_client_secrets_file(
            self.credentials_file,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
    
    def refresh_credentials(self, refresh_token: str, client_id: str, 
                          client_secret: str) -> Credentials:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
        
        Returns:
            Credentials: Refreshed credentials
        """
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret
        )
        
        credentials.refresh(GoogleRequest())
        return credentials
    
    def send_email(self, credentials: Credentials, to: str, subject: str, 
                   body: str, html: bool = False) -> Dict:
        """
        Send email using Gmail API
        
        Args:
            credentials: Google OAuth2 credentials
            to: Recipient email address
            subject: Email subject
            body: Email body
            html: Whether body is HTML
        
        Returns:
            dict: Send result
        """
        try:
            service = build('gmail', 'v1', credentials=credentials)
            
            import base64
            from email.mime.text import MIMEText
            
            message = MIMEText(body, 'html' if html else 'plain')
            message['to'] = to
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            result = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {'success': True, 'message_id': result['id']}
        
        except HttpError as error:
            return {'success': False, 'error': str(error)}
    
    def create_calendar_event(self, credentials: Credentials, summary: str,
                             start_time: str, end_time: str, 
                             attendees: Optional[List[str]] = None,
                             description: Optional[str] = None) -> Dict:
        """
        Create a calendar event
        
        Args:
            credentials: Google OAuth2 credentials
            summary: Event title
            start_time: Start time (ISO format)
            end_time: End time (ISO format)
            attendees: List of attendee emails
            description: Event description
        
        Returns:
            dict: Creation result
        """
        try:
            service = build('calendar', 'v3', credentials=credentials)
            
            event = {
                'summary': summary,
                'description': description or '',
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
            }
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            result = service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'
            ).execute()
            
            return {
                'success': True,
                'event_id': result['id'],
                'html_link': result.get('htmlLink')
            }
        
        except HttpError as error:
            return {'success': False, 'error': str(error)}
    
    def get_user_info(self, credentials: Credentials) -> Dict:
        """
        Get user profile information
        
        Args:
            credentials: Google OAuth2 credentials
        
        Returns:
            dict: User information
        """
        try:
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            
            return {
                'success': True,
                'google_id': user_info.get('id'),
                'email': user_info.get('email'),
                'verified_email': user_info.get('verified_email'),
                'name': user_info.get('name'),
                'given_name': user_info.get('given_name'),
                'family_name': user_info.get('family_name'),
                'picture': user_info.get('picture')
            }
        
        except HttpError as error:
            return {'success': False, 'error': str(error)}
    
    def upload_to_drive(self, credentials: Credentials, file_name: str,
                       file_path: str, mime_type: str = 'application/octet-stream',
                       folder_id: Optional[str] = None) -> Dict:
        """
        Upload a file to Google Drive
        
        Args:
            credentials: Google OAuth2 credentials
            file_name: Name for the file in Drive
            file_path: Local path to the file
            mime_type: MIME type of the file
            folder_id: Optional parent folder ID
        
        Returns:
            dict: Upload result
        """
        try:
            from googleapiclient.http import MediaFileUpload
            
            service = build('drive', 'v3', credentials=credentials)
            
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            media = MediaFileUpload(file_path, mimetype=mime_type)
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            return {
                'success': True,
                'file_id': file.get('id'),
                'web_link': file.get('webViewLink')
            }
        
        except HttpError as error:
            return {'success': False, 'error': str(error)}
