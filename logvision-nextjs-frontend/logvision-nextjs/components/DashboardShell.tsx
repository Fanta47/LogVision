"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { usePathname } from "next/navigation";
import { getSession, SessionUser } from "@/lib/auth";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
export function DashboardShell({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<SessionUser | null>(null);
  const router = useRouter();
  const pathname = usePathname();
  useEffect(() => {
    const s = getSession();
    if (!s) {
      router.push("/login");
      return;
    }
    setUser(s);
    if (pathname === "/dashboard" && s.role === "admin") {
      router.push("/dashboard/admin/system");
      return;
    }
    if (pathname === "/dashboard" && s.role === "manager") {
      router.push("/dashboard/manager");
      return;
    }
  }, [router, pathname]);
  if (!user) {
    return <div className="flex min-h-screen items-center justify-center text-sm text-muted-foreground">Loading dashboard...</div>;
  }
  return <div className="flex h-screen overflow-hidden"><Sidebar role={user.role} /><div className="flex flex-1 flex-col overflow-hidden"><Topbar user={user} /><main className="flex-1 overflow-y-auto p-6">{children}</main></div></div>;
}
