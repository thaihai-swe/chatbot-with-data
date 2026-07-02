import { Link, NavLink, Route, Routes, Navigate } from "react-router-dom";
import React, { useState, useEffect } from "react";

import ErrorBoundary from "./components/ErrorBoundary";
import CollectionsScreen from "./screens/Collections";
import DocumentLibraryScreen from "./screens/DocumentLibrary";
import ChatScreen from "./screens/Chat";
import EvaluationScreen from "./screens/Evaluation";
import SettingsScreen from "./screens/SettingsScreen";
import { WorkspaceProvider } from "./context/WorkspaceContext";
import WorkspaceLayout from "./components/WorkspaceLayout";

function App() {
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "light");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === "light" ? "dark" : "light");
  };

  return (
    <ErrorBoundary>
      <WorkspaceProvider>
      <div className="app-shell">
        <header className="top-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
            <Link to="/" style={{ display: "flex", alignItems: "center", gap: "12px", textDecoration: "none", color: "inherit" }}>
              <div style={{ width: "30px", height: "30px", background: "var(--gradient-primary)", borderRadius: "var(--radius-sm)", display: "flex", alignItems: "center", justifyContent: "center", color: "white", fontWeight: "900", fontSize: "18px" }}>K</div>
              <span style={{ fontWeight: "750", fontSize: "18px", letterSpacing: "-0.02em" }}>KnowledgeBase<span style={{ color: "var(--accent)" }}>Lab</span></span>
            </Link>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
            <nav className="top-nav" aria-label="Primary">
              <NavLink
                className={({ isActive }) =>
                  isActive ? "nav-link nav-link-active" : "nav-link"
                }
                to="/"
                end
              >
                Library
              </NavLink>
              <NavLink
                className={({ isActive }) =>
                  isActive ? "nav-link nav-link-active" : "nav-link"
                }
                to="/collections"
              >
                Collections
              </NavLink>
              <NavLink
                className={({ isActive }) =>
                  isActive ? "nav-link nav-link-active" : "nav-link"
                }
                to="/chat"
              >
                Chat
              </NavLink>
              <NavLink
                className={({ isActive }) =>
                  isActive ? "nav-link nav-link-active" : "nav-link"
                }
                to="/evaluation"
              >
                Evaluation
              </NavLink>
              <NavLink
                className={({ isActive }) =>
                  isActive ? "nav-link nav-link-active" : "nav-link"
                }
                to="/settings"
              >
                Settings
              </NavLink>
            </nav>
            
            <button 
              onClick={toggleTheme} 
              className="button button-ghost" 
              style={{ width: "36px", height: "36px", padding: "0", borderRadius: "var(--radius-full)", border: "1px solid var(--border)" }}
              title={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
            >
              {theme === "light" ? "🌙" : "☀️"}
            </button>
          </div>
        </header>

        <main className="page-shell">
          <Routes>
            <Route path="/" element={<DocumentLibraryScreen />} />
            <Route path="/collections" element={<CollectionsScreen />} />
            <Route path="/chat" element={<WorkspaceLayout />} />
            <Route path="/chat/:sessionId" element={<WorkspaceLayout />} />
            <Route path="/evaluation" element={<EvaluationScreen />} />
            <Route path="/settings" element={<SettingsScreen />} />
          </Routes>
        </main>
      </div>
      </WorkspaceProvider>
    </ErrorBoundary>
  );
}

export default App;
