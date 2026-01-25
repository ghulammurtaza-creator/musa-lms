"""
Google Meet REST API v2 integration for retrieving actual participant data
Official API for Google Meet - provides real-time access to participant sessions
Documentation: https://developers.google.com/workspace/meet/api/guides/overview
"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build_from_document
from datetime import datetime
from typing import List, Dict, Optional
import os
import requests


# Scope needed for Google Meet API (read-only access to spaces)
MEET_API_SCOPE = 'https://www.googleapis.com/auth/meetings.space.readonly'
# Discovery document URL
MEET_API_DISCOVERY_URL = 'https://meet.googleapis.com/$discovery/rest?version=v2'


class GoogleMeetAPIService:
    """Service for fetching actual Google Meet participant data using Meet API v2"""
    
    def __init__(self, token_path: str = None, credentials_dict: dict = None):
        """
        Initialize the Google Meet API service
        
        Args:
            token_path: Path to OAuth2 token with Meet API scope (legacy, for fallback)
            credentials_dict: Dictionary with OAuth credentials from auth_users.google_credentials
        """
        self.token_path = token_path or os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
        self.credentials_dict = credentials_dict
        self.creds = None
        self.service = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Meet API v2 using discovery document
        
        Returns:
            bool: True if authentication successful
        """
        try:
            # Prefer credentials_dict (per-teacher) over token.json (global)
            if self.credentials_dict:
                import json
                # If it's a string, parse it as JSON
                if isinstance(self.credentials_dict, str):
                    self.credentials_dict = json.loads(self.credentials_dict)
                self.creds = Credentials.from_authorized_user_info(self.credentials_dict, [MEET_API_SCOPE])
            elif os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_file(self.token_path, [MEET_API_SCOPE])
            
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    raise Exception(
                        "No valid credentials found. Teacher needs to connect Google Calendar first. "
                        "Go to Settings -> Connect Google Calendar"
                    )
            
            # Fetch the discovery document
            print(f"Fetching Meet API discovery document from {MEET_API_DISCOVERY_URL}")
            response = requests.get(MEET_API_DISCOVERY_URL)
            response.raise_for_status()
            discovery_doc = response.json()
            
            # Build service from the discovery document
            self.service = build_from_document(discovery_doc, credentials=self.creds)
            print("✅ Google Meet API v2 service initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing Google Meet API: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_conference_record_by_code(self, meet_code: str) -> Optional[Dict]:
        """
        Get the conference record for a meeting by its Meet code
        
        Args:
            meet_code: The Google Meet conference code (e.g., 'abc-defg-hij')
        
        Returns:
            Conference record with meeting details, or None if not found
        """
        if not self.service:
            self.authenticate()
        
        try:
            # List conference records filtered by meeting code
            response = self.service.conferenceRecords().list(
                filter=f'space.meeting_code="{meet_code}"',
                pageSize=10
            ).execute()
            
            records = response.get('conferenceRecords', [])
            
            if not records:
                print(f"No conference record found for meet code: {meet_code}")
                return None
            
            # Return the most recent record (first in list)
            return records[0]
            
        except Exception as e:
            print(f"Error getting conference record: {e}")
            return None
    
    def get_participants_with_sessions(
        self,
        conference_record_name: str
    ) -> List[Dict]:
        """
        Get all participants in a conference with their session data
        
        Args:
            conference_record_name: Name of the conference record 
                                   (e.g., 'conferenceRecords/abc-123-xyz')
        
        Returns:
            List of participants with their sessions including join/leave times
        """
        if not self.service:
            self.authenticate()
        
        participants_data = []
        
        try:
            # Get all participants
            participants_response = self.service.conferenceRecords().participants().list(
                parent=conference_record_name,
                pageSize=100
            ).execute()
            
            participants = participants_response.get('participants', [])
            
            for participant in participants:
                participant_name = participant.get('name')
                
                # Extract user info
                signed_in_user = participant.get('signedinUser', {})
                anonymous_user = participant.get('anonymousUser', {})
                phone_user = participant.get('phoneUser', {})
                
                email = signed_in_user.get('user', '')
                display_name = (
                    signed_in_user.get('displayName') or 
                    anonymous_user.get('displayName') or 
                    phone_user.get('displayName') or 
                    'Unknown'
                )
                
                # Get participant sessions (all join/leave events)
                sessions = self.get_participant_sessions(participant_name)
                
                # Calculate total duration across all sessions
                total_duration = sum(s.get('duration_seconds', 0) for s in sessions)
                
                participants_data.append({
                    'email': email,
                    'display_name': display_name,
                    'participant_id': participant_name,
                    'earliest_start': participant.get('earliestStartTime'),
                    'latest_end': participant.get('latestEndTime'),
                    'total_duration_seconds': total_duration,
                    'session_count': len(sessions),
                    'sessions': sessions
                })
            
            return participants_data
            
        except Exception as e:
            print(f"Error getting participants: {e}")
            return []
    
    def get_participant_sessions(
        self,
        participant_name: str
    ) -> List[Dict]:
        """
        Get all sessions for a specific participant
        
        Args:
            participant_name: Resource name of the participant
                             (e.g., 'conferenceRecords/abc-123/participants/xyz-789')
        
        Returns:
            List of sessions with start/end times and duration
        """
        if not self.service:
            self.authenticate()
        
        try:
            sessions_response = self.service.conferenceRecords().participants().participantSessions().list(
                parent=participant_name,
                pageSize=100
            ).execute()
            
            sessions = sessions_response.get('participantSessions', [])
            
            parsed_sessions = []
            for session in sessions:
                start_time_str = session.get('startTime')
                end_time_str = session.get('endTime')
                
                start_time = self._parse_timestamp(start_time_str)
                end_time = self._parse_timestamp(end_time_str)
                
                duration_seconds = 0
                if start_time and end_time:
                    duration_seconds = int((end_time - start_time).total_seconds())
                
                parsed_sessions.append({
                    'session_id': session.get('name'),
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration_seconds': duration_seconds
                })
            
            return parsed_sessions
            
        except Exception as e:
            print(f"Error getting participant sessions: {e}")
            return []
    
    def get_meeting_participants(
        self,
        meet_code: str
    ) -> List[Dict]:
        """
        Get all participants for a meeting by its Meet code
        This is the main method you should use!
        
        Args:
            meet_code: The Google Meet conference code (e.g., 'abc-defg-hij')
        
        Returns:
            List of participant records with actual join/leave times
            
        Example return:
        [
            {
                'email': 'teacher@school.com',
                'display_name': 'Teacher Name',
                'total_duration_seconds': 3600,
                'session_count': 1,
                'sessions': [
                    {
                        'start_time': datetime(...),
                        'end_time': datetime(...),
                        'duration_seconds': 3600
                    }
                ]
            },
            ...
        ]
        """
        if not self.service:
            self.authenticate()
        
        # Step 1: Get the conference record
        conference_record = self.get_conference_record_by_code(meet_code)
        
        if not conference_record:
            return []
        
        conference_record_name = conference_record.get('name')
        
        # Step 2: Get all participants with their sessions
        return self.get_participants_with_sessions(conference_record_name)
    
    def get_meeting_summary(
        self,
        meet_code: str
    ) -> Dict:
        """
        Get a summary of a meeting including all participants
        
        Args:
            meet_code: The Google Meet conference code
        
        Returns:
            Dict with meeting summary and participant data
        """
        conference_record = self.get_conference_record_by_code(meet_code)
        
        if not conference_record:
            return {
                'meet_code': meet_code,
                'found': False,
                'participants': []
            }
        
        participants = self.get_participants_with_sessions(conference_record.get('name'))
        
        return {
            'meet_code': meet_code,
            'found': True,
            'conference_id': conference_record.get('name'),
            'start_time': self._parse_timestamp(conference_record.get('startTime')),
            'end_time': self._parse_timestamp(conference_record.get('endTime')),
            'total_participants': len(participants),
            'participants': participants
        }
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse RFC3339 timestamp string to datetime"""
        if not timestamp_str:
            return None
        
        try:
            # Parse ISO format timestamp
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except Exception as e:
            print(f"Error parsing timestamp {timestamp_str}: {e}")
            return None


# Global service instance
_meet_service = None


def get_meet_service() -> GoogleMeetAPIService:
    """Get or create GoogleMeetAPIService singleton"""
    global _meet_service
    if _meet_service is None:
        _meet_service = GoogleMeetAPIService()
    return _meet_service
