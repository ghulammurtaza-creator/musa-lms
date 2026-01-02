import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Family {
  id: number;
  family_number: string;
  parent_name: string;
  parent_email: string;
  created_at: string;
  updated_at?: string;
}

export interface Student {
  id: number;
  name: string;
  email: string;
  family_id: number;
  hourly_rate: number;
  created_at: string;
  updated_at?: string;
}

export interface Teacher {
  id: number;
  name: string;
  email: string;
  hourly_rate: number;
  subject_specialties?: string;
  created_at: string;
  updated_at?: string;
}

export interface Session {
  id: number;
  meeting_id: string;
  teacher_id: number;
  start_time: string;
  end_time?: string;
  ai_summary?: string;
  created_at: string;
  updated_at?: string;
}

export interface AttendanceLog {
  id: number;
  session_id: number;
  user_email: string;
  role: 'Teacher' | 'Student';
  teacher_id?: number;
  student_id?: number;
  join_time: string;
  exit_time?: string;
  duration_minutes: number;
  created_at: string;
  updated_at?: string;
}

export interface ActiveSessionParticipant {
  user_email: string;
  role: 'Teacher' | 'Student';
  join_time: string;
  is_active: boolean;
}

export interface ActiveSession {
  session_id: number;
  meeting_id: string;
  teacher_name: string;
  start_time: string;
  participants: ActiveSessionParticipant[];
}

export interface StudentBillingItem {
  student_id: number;
  student_name: string;
  student_email: string;
  total_minutes: number;
  hourly_rate: number;
  total_amount: number;
}

export interface FamilyBilling {
  family_id: number;
  family_number: string;
  parent_name: string;
  parent_email: string;
  students: StudentBillingItem[];
  total_family_amount: number;
  billing_month: string;
}

export interface TeacherPayroll {
  teacher_id: number;
  teacher_name: string;
  teacher_email: string;
  total_minutes: number;
  hourly_rate: number;
  total_amount: number;
  billing_month: string;
}

// API Functions

// Families
export const getFamilies = () => api.get<Family[]>('/families');
export const getFamily = (id: number) => api.get<Family>(`/families/${id}`);
export const createFamily = (data: Partial<Family>) => api.post<Family>('/families', data);
export const updateFamily = (id: number, data: Partial<Family>) => api.patch<Family>(`/families/${id}`, data);
export const deleteFamily = (id: number) => api.delete(`/families/${id}`);

// Students
export const getStudents = (familyId?: number) => 
  api.get<Student[]>('/students', { params: { family_id: familyId } });
export const getStudent = (id: number) => api.get<Student>(`/students/${id}`);
export const createStudent = (data: Partial<Student>) => api.post<Student>('/students', data);
export const updateStudent = (id: number, data: Partial<Student>) => api.patch<Student>(`/students/${id}`, data);
export const deleteStudent = (id: number) => api.delete(`/students/${id}`);

// Teachers
export const getTeachers = () => api.get<Teacher[]>('/teachers');
export const getTeacher = (id: number) => api.get<Teacher>(`/teachers/${id}`);
export const createTeacher = (data: Partial<Teacher>) => api.post<Teacher>('/teachers', data);
export const updateTeacher = (id: number, data: Partial<Teacher>) => api.patch<Teacher>(`/teachers/${id}`, data);
export const deleteTeacher = (id: number) => api.delete(`/teachers/${id}`);

// Monitoring
export const getActiveSessions = () => api.get<ActiveSession[]>('/monitoring/active-sessions');
export const getAttendanceLogs = (params?: { session_id?: number; user_email?: string; skip?: number; limit?: number }) => 
  api.get<AttendanceLog[]>('/monitoring/attendance-logs', { params });

// Billing
export const getFamiliesBilling = (year: number, month: number) => 
  api.get<FamilyBilling[]>('/monitoring/billing/families', { params: { year, month } });
export const getFamilyBilling = (familyId: number, year: number, month: number) => 
  api.get<FamilyBilling>(`/monitoring/billing/families/${familyId}`, { params: { year, month } });

// Payroll
export const getTeachersPayroll = (year: number, month: number) => 
  api.get<TeacherPayroll[]>('/monitoring/payroll/teachers', { params: { year, month } });
export const getTeacherPayroll = (teacherId: number, year: number, month: number) => 
  api.get<TeacherPayroll>(`/monitoring/payroll/teachers/${teacherId}`, { params: { year, month } });
