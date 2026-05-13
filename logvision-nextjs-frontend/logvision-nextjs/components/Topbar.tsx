"use client";
import { Search, LogOut, Bell } from "lucide-react";
import { useRouter } from "next/navigation";
import { logout, roleLabel, SessionUser } from "@/lib/auth";
export function Topbar({ user }: { user: SessionUser }) {
  const router = useRouter();
  return <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-surface px-6">
    <div className="relative"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><input placeholder="Search logs, anomalies, dashboards..." className="h-8 w-80 rounded-md bg-secondary pl-9 pr-4 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary" /></div>
    <div className="flex items-center gap-4"><Bell className="h-4 w-4 text-muted-foreground" /><div className="flex items-center gap-2"><div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/20 text-xs font-bold text-primary">{user.initials}</div><div className="hidden flex-col leading-tight md:flex"><span className="text-xs font-medium">{user.name}</span><span className="text-[10px] text-muted-foreground">{roleLabel(user.role)}</span></div><span className="rounded bg-primary/15 px-1.5 py-0.5 text-[10px] font-bold uppercase text-primary">{user.role}</span></div><button onClick={() => { logout(); router.push("/login"); }} className="text-muted-foreground hover:text-foreground"><LogOut className="h-4 w-4" /></button></div>
  </header>;
}
