'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { AttendanceLog, getAttendanceLogs } from '@/lib/api';
import { formatDateTime, formatDuration } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search } from 'lucide-react';

export default function AttendanceLogsView() {
  const [logs, setLogs] = useState<AttendanceLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchEmail, setSearchEmail] = useState('');
  const [filteredLogs, setFilteredLogs] = useState<AttendanceLog[]>([]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await getAttendanceLogs({ limit: 100 });
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
  }, []);

  useEffect(() => {
    if (searchEmail) {
      setFilteredLogs(
        logs.filter(log => log.user_email.toLowerCase().includes(searchEmail.toLowerCase()))
      );
    } else {
      setFilteredLogs(logs);
    }
  }, [searchEmail, logs]);

  if (loading) {
    return <div className="flex justify-center p-8">Loading attendance logs...</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Attendance Logs</CardTitle>
        <CardDescription>Complete history of join/exit events and calculated durations</CardDescription>
        <div className="flex items-center gap-2 mt-4">
          <Search className="h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by email..."
            value={searchEmail}
            onChange={e => setSearchEmail(e.target.value)}
            className="max-w-sm"
          />
          <Button onClick={fetchLogs} variant="outline">
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {filteredLogs.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            {searchEmail ? 'No logs found for this email' : 'No attendance logs yet'}
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Join Time</TableHead>
                <TableHead>Exit Time</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredLogs.map(log => (
                <TableRow key={log.id}>
                  <TableCell className="font-medium">{log.user_email}</TableCell>
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
                  <TableCell>
                    {log.exit_time ? (
                      <span className="text-green-600">Completed</span>
                    ) : (
                      <span className="text-blue-600">Active</span>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
