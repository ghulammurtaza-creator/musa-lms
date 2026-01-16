'use client';

import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import ActiveSessionsView from '@/components/ActiveSessionsView';
import AttendanceLogsView from '@/components/AttendanceLogsView';
import FinancialHubView from '@/components/FinancialHubView';
import UserManagementView from '@/components/UserManagementView';
import ScheduleClassForm from '@/components/ScheduleClassForm';
import ScheduledClassesList from '@/components/ScheduledClassesList';
import { GoogleCalendarConnect } from '@/components/GoogleCalendarConnect';
import { GraduationCap, Activity, DollarSign, Users, Calendar } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <GraduationCap className="h-8 w-8 text-primary" />
            <div>
              <h1 className="text-2xl font-bold">Academy Management System</h1>
              <p className="text-sm text-muted-foreground">
                Automated attendance tracking and billing platform
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <Tabs defaultValue="monitoring" className="w-full">
          <TabsList className="grid w-full grid-cols-5 mb-8">
            <TabsTrigger value="monitoring" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Real-time Monitoring
            </TabsTrigger>
            <TabsTrigger value="schedule" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Schedule Classes
            </TabsTrigger>
            <TabsTrigger value="logs" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Attendance Logs
            </TabsTrigger>
            <TabsTrigger value="financial" className="flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Financial Hub
            </TabsTrigger>
            <TabsTrigger value="users" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              User Management
            </TabsTrigger>
          </TabsList>

          <TabsContent value="monitoring">
            <ActiveSessionsView />
          </TabsContent>

          <TabsContent value="schedule">
            <div className="space-y-8">
              <GoogleCalendarConnect teacherEmail="adil@orinex.co.uk" />
              <ScheduleClassForm />
              <ScheduledClassesList userEmail="adil.gillani@stixor.com" userRole="teacher" />
            </div>
          </TabsContent>

          <TabsContent value="logs">
            <AttendanceLogsView />
          </TabsContent>

          <TabsContent value="financial">
            <FinancialHubView />
          </TabsContent>

          <TabsContent value="users">
            <UserManagementView />
          </TabsContent>
        </Tabs>
      </main>

      <footer className="border-t mt-12">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-sm text-muted-foreground">
            © 2026 Academy Management System. Built with Next.js, FastAPI, and PostgreSQL.
          </p>
        </div>
      </footer>
    </div>
  );
}
