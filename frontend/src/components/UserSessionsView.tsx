'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { formatDuration } from '@/lib/utils';
import { Users, Clock, Download, ArrowLeft, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { getUserSessions, UserSessionReport } from '@/lib/api';

const ITEMS_PER_PAGE = 10;

export default function UserSessionsView() {
  const [users, setUsers] = useState<UserSessionReport[]>([]);
  const [selectedUser, setSelectedUser] = useState<UserSessionReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState<string>(new Date().toISOString().substring(0, 7));
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedRole, setSelectedRole] = useState<'all' | 'tutor' | 'student'>('all');

  useEffect(() => {
    fetchUsers();
  }, [selectedMonth, searchQuery, currentPage, selectedRole]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const [year, month] = selectedMonth.split('-');
      const response = await getUserSessions(parseInt(year), parseInt(month), {
        role: selectedRole === 'all' ? undefined : selectedRole,
        search: searchQuery || undefined,
        skip: (currentPage - 1) * ITEMS_PER_PAGE,
        limit: ITEMS_PER_PAGE
      });
      setUsers(response.data);
    } catch (err) {
      console.error('Failed to fetch user sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    setCurrentPage(1); // Reset to first page on new search
  };

  const handleRoleChange = (role: 'all' | 'tutor' | 'student') => {
    setSelectedRole(role);
    setCurrentPage(1); // Reset to first page on role change
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
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium">Select Month</label>
              <input
                type="month"
                value={selectedMonth}
                onChange={(e) => {
                  setSelectedMonth(e.target.value);
                  setCurrentPage(1);
                }}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Search Users</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search by name or email..."
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </div>
          <div className="mt-4">
            <label className="text-sm font-medium">Filter by Role</label>
            <div className="flex gap-2 mt-2">
              <Button
                variant={selectedRole === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleRoleChange('all')}
              >
                All
              </Button>
              <Button
                variant={selectedRole === 'tutor' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleRoleChange('tutor')}
              >
                Tutors
              </Button>
              <Button
                variant={selectedRole === 'student' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleRoleChange('student')}
              >
                Students
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="text-center py-12">
          <div className="text-xl text-muted-foreground">Loading users...</div>
        </div>
      ) : users.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <div className="text-muted-foreground">No users found</div>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-2">
            {/* Display all users in a combined view */}
            {users.map(user => (
              <Card key={user.user_id} className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => setSelectedUser(user)}>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="font-medium text-lg">{user.full_name}</div>
                      <div className="text-sm text-muted-foreground">{user.email}</div>
                      <div className="text-xs text-muted-foreground mt-2 flex items-center gap-4">
                        <span className="flex items-center gap-1">
                          <Users className="h-3 w-3" />
                          {user.total_sessions} sessions
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatDuration(user.total_minutes)}
                        </span>
                      </div>
                    </div>
                    <Badge variant={user.role === 'tutor' ? 'default' : 'secondary'}>
                      {user.role}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Pagination Controls */}
          <Card>
            <CardContent className="py-4">
              <div className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                  Page {currentPage}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                  >
                    <ChevronLeft className="h-4 w-4 mr-1" />
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(prev => prev + 1)}
                    disabled={users.length < ITEMS_PER_PAGE}
                  >
                    Next
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
