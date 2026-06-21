export function getStoredGameSession(scriptId: string): string {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(`game-session:${scriptId}`) || "";
}

export function buildPlayPath(scriptId: string): string {
  return `/play/${encodeURIComponent(scriptId)}`;
}

export function buildReviewPath(scriptId: string, sessionId?: string): string {
  const session = sessionId || getStoredGameSession(scriptId);
  const base = `/review/${encodeURIComponent(scriptId)}`;
  return session ? `${base}?session=${encodeURIComponent(session)}` : base;
}
