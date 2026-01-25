'use client';

import { useAuth } from '@/contexts/AuthContext';
import { GoogleCalendarConnect } from '@/components/GoogleCalendarConnect';
import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { CheckCircle2, XCircle } from 'lucide-react';

export default function SettingsPage() {
  const { user } = useAuth();
  const searchParams = useSearchParams();
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    const oauthSuccess = searchParams.get('oauth_success');
    const oauthError = searchParams.get('oauth_error');

    if (oauthSuccess) {
      setMessage({ type: 'success', text: 'Google Calendar connected successfully!' });
      // Clear message after 5 seconds
      setTimeout(() => setMessage(null), 5000);
    } else if (oauthError) {
      const errorMessages: Record<string, string> = {
        'access_denied': 'You denied access to Google Calendar.',
        'authentication_failed': 'Failed to authenticate with Google. Please try again.',
      };
      setMessage({ 
        type: 'error', 
        text: errorMessages[oauthError] || 'An error occurred during authentication.' 
      });
      setTimeout(() => setMessage(null), 5000);
    }
  }, [searchParams]);

  if (!user || user.role !== 'admin') {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Only administrators can access settings.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">System Settings</h1>

      {/* OAuth Status Messages */}
      {message && (
        <div className={`mb-6 relative w-full rounded-lg border p-4 ${
            message.type === 'success' 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}>
          {message.type === 'success' ? (
            <CheckCircle2 className="h-4 w-4 text-green-600 inline mr-2" />
          ) : (
            <XCircle className="h-4 w-4 text-red-600 inline mr-2" />
          )}
          <span className={`text-sm ${message.type === 'success' ? 'text-green-800' : 'text-red-800'}`}>
            {message.text}
          </span>
        </div>
      )}

      <div className="space-y-6">
        {/* Google Workspace Integration Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">Google Workspace Integration</h2>
          <p className="text-gray-600 mb-6">
            Connect your Google Workspace account to enable automated scheduling, 
            Google Meet links, and attendance tracking.
          </p>
          
          <GoogleCalendarConnect teacherEmail={user.email} />
        </div>

        {/* Additional Settings Sections Can Be Added Here */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">System Information</h2>
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Admin Email</dt>
              <dd className="mt-1 text-sm text-gray-900">{user.email}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">User Role</dt>
              <dd className="mt-1 text-sm text-gray-900 uppercase">{user.role}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Display Name</dt>
              <dd className="mt-1 text-sm text-gray-900">{user.full_name || user.email}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
}
