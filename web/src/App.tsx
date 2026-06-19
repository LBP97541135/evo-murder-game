/**
 * EvoMap Murder Game - App Entry
 *
 * Figma-inspired dark theatre shell.
 */

import React from "react";
import { MantineProvider, createTheme } from "@mantine/core";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import {
  AgentProvider,
  MysteryProvider,
  ScriptProvider,
  SessionProvider,
} from "./providers/contexts";

import { ScriptLibrary } from "./pages/ScriptLibrary";
import { ScriptDetailPage } from "./pages/ScriptDetailPage";
import { GamePage } from "./pages/GamePage";
import { AgentPanel } from "./pages/AgentPanel";
import { EvolutionTimeline } from "./pages/EvolutionTimeline";
import { MyGamesPage } from "./pages/MyGamesPage";
import { ProfilePage } from "./pages/ProfilePage";
import "./styles.css";

const theme = createTheme({
  primaryColor: "red",
  defaultRadius: "md",
  fontFamily: "Crimson Pro, Georgia, serif",
  headings: {
    fontFamily: "Cinzel Decorative, Crimson Pro, Georgia, serif",
    fontWeight: "700",
  },
  colors: {
    dark: [
      "#f0e8d8",
      "#d8c7ab",
      "#bfa789",
      "#947563",
      "#6b5248",
      "#44302c",
      "#2d1d1c",
      "#1a1211",
      "#120d0d",
      "#0c0808",
    ],
    red: [
      "#fff5f5",
      "#ffe3e3",
      "#ffc9c9",
      "#ffa8a8",
      "#ff8787",
      "#ff6b6b",
      "#fa5252",
      "#f03e3e",
      "#e03131",
      "#c92a2a",
    ],
  },
});

function App() {
  return (
    <MantineProvider theme={theme} defaultColorScheme="dark">
      <BrowserRouter>
        <AgentProvider>
          <ScriptProvider>
            <SessionProvider>
              <MysteryProvider>
                <Routes>
                  <Route path="/" element={<Navigate to="/library" replace />} />
                  <Route path="/library" element={<ScriptLibrary />} />
                  <Route path="/library/:id" element={<ScriptDetailPage />} />
                  <Route path="/games" element={<MyGamesPage />} />
                  <Route path="/play/:id" element={<GamePage />} />
                  <Route path="/agents" element={<AgentPanel />} />
                  <Route path="/evolution" element={<EvolutionTimeline />} />
                  <Route path="/profile" element={<ProfilePage />} />
                </Routes>
              </MysteryProvider>
            </SessionProvider>
          </ScriptProvider>
        </AgentProvider>
      </BrowserRouter>
    </MantineProvider>
  );
}

export default App;
