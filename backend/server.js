import express from "express";
import cors from "cors";

const app = express();
const port = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

app.get("/api/health", (_req, res) => {
  res.json({ ok: true, service: "smart-cctv-search", timestamp: new Date().toISOString() });
});

app.post("/api/auth/login", (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) {
    return res.status(400).json({ error: "Username and password are required" });
  }

  res.json({
    success: true,
    token: "demo-token-123",
    user: {
      id: 1,
      name: username === "admin" ? "Dr. Elena Shaw" : "Operator",
      role: "Forensic Analyst",
    },
  });
});

app.get("/api/dashboard", (_req, res) => {
  res.json({
    overview: {
      totalCameras: 1284,
      videosIndexed: 42500,
      objectsDetected: 892000,
      activeSearches: 14,
      uploadsToday: 156,
      processingQueue: 8,
    },
    alerts: [
      { title: "Unauthorized access detected", detail: "Sector 7G / Server Room B", time: "14:02:44", level: "Priority 1", levelClass: "text-error border-error/30", dotClass: "bg-error" },
      { title: "Perimeter breach (Fence Line 4)", detail: "North Yard Exterior", time: "13:45:12", level: "Priority 2", levelClass: "text-orange-400 border-orange-400/30", dotClass: "bg-orange-400" },
    ],
    searches: [
      { query: "[color:red] AND [type:sedan] AND [loc:sector_4]", operator: "OP-773", time: "Just now", status: "Running", statusClass: "bg-secondary-fixed/10 text-secondary-fixed border-secondary-fixed/20" },
      { query: "[face_match:ID_8922] w/in 24h", operator: "SYS-AUTO", time: "12m ago", status: "Completed (14)", statusClass: "bg-surface-container-highest text-on-surface-variant" },
    ],
  });
});

app.get("/api/uploads", (_req, res) => {
  res.json({
    items: [
      { id: "CAM-082", location: "Sector 7G - Perimeter", time: "2024-05-12 14:30:22", duration: "04:12:00", status: "Indexed" },
      { id: "CAM-114", location: "Sub-Level 2 Parking", time: "2024-05-12 10:15:00", duration: "02:45:30", status: "Processing" },
      { id: "UNKNOWN", location: "Corrupt Header", time: "--", duration: "--", status: "Error" },
    ],
  });
});

app.post("/api/uploads", (req, res) => {
  const item = {
    id: req.body?.id || `CAM-${Math.floor(100 + Math.random() * 900)}`,
    location: req.body?.location || "New Ingest",
    time: new Date().toISOString(),
    duration: req.body?.duration || "00:00:00",
    status: "Queued",
  };
  res.status(201).json({ success: true, item });
});

app.listen(port, () => {
  console.log(`Smart CCTV backend listening on port ${port}`);
});
