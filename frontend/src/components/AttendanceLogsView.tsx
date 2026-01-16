'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { AttendanceLog, getAttendanceLogs } from '@/lib/api';
import { formatDateTime, formatDuration } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, Users } from 'lucide-react';

export default function AttendanceLogsView() {
  const [logs, setLogs] = useState<AttendanceLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchEmail, setSearchEmail] = useState('');
  const [filteredLogs, setFilteredLogs] = useState<AttendanceLog[]>([]);
  const [groupedLogs, setGroupedLogs] = useState<Map<number, AttendanceLog[]>>(new Map());

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
      const filtered = logs.filter(log => 
        log.user_email.toLowerCase().includes(searchEmail.toLowerCase()) ||
        (log.display_name && log.display_name.toLowerCase().includes(searchEmail.toLowerCase()))
      );
      setFilteredLogs(filtered);
    } else {
      setFilteredLogs(logs);
    }
  }, [searchEmail, logs]);

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
            placeholder="Search by name or email..."
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
}
