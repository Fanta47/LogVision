"use client";
import { useEffect, useRef, useState, type ChangeEvent, type DragEvent } from "react";
import { AlertCircle, CheckCircle2, Clock, Upload, X } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/Button";
import { APPLICATIONS, COMPONENTS_BY_APP, ApplicationKey } from "@/lib/constants";
import { cn } from "@/lib/utils";
import { getUploads, uploadLogFile, UploadItem } from "@/lib/api";

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

const statusIcon: Record<string, any> = {
  parsed: CheckCircle2,
  uploaded: Clock,
  etl_processing: Clock,
  failed: AlertCircle,
};

export default function IngestPage() {
  const [app, setApp] = useState<ApplicationKey>("MegaCustody");
  const [component, setComponent] = useState("Persistence");
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploads, setUploads] = useState<UploadItem[]>([]);
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => { getUploads().then(setUploads).catch(() => setUploads([])); }, []);
  useEffect(() => { setComponent(COMPONENTS_BY_APP[app][0]); }, [app]);

  function accept(f?: File | null) {
    if (!f) return;
    if (!/\.(log|txt)$/i.test(f.name)) return toast.error("Only .log and .txt files are accepted.");
    setFile(f);
    toast.success(`Ready: ${f.name}`);
  }

  function drop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    accept(e.dataTransfer.files?.[0]);
  }

  function input(e: ChangeEvent<HTMLInputElement>) {
    accept(e.target.files?.[0]);
    e.target.value = "";
  }

  async function submit() {
    if (!file) return toast.error("Select a log file first.");
    setUploading(true);
    try {
      const row = await uploadLogFile({ file, applicationKey: app, componentName: component });
      setUploads((prev) => [row, ...prev]);
      toast.success(`Uploaded: ${row.upload_uid}`);
      setFile(null);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return <div className="space-y-6"><div className="flex items-center gap-3"><Upload className="h-5 w-5 text-primary"/><div><h1 className="text-xl font-bold">Log ingestion</h1><p className="mt-1 text-sm text-muted-foreground">Upload Vermeg logs into the LogVision ELK/PostgreSQL pipeline.</p></div></div>
    <div className="glass-card animate-slide-up rounded-lg p-5"><h2 className="mb-3 text-sm font-semibold">1 - Target application</h2><div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">{APPLICATIONS.map((a) => <button key={a} onClick={() => setApp(a)} className={cn("rounded-md border p-3 text-left transition", app === a ? "border-primary bg-primary/10" : "border-border bg-secondary hover:border-primary/40")}><p className={cn("text-xs font-semibold", app === a ? "text-primary" : "text-foreground")}>{a}</p><p className="mt-1 text-[10px] text-muted-foreground">Vermeg application</p></button>)}</div></div>
    <div className="glass-card animate-slide-up rounded-lg p-5"><h2 className="mb-3 text-sm font-semibold">2 - Component</h2><select value={component} onChange={(e) => setComponent(e.target.value)} className="h-10 w-full rounded-md border border-border bg-secondary px-3 text-sm outline-none focus:ring-1 focus:ring-primary">{COMPONENTS_BY_APP[app].map((c) => <option key={c} value={c}>{c}</option>)}</select><p className="mt-2 text-xs text-muted-foreground">Backend will store the file in uploads/raw/{app}/{component}/upload_uid.log</p></div>
    <div className="glass-card animate-slide-up rounded-lg p-5"><div className="mb-3 flex items-center justify-between"><h2 className="text-sm font-semibold">3 - Upload file</h2>{file && <button onClick={() => setFile(null)} className="flex items-center gap-1 text-[10px] uppercase text-muted-foreground hover:text-critical"><X className="h-3 w-3"/> Clear</button>}</div><input ref={inputRef} type="file" accept=".log,.txt" onChange={input} className="hidden"/><div onDragEnter={(e) => { e.preventDefault(); setDragActive(true); }} onDragOver={(e) => { e.preventDefault(); setDragActive(true); }} onDragLeave={(e) => { e.preventDefault(); setDragActive(false); }} onDrop={drop} onClick={() => inputRef.current?.click()} className={cn("flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-10 transition", dragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50")}><Upload className="h-8 w-8 text-primary"/><p className="mt-4 text-sm font-semibold">{file ? `${file.name} - ${formatSize(file.size)}` : "Drop .log/.txt here or click to browse"}</p><p className="mt-1 text-xs text-muted-foreground">Application: {app} - Component: {component}</p></div><Button disabled={!file || uploading} onClick={submit} className="mt-4 w-full">{uploading ? "Uploading..." : "Start ingestion"}</Button></div>
    <div className="glass-card animate-slide-up rounded-lg p-5"><h2 className="mb-3 text-sm font-semibold">Recent uploads</h2><div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="text-xs uppercase text-muted-foreground"><tr><th className="py-2">Upload UID</th><th>File</th><th>Application</th><th>Component</th><th>Status</th><th>Parsed</th></tr></thead><tbody>{uploads.map((u) => { const Icon = statusIcon[u.status] || Clock; return <tr key={u.upload_uid} className="border-t border-border"><td className="py-3 font-mono text-xs text-primary">{u.upload_uid}</td><td>{u.original_file_name}</td><td>{u.application_key}</td><td>{u.component_name}</td><td><span className="inline-flex items-center gap-1 rounded-full bg-secondary px-2 py-1 text-xs"><Icon className="h-3 w-3"/>{u.status}</span></td><td>{u.parsed_events ?? "-"}</td></tr>; })}</tbody></table></div></div>
  </div>;
}
