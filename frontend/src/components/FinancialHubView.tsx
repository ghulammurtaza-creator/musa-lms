'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { FamilyBilling, TeacherPayroll, getFamiliesBilling, getTeachersPayroll } from '@/lib/api';
import { formatCurrency, formatDuration } from '@/lib/utils';
import { DollarSign, Download } from 'lucide-react';

export default function FinancialHubView() {
  const [familyBillings, setFamilyBillings] = useState<FamilyBilling[]>([]);
  const [teacherPayrolls, setTeacherPayrolls] = useState<TeacherPayroll[]>([]);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [loading, setLoading] = useState(false);

  const generateReports = async () => {
    try {
      setLoading(true);
      const [familiesResponse, teachersResponse] = await Promise.all([
        getFamiliesBilling(selectedYear, selectedMonth),
        getTeachersPayroll(selectedYear, selectedMonth),
      ]);
      setFamilyBillings(familiesResponse.data);
      setTeacherPayrolls(teachersResponse.data);
    } catch (err) {
      console.error('Failed to generate financial reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const totalFamilyBilling = familyBillings.reduce((sum, fb) => sum + fb.total_family_amount, 0);
  const totalTeacherPayroll = teacherPayrolls.reduce((sum, tp) => sum + tp.total_amount, 0);
  const netRevenue = totalFamilyBilling - totalTeacherPayroll;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Generate Financial Reports</CardTitle>
          <CardDescription>Select month and year to generate billing and payroll reports</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-end">
            <div className="space-y-2">
              <Label>Year</Label>
              <select
                value={selectedYear}
                onChange={e => setSelectedYear(Number(e.target.value))}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2"
              >
                {[2024, 2025, 2026, 2027].map(year => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label>Month</Label>
              <select
                value={selectedMonth}
                onChange={e => setSelectedMonth(Number(e.target.value))}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2"
              >
                {Array.from({ length: 12 }, (_, i) => i + 1).map(month => (
                  <option key={month} value={month}>
                    {new Date(2000, month - 1).toLocaleString('default', { month: 'long' })}
                  </option>
                ))}
              </select>
            </div>
            <Button onClick={generateReports} disabled={loading}>
              {loading ? 'Generating...' : 'Generate Reports'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {(familyBillings.length > 0 || teacherPayrolls.length > 0) && (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{formatCurrency(totalFamilyBilling)}</div>
                <p className="text-xs text-muted-foreground">From {familyBillings.length} families</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Expenses</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{formatCurrency(totalTeacherPayroll)}</div>
                <p className="text-xs text-muted-foreground">For {teacherPayrolls.length} teachers</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Net Revenue</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">{formatCurrency(netRevenue)}</div>
                <p className="text-xs text-muted-foreground">
                  {netRevenue >= 0 ? 'Profit' : 'Loss'} for the month
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Family Billing</CardTitle>
                  <CardDescription>Consolidated billing by family for the selected month</CardDescription>
                </div>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {familyBillings.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">No billing data for this period</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Family #</TableHead>
                      <TableHead>Parent Name</TableHead>
                      <TableHead>Parent Email</TableHead>
                      <TableHead>Students</TableHead>
                      <TableHead>Total Hours</TableHead>
                      <TableHead className="text-right">Amount</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {familyBillings.map(billing => (
                      <TableRow key={billing.family_id}>
                        <TableCell className="font-medium">{billing.family_number}</TableCell>
                        <TableCell>{billing.parent_name}</TableCell>
                        <TableCell>{billing.parent_email}</TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            {billing.students.map(student => (
                              <div key={student.student_id} className="text-sm">
                                {student.student_name} ({formatDuration(student.total_minutes)})
                              </div>
                            ))}
                          </div>
                        </TableCell>
                        <TableCell>
                          {formatDuration(
                            billing.students.reduce((sum, s) => sum + s.total_minutes, 0)
                          )}
                        </TableCell>
                        <TableCell className="text-right font-bold">
                          {formatCurrency(billing.total_family_amount)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Teacher Payroll</CardTitle>
                  <CardDescription>Payroll summary for all teachers for the selected month</CardDescription>
                </div>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {teacherPayrolls.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">No payroll data for this period</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Teacher Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Total Hours</TableHead>
                      <TableHead>Hourly Rate</TableHead>
                      <TableHead className="text-right">Total Amount</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {teacherPayrolls.map(payroll => (
                      <TableRow key={payroll.teacher_id}>
                        <TableCell className="font-medium">{payroll.teacher_name}</TableCell>
                        <TableCell>{payroll.teacher_email}</TableCell>
                        <TableCell>{formatDuration(payroll.total_minutes)}</TableCell>
                        <TableCell>{formatCurrency(payroll.hourly_rate)}/hr</TableCell>
                        <TableCell className="text-right font-bold">
                          {formatCurrency(payroll.total_amount)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
