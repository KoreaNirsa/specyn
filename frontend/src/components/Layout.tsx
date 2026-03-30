import { NavLink, Outlet } from "react-router-dom";

export function Layout() {
  return (
    <div className="layout">
      <header className="topbar">
        <div>
          <h1>Specyn</h1>
          <p>도메인 독립형 AX Builder 프레임워크 · SDD · Multi-Agent · Codex 실행 골격</p>
        </div>
        <nav className="nav-links">
          <NavLink to="/">소개</NavLink>
          <NavLink to="/workspace">워크스페이스</NavLink>
        </nav>
      </header>
      <Outlet />
    </div>
  );
}
