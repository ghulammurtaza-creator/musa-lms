"""
Setup script to authenticate with Google Calendar API and Meet Reports API
Run this ONCE on your host machine to generate token.json
Then the token will be available in Docker container
"""
import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Default scopes for Calendar API
CALENDAR_SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

# Scope for Google Meet REST API (to get participant data)
MEET_API_SCOPE = 'https://www.googleapis.com/auth/meetings.space.readonly'

# Additional scope for Google Meet Reports API (legacy - Admin SDK)
REPORTS_SCOPE = 'https://www.googleapis.com/auth/admin.reports.audit.readonly'

def setup_oauth(include_meet=False, include_reports=False):
    """Run OAuth flow to generate token.json"""
    # Determine which scopes to use
    scopes = CALENDAR_SCOPES.copy()
    if include_meet:
        scopes.append(MEET_API_SCOPE)
        print("📊 Including Google Meet API scope for participant tracking")
    if include_reports:
        scopes.append(REPORTS_SCOPE)
        print("🔍 Including Google Meet Reports API scope (legacy)")
    
    creds = None
    
    # Check if token already exists
    if os.path.exists('token.json'):
        print("✓ token.json already exists!")
        creds = Credentials.from_authorized_user_file('token.json', scopes)
        
        # Check if token is still valid
        if creds and creds.valid:
            print("✓ Token is valid and ready to use!")
            return
        
        # Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print("✓ Token refreshed successfully!")
            return
    
    # No valid credentials, need to log in
    if not os.path.exists('credentials.json'):
        print("❌ ERROR: credentials.json not found!")
        print("\nPlease download OAuth credentials from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Navigate to APIs & Services → Credentials")
        print("3. Create OAuth 2.0 Client ID (Desktop app)")
        print("4. Download and save as credentials.json in backend/")
        return
    
    print("\n🔐 Starting Google OAuth authentication...")
    print("A browser window will open. Please:")
    print("1. Sign in with your Google Workspace account")
    if include_meet:
        print("2. Grant Calendar API AND Meet API permissions")
        print("   (Meet API is needed to track real participant join/leave times)")
    elif include_reports:
        print("2. Grant Calendar API AND Reports API permissions")
        print("   (Reports API is needed to track real participant join/leave times)")
    else:
        print("2. Grant Calendar API permissions")
    print("3. Close the browser when done\n")
    
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', 
        scopes,
        redirect_uri='http://localhost:8000'
    )
    
    # Use port 8000 to match the authorized redirect URI
    creds = flow.run_local_server(port=8000, open_browser=True)
    
    # Save credentials for future use
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
    print("\n✅ SUCCESS! token.json created successfully!")
    print("✅ You can now use Google Calendar API from Docker")
    if include_meet:
        print("✅ You can now track real participant join/leave times with Meet API!")
    if include_reports:
        print("✅ You can now access Meet Reports API (legacy method)!")
    print("\nNext steps:")
    print("1. Rebuild Docker: docker-compose build app")
    print("2. Restart container: docker-compose up -d app")
    print("3. Try scheduling a class from the frontend")
    if include_meet or include_reports:
        print("4. After a meeting ends, sync participants with:")
        print("   POST /api/webhook/sessions/{session_id}/sync-participants")


if __name__ == '__main__':
    # Check for flags
    include_meet = '--meet' in sys.argv or '-m' in sys.argv
    include_reports = '--reports' in sys.argv or '-r' in sys.argv
    
    if include_meet:
        print("\n" + "="*60)
        print("🚀 Setting up OAuth with Google Meet REST API")
        print("="*60)
        print("\n✅ This is the RECOMMENDED method for participant tracking!")
        print("✅ Uses official Google Meet API v2")
        print("✅ No admin privileges required")
        print("✅ Better performance and reliability")
        print()
    elif include_reports:
        print("\n" + "="*60)
        print("🚀 Setting up OAuth with Google Meet Reports API (Legacy)")
        print("="*60)
        print("\n⚠️  IMPORTANT: You must be a Google Workspace Admin")
        print("⚠️  Also enable 'Admin SDK API' in Google Cloud Console")
        print("⚠️  Consider using --meet flag instead (easier setup)")
        print()
    else:
        print("\n" + "="*60)
        print("🚀 Setting up OAuth for Google Calendar")
        print("="*60)
        print("\n💡 TIP: Use --meet flag to also enable participant tracking")
        print("   Example: python setup_google_oauth.py --meet")
        print()
    
    setup_oauth(include_meet=include_meet, include_reports=include_reports)

if __name__ == '__main__':
    setup_oauth()
