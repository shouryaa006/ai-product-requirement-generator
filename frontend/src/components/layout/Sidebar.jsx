import {
  LayoutDashboard,
  Plus,
  FileText,
  Clock3,
  Layers3,
  Settings,
  CircleHelp,
  Sparkles,
} from "lucide-react";

const workspaceItems = [
  { label: "Overview", icon: LayoutDashboard, action: "overview" },
  { label: "New PRD", icon: Plus, action: "new-prd" },
  { label: "Documents", icon: FileText, action: "documents" },
];

const libraryItems = [
  { label: "Recent", icon: Clock3, action: "recent" },
  { label: "Templates", icon: Layers3, action: "templates" },
];

export default function Sidebar() {
  function handleNavigation(action) {
    // Send navigation event to App.jsx
    window.dispatchEvent(
      new CustomEvent("prd:navigate", {
        detail: action,
      })
    );
  }

  return (
    <aside className="sidebar">
      {/* BRAND */}
      <div className="sidebar-brand">
        <div className="brand-icon">
          <Sparkles size={16} />
        </div>

        <div>
          <div className="brand-title">PRD AI</div>
          <div className="brand-caption">Product Intelligence</div>
        </div>
      </div>

      {/* WORKSPACE */}
      <div className="sidebar-section">
        <div className="sidebar-heading">WORKSPACE</div>

        {workspaceItems.map(({ label, icon: Icon, action }) => (
          <button
            key={label}
            type="button"
            className={`sidebar-item ${
              action === "overview" ? "active" : ""
            }`}
            onClick={() => handleNavigation(action)}
          >
            <Icon size={16} strokeWidth={1.8} />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* LIBRARY */}
      <div className="sidebar-section">
        <div className="sidebar-heading">LIBRARY</div>

        {libraryItems.map(({ label, icon: Icon, action }) => (
          <button
            key={label}
            type="button"
            className="sidebar-item"
            onClick={() => handleNavigation(action)}
          >
            <Icon size={16} strokeWidth={1.8} />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* BOTTOM */}
      <div className="sidebar-bottom">
        <button
          type="button"
          className="sidebar-item"
          onClick={() => handleNavigation("settings")}
        >
          <Settings size={16} strokeWidth={1.8} />
          <span>Settings</span>
        </button>

        <button
          type="button"
          className="sidebar-item"
          onClick={() => handleNavigation("help")}
        >
          <CircleHelp size={16} strokeWidth={1.8} />
          <span>Help & feedback</span>
        </button>

        {/* AI STATUS */}
        <div className="engine-status">
          <div className="status-indicator" />

          <div>
            <div className="engine-title">AI Engine</div>
            <div className="engine-caption">Operational</div>
          </div>
        </div>

        {/* USER */}
        <div className="user-profile">
          <div className="avatar">SJ</div>

          <div className="user-info">
            <div className="user-name">Shourya</div>
            <div className="user-role">Workspace owner</div>
          </div>

          <button
            type="button"
            className="profile-menu"
            onClick={() => handleNavigation("profile")}
            aria-label="Open profile menu"
          >
            •••
          </button>
        </div>
      </div>
    </aside>
  );
}