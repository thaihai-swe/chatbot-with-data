import { NavLink, Route, Routes } from "react-router-dom";

import ErrorBoundary from "./components/ErrorBoundary";
import CollectionsScreen from "./screens/Collections";
import DocumentLibraryScreen from "./screens/DocumentLibrary";

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
              Document Library
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link nav-link-active" : "nav-link"
              }
              to="/collections"
            >
              Collections
            </NavLink>
          </nav>
        </header>
        <main className="page-shell">
          <Routes>
            <Route path="/" element={<DocumentLibraryScreen />} />
            <Route path="/collections" element={<CollectionsScreen />} />
          </Routes>
        </main>
      </div>
    </ErrorBoundary>
  );
}

export default App;
