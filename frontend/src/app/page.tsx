'use client';

import React, { useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function HomePage() {
  const { isAuthenticated, user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated && user) {
      // Redirect based on role
      if (user.role === 'admin') {
        router.push('/dashboard');
      } else if (user.role === 'tutor') {
        router.push('/tutor/dashboard');
      } else {
        router.push('/student/dashboard');
      }
    }
  }, [isAuthenticated, user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-indigo-600">Musa LMS</h1>
          <div className="space-x-4">
            <Link
              href="/login"
              className="px-6 py-2 text-indigo-600 border-2 border-indigo-600 rounded-lg hover:bg-indigo-50 transition-colors"
            >
              Login
            </Link>
            <Link
              href="/signup"
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Sign Up
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Welcome to Musa LMS
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            A comprehensive Learning Management System with automated attendance tracking,
            assignment management, and seamless Google Meet integration
          </p>
          
          <div className="grid md:grid-cols-3 gap-8 mt-16">
            <div className="bg-white rounded-lg shadow-lg p-8">
              <div className="text-4xl mb-4">👨‍💼</div>
              <h3 className="text-xl font-semibold mb-3">For Admins</h3>
              <p className="text-gray-600">
                Manage users, assign students to tutors, monitor all sessions and attendance
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-8">
              <div className="text-4xl mb-4">👨‍🏫</div>
              <h3 className="text-xl font-semibold mb-3">For Tutors</h3>
              <p className="text-gray-600">
                Schedule classes, create assignments, track student progress with Google Meet integration
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-8">
              <div className="text-4xl mb-4">👨‍🎓</div>
              <h3 className="text-xl font-semibold mb-3">For Students</h3>
              <p className="text-gray-600">
                View tutors, submit assignments, and attend classes seamlessly
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
