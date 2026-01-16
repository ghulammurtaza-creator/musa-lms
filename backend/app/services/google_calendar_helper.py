"""
Google Calendar API service - refactored for per-teacher credentials
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import Dict, Optional
import json


def create_calendar_service(teacher_credentials_json: str):
    """
    Create a Google Calendar service instance for a specific teacher
    
    Args:
        teacher_credentials_json: JSON string containing OAuth credentials
    
    Returns:
        Google Calendar service instance
    """
    creds_dict = json.loads(teacher_credentials_json)
    credentials = Credentials(
        token=creds_dict.get('token'),
        refresh_token=creds_dict.get('refresh_token'),
        token_uri=creds_dict.get('token_uri'),
        client_id=creds_dict.get('client_id'),
        client_secret=creds_dict.get('client_secret'),
        scopes=creds_dict.get('scopes')
    )
    
    return build('calendar', 'v3', credentials=credentials)


def create_class_event(
    teacher_credentials_json: str,
    teacher_email: str,
    student_emails: list,
    subject: str,
    start_time: datetime,
    duration_minutes: int,
    description: str = ""
) -> Dict:
    """
    Create a Google Calendar event with Google Meet link
    
    Args:
        teacher_credentials_json: Teacher's OAuth credentials
        teacher_email: Teacher's email address
        student_emails: List of student email addresses
        subject: Class subject/title
        start_time: Class start time
        duration_minutes: Duration in minutes
        description: Optional description
    
    Returns:
        Dict containing event_id, meet_link, meet_code, and end_time
    """
    service = create_calendar_service(teacher_credentials_json)
    
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    # Create event with Google Meet
    event = {
        'summary': f'{subject} - Online Class',
        'description': description or f'Online tutoring session for {subject}',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'UTC',
        },
        'attendees': [{'email': email} for email in student_emails],
        'conferenceData': {
            'createRequest': {
                'requestId': f'meet-{start_time.timestamp()}',
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                {'method': 'popup', 'minutes': 30},  # 30 minutes before
            ],
        },
    }
    
    created_event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1,
        sendUpdates='all'  # Send email to attendees
    ).execute()
    
    # Extract Google Meet link
    meet_link = created_event.get('hangoutLink', '')
    meet_code = meet_link.split('/')[-1] if meet_link else ''
    
    return {
        'event_id': created_event['id'],
        'meet_link': meet_link,
        'meet_code': meet_code,
        'end_time': end_time.isoformat()
    }


def update_class_event(
    teacher_credentials_json: str,
    event_id: str,
    subject: Optional[str] = None,
    start_time: Optional[datetime] = None,
    duration_minutes: Optional[int] = None,
    student_emails: Optional[list] = None,
    description: Optional[str] = None
) -> Dict:
    """
    Update an existing calendar event
    
    Args:
        teacher_credentials_json: Teacher's OAuth credentials
        event_id: Google Calendar event ID
        subject: New subject (optional)
        start_time: New start time (optional)
        duration_minutes: New duration (optional)
        student_emails: New attendees list (optional)
        description: New description (optional)
    
    Returns:
        Updated event data
    """
    service = create_calendar_service(teacher_credentials_json)
    
    # Get existing event
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    
    # Update fields if provided
    if subject:
        event['summary'] = f'{subject} - Online Class'
    
    if description is not None:
        event['description'] = description
    
    if start_time and duration_minutes:
        end_time = start_time + timedelta(minutes=duration_minutes)
        event['start'] = {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC',
        }
        event['end'] = {
            'dateTime': end_time.isoformat(),
            'timeZone': 'UTC',
        }
    
    if student_emails:
        event['attendees'] = [{'email': email} for email in student_emails]
    
    updated_event = service.events().update(
        calendarId='primary',
        eventId=event_id,
        body=event,
        sendUpdates='all'
    ).execute()
    
    return {
        'event_id': updated_event['id'],
        'meet_link': updated_event.get('hangoutLink', ''),
        'message': 'Event updated successfully'
    }


def cancel_class_event(teacher_credentials_json: str, event_id: str):
    """
    Cancel/delete a calendar event
    
    Args:
        teacher_credentials_json: Teacher's OAuth credentials
        event_id: Google Calendar event ID
    """
    service = create_calendar_service(teacher_credentials_json)
    
    service.events().delete(
        calendarId='primary',
        eventId=event_id,
        sendUpdates='all'  # Notify attendees
    ).execute()
    
    return {'message': 'Event cancelled successfully'}
