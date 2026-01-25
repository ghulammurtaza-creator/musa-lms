'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { AttendanceLog, getAttendanceLogs } from '@/lib/api';
import { formatDateTime, formatDuration } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, Users, Download, Calendar } from 'lucide-react';
import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectSeparator, SelectTrigger, SelectValue } from '@/components/ui/select';

interface UserOption {
  id: number;
  full_name: string;
  email: string;
  role: string;
}

export default function AttendanceLogsView() {
  const [logs, setLogs] = useState<AttendanceLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchEmail, setSearchEmail] = useState('');
  const [filteredLogs, setFilteredLogs] = useState<AttendanceLog[]>([]);
  const [groupedLogs, setGroupedLogs] = useState<Map<number, AttendanceLog[]>>(new Map());
  
  // New state for user filtering
  const [users, setUsers] = useState<UserOption[]>([]);
  const [selectedUser, setSelectedUser] = useState<string>('all');
  const [selectedMonth, setSelectedMonth] = useState<string>(new Date().toISOString().substring(0, 7)); // YYYY-MM format

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error('No access token found');
        return;
      }
      
      // Fetch tutors and students separately using their specific endpoints
      const [tutorsResponse, studentsResponse] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/tutors`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/auth/students`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);
      
      const allUsers = [];
      
      if (tutorsResponse.ok) {
        const tutors = await tutorsResponse.json();
        allUsers.push(...tutors);
      } else {
        console.error('Failed to fetch tutors:', tutorsResponse.status);
      }
      
      if (studentsResponse.ok) {
        const students = await studentsResponse.json();
        allUsers.push(...students);
      } else {
        console.error('Failed to fetch students:', studentsResponse.status);
      }
      
      setUsers(allUsers);
    } catch (err) {
      console.error('Failed to fetch users:', err);
    }
  };

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await getAttendanceLogs({ limit: 1000 });
      setLogs(response.data);
      setFilteredLogs(response.data);
    } catch (err) {
      console.error('Failed to fetch attendance logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    fetchUsers();
  }, []);

  // Group users by role for dropdown
  const tutors = users.filter(u => u.role === 'tutor');
  const students = users.filter(u => u.role === 'student');

  useEffect(() => {
    let filtered = logs;

    // Update filter logic
    if (selectedUser && selectedUser !== 'all') {
      let userId = selectedUser.replace(/^(tutor|student)-/, '');
      const userOption = users.find(u => u.id.toString() === userId);
      if (userOption) {
        filtered = filtered.filter(log => 
          log.user_email.toLowerCase() === userOption.email.toLowerCase()
        );
      }
    }

    // Filter by selected month
    if (selectedMonth) {
      const [year, month] = selectedMonth.split('-').map(Number);
      filtered = filtered.filter(log => {
        const logDate = new Date(log.join_time);
        return logDate.getFullYear() === year && logDate.getMonth() + 1 === month;
      });
    }

    // Filter by search text
    if (searchEmail) {
      filtered = filtered.filter(log => 
        log.user_email.toLowerCase().includes(searchEmail.toLowerCase()) ||
        (log.display_name && log.display_name.toLowerCase().includes(searchEmail.toLowerCase()))
      );
    }

    setFilteredLogs(filtered);
  }, [searchEmail, logs, selectedUser, selectedMonth, users]);

  useEffect(() => {
    // Group logs by session_id
    const grouped = new Map<number, AttendanceLog[]>();
    filteredLogs.forEach(log => {
      if (!grouped.has(log.session_id)) {
        grouped.set(log.session_id, []);
      }
      grouped.get(log.session_id)!.push(log);
    });
    setGroupedLogs(grouped);
  }, [filteredLogs]);

  const exportToCSV = () => {
    const csvRows = [];
    
    // Header
    csvRows.push(['Session ID', 'Name', 'Email', 'Role', 'Join Time', 'Exit Time', 'Duration (minutes)'].join(','));
    
    // Data rows
    Array.from(groupedLogs.entries())
      .sort(([a], [b]) => b - a)
      .forEach(([sessionId, sessionLogs]) => {
        sessionLogs.forEach(log => {
          csvRows.push([
            sessionId,
            `"${log.display_name || ''}"`,
            log.user_email,
            log.role,
            new Date(log.join_time).toLocaleString(),
            log.exit_time ? new Date(log.exit_time).toLocaleString() : '',
            log.duration_minutes || 0
          ].join(','));
        });
      });
    
    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    
    const selectedUserName = selectedUser !== 'all' ? users.find(u => u.id.toString() === selectedUser)?.full_name : 'All';
    a.download = `attendance_${selectedUserName}_${selectedMonth}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const clearFilters = () => {
    setSelectedUser('all');
    setSearchEmail('');
  };

  if (loading) {
    return <div className="flex justify-center p-8">Loading attendance logs...</div>;
  }

  // Debug logging
  if (typeof window !== 'undefined') {
    console.log('users', users);
    console.log('logs', logs);
    console.log('filteredLogs', filteredLogs);
    console.log('groupedLogs', groupedLogs);
    console.log('selectedUser', selectedUser);
    console.log('selectedMonth', selectedMonth);
  }

  let renderError = null;
  try {
    const selectedUserName = selectedUser !== 'all' ? users.find(u => u.id.toString() === selectedUser)?.full_name : null;
    const totalDuration = filteredLogs.reduce((sum, log) => sum + (log.duration_minutes || 0), 0);

    return (
      <Card>
        <CardHeader>
          <CardTitle>Attendance Logs</CardTitle>
          <CardDescription>View and export attendance history by teacher or student</CardDescription>
          
          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mt-4">
            <Select value={selectedUser} onValueChange={setSelectedUser}>
              <SelectTrigger>
                <SelectValue placeholder="Select Teacher/Student" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>Tutors</SelectLabel>
                  {tutors.length === 0 && <SelectItem value="tutors-none" disabled>No tutors</SelectItem>}
                  {tutors.map(user => (
                    <SelectItem key={user.id} value={`tutor-${user.id}`}>
                      {user.full_name} (Tutor)
                    </SelectItem>
                  ))}
                </SelectGroup>
                <SelectGroup>
                  <SelectLabel>Students</SelectLabel>
                  {students.length === 0 && <SelectItem value="students-none" disabled>No students</SelectItem>}
                  {students.map(user => (
                    <SelectItem key={user.id} value={`student-${user.id}`}>
                      {user.full_name} (Student)
                    </SelectItem>
                  ))}
                </SelectGroup>
                <SelectSeparator />
                <SelectItem value="all">All Users</SelectItem>
              </SelectContent>
            </Select>

            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <Input
                type="month"
                value={selectedMonth}
                onChange={e => setSelectedMonth(e.target.value)}
                className="flex-1"
              />
            </div>

            <div className="flex items-center gap-2">
              <Search className="h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search..."
                value={searchEmail}
                onChange={e => setSearchEmail(e.target.value)}
              />
            </div>

            <div className="flex gap-2">
              <Button onClick={clearFilters} variant="outline" className="flex-1">
                Clear
              </Button>
              <Button onClick={exportToCSV} variant="default" className="flex-1" disabled={filteredLogs.length === 0}>
                <Download className="h-4 w-4 mr-2" />
                Export CSV
              </Button>
            </div>
          </div>

          {/* Summary */}
          {selectedUserName && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-blue-900">
                {selectedUserName} - {new Date(selectedMonth + '-01').toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
              </h4>
              <p className="text-sm text-blue-700 mt-1">
                Total Sessions: {groupedLogs.size} | Total Duration: {formatDuration(totalDuration)}
              </p>
            </div>
          )}
        </CardHeader>
        <CardContent>
          {filteredLogs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              {searchEmail ? 'No logs found' : 'No attendance logs yet'}
            </div>
          ) : (
            <div className="space-y-4">
              {Array.from(groupedLogs.entries())
                .sort(([a], [b]) => b - a) // Sort by session_id descending (newest first)
                .map(([sessionId, sessionLogs]) => {
                  const firstLog = sessionLogs[0];
                  const allCompleted = sessionLogs.every(log => log.exit_time);
                  
                  return (
                    <div key={sessionId} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="font-semibold text-lg flex items-center gap-2">
                            <Users className="h-5 w-5 text-muted-foreground" />
                            Session #{sessionId}
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            {sessionLogs.length} participant{sessionLogs.length !== 1 ? 's' : ''}
                          </p>
                        </div>
                        <div className="text-right">
                          {allCompleted ? (
                            <span className="inline-flex items-center gap-1 text-sm text-green-600">
                              Completed
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-sm text-blue-600">
                              <span className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
                              Active
                            </span>
                          )}
                        </div>
                      </div>

                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Name</TableHead>
                            <TableHead>Email/ID</TableHead>
                            <TableHead>Role</TableHead>
                            <TableHead>Join Time</TableHead>
                            <TableHead>Exit Time</TableHead>
                            <TableHead>Duration</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {sessionLogs.map(log => (
                            <TableRow key={log.id}>
                              <TableCell className="font-medium">
                                {log.display_name || '-'}
                              </TableCell>
                              <TableCell className="text-sm text-muted-foreground">
                                {log.user_email}
                              </TableCell>
                              <TableCell>
                                <span
                                  className={`inline-flex items-center px-2 py-1 rounded text-xs ${
                                    log.role === 'Teacher' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                                  }`}
                                >
                                  {log.role}
                                </span>
                              </TableCell>
                              <TableCell>{formatDateTime(log.join_time)}</TableCell>
                              <TableCell>{log.exit_time ? formatDateTime(log.exit_time) : '-'}</TableCell>
                              <TableCell className="font-semibold">{formatDuration(log.duration_minutes)}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  );
                })}
            </div>
          )}
        </CardContent>
      </Card>
    );
  } catch (err) {
    renderError = err;
    if (typeof window !== 'undefined') {
      console.error('AttendanceLogsView render error:', err);
    }
  }

  if (renderError) {
    return <div className="text-red-600 p-4">Error rendering attendance logs: {String(renderError)}</div>;
  }

  return null;
}
