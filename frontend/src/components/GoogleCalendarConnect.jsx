import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { CheckCircle2, XCircle, Link as LinkIcon } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export function GoogleCalendarConnect({ teacherEmail }) {
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkConnectionStatus();
  }, [teacherEmail]);

  const checkConnectionStatus = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/oauth/status/${teacherEmail}`);
      const data = await response.json();
      
      if (response.ok) {
        setIsConnected(data.connected);
      } else {
        setError(data.detail || 'Failed to check connection status');
      }
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    console.log('handleConnect called with teacherEmail:', teacherEmail);
    setLoading(true);
    setError(null);
    
    try {
      const url = `${API_BASE_URL}/oauth/connect?teacher_email=${encodeURIComponent(teacherEmail)}`;
      console.log('Fetching:', url);
      const response = await fetch(url);
      const data = await response.json();
      console.log('Response:', response.status, data);
      
      if (response.ok && data.authorization_url) {
        // Open Google OAuth in popup or redirect
        console.log('Redirecting to:', data.authorization_url);
        window.location.href = data.authorization_url;
      } else {
        setError(data.detail || 'Failed to initiate connection');
      }
    } catch (err) {
      console.error('Connection error:', err);
      setError('Network error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect Google Calendar?')) {
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/oauth/disconnect/${teacherEmail}`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (response.ok) {
        setIsConnected(false);
        alert('Google Calendar disconnected successfully');
      } else {
        setError(data.detail || 'Failed to disconnect');
      }
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !isConnected) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-gray-500">Checking connection...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <LinkIcon className="h-5 w-5" />
          Google Calendar Integration
        </CardTitle>
        <CardDescription>
          Connect your Google Calendar to schedule classes with automatic Meet links
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <XCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {isConnected ? (
          <div className="space-y-4">
            <Alert className="bg-green-50 border-green-200">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                Google Calendar is connected. You can schedule classes with Meet links.
              </AlertDescription>
            </Alert>
            <Button 
              variant="outline" 
              onClick={handleDisconnect}
              disabled={loading}
            >
              Disconnect Calendar
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <Alert>
              <AlertDescription>
                You need to connect your Google Calendar to schedule classes. This will allow the system to:
                <ul className="list-disc ml-6 mt-2">
                  <li>Create calendar events automatically</li>
                  <li>Generate Google Meet links for online classes</li>
                  <li>Send invitations to students</li>
                </ul>
              </AlertDescription>
            </Alert>
            <Button 
              onClick={handleConnect}
              disabled={loading}
              className="w-full"
            >
              {loading ? 'Connecting...' : 'Connect Google Calendar'}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
