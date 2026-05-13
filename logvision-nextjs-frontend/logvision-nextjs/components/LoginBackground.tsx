export function LoginBackground() {
  return (
    <div className="login-bg pointer-events-none absolute inset-0 overflow-hidden">
      <div className="aurora aurora-1" />
      <div className="aurora aurora-2" />
      <div className="aurora aurora-3" />
      <div className="login-grid" />
      <div className="login-sweep" />
      <div className="particles">
        {Array.from({ length: 24 }).map((_, i) => (
          <span key={i} className={`particle p-${i % 8}`} />
        ))}
      </div>
      <div className="login-vignette" />
    </div>
  );
}
