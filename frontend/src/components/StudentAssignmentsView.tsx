'use client';

import { useCallback, useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

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
    full_name: string;
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
  assignment: Assignment;
}

export default function StudentAssignmentsView() {
  const { token } = useAuth();
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedSubmission, setSelectedSubmission] = useState<Submission | null>(null);
  const [submissionText, setSubmissionText] = useState('');
  const [submissionFile, setSubmissionFile] = useState<File | null>(null);

  // Move fetchSubmissions above useEffect and wrap in useCallback
  const fetchSubmissions = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/assignments/my-submissions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setSubmissions(data);
    } catch (error) {
      console.error('Error fetching submissions:', error);
    } finally {
      setIsLoading(false);
    }
  }, [token]);
  useEffect(() => {
    fetchSubmissions();
  }, [fetchSubmissions]);

  const handleSubmit = async (assignmentId: number) => {
    try {
      const formData = new FormData();
      if (submissionText) {
        formData.append('submission_text', submissionText);
      }
      if (submissionFile) {
        formData.append('file', submissionFile);
      }

      const response = await fetch(`${API_BASE_URL}/assignments/${assignmentId}/submit`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        setSelectedSubmission(null);
        setSubmissionText('');
        setSubmissionFile(null);
        fetchSubmissions();
      }
    } catch (error) {
      console.error('Error submitting assignment:', error);
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
      <h1 className="text-3xl font-bold mb-6">My Assignments</h1>

      {selectedSubmission && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold">{selectedSubmission.assignment.title}</h2>
                <button
                  onClick={() => setSelectedSubmission(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
              <p className="text-gray-600 mb-4">{selectedSubmission.assignment.description}</p>
              <div className="mb-4 space-y-2 text-sm text-gray-600">
                <p>Due: {new Date(selectedSubmission.assignment.due_date).toLocaleString()}</p>
                <p>Points: {selectedSubmission.assignment.total_points}</p>
                <p>Tutor: {selectedSubmission.assignment.tutor.full_name}</p>
              </div>

              {selectedSubmission.status === 'pending' && (
                <div className="space-y-4 mt-6">
                  <h3 className="font-semibold text-lg">Submit Assignment</h3>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Your Answer
                    </label>
                    <textarea
                      rows={6}
                      value={submissionText}
                      onChange={(e) => setSubmissionText(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      placeholder="Type your answer here..."
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Upload File (optional)
                    </label>
                    <input
                      type="file"
                      onChange={(e) => setSubmissionFile(e.target.files?.[0] || null)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    />
                  </div>
                  <button
                    onClick={() => handleSubmit(selectedSubmission.assignment_id)}
                    disabled={!submissionText && !submissionFile}
                    className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50"
                  >
                    Submit Assignment
                  </button>
                </div>
              )}

              {selectedSubmission.status === 'submitted' && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <p className="text-blue-800">
                    Assignment submitted on {new Date(selectedSubmission.submitted_at!).toLocaleString()}
                  </p>
                  {selectedSubmission.submission_text && (
                    <div className="mt-3">
                      <p className="font-medium">Your Answer:</p>
                      <p className="text-gray-700 whitespace-pre-wrap">{selectedSubmission.submission_text}</p>
                    </div>
                  )}
                </div>
              )}

              {selectedSubmission.status === 'graded' && (
                <div className="mt-6 space-y-4">
                  <div className="p-4 bg-green-50 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-green-800">Grade</span>
                      <span className="text-2xl font-bold text-green-800">
                        {selectedSubmission.grade} / {selectedSubmission.assignment.total_points}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">
                      Graded on {new Date(selectedSubmission.graded_at!).toLocaleString()}
                    </p>
                  </div>
                  {selectedSubmission.feedback && (
                    <div>
                      <p className="font-medium mb-2">Feedback:</p>
                      <p className="text-gray-700 p-4 bg-gray-50 rounded-lg whitespace-pre-wrap">
                        {selectedSubmission.feedback}
                      </p>
                    </div>
                  )}
                  {selectedSubmission.submission_text && (
                    <div>
                      <p className="font-medium mb-2">Your Answer:</p>
                      <p className="text-gray-700 p-4 bg-gray-50 rounded-lg whitespace-pre-wrap">
                        {selectedSubmission.submission_text}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="grid gap-4">
        {submissions.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            No assignments yet. Your tutor will assign work to you.
          </div>
        ) : (
          submissions.map((submission) => (
            <div
              key={submission.id}
              className="bg-white rounded-lg shadow-md p-6 cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => setSelectedSubmission(submission)}
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-xl font-semibold">{submission.assignment.title}</h3>
                {getStatusBadge(submission.status)}
              </div>
              <p className="text-gray-600 mb-3 line-clamp-2">{submission.assignment.description}</p>
              <div className="flex justify-between items-center text-sm text-gray-500">
                <span>Due: {new Date(submission.assignment.due_date).toLocaleString()}</span>
                <span>Tutor: {submission.assignment.tutor.full_name}</span>
              </div>
              {submission.status === 'graded' && submission.grade !== null && (
                <div className="mt-3 pt-3 border-t">
                  <span className="text-lg font-semibold text-green-600">
                    Grade: {submission.grade} / {submission.assignment.total_points}
                  </span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}


