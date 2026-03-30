import { BrowserRouter, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { GeneratedProjectRoutePage } from "./pages/GeneratedProjectRoutePage";
import { GeneratedProjectsPage } from "./pages/GeneratedProjectsPage";
import { HomePage } from "./pages/HomePage";
import { WorkspacePage } from "./pages/WorkspacePage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/workspace" element={<WorkspacePage />} />
          <Route path="/generated" element={<GeneratedProjectsPage />} />
          <Route path="/generated/:projectId" element={<GeneratedProjectRoutePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
