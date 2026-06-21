type CalloutPlayer = {
  id: string;
  role: string;
  name: string;
  agent?: boolean;
};

const PLAYER_CALLOUT_NAMES = new Set(["林晓青", "侦探", "玩家", "user"]);

export function resolveCalloutTarget(
  name: string,
  players: CalloutPlayer[],
): CalloutPlayer | undefined {
  const trimmed = name.trim();
  if (!trimmed) return undefined;
  if (PLAYER_CALLOUT_NAMES.has(trimmed)) {
    return players.find((player) => player.id === "user");
  }
  return players.find(
    (player) =>
      player.role === trimmed
      || player.name === trimmed
      || player.id === trimmed,
  );
}

export function calloutTargetOptions(
  players: CalloutPlayer[],
  excludeId?: string,
): Array<{ value: string; label: string }> {
  return players
    .filter((player) => player.id !== "dm" && player.id !== excludeId)
    .map((player) => ({
      value: player.id,
      label: player.agent
        ? `${player.name} · ${player.role}`
        : `${player.role} · ${player.name}（玩家）`,
    }));
}
