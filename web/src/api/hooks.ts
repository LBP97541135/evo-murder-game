import React from "react";

import { backendScriptToCard } from "./adapters";
import { getScript, listScripts, type BackendScript } from "./invoke";
import type { ScriptCard } from "../pages/scriptData";

export function useScripts() {
  const [scripts, setScripts] = React.useState<ScriptCard[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let active = true;
    listScripts()
      .then((items) => {
        if (active && items.length) setScripts(items.map(backendScriptToCard));
        if (active) setError(null);
      })
      .catch((reason) => {
        if (active) setError(reason instanceof Error ? reason.message : String(reason));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  return { scripts, loading, error };
}

export function useScript(scriptId?: string) {
  const [script, setScript] = React.useState<ScriptCard | null>(null);
  const [rawScript, setRawScript] = React.useState<BackendScript | null>(null);
  const [loading, setLoading] = React.useState(Boolean(scriptId));
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!scriptId) {
      setLoading(false);
      return;
    }
    let active = true;
    getScript(scriptId)
      .then((item) => {
        if (!active) return;
        setRawScript(item);
        setScript(backendScriptToCard(item));
        setError(null);
      })
      .catch((reason) => {
        if (active) setError(reason instanceof Error ? reason.message : String(reason));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [scriptId]);

  return { script, rawScript, loading, error };
}
