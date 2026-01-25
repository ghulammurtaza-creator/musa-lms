'use client';

export default function StudentDashboard() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Student Dashboard</h1>
      
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">My Tutors</h3>
          <p className="text-3xl font-bold text-indigo-600">-</p>
          <p className="text-sm text-gray-500 mt-1">Teaching me</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Pending Assignments</h3>
          <p className="text-3xl font-bold text-yellow-600">-</p>
          <p className="text-sm text-gray-500 mt-1">Need to be completed</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <a
            href="/student/tutors"
            className="p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-colors"
          >
            <h3 className="font-semibold mb-2">View My Tutors</h3>
            <p className="text-sm text-gray-600">See all tutors assigned to you</p>
          </a>
          <a
            href="/student/assignments"
            className="p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-colors"
          >
            <h3 className="font-semibold mb-2">View Assignments</h3>
            <p className="text-sm text-gray-600">See and submit your assignments</p>
          </a>
        </div>
      </div>
    </div>
  );
}
