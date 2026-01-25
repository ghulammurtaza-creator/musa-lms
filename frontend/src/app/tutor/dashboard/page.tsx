'use client';

import MyStudentsView from '@/components/MyStudentsView';
import TutorAssignmentsView from '@/components/TutorAssignmentsView';

export default function TutorDashboard() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Tutor Dashboard</h1>
      
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">My Students</h3>
          <p className="text-3xl font-bold text-green-600">-</p>
          <p className="text-sm text-gray-500 mt-1">Assigned to me</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">My Assignments</h3>
          <p className="text-3xl font-bold text-blue-600">-</p>
          <p className="text-sm text-gray-500 mt-1">Created by me</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <a
            href="/tutor/students"
              className="p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-colors"
          >
            <h3 className="font-semibold mb-2">View Students</h3>
            <p className="text-sm text-gray-600">See all students assigned to you</p>
          </a>
          <a
            href="/tutor/assignments"
            className="p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-colors"
          >
            <h3 className="font-semibold mb-2">Manage Assignments</h3>
            <p className="text-sm text-gray-600">Create and grade assignments</p>
          </a>
          <a
            href="/tutor/schedule"
            className="p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-colors"
          >
            <h3 className="font-semibold mb-2">Schedule Class</h3>
            <p className="text-sm text-gray-600">Schedule a new class with Google Meet</p>
          </a>
        </div>
      </div>
    </div>
  );
}
