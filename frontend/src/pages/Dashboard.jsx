import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { getDashboardData } from "../services/api";

const navItems = [
  { label: "Live Monitor", icon: "videocam", active: false },
  { label: "Forensic Search", icon: "search_check", active: true },
  { label: "Evidence Vault", icon: "folder_shared", active: false },
  { label: "AI Analytics", icon: "analytics", active: false },
  { label: "System Health", icon: "settings_input_component", active: false },
];

const searchRows = [
  { query: "[color:red] AND [type:sedan] AND [loc:sector_4]", operator: "OP-773", time: "Just now", status: "Running", statusClass: "bg-secondary-fixed/10 text-secondary-fixed border-secondary-fixed/20" },
  { query: "[face_match:ID_8922] w/in 24h", operator: "SYS-AUTO", time: "12m ago", status: "Completed (14)", statusClass: "bg-surface-container-highest text-on-surface-variant" },
  { query: "[type:person] AND [action:running] AND [time:night]", operator: "OP-219", time: "45m ago", status: "Completed (0)", statusClass: "bg-surface-container-highest text-on-surface-variant" },
  { query: "[plate:partial\"XYZ\"] AND [loc:bridge_south]", operator: "OP-773", time: "1h ago", status: "Completed (2)", statusClass: "bg-surface-container-highest text-on-surface-variant" },
];

