import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard", icon: "◫" },
  { to: "/workspace", label: "Workspace", icon: "✦" },
  { to: "/runs", label: "Runs", icon: "◎" },
  { to: "/agents", label: "Agents", icon: "▣" },
  { to: "/ci-deploy", label: "CI & Deploy", icon: "⇅" },
  { to: "/system", label: "System", icon: "☰" },
  { to: "/projects", label: "Projects", icon: "◌" },
];

function ServicePill({ label, port }: { label: string; port: string }) {
  return (
    <div className="service-pill">
      <span>{label}</span>
      <span>{port}</span>
    </div>
  );
}

export function AppShell() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <strong>Specyn</strong>
          <span>ADMIN DASHBOARD</span>
        </div>
        <nav className="sidebar-nav">
          {links.map((link) => (
            <NavLink
              className={({ isActive }) =>
                `sidebar-link${isActive ? " sidebar-link--active" : ""}`
              }
              key={link.to}
              to={link.to}
            >
              <span className="sidebar-link__icon">{link.icon}</span>
              <span>{link.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="service-pill-group">
            <ServicePill label="Dashboard FE" port=":4173" />
            <ServicePill label="Dashboard BE" port=":8180" />
            <ServicePill label="Dashboard AI" port=":8100" />
            <ServicePill label="Project FE" port=":5173" />
          </div>
          <a className="workspace-button" href="http://localhost:5173" rel="noreferrer" target="_blank">
            Open sample-service
          </a>
        </div>
      </aside>
      <div className="shell-body">
        <header className="topbar">
          <div className="topbar__left">
            <span className="topbar__eyebrow">Spec Driven Development Control Plane</span>
            <strong>Specyn Admin Workspace</strong>
          </div>
          <div className="topbar__right">
            <div className="search-chip">dashboard</div>
            <a className="quick-run-button" href="/workspace">
              Launch Run Studio
            </a>
          </div>
        </header>
        <main className="page-body">
          <Outlet />
        </main>
        <footer className="footer">Specyn dashboard · unified layout · dashboard/* vs projects/* separated runtime</footer>
      </div>
    </div>
  );
}
