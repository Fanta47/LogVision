"use client";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, LineChart, Line } from "recharts";
const trend = [
  { t: "00:00", anomalies: 4, logs: 1200 }, { t: "04:00", anomalies: 7, logs: 1550 }, { t: "08:00", anomalies: 18, logs: 3200 }, { t: "12:00", anomalies: 12, logs: 2800 }, { t: "16:00", anomalies: 31, logs: 4100 }, { t: "20:00", anomalies: 14, logs: 2600 },
];
const health = [
  { t: "Mon", score: 96 }, { t: "Tue", score: 94 }, { t: "Wed", score: 91 }, { t: "Thu", score: 95 }, { t: "Fri", score: 88 }, { t: "Sat", score: 93 }, { t: "Sun", score: 94 },
];
export function AnomalyTrendChart() { return <div className="glass-card rounded-lg p-5"><h2 className="mb-4 text-sm font-semibold">Anomalies over time</h2><div className="h-72"><ResponsiveContainer width="100%" height="100%"><AreaChart data={trend}><CartesianGrid strokeDasharray="3 3" opacity={0.15}/><XAxis dataKey="t" tick={{ fill: "#94a3b8", fontSize: 11 }}/><YAxis tick={{ fill: "#94a3b8", fontSize: 11 }}/><Tooltip contentStyle={{ background: "#151923", border: "1px solid rgba(255,255,255,.08)", color: "white" }}/><Area type="monotone" dataKey="anomalies" stroke="currentColor" fill="currentColor" fillOpacity={0.15}/></AreaChart></ResponsiveContainer></div></div>; }
export function SystemHealthChart() { return <div className="glass-card rounded-lg p-5"><h2 className="mb-4 text-sm font-semibold">System health</h2><div className="h-72"><ResponsiveContainer width="100%" height="100%"><LineChart data={health}><CartesianGrid strokeDasharray="3 3" opacity={0.15}/><XAxis dataKey="t" tick={{ fill: "#94a3b8", fontSize: 11 }}/><YAxis domain={[80,100]} tick={{ fill: "#94a3b8", fontSize: 11 }}/><Tooltip contentStyle={{ background: "#151923", border: "1px solid rgba(255,255,255,.08)", color: "white" }}/><Line type="monotone" dataKey="score" stroke="currentColor" strokeWidth={2}/></LineChart></ResponsiveContainer></div></div>; }
