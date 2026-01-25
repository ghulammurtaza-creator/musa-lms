'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

interface Student {
  id: number;
  email: string;
  full_name: string;
}

export default function MyStudentsView() {
  const { token } = useAuth();
  const [students, setStudents] = useState<Student[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/relationships/my-students`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setStudents(data);
    } catch (error) {
      console.error('Error fetching students:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="p-6">Loading...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">My Students</h1>

      {students.length === 0 ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <p className="text-blue-800">No students assigned yet. Please contact your administrator.</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {students.map((student) => (
            <div key={student.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-green-600 font-bold text-xl">
                    {student.full_name.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold">{student.full_name}</h3>
                  <p className="text-sm text-gray-600">{student.email}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
