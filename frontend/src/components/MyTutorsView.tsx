'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

interface Tutor {
  id: number;
  email: string;
  full_name: string;
}

export default function MyTutorsView() {
  const { token } = useAuth();
  const [tutors, setTutors] = useState<Tutor[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchTutors();
  }, []);

  const fetchTutors = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/relationships/my-tutors`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setTutors(data);
    } catch (error) {
      console.error('Error fetching tutors:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="p-6">Loading...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">My Tutors</h1>

      {tutors.length === 0 ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <p className="text-blue-800">No tutors assigned yet. Please contact your administrator.</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tutors.map((tutor) => (
            <div key={tutor.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
                  <span className="text-indigo-600 font-bold text-xl">
                    {tutor.full_name.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold">{tutor.full_name}</h3>
                  <p className="text-sm text-gray-600">{tutor.email}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}


