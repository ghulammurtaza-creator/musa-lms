"""
Google Calendar API integration service for scheduling classes with Google Meet
"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import json
import uuid


# Scopes required for Calendar API
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]


class GoogleCalendarService:
    """Service for managing Google Calendar events with Meet integration"""
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        """
        Initialize the Google Calendar service
        
        Args:
            credentials_path: Path to OAuth2 credentials JSON file
            token_path: Path to store/retrieve OAuth2 token
        """
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
        self.token_path = token_path or os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
        self.creds = None
        self.service = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API
        
        Returns:
            bool: True if authentication successful
        """
        # Load existing token if available
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # If no valid credentials, let user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found at {self.credentials_path}. "
                        "Please download OAuth2 credentials from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=self.creds)
        return True
    
    def create_class_event(
        self,
        teacher_email: str,
        student_emails: List[str],
        subject: str,
        start_time: datetime,
        duration_minutes: int,
        description: str = ""
    ) -> Dict:
        """
        Create a Google Calendar event with Google Meet link
        
        Args:
            teacher_email: Email of the teacher
            student_emails: List of student emails
            subject: Subject/title of the class
            start_time: When the class starts
            duration_minutes: Duration in minutes
            description: Optional description
        
        Returns:
            Dict containing event details including meet_link and event_id
        """
        if not self.service:
            self.authenticate()
        
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Create event with Google Meet conference
        event = {
            'summary': f'{subject} Class',
            'description': description or f'Online class for {subject}',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': [
                {'email': teacher_email},
                *[{'email': email} for email in student_emails]
            ],
            'conferenceData': {
                'createRequest': {
                    'requestId': str(uuid.uuid4()),
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 10},  # 10 minutes before
                ],
            },
        }
        
        try:
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'  # Send email notifications to all attendees
            ).execute()
            
            # Extract Meet details
            conference_data = created_event.get('conferenceData', {})
            meet_link = conference_data.get('entryPoints', [{}])[0].get('uri', '')
            meet_code = conference_data.get('conferenceId', '')
            
            return {
                'event_id': created_event['id'],
                'meet_link': meet_link,
                'meet_code': meet_code,
                'html_link': created_event.get('htmlLink', ''),
                'status': created_event.get('status', ''),
                'start_time': created_event['start']['dateTime'],
                'end_time': created_event['end']['dateTime']
            }
        
        except HttpError as error:
            raise Exception(f'Error creating calendar event: {error}')
    
    def update_class_event(
        self,
        event_id: str,
        start_time: Optional[datetime] = None,
        duration_minutes: Optional[int] = None,
        student_emails: Optional[List[str]] = None
    ) -> Dict:
        """
        Update an existing calendar event
        
        Args:
            event_id: Google Calendar event ID
            start_time: New start time (optional)
            duration_minutes: New duration (optional)
            student_emails: New list of students (optional)
        
        Returns:
            Dict with updated event details
        """
        if not self.service:
            self.authenticate()
        
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update fields if provided
            if start_time:
                end_time = start_time + timedelta(minutes=duration_minutes or 60)
                event['start']['dateTime'] = start_time.isoformat()
                event['end']['dateTime'] = end_time.isoformat()
            
            if student_emails is not None:
                # Preserve teacher, update students
                teacher = [a for a in event['attendees'] if 'organizer' in a or 'teacher' in a.get('email', '').lower()]
                event['attendees'] = teacher + [{'email': email} for email in student_emails]
            
            # Update event
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            return {
                'event_id': updated_event['id'],
                'status': 'updated',
                'html_link': updated_event.get('htmlLink', '')
            }
        
        except HttpError as error:
            raise Exception(f'Error updating calendar event: {error}')
    
    def cancel_class_event(self, event_id: str) -> bool:
        """
        Cancel/delete a calendar event
        
        Args:
            event_id: Google Calendar event ID
        
        Returns:
            bool: True if successful
        """
        if not self.service:
            self.authenticate()
        
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates='all'  # Notify all attendees
            ).execute()
            return True
        
        except HttpError as error:
            raise Exception(f'Error canceling calendar event: {error}')
    
    def get_upcoming_classes(self, max_results: int = 10) -> List[Dict]:
        """
        Get upcoming calendar events
        
        Args:
            max_results: Maximum number of events to return
        
        Returns:
            List of event dictionaries
        """
        if not self.service:
            self.authenticate()
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        
        except HttpError as error:
            raise Exception(f'Error fetching upcoming events: {error}')


# Singleton instance
_calendar_service = None


def get_calendar_service() -> GoogleCalendarService:
    """Get or create GoogleCalendarService singleton"""
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = GoogleCalendarService()
    return _calendar_service
