import React, { useState } from 'react';
import { Calendar, Clock, Users, BookOpen, Plus, X } from 'lucide-react';

const ScheduleClassForm = () => {
  const [formData, setFormData] = useState({
    teacher_email: '',
    student_emails: [''],
    subject: '',
    start_time: '',
    duration_minutes: 60,
    description: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  const addStudentEmail = () => {
    setFormData({
      ...formData,
      student_emails: [...formData.student_emails, '']
    });
  };

  const removeStudentEmail = (index) => {
    const newEmails = formData.student_emails.filter((_, i) => i !== index);
    setFormData({ ...formData, student_emails: newEmails });
  };

  const updateStudentEmail = (index, value) => {
    const newEmails = [...formData.student_emails];
    newEmails[index] = value;
    setFormData({ ...formData, student_emails: newEmails });
  };

  const scheduleForNow = () => {
    const now = new Date();
    // Format as datetime-local string
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const datetimeLocal = `${year}-${month}-${day}T${hours}:${minutes}`;
    
    setFormData({ ...formData, start_time: datetimeLocal });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('http://localhost:8000/api/schedule/class', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          student_emails: formData.student_emails.filter(email => email.trim() !== ''),
          start_time: new Date(formData.start_time).toISOString()
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to schedule class');
      }

      const data = await response.json();
      setSuccess({
        message: 'Class scheduled successfully!',
        meetLink: data.google_meet_link,
        classId: data.id
      });

      // Reset form
      setFormData({
        teacher_email: '',
        student_emails: [''],
        subject: '',
        start_time: '',
        duration_minutes: 60,
        description: ''
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-3xl font-bold mb-6 text-gray-800 flex items-center gap-2">
          <Calendar className="w-8 h-8 text-blue-600" />
          Schedule a Class
        </h2>

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <h3 className="font-semibold text-green-800 mb-2">{success.message}</h3>
            <p className="text-sm text-green-700 mb-2">Class ID: {success.classId}</p>
            <div className="flex items-center gap-2">
              <a
                href={success.meetLink}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline text-sm"
              >
                {success.meetLink}
              </a>
            </div>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Teacher Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Teacher Email
            </label>
            <input
              type="email"
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="teacher@youracademy.com"
              value={formData.teacher_email}
              onChange={(e) => setFormData({ ...formData, teacher_email: e.target.value })}
            />
          </div>

          {/* Subject */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <BookOpen className="w-4 h-4" />
              Subject
            </label>
            <input
              type="text"
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Physics, Mathematics, Chemistry"
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
            />
          </div>

          {/* Student Emails */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <Users className="w-4 h-4" />
              Student Emails
            </label>
            {formData.student_emails.map((email, index) => (
              <div key={index} className="flex gap-2 mb-2">
                <input
                  type="email"
                  required
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="student@email.com"
                  value={email}
                  onChange={(e) => updateStudentEmail(index, e.target.value)}
                />
                {formData.student_emails.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeStudentEmail(index)}
                    className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            ))}
            <button
              type="button"
              onClick={addStudentEmail}
              className="mt-2 flex items-center gap-2 text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              <Plus className="w-4 h-4" />
              Add Another Student
            </button>
          </div>

          {/* Date and Time */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Date & Time
              </label>
              <div className="flex gap-2">
                <input
                  type="datetime-local"
                  required
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={formData.start_time}
                  onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                />
                <button
                  type="button"
                  onClick={scheduleForNow}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium whitespace-nowrap"
                  title="Schedule for now"
                >
                  Now
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Duration (minutes)
              </label>
              <select
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={formData.duration_minutes}
                onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })}
              >
                <option value={3}>3 minutes</option>
                <option value={30}>30 minutes</option>
                <option value={45}>45 minutes</option>
                <option value={60}>1 hour</option>
                <option value={90}>1.5 hours</option>
                <option value={120}>2 hours</option>
                <option value={180}>3 hours</option>
              </select>
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description (Optional)
            </label>
            <textarea
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
              placeholder="Topics to be covered, homework, etc."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Scheduling...
              </>
            ) : (
              <>
                <Calendar className="w-5 h-5" />
                Schedule Class
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ScheduleClassForm;
