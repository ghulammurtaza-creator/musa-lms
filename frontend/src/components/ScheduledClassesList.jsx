import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Video, Users, BookOpen, RefreshCw } from 'lucide-react';

const ScheduledClassesList = ({ userEmail, userRole = 'teacher' }) => {
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('upcoming');

  useEffect(() => {
    fetchClasses();
  }, [userEmail, userRole, filter]);

  const fetchClasses = async () => {
    setLoading(true);
    setError(null);

    try {
      const param = userRole === 'teacher' ? `teacher_email=${userEmail}` : `student_email=${userEmail}`;
      const upcomingParam = filter === 'upcoming' ? '&upcoming_only=true' : '&upcoming_only=false';
      
      const response = await fetch(`http://localhost:8000/api/schedule/classes?${param}${upcomingParam}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch classes');
      }

      const data = await response.json();
      setClasses(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDateTime = (isoString) => {
    const date = new Date(isoString);
    return {
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    };
  };

  const getStatusBadge = (classItem) => {
    if (classItem.is_completed) {
      return <span className="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm">Completed</span>;
    }
    if (classItem.is_active) {
      return <span className="px-3 py-1 bg-green-200 text-green-700 rounded-full text-sm animate-pulse">Live Now</span>;
    }
    return <span className="px-3 py-1 bg-blue-200 text-blue-700 rounded-full text-sm">Scheduled</span>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error: {error}</p>
        <button
          onClick={fetchClasses}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
            <Calendar className="w-8 h-8 text-blue-600" />
            {userRole === 'teacher' ? 'My Scheduled Classes' : 'My Classes'}
          </h2>
          <button
            onClick={fetchClasses}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setFilter('upcoming')}
            className={`pb-3 px-4 font-medium transition-colors ${
              filter === 'upcoming'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Upcoming
          </button>
          <button
            onClick={() => setFilter('all')}
            className={`pb-3 px-4 font-medium transition-colors ${
              filter === 'all'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            All Classes
          </button>
        </div>

        {/* Classes List */}
        {classes.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Calendar className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg">No classes scheduled</p>
          </div>
        ) : (
          <div className="space-y-4">
            {classes.map((classItem) => {
              const startDateTime = formatDateTime(classItem.start_time);
              const endDateTime = formatDateTime(classItem.end_time);

              return (
                <div
                  key={classItem.id}
                  className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-3 bg-blue-100 rounded-lg">
                        <BookOpen className="w-6 h-6 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="text-xl font-semibold text-gray-800">
                          {classItem.subject}
                        </h3>
                        <p className="text-sm text-gray-500">Class ID: {classItem.id}</p>
                      </div>
                    </div>
                    {getStatusBadge(classItem)}
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="flex items-center gap-2 text-gray-600">
                      <Calendar className="w-4 h-4" />
                      <span className="text-sm">{startDateTime.date}</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <Clock className="w-4 h-4" />
                      <span className="text-sm">
                        {startDateTime.time} - {endDateTime.time}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <Clock className="w-4 h-4" />
                      <span className="text-sm">{classItem.duration_minutes} minutes</span>
                    </div>
                    {classItem.students && (
                      <div className="flex items-center gap-2 text-gray-600">
                        <Users className="w-4 h-4" />
                        <span className="text-sm">{classItem.students.length} students</span>
                      </div>
                    )}
                  </div>

                  {classItem.google_meet_link && (
                    <div className="flex items-center gap-4">
                      <a
                        href={classItem.google_meet_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                      >
                        <Video className="w-4 h-4" />
                        Join Meeting
                      </a>
                      <span className="text-sm text-gray-500">
                        Code: {classItem.google_meet_code}
                      </span>
                    </div>
                  )}

                  {classItem.students && userRole === 'teacher' && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <p className="text-sm font-medium text-gray-700 mb-2">Students:</p>
                      <div className="flex flex-wrap gap-2">
                        {classItem.students.map((student, index) => (
                          <span
                            key={index}
                            className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                          >
                            {student.name || student.email}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default ScheduledClassesList;
