'use client';

import { useCallback, useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Download, FileText, CheckCircle, Clock, XCircle } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

interface Assignment {
  id: number;
  tutor_id: number;
  title: string;
  description: string;
  due_date: string;
  total_points: number;
  created_at: string;
  tutor: {
    id: number;
    email: string;
    full_name: string;
    role: string;
  };
}

interface Submission {
  id: number;
  assignment_id: number;
  student_id: number;
  submission_text: string | null;
  file_path: string | null;
  status: 'pending' | 'submitted' | 'graded';
  grade: number | null;
  feedback: string | null;
  submitted_at: string | null;
  graded_at: string | null;
  student: {
    id: number;
    email: string;
    full_name: string;
  };
  assignment: Assignment;
}

interface Student {
  id: number;
  email: string;
  full_name: string;
}

export default function TutorAssignmentsView() {
  const { token } = useAuth();
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [submissions, setSubmissions] = useState<Record<number, Submission[]>>({});
  const [selectedAssignment, setSelectedAssignment] = useState<number | null>(null);
  const [selectedSubmission, setSelectedSubmission] = useState<Submission | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [gradeForm, setGradeForm] = useState({
    grade: 0,
    feedback: '',
  });
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    due_date: '',
    total_points: 100,
    student_ids: [] as number[],
  });

  // Move fetchAssignments and fetchStudents above useEffect and wrap in useCallback
  const fetchAssignments = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/assignments`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setAssignments(data);
    } catch (error) {
      console.error('Error fetching assignments:', error);
    } finally {
      setIsLoading(false);
    }
  }, [token]);
  const fetchStudents = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/relationships/my-students`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setStudents(data);
    } catch (error) {
      console.error('Error fetching students:', error);
    }
  }, [token]);

  const fetchSubmissions = useCallback(async (assignmentId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/assignments/${assignmentId}/submissions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setSubmissions(prev => ({ ...prev, [assignmentId]: data }));
    } catch (error) {
      console.error('Error fetching submissions:', error);
    }
  }, [token]);

  useEffect(() => {
    fetchAssignments();
    fetchStudents();
  }, [fetchAssignments, fetchStudents]);

  const handleCreateAssignment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE_URL}/assignments`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setShowCreateForm(false);
        setFormData({
          title: '',
          description: '',
          due_date: '',
          total_points: 100,
          student_ids: [],
        });
        fetchAssignments();
      }
    } catch (error) {
      console.error('Error creating assignment:', error);
    }
  };

  const toggleStudent = (studentId: number) => {
    setFormData(prev => ({
      ...prev,
      student_ids: prev.student_ids.includes(studentId)
        ? prev.student_ids.filter(id => id !== studentId)
        : [...prev.student_ids, studentId],
    }));
  };

  const handleViewSubmissions = async (assignmentId: number) => {
    setSelectedAssignment(assignmentId);
    await fetchSubmissions(assignmentId);
  };

  const handleDownloadFile = async (submissionId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/assignments/submissions/${submissionId}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const contentDisposition = response.headers.get('Content-Disposition');
        const filenameMatch = contentDisposition?.match(/filename="(.+)"/);
        const filename = filenameMatch ? filenameMatch[1] : 'download';

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error downloading file:', error);
      alert('Failed to download file');
    }
  };

  const handleGradeSubmission = async (submissionId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/assignments/submissions/${submissionId}/grade`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(gradeForm),
      });

      if (response.ok) {
        setSelectedSubmission(null);
        setGradeForm({ grade: 0, feedback: '' });
        if (selectedAssignment) {
          await fetchSubmissions(selectedAssignment);
        }
      }
    } catch (error) {
      console.error('Error grading submission:', error);
      alert('Failed to grade submission');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'submitted':
        return <FileText className="w-5 h-5 text-blue-500" />;
      case 'graded':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      default:
        return <XCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      submitted: 'bg-blue-100 text-blue-800',
      graded: 'bg-green-100 text-green-800',
    };
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors[status as keyof typeof colors]}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  if (isLoading) {
    return <div className="p-6">Loading...</div>;
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">My Assignments</h1>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
        >
          {showCreateForm ? 'Cancel' : 'Create Assignment'}
        </button>
      </div>

      {showCreateForm && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Create New Assignment</h2>
          <form onSubmit={handleCreateAssignment} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                required
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                <input
                  type="datetime-local"
                  required
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Total Points</label>
                <input
                  type="number"
                  required
                  min="1"
                  value={formData.total_points}
                  onChange={(e) => setFormData({ ...formData, total_points: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Assign to Students</label>
              <div className="max-h-40 overflow-y-auto border border-gray-300 rounded-md p-3 space-y-2">
                {students.map((student) => (
                  <label key={student.id} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={formData.student_ids.includes(student.id)}
                      onChange={() => toggleStudent(student.id)}
                      className="rounded"
                    />
                    <span>{student.full_name} ({student.email})</span>
                  </label>
                ))}
              </div>
            </div>
            <button
              type="submit"
              disabled={formData.student_ids.length === 0}
              className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              Create Assignment
            </button>
          </form>
        </div>
      )}

      <div className="grid gap-4">
        {assignments.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            No assignments yet. Create your first assignment!
          </div>
        ) : (
          assignments.map((assignment) => (
            <div key={assignment.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-xl font-semibold">{assignment.title}</h3>
                <span className="text-sm text-gray-500">
                  {assignment.total_points} points
                </span>
              </div>
              <p className="text-gray-600 mb-3">{assignment.description}</p>
              <div className="flex justify-between items-center text-sm text-gray-500">
                <span>Due: {new Date(assignment.due_date).toLocaleString()}</span>
                <span>Created: {new Date(assignment.created_at).toLocaleDateString()}</span>
              </div>
              <button
                onClick={() => handleViewSubmissions(assignment.id)}
                className="mt-4 w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700"
              >
                View Submissions
              </button>
            </div>
          ))
        )}
      </div>

      {/* Submissions Modal */}
      {selectedAssignment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-center">
              <h2 className="text-2xl font-bold">
                {assignments.find(a => a.id === selectedAssignment)?.title} - Submissions
              </h2>
              <button
                onClick={() => setSelectedAssignment(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                &times;
              </button>
            </div>
            
            <div className="p-6">
              {submissions[selectedAssignment]?.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  No submissions yet
                </div>
              ) : (
                <div className="space-y-4">
                  {submissions[selectedAssignment]?.map((submission) => (
                    <div key={submission.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h4 className="font-semibold text-lg">{submission.student.full_name}</h4>
                          <p className="text-sm text-gray-500">{submission.student.email}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(submission.status)}
                          {getStatusBadge(submission.status)}
                        </div>
                      </div>

                      {submission.submission_text && (
                        <div className="mb-3">
                          <p className="text-sm font-medium text-gray-700 mb-1">Submission Text:</p>
                          <p className="text-gray-600 bg-gray-50 p-3 rounded">{submission.submission_text}</p>
                        </div>
                      )}

                      {submission.file_path && (
                        <button
                          onClick={() => handleDownloadFile(submission.id)}
                          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 mb-3"
                        >
                          <Download className="w-4 h-4" />
                          Download File
                        </button>
                      )}

                      <div className="grid grid-cols-2 gap-4 text-sm text-gray-500 mb-3">
                        {submission.submitted_at && (
                          <div>
                            <span className="font-medium">Submitted:</span>{' '}
                            {new Date(submission.submitted_at).toLocaleString()}
                          </div>
                        )}
                        {submission.grade !== null && (
                          <div>
                            <span className="font-medium">Grade:</span>{' '}
                            {submission.grade}/{submission.assignment.total_points}
                          </div>
                        )}
                      </div>

                      {submission.feedback && (
                        <div className="mb-3">
                          <p className="text-sm font-medium text-gray-700 mb-1">Feedback:</p>
                          <p className="text-gray-600 bg-gray-50 p-3 rounded">{submission.feedback}</p>
                        </div>
                      )}

                      {submission.status !== 'graded' && (
                        <button
                          onClick={() => setSelectedSubmission(submission)}
                          className="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700"
                        >
                          Grade Submission
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Grade Submission Modal */}
      {selectedSubmission && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="bg-white border-b border-gray-200 p-6 flex justify-between items-center">
              <h2 className="text-xl font-bold">Grade Submission</h2>
              <button
                onClick={() => setSelectedSubmission(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                &times;
              </button>
            </div>
            
            <div className="p-6">
              <p className="mb-4 text-gray-600">
                Grading submission from <strong>{selectedSubmission.student.full_name}</strong>
              </p>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Grade (out of {selectedSubmission.assignment.total_points})
                  </label>
                  <input
                    type="number"
                    min="0"
                    max={selectedSubmission.assignment.total_points}
                    value={gradeForm.grade}
                    onChange={(e) => setGradeForm({ ...gradeForm, grade: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Feedback</label>
                  <textarea
                    rows={4}
                    value={gradeForm.feedback}
                    onChange={(e) => setGradeForm({ ...gradeForm, feedback: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="Enter feedback for the student..."
                  />
                </div>
                
                <button
                  onClick={() => handleGradeSubmission(selectedSubmission.id)}
                  className="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700"
                >
                  Submit Grade
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


