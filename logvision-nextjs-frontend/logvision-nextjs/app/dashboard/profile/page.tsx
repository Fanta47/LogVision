export default function ProfilePage() {
  return <div className="space-y-6"><div><h1 className="text-xl font-bold">Profile</h1><p className="mt-1 text-sm text-muted-foreground">Frontend demo profile. Replace with Keycloak user info when auth is connected.</p></div><div className="glass-card animate-slide-up rounded-lg p-5 text-sm text-muted-foreground">Authentication is currently local demo auth. Keep Keycloak validation in FastAPI for production.</div></div>;
}
