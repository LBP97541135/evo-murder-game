/**
 * EvoMap Murder Game - Context Providers
 *
 * 使用 constate 管理全局状态：剧本、角色、游戏会话、Agent。
 */

import { createContext, useContext } from "react";
import constate from "constate";
import { Actor, Script, GameSession, AgentNodeInfo } from "../types";


// ============================
// Mystery Context（游戏核心状态）
// ============================

function useMysteryState() {
  const [globalStory, setGlobalStory] = React.useState("");
  const [actors, setActors] = React.useState<Actor[]>([]);
  const [currentActorId, setCurrentActorId] = React.useState<string>("");

  return {
    globalStory, setGlobalStory,
    actors, setActors,
    currentActorId, setCurrentActorId,
  };
}

// ⚠️ 需要 import React
import React from "react";

export const [MysteryProvider, useMystery] = constate(useMysteryState);


// ============================
// Session Context（游戏会话ID）
// ============================

function useSessionState() {
  const [sessionId, setSessionId] = React.useState(() => {
    const saved = localStorage.getItem("evo_session_id");
    return saved || "";
  });

  const newSession = () => {
    const id = `ses_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    setSessionId(id);
    localStorage.setItem("evo_session_id", id);
    return id;
  };

  return { sessionId, setSessionId, newSession };
}

export const [SessionProvider, useSession] = constate(useSessionState);


// ============================
// Script Context（剧本状态）
// ============================

function useScriptState() {
  const [script, setScript] = React.useState<Script | null>(null);
  const [scripts, setScripts] = React.useState<Script[]>([]);

  const loadScript = (s: Script) => setScript(s);
  const clearScript = () => setScript(null);

  return { script, scripts, setScripts, loadScript, clearScript };
}

export const [ScriptProvider, useScript] = constate(useScriptState);


// ============================
// Agent Context（Agent 状态）
// ============================

function useAgentState() {
  const [agents, setAgents] = React.useState<AgentNodeInfo[]>([]);
  const [currentPhase, setCurrentPhase] = React.useState("idle");

  return { agents, setAgents, currentPhase, setCurrentPhase };
}

export const [AgentProvider, useAgent] = constate(useAgentState);
