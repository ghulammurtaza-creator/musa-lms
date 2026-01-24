'use client';

import React from 'react';
import { GoogleCalendarConnect } from '@/components/GoogleCalendarConnect';
import ScheduleClassForm from '@/components/ScheduleClassForm';
import ScheduledClassesList from '@/components/ScheduledClassesList';
import { useAuth } from '@/contexts/AuthContext';

export default function TutorSchedulePage() {
  const { user } = useAuth();

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Schedule Classes</h1>
      
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Connect Google Calendar</h2>
          <p className="text-gray-600 mb-4">
            Connect your Google Calendar to schedule classes with Google Meet integration
          </p>
          {user && <GoogleCalendarConnect teacherEmail={user.email} />}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Schedule New Class</h2>
          <ScheduleClassForm />
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">My Scheduled Classes</h2>
          {user && <ScheduledClassesList userEmail={user.email} userRole="teacher" />}
        </div>
      </div>
    </div>
  );
}
