"use client";
import { useEffect, useState } from "react";
import { Activity, AlertTriangle, Cpu, FileText } from "lucide-react";
import { StatCard } from "@/components/StatCard";
import { AnomalyTrendChart, SystemHealthChart } from "@/components/Charts";
import { getDashboardSummary, DashboardSummary } from "@/lib/api";

const fallback: DashboardSummary = {
  total_events: 0,
  total_uploads: 0,
  total_anomalies: 0,
  high_risk_anomalies: 0,
  latest_model: "ensemble_logbert_like:v1",
  health_score: 94.2,
};

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary>(fallback);

  useEffect(() => {
    getDashboardSummary().then(setSummary).catch(() => setSummary(fallback));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold">Operational overview</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          FastAPI, Elasticsearch, PostgreSQL and LogBERT anomaly detection summary.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total events"
          value={summary.total_events?.toLocaleString() ?? "0"}
          change="PostgreSQL base_event"
          icon={FileText}
        />
        <StatCard
          title="Uploads"
          value={summary.total_uploads?.toLocaleString() ?? "0"}
          change="Frontend ingestion"
          changeType="positive"
          icon={Activity}
        />
        <StatCard
          title="Anomalies"
          value={summary.total_anomalies?.toLocaleString() ?? "0"}
          change={`${summary.high_risk_anomalies ?? 0} high risk`}
          changeType="negative"
          icon={AlertTriangle}
          iconColor="bg-warning/10"
        />
        <StatCard
          title="Health"
          value={`${summary.health_score ?? 94.2}%`}
          change={summary.latest_model || "Latest model"}
          changeType="positive"
          icon={Cpu}
          iconColor="bg-success/10"
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <AnomalyTrendChart />
        <SystemHealthChart />
      </div>

      <div className="glass-card animate-slide-up rounded-lg p-5">
        <h2 className="text-sm font-semibold">LogVision data flow</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Frontend upload {"->"} FastAPI {"->"} uploads/raw/app/component/upload_uid.log {"->"} Logstash {"->"}
          Elasticsearch {"->"} ETL {"->"} PostgreSQL {"->"} ML service {"->"} Kibana.
        </p>
      </div>
    </div>
  );
}
