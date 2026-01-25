'use client';

import ActiveSessionsView from '@/components/ActiveSessionsView';
import AttendanceLogsView from '@/components/AttendanceLogsView';
import { useAuth } from '@/contexts/AuthContext';

export default function AdminDashboard() {
  const { user } = useAuth();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-2xl font-semibold mb-4">Active Sessions</h2>
        <ActiveSessionsView />
      </div>
    </div>
  );
}
