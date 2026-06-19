/**
 * EvoMap Murder Game - App Entry
 */

import React from "react";
import { MantineProvider, createTheme } from "@mantine/core";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import {
  MysteryProvider,
  SessionProvider,
  ScriptProvider,
  AgentProvider,
} from "./providers/contexts";

import { ScriptLibrary } from "./pages/ScriptLibrary";
import { GamePage } from "./pages/GamePage";
import { AgentPanel } from "./pages/AgentPanel";
import { EvolutionTimeline } from "./pages/EvolutionTimeline";

const theme = createTheme({
  primaryColor: "blue",
  colors: {
    dark: [
      "#C1C2C5", "#A6A7AB", "#909296", "#5C5F66", "#373A40",
      "#2C2E33", "#25262B", "#1A1B1E", "#141517", "#101113",
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
                  <Route path="/play/:id" element={<GamePage />} />
                  <Route path="/agents" element={<AgentPanel />} />
                  <Route path="/evolution" element={<EvolutionTimeline />} />
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
