"""
Google Meet REST API integration for retrieving actual participant data
Uses the official Google Meet API v2 for participant tracking
"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os


# Scope needed for Google Meet API
MEET_API_SCOPE = 'https://www.googleapis.com/auth/meetings.space.readonly'


class GoogleMeetService:
    """Service for fetching actual Google Meet participant data using Meet API v2"""
    
    def __init__(self, token_path: str = None):
        """
        Initialize the Google Meet service
        
        Args:
            token_path: Path to OAuth2 token with Meet API scope
        """
        self.token_path = token_path or os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
        self.creds = None
        self.service = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Meet API
        
        Returns:
            bool: True if authentication successful
        """
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, [MEET_API_SCOPE])
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                raise Exception(
                    "No valid credentials found. You need to re-authenticate with Meet API scope. "
                    "Run setup_google_oauth.py --meet flag"
                )
        
        self.service = build('meet', 'v2', credentials=self.creds)
        return True
    
    def get_meeting_participants(
        self,
        meet_code: str,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Retrieve actual participant join/leave data from Google Meet Reports
        
        Args:
            meet_code: The Google Meet conference code (e.g., 'abc-defg-hij')
            start_time: When the meeting started (to narrow search)
            end_time: When the meeting ended (optional)
        
        Returns:
            List of participant records with actual join/leave times
        """
        if not self.service:
            self.authenticate()
        
        # Calculate time range for API query
        start_str = start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        end_str = (end_time or datetime.utcnow()).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
        participants = []
        
        try:
            # Query Google Meet activity reports
            results = self.service.activities().list(
                userKey='all',
                applicationName='meet',
                startTime=start_str,
                endTime=end_str,
                maxResults=500
            ).execute()
            
            activities = results.get('items', [])
            
            for activity in activities:
                actor_email = activity.get('actor', {}).get('email')
                events = activity.get('events', [])
                
                for event in events:
                    event_name = event.get('name')
                    parameters = {p['name']: p['value'] for p in event.get('parameters', [])}
                    
                    # Check if this is our meeting
                    if parameters.get('meeting_code') == meet_code:
                        # Parse participant data based on event type
                        if event_name == 'call_ended':
                            # This gives us full session data
                            participants.append({
                                'email': actor_email,
                                'join_time': self._parse_meet_timestamp(parameters.get('start_time')),
                                'leave_time': self._parse_meet_timestamp(parameters.get('end_time')),
                                'duration_seconds': int(parameters.get('duration_seconds', 0)),
                                'device_type': parameters.get('device_type'),
                                'ip_address': parameters.get('ip_address'),
                                'location': parameters.get('location_country')
                            })
                        
                        elif event_name in ['call_joined', 'call_left']:
                            # Individual join/leave events
                            timestamp = activity.get('id', {}).get('time')
                            participants.append({
                                'email': actor_email,
                                'event': event_name,
                                'timestamp': self._parse_meet_timestamp(timestamp),
                                'meeting_code': meet_code
                            })
            
            return participants
        
        except Exception as e:
            print(f"Error fetching Meet reports: {e}")
            return []
    
    def get_meeting_summary(
        self,
        meet_code: str,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> Dict:
        """
        Get summary statistics for a meeting
        
        Returns:
            Dict with meeting stats (total participants, duration, etc.)
        """
        participants = self.get_meeting_participants(meet_code, start_time, end_time)
        
        if not participants:
            return {
                'meeting_code': meet_code,
                'total_participants': 0,
                'participants': []
            }
        
        # Group by email and aggregate sessions
        participant_sessions = {}
        for p in participants:
            email = p['email']
            if email not in participant_sessions:
                participant_sessions[email] = []
            
            if 'duration_seconds' in p:
                participant_sessions[email].append({
                    'join_time': p['join_time'],
                    'leave_time': p['leave_time'],
                    'duration_minutes': round(p['duration_seconds'] / 60, 2)
                })
        
        return {
            'meeting_code': meet_code,
            'total_participants': len(participant_sessions),
            'participants': [
                {
                    'email': email,
                    'total_sessions': len(sessions),
                    'total_duration_minutes': sum(s['duration_minutes'] for s in sessions),
                    'sessions': sessions
                }
                for email, sessions in participant_sessions.items()
            ]
        }
    
    def _parse_meet_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse Google Meet timestamp string to datetime"""
        if not timestamp_str:
            return None
        
        try:
            # Google Meet timestamps are in RFC3339 format
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except Exception:
            return None


# Global service instance
_reports_service = None


def get_reports_service() -> GoogleMeetReportsService:
    """Get or create GoogleMeetReportsService singleton"""
    global _reports_service
    if _reports_service is None:
        _reports_service = GoogleMeetReportsService()
    return _reports_service
