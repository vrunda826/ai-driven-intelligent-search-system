import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import UploadCenter from "./pages/UploadCenter";
import AnalysisWorkflow from "./pages/AnalysisWorkflow";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<UploadCenter />} />
          <Route path="/analysis-workflow" element={<AnalysisWorkflow />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
