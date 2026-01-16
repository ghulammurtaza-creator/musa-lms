"""
Test script for Google Meet REST API v2
Run this to verify your setup and test getting participant data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.google_meet_api import GoogleMeetAPIService
from datetime import datetime


def test_meet_api():
    """Test Google Meet API setup and functionality"""
    print("\n" + "="*70)
    print("🧪 Testing Google Meet REST API v2")
    print("="*70 + "\n")
    
    try:
        # Step 1: Initialize
        print("Step 1: Initializing Google Meet API service...")
        service = GoogleMeetAPIService()
        
        # Step 2: Authenticate
        print("Step 2: Authenticating...")
        service.authenticate()
        print("   ✅ Authentication successful!\n")
        
        # Step 3: Test with a meet code
        print("Step 3: Testing API with a meet code...")
        print("\n" + "-"*70)
        meet_code = input("Enter a Google Meet code to test (e.g., abc-defg-hij): ").strip()
        
        if not meet_code:
            print("\n⚠️  No meet code provided. Skipping participant lookup.")
            print("   To test participant tracking:")
            print("   1. Schedule a meeting")
            print("   2. Join with at least 1 person")
            print("   3. Run this test again with the meet code")
            return True
        
        print(f"\n   Fetching participants for: {meet_code}...")
        
        # Get meeting summary
        summary = service.get_meeting_summary(meet_code)
        
        if not summary.get('found'):
            print(f"\n   ⚠️  No conference record found for: {meet_code}")
            print("\n   This could mean:")
            print("   - Meeting hasn't started yet")
            print("   - Meet code is incorrect")
            print("   - No one has joined the meeting")
            return True
        
        print(f"\n   ✅ Conference found!")
        print(f"   Conference ID: {summary['conference_id']}")
        print(f"   Start time: {summary.get('start_time')}")
        print(f"   End time: {summary.get('end_time')}")
        print(f"   Total participants: {summary['total_participants']}")
        
        # Display participant details
        if summary['participants']:
            print("\n   Participants:")
            print("   " + "-"*66)
            for p in summary['participants']:
                print(f"\n   📧 {p['email']}")
                print(f"      Name: {p['display_name']}")
                print(f"      Sessions: {p['session_count']}")
                print(f"      Total duration: {p['total_duration_seconds']}s ({p['total_duration_seconds']/60:.1f} min)")
                
                for i, session in enumerate(p['sessions'], 1):
                    print(f"\n      Session {i}:")
                    print(f"         Join:  {session['start_time']}")
                    print(f"         Leave: {session['end_time']}")
                    print(f"         Duration: {session['duration_seconds']}s ({session['duration_seconds']/60:.1f} min)")
        
        print("\n" + "="*70)
        print("✅ SUCCESS! Google Meet API is working correctly!")
        print("="*70)
        print("\n✨ You can now get real participant data from your meetings!")
        print("\nTo use in your app:")
        print("   POST /api/webhook/sessions/{session_id}/sync-participants\n")
        
        return True
        
    except FileNotFoundError:
        print("\n❌ ERROR: token.json not found!")
        print("\nPlease run:")
        print("   cd backend")
        print("   python setup_google_oauth.py --meet")
        return False
        
    except Exception as e:
        error_msg = str(e)
        
        if "No valid credentials" in error_msg or "refresh_token" in error_msg:
            print("\n❌ ERROR: Invalid or expired credentials!")
            print("\nYour token doesn't have the Meet API scope.")
            print("\nFix this:")
            print("1. Delete token.json")
            print("2. Run: python setup_google_oauth.py --meet")
            print("3. Grant ALL permissions in browser")
            
        elif "Google Meet API" in error_msg or "404" in error_msg:
            print("\n❌ ERROR: Google Meet API not enabled!")
            print("\nPlease:")
            print("1. Go to https://console.cloud.google.com/")
            print("2. Navigate to: APIs & Services → Library")
            print("3. Search: 'Google Meet API'")
            print("4. Click ENABLE")
            print("5. Run this test again")
            
        elif "403" in error_msg or "Insufficient Permission" in error_msg:
            print("\n❌ ERROR: Insufficient permissions!")
            print("\nMake sure:")
            print("1. You authenticated with --meet flag")
            print("2. You granted Meet API permissions")
            print("3. Your credentials.json is correct")
            
        else:
            print(f"\n❌ ERROR: {error_msg}")
            print("\nTroubleshooting:")
            print("1. Enable Google Meet API in Cloud Console")
            print("2. Run: python setup_google_oauth.py --meet")
            print("3. Grant all requested permissions")
        
        return False


if __name__ == '__main__':
    success = test_meet_api()
    sys.exit(0 if success else 1)
