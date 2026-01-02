'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ActiveSession, getActiveSessions } from '@/lib/api';
import { formatDateTime } from '@/lib/utils';
import { Users, Clock, CheckCircle, XCircle } from 'lucide-react';

export default function ActiveSessionsView() {
  const [sessions, setSessions] = useState<ActiveSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await getActiveSessions();
      setSessions(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch active sessions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
    // Refresh every 30 seconds
    const interval = setInterval(fetchSessions, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && sessions.length === 0) {
    return <div className="flex justify-center p-8">Loading active sessions...</div>;
  }

  if (error) {
    return <div className="text-red-500 p-4">{error}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{sessions.length}</div>
            <p className="text-xs text-muted-foreground">Currently in progress</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Participants</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sessions.reduce((sum, s) => sum + s.participants.filter(p => p.is_active).length, 0)}
            </div>
            <p className="text-xs text-muted-foreground">Active now</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Longest Session</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sessions.length > 0
                ? Math.max(
                    ...sessions.map(
                      s => Math.floor((new Date().getTime() - new Date(s.start_time).getTime()) / 60000)
                    )
                  )
                : 0}
              m
            </div>
            <p className="text-xs text-muted-foreground">Minutes</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Real-time Session Monitoring</CardTitle>
          <CardDescription>View currently active Google Meet sessions and participants</CardDescription>
        </CardHeader>
        <CardContent>
          {sessions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">No active sessions at the moment</div>
          ) : (
            <div className="space-y-4">
              {sessions.map(session => (
                <div key={session.session_id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-semibold text-lg">{session.teacher_name}</h3>
                      <p className="text-sm text-muted-foreground">Meeting ID: {session.meeting_id}</p>
                      <p className="text-sm text-muted-foreground">Started: {formatDateTime(session.start_time)}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center gap-1 text-sm">
                        <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                        Live
                      </span>
                    </div>
                  </div>

                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Participant</TableHead>
                        <TableHead>Role</TableHead>
                        <TableHead>Join Time</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {session.participants.map((participant, idx) => (
                        <TableRow key={idx}>
                          <TableCell className="font-medium">{participant.user_email}</TableCell>
                          <TableCell>
                            <span
                              className={`inline-flex items-center px-2 py-1 rounded text-xs ${
                                participant.role === 'Teacher'
                                  ? 'bg-blue-100 text-blue-800'
                                  : 'bg-green-100 text-green-800'
                              }`}
                            >
                              {participant.role}
                            </span>
                          </TableCell>
                          <TableCell>{formatDateTime(participant.join_time)}</TableCell>
                          <TableCell>
                            {participant.is_active ? (
                              <CheckCircle className="h-4 w-4 text-green-500" />
                            ) : (
                              <XCircle className="h-4 w-4 text-gray-400" />
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
