"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function StudentsPage() {
  const [studentsData, setStudentsData] = useState<any[]>([]);
  const [myCourses, setMyCourses] = useState<{ course_id: string; course_name: string }[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCourse, setSelectedCourse] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [studentsRes, coursesRes] = await Promise.all([
          fetch("/api/students"),
          fetch("/api/my-courses"),
        ]);
        if (studentsRes.ok) {
          setStudentsData(await studentsRes.json());
        }
        if (coursesRes.ok) {
          setMyCourses(await coursesRes.json());
        }
      } catch (error) {
        console.error("Failed to fetch data:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case "High":
        return <Badge variant="destructive" className="bg-red-500 hover:bg-red-600">High Risk</Badge>;
      case "Moderate":
        return <Badge variant="default" className="bg-amber-500 hover:bg-amber-600 text-white">Moderate Risk</Badge>;
      case "Low":
        return <Badge variant="default" className="bg-emerald-500 hover:bg-emerald-600 text-white">Low Risk</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Student Roster</h1>
          <p className="text-muted-foreground mt-1">View and manage all students in your courses.</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
          <Select value={selectedCourse} onValueChange={setSelectedCourse}>
            <SelectTrigger className="w-full sm:w-[220px] bg-white">
              <SelectValue placeholder="All Courses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Courses</SelectItem>
              {myCourses.map((course) => (
                <SelectItem key={course.course_id} value={course.course_id}>
                  {course.course_id} — {course.course_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search by name or ID..."
              className="pl-8 bg-white"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Enrolled Students</CardTitle>
          <CardDescription>A comprehensive list of students and their current academic standing.</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-4 text-slate-500">Loading...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Student Name</TableHead>
                  <TableHead>Student ID</TableHead>
                  <TableHead>Course ID</TableHead>
                  <TableHead>Absences</TableHead>
                  <TableHead>Past Failures</TableHead>
                  <TableHead>Risk Level</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {studentsData
                  .filter((student) => selectedCourse === "all" || student.courseId === selectedCourse)
                  .filter((student) => 
                    student.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                    student.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
                    (student.courseId && student.courseId.toLowerCase().includes(searchQuery.toLowerCase()))
                  )
                  .map((student, index) => (
                  <TableRow key={`${student.id}-${index}`}>
                    <TableCell className="font-medium">{student.name}</TableCell>
                    <TableCell>{student.id}</TableCell>
                    <TableCell>{student.courseId}</TableCell>
                    <TableCell>{student.absences}</TableCell>
                    <TableCell>{student.pastFailures}</TableCell>
                    <TableCell>{getRiskBadge(student.riskLevel)}</TableCell>
                    <TableCell className="text-right">
                      <Link href={`/students/${student.id}`}>
                        <Button variant="outline" size="sm">
                          View Details
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
