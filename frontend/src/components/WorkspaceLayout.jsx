import { useState } from "react";
import { useWorkspace } from "../context/WorkspaceContext";
import SourcesPanel from "./SourcesPanel";
import ChatPanel from "./ChatPanel";
import StudioPanel from "./StudioPanel";

function PanelToggle({ icon, label, collapsed, onToggle }) {
  return (
    <div className="panel-toggle" onClick={onToggle} title={label}>
      <span className="panel-toggle-icon">{icon}</span>
      {collapsed && <span className="panel-toggle-label">{label}</span>}
    </div>
  );
}

function PanelContainer({ side, collapsed, togglePanel, icon, label, mobileVisible, children }) {
  return (
    <div
      className={`panel-container panel-${side} ${collapsed ? "panel-collapsed" : "panel-expanded"} ${mobileVisible ? "visible" : ""}`}
    >
      <PanelToggle icon={icon} label={label} collapsed={collapsed} onToggle={togglePanel} />
      {!collapsed && <div className="panel-content">{children}</div>}
    </div>
  );
}

export default function WorkspaceLayout() {
  const {
    sourcesCollapsed,
    studioCollapsed,
    toggleSourcesPanel,
    toggleStudioPanel,
  } = useWorkspace();

  const [mobileTab, setMobileTab] = useState("chat");

  const handleMobileTab = (tab) => {
    setMobileTab(tab);
    if (tab === "sources" && sourcesCollapsed) toggleSourcesPanel();
    if (tab === "studio" && studioCollapsed) toggleStudioPanel();
  };

  return (
    <div className="workspace-layout">
      <PanelContainer
        side="left"
        collapsed={sourcesCollapsed}
        togglePanel={toggleSourcesPanel}
        icon="📄"
        label="Sources"
        mobileVisible={mobileTab === "sources"}
      >
        <SourcesPanel />
      </PanelContainer>

      <div className={`panel-center panel-expanded ${mobileTab === "chat" ? "visible" : ""}`}>
        <ChatPanel />
      </div>

      <PanelContainer
        side="right"
        collapsed={studioCollapsed}
        togglePanel={toggleStudioPanel}
        icon="🎨"
        label="Studio"
        mobileVisible={mobileTab === "studio"}
      >
        <StudioPanel />
      </PanelContainer>

      <div className="workspace-tab-bar">
        <button
          className={`tab-bar-btn ${mobileTab === "sources" ? "tab-bar-btn-active" : ""}`}
          onClick={() => handleMobileTab("sources")}
        >
          📄 Sources
        </button>
        <button
          className={`tab-bar-btn ${mobileTab === "chat" ? "tab-bar-btn-active" : ""}`}
          onClick={() => handleMobileTab("chat")}
        >
          💬 Chat
        </button>
        <button
          className={`tab-bar-btn ${mobileTab === "studio" ? "tab-bar-btn-active" : ""}`}
          onClick={() => handleMobileTab("studio")}
        >
          🎨 Studio
        </button>
      </div>
    </div>
  );
}
