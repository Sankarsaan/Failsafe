"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { ArrowLeft, AlertTriangle, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Cell } from "recharts";

// Maps SHAP feature names to actionable faculty interventions
const INTERVENTION_MAP: Record<string, { title: string; action: string }> = {
  "Absences": {
    title: "Address High Absenteeism",
    action: "Contact the student directly to understand reasons for absences. Schedule a 1-on-1 meeting and set an attendance improvement plan.",
  },
  "Past Failures": {
    title: "Review Academic History",
    action: "Discuss previous failure patterns with the student. Recommend supplemental tutoring and assign structured practice exercises.",
  },
  "Study Time": {
    title: "Improve Study Habits",
    action: "Guide the student on effective study schedules. Share resources on time-management techniques and connect them with study groups.",
  },
  "Alcohol Consumption": {
    title: "Student Wellness Check",
    action: "Discretely refer the student to the campus wellness or counselling center for well-being support.",
  },
  "Health": {
    title: "Health & Wellness Support",
    action: "Encourage the student to visit campus health services and discuss any chronic issues affecting their attendance or focus.",
  },
  "Family Relationship": {
    title: "Social & Family Support",
    action: "Refer the student to student affairs or counselling services for personal support outside academics.",
  },
  "Has Family Support": {
    title: "Strengthen Support Network",
    action: "Encourage the student to communicate with family about academic goals. Share parental engagement resources if available.",
  },
  "No Family Support": {
    title: "Peer Mentoring",
    action: "Connect the student with a senior peer mentor or faculty advisor to provide the social support they may lack at home.",
  },
  "Free Time": {
    title: "Structured Free Time",
    action: "Help the student channel excess unstructured time into productive activities like study groups, labs, or clubs.",
  },
  "Parents Job Status": {
    title: "Socioeconomic Support",
    action: "Check if the student qualifies for financial aid or scholarships. Refer to student services for economic assistance programs.",
  },
  "Parents Education": {
    title: "Academic Guidance",
    action: "Provide additional academic orientation. Students from lower parental education backgrounds may need more structured guidance.",
  },
  "Wants Higher Education": {
    title: "Motivational Counselling",
    action: "Discuss career pathways and goals with the student. Help them understand the long-term value of academic performance.",
  },
  "No Higher Ed Goals": {
    title: "Career Awareness Session",
    action: "Arrange a career counselling session to help the student identify motivating goals tied to their field of study.",
  },
  "Has Internet": {
    title: "Digital Resource Access",
    action: "Ensure the student is utilizing online learning resources effectively. Share curated links for the course.",
  },
  "No Internet": {
    title: "Digital Access Support",
    action: "Help the student access campus computer labs or apply for internet subsidies. Share offline study materials.",
  },
  "Extracurriculars": {
    title: "Manage Extracurricular Load",
    action: "If overcommitted, help the student prioritize activities. If underengaged, suggest study-related clubs for peer learning.",
  },
  "No Extracurriculars": {
    title: "Encourage Engagement",
    action: "Suggest the student join academic clubs or peer study groups to improve motivation and social connections.",
  },
  "In Relationship": {
    title: "Work-Life Balance",
    action: "Have a supportive conversation about balancing personal life with academic commitments.",
  },
  "School & Paid Support": {
    title: "Leverage Existing Support",
    action: "Ensure the student is attending all tutoring and school support sessions. Monitor if current support is effective.",
  },
  "School Support Only": {
    title: "Optimize School Support",
    action: "Review whether current school support sessions align with the student's weak areas and adjust accordingly.",
  },
};

function getIntervention(featureName: string): { title: string; action: string } {
  if (INTERVENTION_MAP[featureName]) return INTERVENTION_MAP[featureName];
  return {
    title: `Address: ${featureName}`,
    action: `This factor is significantly increasing the student's risk score. Discuss this area with the student and create a targeted improvement plan.`,
  };
}

const RANK_STYLES = [
  "bg-red-50 border-red-200",
  "bg-amber-50 border-amber-200",
  "bg-yellow-50 border-yellow-200",
];

const RANK_BADGE_CLASSES = [
  "bg-red-500 hover:bg-red-500 text-white text-xs shrink-0",
  "bg-amber-500 hover:bg-amber-500 text-white text-xs shrink-0",
  "bg-yellow-500 hover:bg-yellow-500 text-white text-xs shrink-0",
];

const RANK_LABELS = ["⚠ Priority 1", "Priority 2", "Priority 3"];

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

  // Top 3 risk-increasing SHAP factors (positive impact, sorted high → low)
  const top3: { feature: string; impact: number }[] = (student.shapData ?? [])
    .filter((d: any) => d.impact > 0)
    .sort((a: any, b: any) => b.impact - a.impact)
    .slice(0, 3);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/students">
          <Button variant="outline" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">{student.name}</h1>
          <p className="text-muted-foreground mt-1">Student ID: {student.id}</p>
        </div>
        <div className="ml-auto">
          <Badge
            className={
              student.riskLevel === "High"
                ? "bg-red-500 hover:bg-red-500 text-sm py-1 px-3"
                : student.riskLevel === "Moderate"
                ? "bg-amber-500 hover:bg-amber-500 text-sm py-1 px-3"
                : "bg-emerald-500 hover:bg-emerald-500 text-sm py-1 px-3"
            }
          >
            Risk Score: {student.riskScore}/100
          </Badge>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* SHAP Chart */}
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle>Explainable AI (SHAP Values)</CardTitle>
            <CardDescription>
              Factors contributing to the ML model&apos;s risk assessment. Positive values increase risk, negative values decrease it.
            </CardDescription>
          </CardHeader>
          <CardContent className="h-[380px] flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={student.shapData}
                margin={{ top: 20, right: 30, left: 40, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" />
                <XAxis type="number" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis dataKey="feature" type="category" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} width={130} />
                <RechartsTooltip
                  cursor={{ fill: "transparent" }}
                  contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                  formatter={(value: any) => [Number(value).toFixed(3), "SHAP Impact"]}
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

        {/* Intervention Plan — dynamic top 3 risk drivers */}
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-red-500" />
              Intervention Plan
            </CardTitle>
            <CardDescription>
              Top 3 attributes most responsible for elevating this student&apos;s risk. Address these first for maximum impact.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1">
            {top3.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center py-10 text-slate-500">
                <AlertTriangle className="h-8 w-8 mb-3 text-emerald-400" />
                <p className="font-medium text-slate-700">No significant risk factors detected.</p>
                <p className="text-sm mt-1">This student has a low or moderate risk profile with no dominant risk drivers.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {top3.map((factor, idx) => {
                  const intervention = getIntervention(factor.feature);
                  return (
                    <div
                      key={factor.feature}
                      className={`p-4 rounded-lg border ${RANK_STYLES[idx]}`}
                    >
                      <div className="flex items-start justify-between gap-2 mb-1.5">
                        <p className="text-sm font-semibold text-slate-800 leading-tight">{intervention.title}</p>
                        <Badge className={RANK_BADGE_CLASSES[idx]}>{RANK_LABELS[idx]}</Badge>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed">{intervention.action}</p>
                      <p className="text-xs text-slate-400 mt-2 font-mono">
                        SHAP: <span className="text-red-600 font-semibold">+{factor.impact.toFixed(3)}</span>
                        <span className="mx-1.5">·</span>
                        Attribute: <span className="text-slate-500 font-medium not-italic">{factor.feature}</span>
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
