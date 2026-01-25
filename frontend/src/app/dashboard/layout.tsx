'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { 
  LayoutDashboard, 
  Users, 
  Link2, 
  Activity, 
  FileText, 
  BarChart3, 
  DollarSign,
  Settings,
  Menu,
  X,
  LogOut
} from 'lucide-react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const getNavItems = () => {
    if (user?.role === 'admin') {
      return [
        { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { href: '/dashboard/users', label: 'User Management', icon: Users },
        { href: '/dashboard/relationships', label: 'Assignments', icon: Link2 },
        { href: '/dashboard/sessions', label: 'Active Sessions', icon: Activity },
        { href: '/dashboard/logs', label: 'Attendance Logs', icon: FileText },
        { href: '/dashboard/reports', label: 'User Reports', icon: BarChart3 },
        { href: '/dashboard/financial', label: 'Financial Hub', icon: DollarSign },
        { href: '/dashboard/settings', label: 'Settings', icon: Settings },
      ];
    } else if (user?.role === 'tutor') {
      return [
        { href: '/tutor/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { href: '/tutor/students', label: 'My Students', icon: Users },
        { href: '/tutor/assignments', label: 'Assignments', icon: FileText },
        { href: '/tutor/schedule', label: 'Schedule Class', icon: Activity },
      ];
    } else {
      return [
        { href: '/student/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { href: '/student/tutors', label: 'My Tutors', icon: Users },
        { href: '/student/assignments', label: 'Assignments', icon: FileText },
      ];
    }
  };

  const navItems = getNavItems();

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-white shadow-lg transition-all duration-300 flex flex-col`}>
        {/* Logo and Toggle */}
        <div className="h-16 flex items-center justify-between px-4 border-b">
          {sidebarOpen && (
            <Link href="/" className="text-xl font-bold text-indigo-600">
              Musa LMS
            </Link>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100"
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-1 px-3">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-indigo-50 text-indigo-600 font-medium'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                    title={!sidebarOpen ? item.label : ''}
                  >
                    <Icon className="h-5 w-5 flex-shrink-0" />
                    {sidebarOpen && <span>{item.label}</span>}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* User Info and Logout */}
        <div className="border-t p-4">
          {sidebarOpen ? (
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
              <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
            </div>
          ) : (
            <div className="flex justify-center mb-3">
              <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
                <span className="text-sm font-medium text-indigo-600">
                  {user?.full_name?.charAt(0) || 'U'}
                </span>
              </div>
            </div>
          )}
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-red-600 hover:bg-red-50 transition-colors"
            title={!sidebarOpen ? 'Logout' : ''}
          >
            <LogOut className="h-5 w-5 flex-shrink-0" />
            {sidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
