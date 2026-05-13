import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
export function StatCard({ title, value, change, changeType = "neutral", icon: Icon, iconColor }: { title: string; value: string; change?: string; changeType?: "positive" | "negative" | "neutral"; icon: LucideIcon; iconColor?: string; }) {
  return <div className="glass-card rounded-lg p-5">
    <div className="flex items-start justify-between">
      <div><p className="text-xs uppercase tracking-wider text-muted-foreground">{title}</p><p className="mt-2 text-2xl font-bold text-foreground">{value}</p>{change && <p className={cn("mt-1 text-xs", changeType === "positive" ? "text-success" : changeType === "negative" ? "text-critical" : "text-muted-foreground")}>{change}</p>}</div>
      <div className={cn("rounded-lg bg-primary/10 p-3", iconColor)}><Icon className="h-5 w-5 text-primary" /></div>
    </div>
  </div>;
}
