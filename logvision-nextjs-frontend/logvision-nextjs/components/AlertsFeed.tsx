import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { AlertTriangle, CheckCircle2, XCircle, Check } from "lucide-react";
import { toast } from "sonner";

interface Alert {
  id: string;
  severity: "critical" | "warning" | "normal";
  type: string;
  app: string;
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

const initialAlerts: Alert[] = [
  { id: "1", severity: "critical", type: "Crash Prediction", app: "payment-svc", message: "Crash probability at 92% — memory leak pattern detected", timestamp: "2 min ago", acknowledged: false },
  { id: "2", severity: "critical", type: "Anomaly Detected", app: "risk-engine", message: "GPU utilization anomaly on node gpu-03 — inference failures rising", timestamp: "5 min ago", acknowledged: false },
  { id: "3", severity: "warning", type: "Performance Degradation", app: "auth-svc", message: "P99 latency exceeds 3s threshold for token refresh endpoint", timestamp: "12 min ago", acknowledged: false },
  { id: "4", severity: "warning", type: "Error Rate Spike", app: "ledger-svc", message: "Error rate increased 340% in last 15 minutes", timestamp: "18 min ago", acknowledged: true },
  { id: "5", severity: "normal", type: "Recovery", app: "api-gateway", message: "Rate limiter recovered — normal throughput restored", timestamp: "25 min ago", acknowledged: true },
  { id: "6", severity: "critical", type: "Security", app: "compliance-svc", message: "External KYC provider returning 503 — failover initiated", timestamp: "30 min ago", acknowledged: false },
  { id: "7", severity: "warning", type: "Resource Warning", app: "scheduler", message: "Disk usage at 87% on node batch-worker-02", timestamp: "45 min ago", acknowledged: true },
  { id: "8", severity: "normal", type: "Deployment", app: "notification-svc", message: "v2.4.1 deployment completed successfully", timestamp: "1 hr ago", acknowledged: true },
];

const severityConfig = {
  critical: { dot: "status-dot-critical", bg: "border-l-critical", icon: XCircle, iconClass: "text-destructive" },
  warning: { dot: "status-dot-warning", bg: "border-l-warning", icon: AlertTriangle, iconClass: "text-warning" },
  normal: { dot: "status-dot-success", bg: "border-l-success", icon: CheckCircle2, iconClass: "text-success" },
};

export function AlertsFeed() {
  const [alerts, setAlerts] = useState<Alert[]>(initialAlerts);

  const acknowledge = (a: Alert) => {
    setAlerts((rows) => rows.map((r) => (r.id === a.id ? { ...r, acknowledged: true } : r)));
    toast.success(`Acknowledged: ${a.type} (${a.app})`);
  };

  return (
    <div className="space-y-2">
      {alerts.map((alert) => {
        const config = severityConfig[alert.severity];
        const Icon = config.icon as any;
        return (
          <div
            key={alert.id}
            className={cn(
              "glass-card flex items-start gap-3 rounded-lg border-l-2 p-4 transition-colors hover:bg-accent/30",
              config.bg
            )}
          >
            <Icon className={cn("mt-0.5 h-4 w-4 shrink-0", config.iconClass)} />
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-foreground">{alert.type}</span>
                <span className="text-[10px] text-muted-foreground">•</span>
                <span className="text-[10px] font-medium text-primary">{alert.app}</span>
                {alert.acknowledged && (
                  <span className="rounded-full bg-success/15 px-1.5 py-0.5 text-[9px] font-bold uppercase text-success">ACK</span>
                )}
              </div>
              <p className="mt-1 text-xs leading-relaxed text-muted-foreground">{alert.message}</p>
              <p className="mt-1 text-[10px] text-muted-foreground/60">{alert.timestamp}</p>
            </div>
            {!alert.acknowledged && (
              <button
                onClick={() => acknowledge(alert)}
                title="Acknowledge"
                className="shrink-0 rounded-md border border-border bg-secondary px-2 py-1 text-[10px] font-semibold text-foreground transition-colors hover:bg-primary hover:text-primary-foreground"
              >
                <Check className="inline h-3 w-3" /> Ack
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default AlertsFeed;
"use client";

import { cn } from "@/lib/utils";
import { AlertTriangle, CheckCircle2, XCircle, Check } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

interface Alert {
  id: string;
  severity: "critical" | "warning" | "normal";
  type: string;
  app: string;
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

const initialAlerts: Alert[] = [
  { id: "1", severity: "critical", type: "Crash Prediction", app: "payment-svc", message: "Crash probability at 92% — memory leak pattern detected", timestamp: "2 min ago", acknowledged: false },
  { id: "2", severity: "critical", type: "Anomaly Detected", app: "risk-engine", message: "GPU utilization anomaly on node gpu-03 — inference failures rising", timestamp: "5 min ago", acknowledged: false },
  { id: "3", severity: "warning", type: "Performance Degradation", app: "auth-svc", message: "P99 latency exceeds 3s threshold for token refresh endpoint", timestamp: "12 min ago", acknowledged: false },
  { id: "4", severity: "warning", type: "Error Rate Spike", app: "ledger-svc", message: "Error rate increased 340% in last 15 minutes", timestamp: "18 min ago", acknowledged: true },
  { id: "5", severity: "normal", type: "Recovery", app: "api-gateway", message: "Rate limiter recovered — normal throughput restored", timestamp: "25 min ago", acknowledged: true },
  { id: "6", severity: "critical", type: "Security", app: "compliance-svc", message: "External KYC provider returning 503 — failover initiated", timestamp: "30 min ago", acknowledged: false },
  { id: "7", severity: "warning", type: "Resource Warning", app: "scheduler", message: "Disk usage at 87% on node batch-worker-02", timestamp: "45 min ago", acknowledged: true },
  { id: "8", severity: "normal", type: "Deployment", app: "notification-svc", message: "v2.4.1 deployment completed successfully", timestamp: "1 hr ago", acknowledged: true },
];

const severityConfig = {
  critical: { bg: "border-l-critical", icon: XCircle, iconClass: "text-critical" },
  warning: { bg: "border-l-warning", icon: AlertTriangle, iconClass: "text-warning" },
  normal: { bg: "border-l-success", icon: CheckCircle2, iconClass: "text-success" },
};

export function AlertsFeed() {
  const [alerts, setAlerts] = useState<Alert[]>(initialAlerts);

  const acknowledge = (a: Alert) => {
    setAlerts((rows) => rows.map((r) => (r.id === a.id ? { ...r, acknowledged: true } : r)));
    toast.success(`Acknowledged: ${a.type} (${a.app})`);
  };

  return (
    <div className="space-y-2">
      {alerts.map((alert) => {
        const config = severityConfig[alert.severity];
        const Icon = config.icon;
        return (
          <div key={alert.id} className={cn("glass-card flex items-start gap-3 rounded-lg border-l-2 p-4 transition-colors hover:bg-accent/30", config.bg)}>
            <Icon className={cn("mt-0.5 h-4 w-4 shrink-0", config.iconClass)} />
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-foreground">{alert.type}</span>
                <span className="text-[10px] text-muted-foreground">•</span>
                <span className="text-[10px] font-medium text-primary">{alert.app}</span>
                {alert.acknowledged && <span className="rounded-full bg-success/15 px-1.5 py-0.5 text-[9px] font-bold uppercase text-success">ACK</span>}
              </div>
              <p className="mt-1 text-xs leading-relaxed text-muted-foreground">{alert.message}</p>
              <p className="mt-1 text-[10px] text-muted-foreground/60">{alert.timestamp}</p>
            </div>
            {!alert.acknowledged && (
              <button onClick={() => acknowledge(alert)} title="Acknowledge" className="shrink-0 rounded-md border border-border bg-secondary px-2 py-1 text-[10px] font-semibold text-foreground transition-colors hover:bg-primary hover:text-primary-foreground">
                <Check className="inline h-3 w-3" /> Ack
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
