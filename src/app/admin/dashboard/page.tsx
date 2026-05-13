import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ShieldAlert, CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { revalidatePath } from "next/cache";
import { logoutAction } from "@/actions/auth";

async function getPendingFaculty(token: string) {
  try {
    console.log("Fetching pending faculty with token:", token.substring(0, 20) + "...");
    const res = await fetch("http://127.0.0.1:8000/api/admin/pending-faculty", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    });
    console.log("getPendingFaculty status:", res.status, res.statusText);
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        console.log("Unauthorized or forbidden:", res.status);
        return null;
      }
      const errText = await res.text();
      console.error("Failed to fetch pending faculty. Status:", res.status, "Body:", errText);
      throw new Error("Failed to fetch pending faculty");
    }
    const data = await res.json();
    console.log("getPendingFaculty data:", data);
    return data;
  } catch (error) {
    console.error("Error in getPendingFaculty:", error);
    return [];
  }
}

async function approveFaculty(userId: number, token: string) {
  "use server";
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/admin/approve-faculty/${userId}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (res.ok) {
      revalidatePath("/admin/dashboard");
    }
  } catch (error) {
    console.error("Approval failed", error);
  }
}

export default async function AdminDashboardPage() {
  const cookieStore = await cookies();
  const token = cookieStore.get("auth_token")?.value;

  if (!token) {
    redirect("/login");
  }

  const pendingFaculty = await getPendingFaculty(token);
  
  if (pendingFaculty === null) {
    redirect("/dashboard");
  }

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">HOD Admin Portal</h1>
          <p className="text-muted-foreground mt-2">Manage faculty access and department resources.</p>
        </div>
        <div className="flex gap-4">
          <Button variant="default" asChild>
            <a href="/dashboard">Faculty Dashboard</a>
          </Button>
          <form action={logoutAction}>
            <Button type="submit" variant="outline">Log out</Button>
          </form>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-500" />
            Pending Faculty Approvals
          </CardTitle>
          <CardDescription>
            Review and approve registration requests from faculty members in your department.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {pendingFaculty.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-8 text-center bg-muted/50 rounded-lg border border-dashed">
              <CheckCircle2 className="w-10 h-10 text-muted-foreground mb-3" />
              <h3 className="text-lg font-medium">All caught up!</h3>
              <p className="text-sm text-muted-foreground">There are no pending faculty registration requests.</p>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Department</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {pendingFaculty.map((faculty: any) => (
                    <TableRow key={faculty.id}>
                      <TableCell className="font-medium">{faculty.name}</TableCell>
                      <TableCell>{faculty.email}</TableCell>
                      <TableCell className="capitalize">{faculty.department}</TableCell>
                      <TableCell className="text-right">
                        <form action={async () => {
                          "use server";
                          await approveFaculty(faculty.id, token);
                        }}>
                          <Button size="sm" type="submit">
                            Approve Access
                          </Button>
                        </form>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
