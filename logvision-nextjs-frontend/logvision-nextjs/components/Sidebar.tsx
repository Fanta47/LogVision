"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Upload, Search, AlertTriangle, Brain, Activity, Gauge, Settings, User, ChevronLeft, ChevronRight, FileText, Siren, ShieldAlert, Users, Shield, Bell, Server, Settings2 } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Role } from "@/lib/auth";
import { VermegLogo } from "./VermegLogo";

type NavItem = {
  label: string;
  href: string;
  icon: any;
  roles: Role[];
};

const nav: NavItem[] = [
  { label: "Overview", href: "/dashboard", icon: BarChart3, roles: ["user", "manager", "admin"] },
  { label: "Ingestion", href: "/dashboard/ingest", icon: Upload, roles: ["user", "admin"] },
  { label: "Logs", href: "/dashboard/logs", icon: Search, roles: ["user", "manager", "admin"] },
  { label: "Alerts", href: "/dashboard/alerts", icon: Siren, roles: ["manager", "admin"] },
  { label: "Incidents", href: "/dashboard/incidents", icon: ShieldAlert, roles: ["manager", "admin"] },
  { label: "Anomalies", href: "/dashboard/anomalies", icon: AlertTriangle, roles: ["user", "manager", "admin"] },
  { label: "Predictions", href: "/dashboard/predictions", icon: Brain, roles: ["manager", "admin"] },
  { label: "Reports", href: "/dashboard/reports", icon: FileText, roles: ["manager", "admin"] },
  { label: "Manager", href: "/dashboard/manager", icon: Users, roles: ["manager", "admin"] },
  { label: "ML Models", href: "/dashboard/models", icon: Activity, roles: ["user", "manager", "admin"] },
  { label: "Kibana", href: "/dashboard/kibana", icon: Gauge, roles: ["user", "manager", "admin"] },
  { label: "Profile", href: "/dashboard/profile", icon: User, roles: ["user", "manager", "admin"] },
  { label: "Admin System", href: "/dashboard/admin/system", icon: Server, roles: ["admin"] },
  { label: "Admin Users", href: "/dashboard/admin/users", icon: Users, roles: ["admin"] },
  { label: "Admin Roles", href: "/dashboard/admin/roles", icon: Shield, roles: ["admin"] },
  { label: "Admin Alerts", href: "/dashboard/admin/alerts", icon: Bell, roles: ["admin"] },
  { label: "Admin Config", href: "/dashboard/admin/config", icon: Settings2, roles: ["admin"] },
  { label: "Settings", href: "/dashboard/settings", icon: Settings, roles: ["admin"] },
];

export function Sidebar({ role }: { role: Role }) {
  const [collapsed, setCollapsed] = useState(false);
  const path = usePathname();
  const items = nav.filter((n) => n.roles.includes(role));

  return (
    <aside className={cn("flex h-screen flex-col border-r border-sidebar-border bg-sidebar transition-all", collapsed ? "w-16" : "w-60")}>
      <div className="flex h-16 items-center justify-center border-b border-sidebar-border px-3">
        <VermegLogo small={collapsed} />
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto p-2 pt-4">
        {items.map((item) => {
          const active = path === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                active ? "bg-sidebar-accent text-primary" : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {!collapsed && <span className="truncate">{item.label}</span>}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-sidebar-border p-2">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex w-full items-center justify-center rounded-md p-2 text-muted-foreground hover:bg-sidebar-accent hover:text-foreground"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>
    </aside>
  );
}
