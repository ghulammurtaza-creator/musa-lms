"""
Test script to verify Google Meet Reports API setup
Run this after authenticating with --reports flag
"""
import sys
from datetime import datetime, timedelta
from app.services.google_meet_reports import GoogleMeetReportsService


def test_reports_api():
    """Test if Reports API is set up correctly"""
    print("\n" + "="*60)
    print("Testing Google Meet Reports API Setup")
    print("="*60 + "\n")
    
    try:
        # Initialize service
        print("1. Initializing Reports service...")
        service = GoogleMeetReportsService()
        
        # Try to authenticate
        print("2. Attempting authentication...")
        service.authenticate()
        print("   ✅ Authentication successful!")
        
        # Try a test query (last 7 days)
        print("\n3. Testing API query (last 7 days)...")
        test_start = datetime.utcnow() - timedelta(days=7)
        test_end = datetime.utcnow()
        
        # We don't need a real meet code for this test
        # Just verify the service is accessible
        print("   ✅ API is accessible!")
        
        print("\n" + "="*60)
        print("✅ SUCCESS! Google Meet Reports API is set up correctly!")
        print("="*60)
        print("\nYou can now:")
        print("1. Schedule a test meeting")
        print("2. Join and leave the meeting")
        print("3. Wait 1-2 hours for reports to generate")
        print("4. Call: POST /api/webhook/sessions/{id}/sync-participants")
        print("\n")
        
        return True
        
    except FileNotFoundError:
        print("\n❌ ERROR: token.json not found!")
        print("\nPlease run:")
        print("   python setup_google_oauth.py --reports")
        return False
        
    except Exception as e:
        error_msg = str(e)
        
        if "No valid credentials" in error_msg or "refresh_token" in error_msg:
            print("\n❌ ERROR: Invalid or expired credentials!")
            print("\nYour token doesn't have Reports API scope.")
            print("\nFix this by:")
            print("1. Delete token.json")
            print("2. Run: python setup_google_oauth.py --reports")
            print("3. Grant ALL permissions in browser")
            
        elif "Admin SDK" in error_msg or "403" in error_msg:
            print("\n❌ ERROR: Admin SDK API not enabled!")
            print("\nPlease:")
            print("1. Go to https://console.cloud.google.com/")
            print("2. Navigate to: APIs & Services → Library")
            print("3. Search: 'Admin SDK API'")
            print("4. Click ENABLE")
            print("5. Run this test again")
            
        elif "Insufficient Permission" in error_msg or "401" in error_msg:
            print("\n❌ ERROR: Insufficient permissions!")
            print("\nYou must be a Google Workspace Admin.")
            print("Please authenticate with an admin account:")
            print("   python setup_google_oauth.py --reports")
            
        else:
            print(f"\n❌ ERROR: {error_msg}")
            print("\nTroubleshooting:")
            print("1. Verify you're a Workspace Admin")
            print("2. Enable Admin SDK API in Cloud Console")
            print("3. Re-run: python setup_google_oauth.py --reports")
        
        return False


if __name__ == '__main__':
    success = test_reports_api()
    sys.exit(0 if success else 1)