const alerts = [
  { title: "Unauthorized Access Detected", detail: "LOC: Sector 7G / Server Room B", time: "14:02:44", level: "Priority 1", levelClass: "text-error border-error/30", dotClass: "bg-error" },
  { title: "Perimeter Breach (Fence Line 4)", detail: "LOC: North Yard Exterior", time: "13:45:12", level: "Priority 2", levelClass: "text-orange-400 border-orange-400/30", dotClass: "bg-orange-400" },
  { title: "Watchlist Match (Vehicle Plate)", detail: "LOC: Main Gate Exit Cam", time: "11:20:05", level: "Priority 2", levelClass: "text-orange-400 border-orange-400/30", dotClass: "bg-orange-400" },
];

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const result = await getDashboardData();
        setData(result);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const stats = data ? [
    { title: "Total Cameras", value: data.overview.totalCameras.toLocaleString(), detail: "+12 online", icon: "nest_cam_outdoor", accent: "secondary-fixed" },
    { title: "Videos Indexed", value: data.overview.videosIndexed.toLocaleString(), detail: "Last 24h", icon: "video_library" },
    { title: "Objects Detected", value: data.overview.objectsDetected.toLocaleString(), detail: "342/sec", icon: "center_focus_strong", accent: "secondary-fixed" },
    { title: "Active Searches", value: data.overview.activeSearches.toString(), detail: "Running queries...", icon: "radar", accent: "secondary-fixed" },
    { title: "Today's Uploads", value: data.overview.uploadsToday.toString(), detail: "45GB processed", icon: "cloud_upload" },
    { title: "Processing Queue", value: `${data.overview.processingQueue} active`, detail: "75% complete", icon: "hourglass_top" },
  ] : [];

  return (
    <div className="min-h-screen bg-background text-on-background flex antialiased selection:bg-primary-container selection:text-on-primary-container">
      <nav className="bg-surface-container-low hidden md:flex w-[280px] flex-col fixed left-0 top-0 h-full z-40 border-r border-outline-variant pt-16 pb-4">
        <div className="px-4 mb-8 mt-4">
          <h2 className="font-headline-md text-headline-md text-primary font-bold tracking-tight">Command Center</h2>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">Sector 7G - Active</p>
        </div>
        <div className="flex-1 overflow-y-auto w-full px-2">
          {navItems.map((item) => (
            <a key={item.label} href="#" className={`mx-2 my-1 flex items-center px-4 py-3 rounded-lg transition-all ${item.active ? "bg-primary-container text-on-primary-container scale-[0.98]" : "text-on-surface-variant hover:text-on-surface hover:bg-surface-variant"}`}>
              <span className={`material-symbols-outlined mr-3 ${item.active ? "text-on-primary-container" : "text-on-surface-variant group-hover:text-primary"}`} style={{ fontVariationSettings: "'FILL' 1" }}>{item.icon}</span>
              <span className="font-label-md text-label-md">{item.label}</span>
            </a>
          ))}
        </div>
        <div className="px-4 mt-auto">
          <button className="w-full bg-gradient-to-r from-[#0052FF] to-[#0041CC] text-white font-label-md text-label-md py-3 rounded-lg mb-6 flex justify-center items-center hover:opacity-90 transition-opacity shadow-[0_0_15px_rgba(0,82,255,0.2)]">
            <span className="material-symbols-outlined mr-2 text-lg">add</span>
            New Investigation
          </button>
          <div className="border-t border-outline-variant pt-4 space-y-2">
            <a href="#" className="text-on-surface-variant hover:text-on-surface mx-2 my-1 hover:bg-surface-variant transition-all flex items-center px-2 py-2 rounded-lg">
              <span className="material-symbols-outlined mr-3 text-sm text-on-surface-variant">ios_share</span>
              <span className="font-label-sm text-label-sm">Export Logs</span>
            </a>
            <Link to="/" className="text-on-surface-variant hover:text-on-surface mx-2 my-1 hover:bg-surface-variant transition-all flex items-center px-2 py-2 rounded-lg">
              <span className="material-symbols-outlined mr-3 text-sm text-error">logout</span>
              <span className="font-label-sm text-label-sm text-error">Logout</span>
            </Link>
          </div>
        </div>
      </nav>

      <div className="flex-1 flex flex-col md:ml-[280px] min-h-screen">
        <header className="bg-surface/80 backdrop-blur-xl border-b border-outline-variant fixed top-0 left-0 w-full z-50 flex justify-between items-center px-gutter h-16 md:pl-[calc(280px+16px)]">
          <div className="flex items-center">
            <h1 className="font-headline-md text-headline-md font-bold text-primary tracking-tight">Aegis Forensic Lab</h1>
          </div>
          <div className="flex-1 max-w-xl mx-8 hidden lg:flex">
            <div className="relative w-full group">
              <span className="material-symbols-outlined absolute left-3 top-1/2 transform -translate-y-1/2 text-on-surface-variant group-focus-within:text-secondary-fixed transition-colors">search</span>
              <input className="w-full bg-surface-container-high border border-outline-variant rounded-full py-2 pl-10 pr-4 text-on-surface font-label-md text-label-md focus:outline-none focus:border-secondary-fixed focus:ring-1 focus:ring-secondary-fixed/50 transition-all placeholder:text-on-surface-variant/50 font-mono text-sm" placeholder="Search parameters (e.g., 'red sedan sector 4')..." type="text" />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button className="p-2 text-on-surface-variant hover:bg-surface-variant/50 transition-colors rounded-full relative">
              <span className="material-symbols-outlined">notifications</span>
              <span className="absolute top-2 right-2 w-2 h-2 bg-secondary-fixed rounded-full pulse-dot"></span>
            </button>
            <button className="p-2 text-on-surface-variant hover:bg-surface-variant/50 transition-colors rounded-full">
              <span className="material-symbols-outlined">settings</span>
            </button>
            <button className="p-2 text-on-surface-variant hover:bg-surface-variant/50 transition-colors rounded-full">
              <span className="material-symbols-outlined">help</span>
            </button>
            <div className="h-8 w-px bg-outline-variant mx-2"></div>
            <button className="bg-primary/10 border border-primary/30 text-primary font-label-md text-label-md px-4 py-1.5 rounded-full hover:bg-primary/20 transition-colors flex items-center ml-2 hidden sm:flex">Investigate</button>
            <div className="ml-4 w-9 h-9 rounded-full border-2 border-primary/50 overflow-hidden cursor-pointer relative group">
              <img className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCSTYcgbAyGMDHg6YDJEfnOOOmfl6Pi0vfZcm84EZ8Di_WAK3baayA2VDjx6SP-19fcEr42Va2ru3b5iXfA_n_RHtIqFC194nOPBop-gPLKN0F2wNeNGrm4iZGoSzZR8WcP-UbEsK8DObWxmYDs61oAUvHoONarOaKLrBqoDn2ldWJ0EAsIj9pKj2vimAbmLWeZuGCN6DxE2-mj_vpMWiAvAlGq_0MJTXo9SHs12DTJOmqxmFrYy5CGGQ" alt="operator" />
              <div className="absolute inset-0 bg-primary/20 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </div>
          </div>
        </header>

        <main className="flex-1 p-container-padding pt-[calc(64px+24px)] space-y-6 max-w-[1920px] mx-auto w-full">
          <div className="flex justify-between items-end mb-8">
            <div>
              <div className="flex items-center space-x-2 mb-1">
                <span className="w-2 h-2 rounded-full bg-secondary-fixed pulse-dot"></span>
                <span className="font-label-sm text-label-sm text-secondary-fixed uppercase tracking-wider">Live Telemetry</span>
              </div>
              <h2 className="font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-surface">System Overview</h2>
            </div>
            <div className="flex gap-2">
              <Link to="/analysis-workflow" className="font-label-md text-label-md text-on-surface-variant font-mono bg-surface-container px-3 py-1.5 rounded border border-outline-variant hover:border-primary transition-colors">Open Workflow</Link>
              <Link to="/upload" className="font-label-md text-label-md text-on-surface-variant font-mono bg-surface-container px-3 py-1.5 rounded border border-outline-variant hover:border-primary transition-colors">Open Upload Center</Link>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {loading ? <div className="col-span-full text-on-surface-variant">Loading live telemetry...</div> : stats.map((stat, index) => (
              <div key={stat.title} className={`rounded-xl p-4 flex flex-col justify-between h-32 relative overflow-hidden group ${index === 3 ? "glass-overlay" : "glass-panel"}`}>
                <div className="absolute top-0 right-0 w-16 h-16 bg-primary/5 rounded-bl-full -mr-8 -mt-8 group-hover:scale-110 transition-transform"></div>
                <div className="flex justify-between items-start relative z-10">
                  <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">{stat.title}</span>
                  <span className={`material-symbols-outlined text-xl ${stat.accent === "secondary-fixed" ? "text-secondary-fixed" : "text-primary"}`}>{stat.icon}</span>
                </div>
                <div className="relative z-10">
                  <div className="font-display-lg text-[32px] leading-tight font-bold text-on-surface">{stat.value}</div>
                  <div className={`font-label-sm text-label-sm mt-1 flex items-center ${stat.accent === "secondary-fixed" ? "text-secondary-fixed" : "text-on-surface-variant"}`}>
                    {stat.accent === "secondary-fixed" ? <span className="material-symbols-outlined text-[14px] mr-1">trending_up</span> : <span className="w-1.5 h-1.5 bg-outline rounded-full mr-2"></span>}
                    {stat.detail}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="glass-panel rounded-xl p-6 lg:col-span-2 flex flex-col">
              <div className="flex justify-between items-center mb-6">
                <h3 className="font-headline-md text-headline-md text-on-surface">Detection Timeline</h3>
                <div className="flex space-x-2">
                  <button className="px-3 py-1 text-xs font-label-sm font-mono border border-outline-variant rounded bg-surface-container-high text-on-surface">1H</button>
                  <button className="px-3 py-1 text-xs font-label-sm font-mono border border-primary/50 rounded bg-primary/10 text-primary">24H</button>
                  <button className="px-3 py-1 text-xs font-label-sm font-mono border border-outline-variant rounded bg-surface-container text-on-surface-variant">7D</button>
                </div>
              </div>
              <div className="flex-1 relative min-h-[250px] bg-surface-container-lowest rounded-lg border border-outline-variant/50 p-4 flex items-end">
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiPjxkZWZzPjxwYXR0ZXJuIGlkPSJncmlkIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiPjxwYXRoIGQ9Ik0gNDAgMCBMIDAgMCAwIDQwIiBmaWxsPSJub25lIiBzdHJva2U9InJnYmEoNjcsIDcwLCA4NiwgMC4xKSIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIiAvPjwvc3ZnPg==')] opacity-50 rounded-lg"></div>
                <div className="w-full h-full relative z-10 flex items-end justify-between space-x-1 pb-6 pt-4 px-2">
                  {[30,45,25,85,60,35,15,50,75,95,65,40].map((height, index) => (
                    <div key={index} className={`w-full rounded-t ${index === 9 ? "bg-error/40 border-t-2 border-error shadow-[0_-5px_15px_rgba(255,180,171,0.2)]" : "bg-primary/40"}`} style={{ height: `${height}%` }}></div>
                  ))}
                </div>
                <div className="absolute bottom-1 left-4 right-4 flex justify-between text-xs font-label-sm text-on-surface-variant font-mono">
                  <span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>NOW</span>
                </div>
              </div>
            </div>

            <div className="glass-panel rounded-xl p-6 flex flex-col">
              <h3 className="font-headline-md text-headline-md text-on-surface mb-6">Object Distribution</h3>
              <div className="flex-1 flex flex-col justify-center items-center relative">
                <div className="w-48 h-48 rounded-full border-[16px] border-surface-container-highest relative flex items-center justify-center">
                  <div className="absolute inset-0 rounded-full border-[16px] border-primary" style={{ clipPath: "polygon(50% 50%, 100% 0, 100% 100%, 0 100%, 0 70%)" }}></div>
                  <div className="absolute inset-0 rounded-full border-[16px] border-secondary-fixed" style={{ clipPath: "polygon(50% 50%, 0 70%, 0 0, 30% 0)", transform: "rotate(-5deg)" }}></div>
                  <div className="absolute inset-0 rounded-full border-[16px] border-tertiary" style={{ clipPath: "polygon(50% 50%, 30% 0, 100% 0)", transform: "rotate(2deg)" }}></div>
                  <div className="text-center">
                    <div className="font-display-lg text-2xl font-bold text-on-surface">892k</div>
                    <div className="font-label-sm text-[10px] text-on-surface-variant uppercase">Total Hits</div>
                  </div>
                </div>
                <div className="w-full mt-8 space-y-3">
                  <div className="flex justify-between items-center text-sm"><div className="flex items-center"><span className="w-3 h-3 rounded-sm bg-primary mr-2"></span><span className="text-on-surface font-body-sm">Vehicle</span></div><span className="font-mono text-on-surface-variant">52%</span></div>
                  <div className="flex justify-between items-center text-sm"><div className="flex items-center"><span className="w-3 h-3 rounded-sm bg-secondary-fixed mr-2"></span><span className="text-on-surface font-body-sm">Person</span></div><span className="font-mono text-on-surface-variant">31%</span></div>
                  <div className="flex justify-between items-center text-sm"><div className="flex items-center"><span className="w-3 h-3 rounded-sm bg-tertiary mr-2"></span><span className="text-on-surface font-body-sm">License Plate</span></div><span className="font-mono text-on-surface-variant">12%</span></div>
                  <div className="flex justify-between items-center text-sm"><div className="flex items-center"><span className="w-3 h-3 rounded-sm bg-surface-container-highest mr-2 border border-outline-variant"></span><span className="text-on-surface font-body-sm">Face / Other</span></div><span className="font-mono text-on-surface-variant">5%</span></div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 pb-12">
            <div className="glass-panel rounded-xl overflow-hidden flex flex-col h-[400px]">
              <div className="p-4 border-b border-outline-variant/50 bg-surface-container-low/50 flex justify-between items-center">
                <div className="flex items-center">
                  <span className="material-symbols-outlined text-primary mr-2 text-sm">manage_search</span>
                  <h3 className="font-body-lg text-body-lg text-on-surface font-semibold">Active & Recent Searches</h3>
                </div>
                <button className="text-secondary-fixed font-label-sm text-xs hover:underline">View All</button>
              </div>
              <div className="overflow-x-auto flex-1">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-outline-variant/30 text-on-surface-variant font-label-sm text-xs uppercase bg-surface-container-lowest/50">
                      <th className="p-3 font-medium">Query Syntax</th>
                      <th className="p-3 font-medium">Operator</th>
                      <th className="p-3 font-medium">Time</th>
                      <th className="p-3 font-medium text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody className="font-body-sm text-sm divide-y divide-outline-variant/20">
                    {searchRows.map((row) => (
                      <tr key={row.query} className="hover:bg-surface-container-highest/30 transition-colors">
                        <td className="p-3 font-mono text-secondary-fixed text-xs max-w-[200px] truncate" title={row.query}>{row.query}</td>
                        <td className="p-3 text-on-surface">{row.operator}</td>
                        <td className="p-3 text-on-surface-variant text-xs">{row.time}</td>
                        <td className="p-3 text-right">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium border ${row.statusClass}`}>
                            {row.status.startsWith("Running") ? <span className="w-1.5 h-1.5 rounded-full bg-secondary-fixed mr-1 animate-pulse"></span> : null}
                            {row.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="glass-overlay rounded-xl overflow-hidden flex flex-col h-[400px] border-error/20">
              <div className="p-4 border-b border-outline-variant/50 bg-error/5 flex justify-between items-center relative overflow-hidden">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-error"></div>
                <div className="flex items-center pl-2">
                  <span className="material-symbols-outlined text-error mr-2 text-sm">warning</span>
                  <h3 className="font-body-lg text-body-lg text-white font-semibold">Critical Alerts</h3>
                </div>
                <button className="text-on-surface-variant font-label-sm text-xs hover:text-white transition-colors">Acknowledge All</button>
              </div>
              <div className="flex-1 overflow-y-auto p-2 space-y-2">
                {alerts.map((alert) => (
                  <div key={alert.title} className="bg-surface-container-high border border-error/30 rounded-lg p-3 hover:bg-surface-bright transition-colors cursor-pointer relative overflow-hidden group">
                    <div className="absolute right-0 top-0 bottom-0 w-12 bg-gradient-to-l from-error/10 to-transparent"></div>
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center">
                        <span className={`w-2 h-2 rounded-full mr-2 pulse-dot ${alert.dotClass}`}></span>
                        <span className={`font-label-sm text-[10px] uppercase tracking-wider border px-1.5 rounded ${alert.levelClass}`}>{alert.level}</span>
                        <span className="font-mono text-xs text-on-surface-variant ml-2">{alert.time}</span>
                      </div>
                      <span className="material-symbols-outlined text-on-surface-variant text-sm group-hover:text-white">chevron_right</span>
                    </div>
                    <div className="font-body-sm text-on-surface font-medium mb-1">{alert.title}</div>
                    <div className="font-label-sm text-xs text-on-surface-variant font-mono">{alert.detail}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
