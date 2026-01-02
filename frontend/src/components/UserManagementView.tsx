'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Family,
  Student,
  Teacher,
  getFamilies,
  getStudents,
  getTeachers,
  createFamily,
  createStudent,
  createTeacher,
} from '@/lib/api';
import { UserPlus, Users, GraduationCap, Home } from 'lucide-react';

export default function UserManagementView() {
  const [families, setFamilies] = useState<Family[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [teachers, setTeachers] = useState<Teacher[]>([]);

  // Form states
  const [familyForm, setFamilyForm] = useState({ family_number: '', parent_name: '', parent_email: '' });
  const [studentForm, setStudentForm] = useState({ name: '', email: '', family_id: '', hourly_rate: '' });
  const [teacherForm, setTeacherForm] = useState({
    name: '',
    email: '',
    hourly_rate: '',
    subject_specialties: '',
  });

  const fetchData = async () => {
    try {
      const [familiesRes, studentsRes, teachersRes] = await Promise.all([
        getFamilies(),
        getStudents(),
        getTeachers(),
      ]);
      setFamilies(familiesRes.data);
      setStudents(studentsRes.data);
      setTeachers(teachersRes.data);
    } catch (err) {
      console.error('Failed to fetch data:', err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateFamily = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createFamily(familyForm);
      setFamilyForm({ family_number: '', parent_name: '', parent_email: '' });
      fetchData();
    } catch (err) {
      console.error('Failed to create family:', err);
    }
  };

  const handleCreateStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createStudent({
        ...studentForm,
        family_id: Number(studentForm.family_id),
        hourly_rate: Number(studentForm.hourly_rate),
      });
      setStudentForm({ name: '', email: '', family_id: '', hourly_rate: '' });
      fetchData();
    } catch (err) {
      console.error('Failed to create student:', err);
    }
  };

  const handleCreateTeacher = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createTeacher({
        ...teacherForm,
        hourly_rate: Number(teacherForm.hourly_rate),
      });
      setTeacherForm({ name: '', email: '', hourly_rate: '', subject_specialties: '' });
      fetchData();
    } catch (err) {
      console.error('Failed to create teacher:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Families</CardTitle>
            <Home className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{families.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Students</CardTitle>
            <GraduationCap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{students.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Teachers</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{teachers.length}</div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="families" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="families">Families</TabsTrigger>
          <TabsTrigger value="students">Students</TabsTrigger>
          <TabsTrigger value="teachers">Teachers</TabsTrigger>
        </TabsList>

        <TabsContent value="families" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Add New Family</CardTitle>
              <CardDescription>Register a new family for student enrollment</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateFamily} className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="family_number">Family Number</Label>
                    <Input
                      id="family_number"
                      value={familyForm.family_number}
                      onChange={e => setFamilyForm({ ...familyForm, family_number: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="parent_name">Parent Name</Label>
                    <Input
                      id="parent_name"
                      value={familyForm.parent_name}
                      onChange={e => setFamilyForm({ ...familyForm, parent_name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="parent_email">Parent Email</Label>
                    <Input
                      id="parent_email"
                      type="email"
                      value={familyForm.parent_email}
                      onChange={e => setFamilyForm({ ...familyForm, parent_email: e.target.value })}
                      required
                    />
                  </div>
                </div>
                <Button type="submit">
                  <UserPlus className="h-4 w-4 mr-2" />
                  Add Family
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Registered Families</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Family Number</TableHead>
                    <TableHead>Parent Name</TableHead>
                    <TableHead>Parent Email</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {families.map(family => (
                    <TableRow key={family.id}>
                      <TableCell className="font-medium">{family.family_number}</TableCell>
                      <TableCell>{family.parent_name}</TableCell>
                      <TableCell>{family.parent_email}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="students" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Add New Student</CardTitle>
              <CardDescription>Register a new student and assign to a family</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateStudent} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="student_name">Student Name</Label>
                    <Input
                      id="student_name"
                      value={studentForm.name}
                      onChange={e => setStudentForm({ ...studentForm, name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="student_email">Student Email</Label>
                    <Input
                      id="student_email"
                      type="email"
                      value={studentForm.email}
                      onChange={e => setStudentForm({ ...studentForm, email: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="family_id">Family</Label>
                    <select
                      id="family_id"
                      value={studentForm.family_id}
                      onChange={e => setStudentForm({ ...studentForm, family_id: e.target.value })}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2"
                      required
                    >
                      <option value="">Select a family</option>
                      {families.map(family => (
                        <option key={family.id} value={family.id}>
                          {family.family_number} - {family.parent_name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="student_rate">Hourly Rate ($)</Label>
                    <Input
                      id="student_rate"
                      type="number"
                      step="0.01"
                      value={studentForm.hourly_rate}
                      onChange={e => setStudentForm({ ...studentForm, hourly_rate: e.target.value })}
                      required
                    />
                  </div>
                </div>
                <Button type="submit">
                  <UserPlus className="h-4 w-4 mr-2" />
                  Add Student
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Registered Students</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Student Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Family ID</TableHead>
                    <TableHead>Hourly Rate</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {students.map(student => (
                    <TableRow key={student.id}>
                      <TableCell className="font-medium">{student.name}</TableCell>
                      <TableCell>{student.email}</TableCell>
                      <TableCell>{student.family_id}</TableCell>
                      <TableCell>${student.hourly_rate.toFixed(2)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="teachers" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Add New Teacher</CardTitle>
              <CardDescription>Register a new teacher with their specialties</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateTeacher} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="teacher_name">Teacher Name</Label>
                    <Input
                      id="teacher_name"
                      value={teacherForm.name}
                      onChange={e => setTeacherForm({ ...teacherForm, name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="teacher_email">Teacher Email</Label>
                    <Input
                      id="teacher_email"
                      type="email"
                      value={teacherForm.email}
                      onChange={e => setTeacherForm({ ...teacherForm, email: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="teacher_rate">Hourly Rate ($)</Label>
                    <Input
                      id="teacher_rate"
                      type="number"
                      step="0.01"
                      value={teacherForm.hourly_rate}
                      onChange={e => setTeacherForm({ ...teacherForm, hourly_rate: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="specialties">Subject Specialties</Label>
                    <Input
                      id="specialties"
                      value={teacherForm.subject_specialties}
                      onChange={e => setTeacherForm({ ...teacherForm, subject_specialties: e.target.value })}
                      placeholder="Math, Science, English"
                    />
                  </div>
                </div>
                <Button type="submit">
                  <UserPlus className="h-4 w-4 mr-2" />
                  Add Teacher
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Registered Teachers</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Teacher Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Hourly Rate</TableHead>
                    <TableHead>Specialties</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {teachers.map(teacher => (
                    <TableRow key={teacher.id}>
                      <TableCell className="font-medium">{teacher.name}</TableCell>
                      <TableCell>{teacher.email}</TableCell>
                      <TableCell>${teacher.hourly_rate.toFixed(2)}</TableCell>
                      <TableCell>{teacher.subject_specialties || '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
