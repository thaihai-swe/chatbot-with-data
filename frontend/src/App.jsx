import { NavLink, Route, Routes } from "react-router-dom";

import ErrorBoundary from "./components/ErrorBoundary";
import CollectionsScreen from "./screens/Collections";
import DocumentLibraryScreen from "./screens/DocumentLibrary";
import ChatScreen from "./screens/Chat";
import EvaluationScreen from "./screens/Evaluation";

function App() {
  return (
    <ErrorBoundary>
      <div className="app-shell">
        <header className="hero">
          <div>
            <p className="eyebrow">Knowledge Operations</p>
            <h1>Ingest documents, spot duplicates, and keep collections clean.</h1>
            <p className="hero-copy">
              Ingestion completion means the source is stored and inspected. It does
              not mean the source is indexed or chat-ready yet.
            </p>
          </div>
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
          </nav>
        </header>
        <main className="page-shell">
          <Routes>
            <Route path="/" element={<DocumentLibraryScreen />} />
            <Route path="/collections" element={<CollectionsScreen />} />
            <Route path="/chat" element={<ChatScreen />} />
            <Route path="/chat/:sessionId" element={<ChatScreen />} />
            <Route path="/evaluation" element={<EvaluationScreen />} />
          </Routes>
        </main>
      </div>
    </ErrorBoundary>
  );
}

export default App;
