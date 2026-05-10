import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { UserCircle } from "lucide-react";

export default async function ProfilePage() {
  const cookieStore = await cookies();
  const token = cookieStore.get("auth_token")?.value;

  if (!token) {
    redirect("/login");
  }

  let payload;
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map(function (c) {
          return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join("")
    );
    payload = JSON.parse(jsonPayload);
  } catch (error) {
    payload = { sub: "Unknown" };
  }

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Faculty Profile</h1>
        <p className="text-muted-foreground mt-2">View your personal details and role information.</p>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center gap-4">
          <UserCircle className="w-16 h-16 text-primary" />
          <div>
            <CardTitle className="text-2xl">{payload.sub}</CardTitle>
            <CardDescription className="capitalize mt-1">
              {payload.role} • {payload.department} Department
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 mt-4">
            <div className="grid grid-cols-3 gap-4 border-b pb-4">
              <div className="text-sm font-medium text-muted-foreground">Email</div>
              <div className="col-span-2 font-medium">{payload.sub}</div>
            </div>
            <div className="grid grid-cols-3 gap-4 border-b pb-4">
              <div className="text-sm font-medium text-muted-foreground">Department</div>
              <div className="col-span-2 font-medium uppercase">{payload.department}</div>
            </div>
            <div className="grid grid-cols-3 gap-4 border-b pb-4">
              <div className="text-sm font-medium text-muted-foreground">Role</div>
              <div className="col-span-2 font-medium capitalize">{payload.role}</div>
            </div>
            <div className="grid grid-cols-3 gap-4 pb-4">
              <div className="text-sm font-medium text-muted-foreground">Status</div>
              <div className="col-span-2 font-medium capitalize text-green-600">{payload.status || 'Approved'}</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
