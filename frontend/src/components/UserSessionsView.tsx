'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { formatDuration } from '@/lib/utils';
import { Users, Clock, Download, ArrowLeft } from 'lucide-react';
import { getUserSessions, UserSessionReport } from '@/lib/api';

export default function UserSessionsView() {
  const [users, setUsers] = useState<UserSessionReport[]>([]);
  const [selectedUser, setSelectedUser] = useState<UserSessionReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState<string>(new Date().toISOString().substring(0, 7));

  useEffect(() => {
    fetchUsers();
  }, [selectedMonth]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const [year, month] = selectedMonth.split('-');
      const response = await getUserSessions(parseInt(year), parseInt(month));
      setUsers(response.data);
    } catch (err) {
      console.error('Failed to fetch user sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const exportToCSV = () => {
    if (!selectedUser || selectedUser.sessions.length === 0) return;

    const csvRows = [
      ['Session ID', 'Date', 'Join Time', 'Exit Time', 'Duration (minutes)', 'Role']
    ];

    selectedUser.sessions.forEach(session => {
      const joinDate = new Date(session.join_time);
      const exitDate = session.exit_time ? new Date(session.exit_time) : null;

      csvRows.push([
        session.session_id.toString(),
        joinDate.toLocaleDateString(),
        joinDate.toLocaleTimeString(),
        exitDate ? exitDate.toLocaleTimeString() : 'Still Active',
        session.duration_minutes?.toFixed(2) || '0',
        selectedUser.role
      ]);
    });

    const csvContent = csvRows.map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedUser.email}_sessions_${selectedMonth}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const tutors = users.filter(u => u.role === 'tutor');
  const students = users.filter(u => u.role === 'student');

  if (selectedUser) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center gap-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedUser(null)}
                  >
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to Users
                  </Button>
                </div>
                <CardTitle className="mt-4">{selectedUser.full_name}</CardTitle>
                <CardDescription>
                  <Badge variant={selectedUser.role === 'tutor' ? 'default' : 'secondary'}>
                    {selectedUser.role}
                  </Badge>
                  <span className="ml-2">{selectedUser.email}</span>
                </CardDescription>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Month</label>
                <input
                  type="month"
                  value={selectedMonth}
                  onChange={(e) => setSelectedMonth(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2"
                />
              </div>
            </div>
          </CardHeader>
        </Card>

        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{selectedUser.total_sessions}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Duration</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatDuration(selectedUser.total_minutes)}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Session</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {selectedUser.total_sessions > 0 ? formatDuration(selectedUser.total_minutes / selectedUser.total_sessions) : '0h'}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Session History</CardTitle>
                <CardDescription>
                  {new Date(selectedMonth + '-01').toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={exportToCSV} disabled={selectedUser.sessions.length === 0}>
                <Download className="h-4 w-4 mr-2" />
                Export CSV
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8 text-muted-foreground">Loading sessions...</div>
            ) : selectedUser.sessions.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No sessions found for this month
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Session #</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Join Time</TableHead>
                    <TableHead>Exit Time</TableHead>
                    <TableHead>Duration</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {selectedUser.sessions.map(session => {
                      const joinDate = new Date(session.join_time);
                      const exitDate = session.exit_time ? new Date(session.exit_time) : null;
                      
                      return (
                        <TableRow key={`${session.session_id}-${session.join_time}`}>
                          <TableCell className="font-medium">#{session.session_id}</TableCell>
                          <TableCell>{joinDate.toLocaleDateString()}</TableCell>
                          <TableCell>{joinDate.toLocaleTimeString()}</TableCell>
                          <TableCell>
                            {exitDate ? exitDate.toLocaleTimeString() : '-'}
                          </TableCell>
                          <TableCell>{formatDuration(session.duration_minutes || 0)}</TableCell>
                          <TableCell>
                            {session.exit_time ? (
                              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                                Completed
                              </Badge>
                            ) : (
                              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                                Active
                              </Badge>
                            )}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>User Session Reports</CardTitle>
          <CardDescription>View detailed session history for students and tutors</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <label className="text-sm font-medium">Select Month</label>
            <input
              type="month"
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 max-w-xs"
            />
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="text-center py-12">
          <div className="text-xl text-muted-foreground">Loading users...</div>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {/* Tutors Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Tutors
              </CardTitle>
              <CardDescription>{tutors.length} tutor{tutors.length !== 1 ? 's' : ''}</CardDescription>
            </CardHeader>
            <CardContent>
              {tutors.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">No tutors found</div>
              ) : (
                <div className="space-y-2">
                  {tutors.map(tutor => (
                    <div
                      key={tutor.user_id}
                      onClick={() => setSelectedUser(tutor)}
                      className="flex items-center justify-between p-3 rounded-lg border hover:bg-accent cursor-pointer transition-colors"
                    >
                      <div>
                        <div className="font-medium">{tutor.full_name}</div>
                        <div className="text-sm text-muted-foreground">{tutor.email}</div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {tutor.total_sessions} sessions · {formatDuration(tutor.total_minutes)}
                        </div>
                      </div>
                      <Badge variant="default">Tutor</Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Students Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Students
              </CardTitle>
              <CardDescription>{students.length} student{students.length !== 1 ? 's' : ''}</CardDescription>
            </CardHeader>
            <CardContent>
              {students.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">No students found</div>
              ) : (
                <div className="space-y-2">
                  {students.map(student => (
                    <div
                      key={student.user_id}
                      onClick={() => setSelectedUser(student)}
                      className="flex items-center justify-between p-3 rounded-lg border hover:bg-accent cursor-pointer transition-colors"
                    >
                      <div>
                        <div className="font-medium">{student.full_name}</div>
                        <div className="text-sm text-muted-foreground">{student.email}</div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {student.total_sessions} sessions · {formatDuration(student.total_minutes)}
                        </div>
                      </div>
                      <Badge variant="secondary">Student</Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
