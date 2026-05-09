"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Cell } from "recharts";

export default function StudentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const [student, setStudent] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStudentDetail() {
      try {
        const res = await fetch(`/api/students/${resolvedParams.id}`);
        if (res.ok) {
          const data = await res.json();
          setStudent(data);
        }
      } catch (error) {
        console.error("Failed to fetch student detail:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchStudentDetail();
  }, [resolvedParams.id]);

  if (loading) return <div className="p-8 text-center text-slate-500">Loading student details...</div>;
  if (!student) return <div className="p-8 text-center text-slate-500">Student not found</div>;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center gap-4">
        <Link href="/students">
          <Button variant="outline" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">{student.name}</h1>
          <p className="text-muted-foreground mt-1">Student ID: {student.id} | {student.major}, {student.year}</p>
        </div>
        <div className="ml-auto">
          <Badge variant="destructive" className={student.riskLevel === "High" ? "bg-red-500 text-sm py-1 px-3" : student.riskLevel === "Moderate" ? "bg-amber-500 text-sm py-1 px-3" : "bg-emerald-500 text-sm py-1 px-3"}>
            Risk Score: {student.riskScore}/100
          </Badge>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle>Explainable AI (SHAP Values)</CardTitle>
            <CardDescription>
              Factors contributing to the ML model's risk assessment. Positive values increase risk, negative values decrease it.
            </CardDescription>
          </CardHeader>
          <CardContent className="h-[350px] flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={student.shapData}
                margin={{ top: 20, right: 30, left: 40, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" />
                <XAxis type="number" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis dataKey="feature" type="category" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} width={120} />
                <RechartsTooltip 
                  cursor={{fill: 'transparent'}}
                  contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                  formatter={(value: any) => [Number(value).toFixed(2), "Impact"]}
                />
                <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
                  {student.shapData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle>Intervention Plan</CardTitle>
            <CardDescription>
              Recommended actions to support this student based on risk factors.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1">
            <div className="space-y-4">
              <div className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                <Checkbox id="task-1" className="mt-1" />
                <div className="space-y-1">
                  <Label htmlFor="task-1" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                    Schedule 1-on-1 Advising Session
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    Discuss recent drop in attendance and missed midterm.
                  </p>
                </div>
                <Badge variant="outline" className="ml-auto bg-white">Active</Badge>
              </div>

              <div className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                <Checkbox id="task-2" className="mt-1" defaultChecked />
                <div className="space-y-1">
                  <Label htmlFor="task-2" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 line-through text-slate-400">
                    Send Early Warning Email
                  </Label>
                  <p className="text-sm text-muted-foreground line-through text-slate-400">
                    Automated email sent to student regarding missed assignments.
                  </p>
                </div>
                <Badge variant="secondary" className="ml-auto">Resolved</Badge>
              </div>
              
              <div className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                <Checkbox id="task-3" className="mt-1" />
                <div className="space-y-1">
                  <Label htmlFor="task-3" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                    Refer to Tutoring Center
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    Specifically for upcoming CS201 final project.
                  </p>
                </div>
                <Badge variant="outline" className="ml-auto bg-white">Active</Badge>
              </div>
            </div>
            
            <div className="mt-6">
              <Button className="w-full">Add New Action Item</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
