'use client';

import { useCallback, useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

export default function StudentTutorManagement() {
  const { token, user } = useAuth();
  const [students, setStudents] = useState<User[]>([]);
  const [tutors, setTutors] = useState<User[]>([]);
  const [allStudents, setAllStudents] = useState<User[]>([]);
  const [allTutors, setAllTutors] = useState<User[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<number | null>(null);
  const [selectedTutor, setSelectedTutor] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Move fetchAllUsers above useEffect and wrap in useCallback
  const fetchAllUsers = useCallback(async () => {
    try {
      const [studentsRes, tutorsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/auth/students`, {
          headers: { 'Authorization': `Bearer ${token}` },
        }),
        fetch(`${API_BASE_URL}/api/auth/tutors`, {
          headers: { 'Authorization': `Bearer ${token}` },
        }),
      ]);
      const studentsData = await studentsRes.json();
      const tutorsData = await tutorsRes.json();
      setAllStudents(studentsData);
      setAllTutors(tutorsData);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setIsLoading(false);
    }
  }, [token]);
  useEffect(() => {
    if (user?.role === 'admin') {
      fetchAllUsers();
    }
  }, [user, fetchAllUsers]);

  const fetchRelationships = async (studentId: number) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/relationships/student/${studentId}/tutors`,
        {
          headers: { 'Authorization': `Bearer ${token}` },
        }
      );
      const data = await response.json();
      setTutors(data);
    } catch (error) {
      console.error('Error fetching tutors:', error);
    }
  };

  const handleAssign = async () => {
    if (!selectedStudent || !selectedTutor) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/relationships/assign`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_id: selectedStudent,
          tutor_id: selectedTutor,
        }),
      });

      if (response.ok) {
        alert('Student assigned to tutor successfully!');
        fetchRelationships(selectedStudent);
      }
    } catch (error) {
      console.error('Error assigning student:', error);
    }
  };

  const handleUnassign = async (studentId: number, tutorId: number) => {
    if (!confirm('Are you sure you want to unassign this student from the tutor?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/relationships/unassign`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_id: studentId,
          tutor_id: tutorId,
        }),
      });

      if (response.ok) {
        alert('Student unassigned successfully!');
        fetchRelationships(studentId);
      }
    } catch (error) {
      console.error('Error unassigning student:', error);
    }
  };

  if (user?.role !== 'admin') {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Only administrators can manage student-tutor assignments.</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return <div className="p-6">Loading...</div>;
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Student-Tutor Management</h1>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Assign Student to Tutor</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Select Student
              </label>
              <select
                value={selectedStudent || ''}
                onChange={(e) => {
                  const id = parseInt(e.target.value);
                  setSelectedStudent(id);
                  fetchRelationships(id);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="">Choose a student...</option>
                {allStudents.map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.full_name} ({student.email})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Select Tutor
              </label>
              <select
                value={selectedTutor || ''}
                onChange={(e) => setSelectedTutor(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="">Choose a tutor...</option>
                {allTutors.map((tutor) => (
                  <option key={tutor.id} value={tutor.id}>
                    {tutor.full_name} ({tutor.email})
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={handleAssign}
              disabled={!selectedStudent || !selectedTutor}
              className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              Assign Student to Tutor
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Current Tutors</h2>
          {!selectedStudent ? (
            <p className="text-gray-500">Select a student to view their tutors</p>
          ) : tutors.length === 0 ? (
            <p className="text-gray-500">No tutors assigned to this student</p>
          ) : (
            <div className="space-y-2">
              {tutors.map((tutor) => (
                <div
                  key={tutor.id}
                  className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium">{tutor.full_name}</p>
                    <p className="text-sm text-gray-600">{tutor.email}</p>
                  </div>
                  <button
                    onClick={() => handleUnassign(selectedStudent, tutor.id)}
                    className="text-red-600 hover:text-red-800 text-sm font-medium"
                  >
                    Unassign
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">All Students</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {allStudents.map((student) => (
                <tr key={student.id}>
                  <td className="px-6 py-4 whitespace-nowrap">{student.full_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{student.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => {
                        setSelectedStudent(student.id);
                        fetchRelationships(student.id);
                      }}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      View Tutors
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}


