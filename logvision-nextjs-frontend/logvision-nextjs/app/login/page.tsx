"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Globe, Lock, Mail } from "lucide-react";
import { toast } from "sonner";
import { login } from "@/lib/auth";
import { Button } from "@/components/Button";
import { VermegAnimatedLogo } from "@/components/VermegAnimatedLogo";
import { LoginBackground } from "@/components/LoginBackground";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("user@vermeg.com");
  const [password, setPassword] = useState("demo1234");
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  function submit(e: React.FormEvent) {
    e.preventDefault(); setLoading(true);
    try { login(email, password); router.push("/dashboard"); } catch (err) { toast.error(err instanceof Error ? err.message : "Unable to sign in"); } finally { setLoading(false); }
  }
  return <div className="relative flex min-h-screen overflow-hidden">
    <LoginBackground />
    <div className="relative z-10 hidden flex-1 flex-col justify-between p-12 lg:flex">
      <div className="flex items-center"><VermegAnimatedLogo size="lg" /></div>
      <div>
        <h1 className="text-5xl font-bold leading-tight text-foreground">Analyse de logs en temps réel.<br /><span className="text-primary">Intelligence prédictive.</span></h1>
        <p className="mt-6 max-w-xl text-3 leading-relaxed text-muted-foreground">Surveillez, détectez les anomalies et anticipez les pannes. Une observabilité de niveau entreprise pour vos systèmes critiques.</p>
      </div>
      <p className="text-2 text-muted-foreground">© 2026 logVision par Vermeg. Tous droits réservés.</p>
    </div>
    <div className="absolute right-4 top-4 z-20 rounded-xl border border-white/15 bg-black/20 px-4 py-2 text-sm font-semibold text-foreground backdrop-blur"><span className="inline-flex items-center gap-2"><Globe className="h-4 w-4" />FR</span></div>
    <div className="relative z-10 flex flex-1 items-center justify-center px-6 py-10">
      <div className="w-full max-w-lg rounded-3xl border border-white/12 bg-background/58 p-10 shadow-2xl shadow-black/45 backdrop-blur-xl">
      <div className="mb-8 flex items-center justify-center"><VermegAnimatedLogo size="md" /></div>
      <h2 className="text-5 font-bold text-foreground">Bon retour</h2>
      <p className="mt-2 text-muted-foreground">Connectez-vous à votre compte</p>
      <form onSubmit={submit} className="mt-6 space-y-4">
        <label className="block text-sm font-medium text-muted-foreground">E-mail</label>
        <div className="relative"><Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><input value={email} onChange={(e) => setEmail(e.target.value)} className="h-11 w-full rounded-md border border-border bg-secondary pl-10 pr-3 text-sm outline-none focus:ring-1 focus:ring-primary" /></div>
        <label className="block text-sm font-medium text-muted-foreground">Mot de passe</label>
        <div className="relative"><Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><input type={show ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} className="h-11 w-full rounded-md border border-border bg-secondary pl-10 pr-10 text-sm outline-none focus:ring-1 focus:ring-primary" /><button type="button" onClick={() => setShow(!show)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">{show ? <EyeOff className="h-4 w-4"/> : <Eye className="h-4 w-4"/>}</button></div>
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 text-sm text-muted-foreground"><input type="checkbox" className="rounded border-border" defaultChecked />Se souvenir de moi</label>
          <a href="/forgot-password" className="text-sm text-primary hover:underline">Mot de passe oublié ?</a>
        </div>
        <Button disabled={loading} className="mt-6 h-12 w-full rounded-lg text-lg">{loading ? "Connexion..." : "Se connecter"}</Button>
      </form>
      <div className="my-6 flex items-center gap-4 text-sm text-muted-foreground"><div className="h-px flex-1 bg-border" /><span>ou</span><div className="h-px flex-1 bg-border" /></div>
      <button type="button" className="h-12 w-full rounded-lg border border-border bg-secondary font-semibold text-foreground">Se connecter avec Keycloak SSO</button>
    </div>
    </div>
  </div>;
}
