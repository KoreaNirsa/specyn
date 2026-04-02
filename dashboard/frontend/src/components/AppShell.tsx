import { NavLink, Outlet } from "react-router-dom";

import { useI18n } from "../i18n";
import { LanguageSelector } from "./LanguageSelector";

function ServicePill({ label, port }: { label: string; port: string }) {
  return (
    <div className="service-pill">
      <span>{label}</span>
      <span>{port}</span>
    </div>
  );
}

/**
 * Handle app shell for the current workflow.
 */
export function AppShell() {
  const { t } = useI18n();

  const links = [
    { to: "/", label: t("common.dashboard"), icon: "DS" },
    { to: "/workspace", label: t("common.workspace"), icon: "WS" },
    { to: "/runs", label: t("common.runs"), icon: "RN" },
    { to: "/agents", label: t("common.agents"), icon: "AG" },
    { to: "/ci-deploy", label: t("common.deploy"), icon: "CI" },
    { to: "/system", label: t("common.system"), icon: "SY" },
    { to: "/projects", label: t("common.projects"), icon: "PJ" },
  ];

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
            <ServicePill label="sample FE" port=":5173" />
          </div>
          <a
            className="workspace-button"
            href="http://localhost:5173"
            rel="noreferrer"
            target="_blank"
          >
            {t("common.openSample")}
          </a>
        </div>
      </aside>
      <div className="shell-body">
        <header className="topbar">
          <div className="topbar__left">
            <span className="topbar__eyebrow">{t("shell.subtitle")}</span>
            <strong>{t("shell.title")}</strong>
          </div>
          <div className="topbar__right">
            <LanguageSelector />
            <a className="quick-run-button" href="/">
              {t("common.openAgentConsole")}
            </a>
          </div>
        </header>
        <main className="page-body">
          <Outlet />
        </main>
        <footer className="footer">{t("shell.footer")}</footer>
      </div>
    </div>
  );
}
