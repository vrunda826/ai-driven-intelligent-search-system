import { Link, useNavigate } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { createUpload, getUploads } from "../services/api";
import { clearAuthSession } from "../utils/auth";

const navItems = [
  { label: "Live Feeds", icon: "videocam", active: false },
  { label: "Evidence Vault", icon: "folder_shared", active: false },
  { label: "Upload Center", icon: "cloud_upload", active: true },
  { label: "Analysis Workflow", icon: "analytics", active: false },
  { label: "System Logs", icon: "terminal", active: false },
];

function badgeForStatus(status) {
  const normalized = status?.toLowerCase() || "";
  if (normalized.includes("processing")) {
    return { badgeClass: "bg-surface-container border-[#00eefc]/30 text-[#00eefc]", dotClass: "bg-[#00eefc] animate-pulse" };
  }
  if (normalized.includes("error")) {
    return { badgeClass: "bg-error-container/20 border-error/30 text-error", dotClass: "bg-error" };
  }
  return { badgeClass: "bg-surface-container border-[#0052FF]/30 text-[#b7c4ff]", dotClass: "bg-[#0052FF]" };
}

export default function UploadCenter() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusMessage, setStatusMessage] = useState("Syncing queue...");
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      try {
        const result = await getUploads();
        setRows(result.items || []);
        setStatusMessage("Queue synced from backend");
      } catch (err) {
        setStatusMessage("Using fallback queue while backend is offline");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  async function handleUpload(file) {
    if (!file) return;
    try {
      const result = await createUpload({
        id: `CAM-${Date.now().toString().slice(-4)}`,
        location: file.name.replace(/\.[^/.]+$/, ""),
        duration: "00:07:14",
      });
      setRows((prev) => [
        {
          ...result.item,
          time: new Date().toLocaleString(),
          status: result.item.status || "Queued",
          ...badgeForStatus(result.item.status || "Queued"),
        },
        ...prev,
      ]);
      setStatusMessage(`Queued ${file.name}`);
    } catch (err) {
      setStatusMessage("Upload failed. Please try again.");
    }
  }

  function handleLogout() {
    clearAuthSession();
    navigate("/");
  }

  return (
    <div className="min-h-screen bg-surface text-on-background flex overflow-hidden">
      <aside className="hidden md:flex flex-col h-full w-[280px] p-4 gap-2 border-r border-outline-variant bg-surface-container shrink-0">
        <div className="flex items-center gap-3 mb-6 px-2 mt-2">
          <div className="w-10 h-10 rounded bg-primary-container flex items-center justify-center shrink-0">
            <img alt="Command Center Logo" className="w-8 h-8 object-cover rounded" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCadrbhJufQVZjPwgvk-EXCeN63BUQz6iksCrINb8nTyLlrP7oGdYXgOQ2vMLWpkjOn1P1wc2oiPKKJuitTD4D8ywaDE2oMF8Qfd0kSPX8ZOOnUYXcgCgdWtArfUHjeelI7AsN40noMCRD97DSs0r1kOm3HQep3QLSuik15DUG8j1-dNZBzcalEM--N0ECuI9AK-ghVPrnhUUQKx-mJiJfUHG4eOXw2oWBbMcRjUTrRkVeVZ6YgIR6RSw" />
          </div>
          <div>
            <h1 className="font-headline-md text-headline-md text-on-surface">Unit 04</h1>
            <p className="font-label-sm text-label-sm text-on-surface-variant">Forensic Division</p>
          </div>
        </div>

        <button className="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-[#0052FF] to-[#0041CC] text-on-primary font-label-md text-label-md mb-4 flex items-center justify-center gap-2 hover:opacity-90 transition-opacity">
          <span className="material-symbols-outlined text-[18px]">add</span>
          NEW INVESTIGATION
        </button>

        <nav className="flex-1 flex flex-col gap-1">
          {navItems.map((item) => (
            <Link key={item.label} to={item.label === "Upload Center" ? "/upload" : item.label === "Analysis Workflow" ? "/analysis-workflow" : item.label === "Analytics" ? "/dashboard" : "#"} className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-all scale-95 duration-150 ${item.active ? "bg-primary-container text-on-primary-container" : "text-on-surface-variant hover:bg-surface-variant"}`}>
              <span className="material-symbols-outlined" style={{ fontVariationSettings: item.active ? "'FILL' 1" : "'FILL' 0" }}>{item.icon}</span>
              <span className="font-label-md text-label-md">{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="flex flex-col gap-1 pt-4 border-t border-outline-variant mt-auto">
          <a className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-surface-variant rounded-lg transition-all scale-95 duration-150" href="#">
            <span className="material-symbols-outlined">help</span>
            <span className="font-label-md text-label-md">Support</span>
          </a>
          <button onClick={handleLogout} className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-surface-variant rounded-lg transition-all scale-95 duration-150">
            <span className="material-symbols-outlined">logout</span>
            <span className="font-label-md text-label-md">Logout</span>
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        <header className="flex justify-between items-center w-full px-container-padding h-16 bg-surface border-b border-outline-variant shrink-0 z-10">
          <div className="flex items-center gap-6">
            <span className="font-headline-md text-headline-md font-bold tracking-tighter text-primary md:hidden">SENTINEL COMMAND</span>
            <div className="hidden md:flex relative w-64 rounded scanning-focus">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px]">search</span>
              <input className="w-full bg-surface-container-high border border-outline-variant text-on-surface font-label-md text-label-md py-1.5 pl-10 pr-3 rounded focus:outline-none focus:ring-0 placeholder:text-on-surface-variant/50" placeholder="Query ID or Location..." type="text" />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button className="text-on-surface-variant hover:text-primary transition-colors cursor-pointer active:opacity-80"><span className="material-symbols-outlined">notifications</span></button>
            <button className="text-on-surface-variant hover:text-primary transition-colors cursor-pointer active:opacity-80"><span className="material-symbols-outlined">settings</span></button>
            <div className="w-8 h-8 rounded-full border border-outline-variant overflow-hidden bg-surface-container ml-2">
              <img alt="Officer Profile" className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDlEKUFrUxndcYm0rz1v_6-IH3r7kgTmu_mvJuksX49xkV75ApWbdUTKvrn64LRb24-aF8sWdAWE9sJNeqmcQaKDeR3RQgizZFw_bSjGjz1nJgeS-8LidEuRGlWctfmHonhYRprcMo9Z0b6aOp1ExboEvqN3d6-ZCSdOehwQQ7hreO9MMvOgiRJI45P8CVgQbr423ArlBeJ7-jb5EVBNT256HYNym1FfKacGXe-07DZgTI_wONDRGMNRA" />
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-container-padding relative">
          <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-surface-container-low via-[#020617] to-[#020617] opacity-80 z-0"></div>
          <div className="max-w-7xl mx-auto space-y-gutter relative z-10 flex flex-col h-full">
            <div className="shrink-0 mb-2">
              <h2 className="font-headline-lg text-headline-lg text-on-surface">Upload Center</h2>
              <p className="font-body-md text-body-md text-on-surface-variant mt-1">Ingest and index CCTV footage for forensic analysis.</p>
            </div>

            <section className="shrink-0 glass-panel rounded-xl p-6 flex flex-col gap-4">
              <input ref={fileInputRef} type="file" accept="video/*" className="hidden" onChange={(e) => handleUpload(e.target.files?.[0])} />
              <div onClick={() => fileInputRef.current?.click()} className="border-2 border-dashed border-outline-variant hover:border-secondary-container hover:bg-surface-container-high/30 transition-colors rounded-lg flex flex-col items-center justify-center py-12 px-4 cursor-pointer relative group">
                <div className="w-16 h-16 rounded-full bg-surface-container-high flex items-center justify-center mb-4 group-hover:bg-secondary-container/10 transition-colors">
                  <span className="material-symbols-outlined text-[32px] text-on-surface-variant group-hover:text-secondary-container transition-colors">cloud_upload</span>
                </div>
                <h3 className="font-headline-md text-headline-md text-on-surface mb-2">Drop video files here or click to browse</h3>
                <p className="font-label-sm text-label-sm text-on-surface-variant font-mono">Supported formats: MP4, AVI, MKV, MOV (max 2GB)</p>
              </div>

              <div className="bg-surface-container rounded-lg p-4 border border-outline-variant flex flex-col gap-3">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-primary">movie</span>
                    <span className="font-label-md text-label-md text-on-surface font-mono">{statusMessage}</span>
                  </div>
                </div>
                <div className="w-full bg-surface-container-highest rounded-full h-2 overflow-hidden">
                  <div className="bg-gradient-to-r from-[#0052FF] to-[#00eefc] h-2 rounded-full w-[68%] relative">
                    <div className="absolute right-0 top-0 bottom-0 w-8 bg-white/20 animate-pulse"></div>
                  </div>
                </div>
                <div className="flex justify-between items-center font-label-sm text-label-sm text-on-surface-variant">
                  <span>{loading ? "Preparing queue..." : "Uploads are being tracked by the backend"}</span>
                  <span className="text-secondary-fixed">Live sync enabled</span>
                </div>
              </div>
            </section>

            <section className="flex-1 flex flex-col glass-panel rounded-xl overflow-hidden mt-4">
              <div className="p-4 border-b border-outline-variant flex flex-wrap gap-4 justify-between items-center bg-surface-container/50">
                <div className="flex items-center gap-3">
                  <h3 className="font-label-md text-label-md text-on-surface uppercase tracking-widest text-on-surface-variant">Evidence Queue</h3>
                  <span className="bg-surface-container-high text-on-surface-variant font-label-sm text-label-sm px-2 py-0.5 rounded">{rows.length} Items</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex gap-2">
                    <select className="bg-surface-container border border-outline-variant text-on-surface font-label-sm text-label-sm rounded px-3 py-1.5 focus:ring-1 focus:ring-primary focus:border-primary">
                      <option>Date: All Time</option>
                      <option>Last 24 Hours</option>
                      <option>Last 7 Days</option>
                    </select>
                    <select className="bg-surface-container border border-outline-variant text-on-surface font-label-sm text-label-sm rounded px-3 py-1.5 focus:ring-1 focus:ring-primary focus:border-primary">
                      <option>Status: All</option>
                      <option>Processing</option>
                      <option>Indexed</option>
                    </select>
                  </div>
                  <div className="relative w-48 rounded scanning-focus">
                    <span className="material-symbols-outlined absolute left-2 top-1/2 -translate-y-1/2 text-on-surface-variant text-[16px]">search</span>
                    <input className="w-full bg-surface border border-outline-variant text-on-surface font-label-sm text-label-sm py-1.5 pl-8 pr-2 rounded focus:outline-none" placeholder="Filter ID..." type="text" />
                  </div>
                </div>
              </div>

              <div className="flex-1 overflow-auto">
                <table className="w-full text-left border-collapse">
                  <thead className="sticky top-0 bg-surface-container-high border-b border-outline-variant font-label-sm text-label-sm text-on-surface-variant z-10">
                    <tr>
                      <th className="p-3 font-normal w-12 text-center"><input className="rounded border-outline-variant bg-surface text-primary focus:ring-primary" type="checkbox" /></th>
                      <th className="p-3 font-normal">Preview</th>
                      <th className="p-3 font-normal">Camera ID</th>
                      <th className="p-3 font-normal">Location</th>
                      <th className="p-3 font-normal">Date / Time</th>
                      <th className="p-3 font-normal">Duration</th>
                      <th className="p-3 font-normal">Status</th>
                      <th className="p-3 font-normal text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="font-body-sm text-body-sm text-on-surface divide-y divide-outline-variant/50">
                    {rows.map((row) => {
                      const badge = badgeForStatus(row.status);
                      return (
                        <tr key={row.id} className="hover:bg-surface-container-high/50 transition-colors group">
                          <td className="p-3 text-center"><input className="rounded border-outline-variant bg-surface text-primary focus:ring-primary" type="checkbox" /></td>
                          <td className="p-3">
                            <div className="w-16 h-9 bg-surface-container rounded border border-outline-variant overflow-hidden relative group-hover:border-secondary-fixed transition-colors">
                              <div className="absolute inset-0 bg-black/40 group-hover:bg-transparent transition-colors z-10"></div>
                              <img alt="Video thumbnail" className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuARzPcjm5726XVrld0tt40RQ4DNSLJaFtvgFRiCDi_Iz8EY9a1z-qn3h0A2IpKHzgRuWn32Y1p0BIW9S9i4627Mt0uE3tMJ7dMSL0v-wpcikgVrL1n6Rpt8WlDu7SlLe_OvFfaVIQ1I1EV3t6EmksrBZuohMwq7oA_vczMiqTyYT7r2oifCtSPmmw6WAg5L_Q4TOoluobWpH90o5TxGVON6vjIgh1pXRrtBLh9YMiYxXbRNKJiqauAp1g" />
                              <span className="material-symbols-outlined absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-white/70 text-[16px] z-20">play_circle</span>
                            </div>
                          </td>
                          <td className="p-3 font-label-sm text-label-sm font-mono">{row.id}</td>
                          <td className="p-3 text-on-surface-variant">{row.location}</td>
                          <td className="p-3 font-mono text-on-surface-variant text-[13px]">{row.time}</td>
                          <td className="p-3 font-mono text-on-surface-variant">{row.duration}</td>
                          <td className="p-3"><span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full border font-label-sm text-[11px] ${badge.badgeClass}`}><span className={`w-1.5 h-1.5 rounded-full ${badge.dotClass}`}></span>{row.status}</span></td>
                          <td className="p-3 text-right"><div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity"><button className="text-on-surface-variant hover:text-secondary-fixed p-1"><span className="material-symbols-outlined text-[18px]">visibility</span></button><button className="text-on-surface-variant hover:text-primary p-1"><span className="material-symbols-outlined text-[18px]">memory</span></button><button className="text-on-surface-variant hover:text-error p-1"><span className="material-symbols-outlined text-[18px]">delete</span></button></div></td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <div className="p-4 border-t border-outline-variant bg-surface-container-low flex justify-between items-center text-label-sm font-label-sm text-on-surface-variant">
                <span>Showing <span className="text-on-surface font-mono">{rows.length}</span> entries</span>
                <div className="flex gap-1">
                  <button className="px-2 py-1 rounded bg-surface border border-outline-variant hover:bg-surface-variant disabled:opacity-50 flex items-center" disabled><span className="material-symbols-outlined text-[16px]">chevron_left</span></button>
                  <button className="px-3 py-1 rounded bg-primary-container text-on-primary-container border border-primary-container font-mono">1</button>
                  <button className="px-3 py-1 rounded bg-surface border border-outline-variant hover:bg-surface-variant font-mono">2</button>
                  <button className="px-3 py-1 rounded bg-surface border border-outline-variant hover:bg-surface-variant font-mono">3</button>
                  <span className="px-2 py-1">...</span>
                  <button className="px-3 py-1 rounded bg-surface border border-outline-variant hover:bg-surface-variant font-mono">25</button>
                  <button className="px-2 py-1 rounded bg-surface border border-outline-variant hover:bg-surface-variant flex items-center"><span className="material-symbols-outlined text-[16px]">chevron_right</span></button>
                </div>
              </div>
            </section>
          </div>
        </main>
      </div>
    </div>
  );
}
