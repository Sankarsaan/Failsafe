"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Users, UploadCloud, AlertCircle, LogOut, ShieldAlert } from "lucide-react";
import { logoutAction } from "@/actions/auth";

const baseNavItems = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/students", icon: Users, label: "Students" },
  { href: "/upload", icon: UploadCloud, label: "Upload Data" },
];

export function Sidebar({ role }: { role?: string }) {
  const pathname = usePathname();

  const navItems = [...baseNavItems];
  if (role === "admin") {
    navItems.push({ href: "/admin/dashboard", icon: ShieldAlert, label: "HOD Portal" });
  }

  return (
    <aside className="w-64 bg-white border-r min-h-screen flex flex-col hidden md:flex">
      <div className="h-16 flex items-center px-6 border-b font-bold text-xl text-primary tracking-tight">
        <Link href="/profile" className="hover:opacity-80 transition-opacity">FAILSAFE</Link>
      </div>
      <nav className="flex-1 px-4 py-6 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-slate-100 hover:text-foreground"
              }`}
            >
              <Icon className="w-5 h-5 mr-3" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t">
        <form action={logoutAction}>
          <button
            type="submit"
            className="flex w-full items-center px-3 py-2.5 rounded-md text-sm font-medium text-muted-foreground hover:bg-red-50 hover:text-red-600 transition-colors"
          >
            <LogOut className="w-5 h-5 mr-3" />
            Log out
          </button>
        </form>
      </div>
    </aside>
  );
}
