import { Link } from "react-router-dom";

const stages = [
  {
    title: "Upload",
    progress: "100%",
    eta: "ETA: 00:00",
    meta: "Vol: 4.2GB",
    icon: "check",
    state: "complete",
    accent: "text-primary",
    progressClass: "bg-primary",
    cardClass: "",
  },
  {
    title: "Frame Extraction",
    progress: "100%",
    eta: "ETA: 00:00",
    meta: "FPS: 120",
    icon: "check",
    state: "complete",
    accent: "text-primary",
    progressClass: "bg-primary",
    cardClass: "",
  },
  {
    title: "Object Detection",
    progress: "75%",
    eta: "ETA: 02:45",
    meta: "FPS: 45",
    icon: "sync",
    state: "active",
    accent: "text-secondary",
    progressClass: "bg-secondary",
    cardClass: "border-secondary/50 bg-secondary/5",
  },
  {
    title: "Tracking",
    progress: "0%",
    eta: "ETA: --:--",
    meta: "FPS: --",
    icon: "more_horiz",
    state: "pending",
    accent: "text-on-surface-variant",
    progressClass: "bg-outline-variant",
    cardClass: "opacity-50",
  },
  {
    title: "Attribute Rec.",
    progress: "0%",
    eta: "--",
    meta: "--",
    icon: "more_horiz",
    state: "pending",
    accent: "text-on-surface-variant",
    progressClass: "bg-outline-variant",
    cardClass: "opacity-50",
  },
  {
    title: "Metadata",
    progress: "0%",
    eta: "--",
    meta: "--",
    icon: "more_horiz",
    state: "pending",
    accent: "text-on-surface-variant",
    progressClass: "bg-outline-variant",
    cardClass: "opacity-50",
  },
  {
    title: "Index Complete",
    progress: "0%",
    eta: "--",
    meta: "--",
    icon: "flag",
    state: "pending",
    accent: "text-on-surface-variant",
    progressClass: "bg-outline-variant",
    cardClass: "opacity-50",
  },
];

const stats = [
  { title: "Total Objects Tagged", value: "12.4k", detail: "+14% /min", icon: "trending_up", accent: "text-primary" },
  { title: "Confidence Score", value: "94.2%", detail: "Avg across models", icon: "verified", accent: "text-on-surface" },
  { title: "GPU Utilization", value: "88%", detail: "Thermal stable", icon: "memory", accent: "text-secondary-fixed" },
  { title: "Throughput (FPS)", value: "45", detail: "Live inference", icon: "speed", accent: "text-primary" },
];

const logs = [
  "Worker node 01: Frame extraction complete (12400 frames)",
  "Initializing YOLOv8 ensemble on TensorCore-4",
  "Thermal threshold approaching on GPU-2 (78C)",
  "Detection phase initiated. Batch size 64",
  "Processing batch 1/193...",
  "Processing batch 2/193...",
];

export default function AnalysisWorkflow() {
  return (
    <div className="min-h-screen bg-background text-on-surface font-body-md min-h-screen overflow-x-hidden">
      <header className="fixed top-0 w-full z-50 flex justify-between items-center px-gutter h-16 bg-background/80 backdrop-blur-xl border-b border-outline-variant/30">
        <div className="flex items-center gap-6">
          <Link to="/dashboard" className="font-headline-md text-headline-md font-bold text-primary tracking-tighter">SENTINEL AI</Link>
          <nav className="hidden md:flex gap-6">
            <Link to="/dashboard" className="text-on-surface-variant hover:text-primary transition-colors font-label-md text-label-md">Dashboard</Link>
            <Link to="/analysis-workflow" className="text-primary border-b-2 border-primary pb-1 hover:text-primary transition-colors font-label-md text-label-md">Forensics</Link>
            <Link to="/upload" className="text-on-surface-variant hover:text-primary transition-colors font-label-md text-label-md">Upload</Link>
            <a className="text-on-surface-variant hover:text-primary transition-colors font-label-md text-label-md" href="#">Archive</a>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <button className="text-on-surface hover:text-primary transition-colors">
            <span className="material-symbols-outlined">search</span>
          </button>
          <button className="text-on-surface hover:text-primary transition-colors">
            <span className="material-symbols-outlined">settings</span>
          </button>
          <div className="w-8 h-8 rounded-full overflow-hidden border border-outline-variant">
            <img
              alt="Analyst Profile"
              className="object-cover w-full h-full"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuDpTJ_ggVKqyYRA6moYvVLplV-rQBtD4b29_KIL3oce2Ss1AhlkiZDtqRAuEwp7VhHFgSyTL6N4oogvlhxT47UT1NicyDbE5IWQQaA6ng3af8KEeROpRWBWRWxZHFzCsTj07pDoHC4KWpUDyX6dQ-YIGb3FPV_kWPf4NlTfiRXbR9ViHtwN_0SG8lLV0iPBVuQmEfihm4OJ3QPRQEQnZoppaVc0Ez1DGrJobAzrBNYiHM_Zo6vkduv-zg"
            />
          </div>
        </div>
      </header>

      <aside className="fixed left-0 top-16 h-[calc(100vh-64px)] z-40 flex flex-col bg-surface-container-low/90 backdrop-blur-md border-r border-outline-variant/20 w-sidebar-width hidden md:flex">
        <div className="p-container-padding border-b border-outline-variant/20">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-10 h-10 rounded-full bg-surface-container-highest flex items-center justify-center border border-primary/30">
              <span className="material-symbols-outlined text-primary">psychiatry</span>
            </div>
            <div>
              <div className="font-headline-md text-headline-md text-primary leading-tight">SENTINEL</div>
              <div className="font-label-sm text-label-sm text-on-surface-variant">Forensic Engine v4.2</div>
            </div>
          </div>
          <button className="w-full bg-gradient-to-r from-primary-container to-[#0041CC] text-white rounded-lg py-2 font-label-md text-label-md flex items-center justify-center gap-2 hover:opacity-90 transition-opacity">
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>add</span>
            New Analysis
          </button>
        </div>
        <nav className="flex-1 py-4 flex flex-col gap-1 overflow-y-auto">
          <Link to="/analysis-workflow" className="bg-primary-container/20 text-primary border-r-4 border-primary px-container-padding py-3 flex items-center gap-4 hover:bg-surface-container-highest transition-all font-label-md text-label-md">
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>analytics</span>
            Pipeline
          </Link>
          <Link to="/upload" className="text-on-surface-variant hover:bg-surface-container-high px-container-padding py-3 flex items-center gap-4 hover:bg-surface-container-highest transition-all font-label-md text-label-md">
            <span className="material-symbols-outlined">input</span>
            Ingest
          </Link>
          <Link to="/dashboard" className="text-on-surface-variant hover:bg-surface-container-high px-container-padding py-3 flex items-center gap-4 hover:bg-surface-container-highest transition-all font-label-md text-label-md">
            <span className="material-symbols-outlined">phonelink_setup</span>
            Detection
          </Link>
          <a className="text-on-surface-variant hover:bg-surface-container-high px-container-padding py-3 flex items-center gap-4 hover:bg-surface-container-highest transition-all font-label-md text-label-md" href="#">
            <span className="material-symbols-outlined">route</span>
            Tracking
          </a>
          <a className="text-on-surface-variant hover:bg-surface-container-high px-container-padding py-3 flex items-center gap-4 hover:bg-surface-container-highest transition-all font-label-md text-label-md" href="#">
            <span className="material-symbols-outlined">database_spark</span>
            Metadata
          </a>
          <a className="text-on-surface-variant hover:bg-surface-container-high px-container-padding py-3 flex items-center gap-4 hover:bg-surface-container-highest transition-all font-label-md text-label-md" href="#">
            <span className="material-symbols-outlined">inventory_2</span>
            Indexing
          </a>
        </nav>
        <div className="border-t border-outline-variant/20 py-4 flex flex-col gap-1">
          <a className="text-on-surface-variant hover:bg-surface-container-high px-container-padding py-2 flex items-center gap-4 hover:bg-surface-container-highest transition-all font-label-md text-label-md" href="#">
            <span className="material-symbols-outlined">terminal</span>
            System Logs
          </a>
          <Link to="/" className="text-on-surface-variant hover:bg-surface-container-high px-container-padding py-2 flex items-center gap-4 hover:bg-surface-container-highest transition-all font-label-md text-label-md">
            <span className="material-symbols-outlined">help</span>
            Support
          </Link>
        </div>
      </aside>

      <main className="pt-16 md:pl-[280px] p-container-padding min-h-screen flex flex-col gap-container-padding">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface">Forensic Pipeline</h1>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">Analysis Job ID: XJ-9482-B | Sequence: Alpha</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="px-3 py-1 rounded-full border border-primary/50 bg-primary/10 text-primary font-label-sm text-label-sm flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
              Processing
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-container-padding">
          <div className="xl:col-span-2 flex flex-col gap-4">
            <div className="glass-panel rounded-xl p-6 relative overflow-hidden">
              <div className="scan-line"></div>
              <h2 className="font-headline-md text-headline-md text-on-surface mb-6 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">account_tree</span>
                Execution Sequence
              </h2>
              <div className="flex flex-col gap-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-primary before:via-outline-variant before:to-surface-container-lowest">
                {stages.map((stage, index) => (
                  <div key={stage.title} className={`relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group ${stage.state === "active" ? "is-active" : ""}`}>
                    <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${stage.state === "active" ? "border-secondary bg-surface-container-lowest text-secondary pulse-border" : stage.state === "complete" ? "border-primary bg-surface-container-lowest text-primary" : "border-outline-variant bg-surface-container-lowest text-outline-variant"} shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10`}>
                      <span className={`material-symbols-outlined text-sm ${stage.state === "active" ? "animate-spin" : ""}`}>{stage.icon}</span>
                    </div>
                    <div className={`w-[calc(100%-3rem)] md:w-[calc(50%-2.5rem)] glass-panel rounded-lg p-4 border border-outline-variant/30 ${stage.cardClass}`}>
                      <div className="flex justify-between items-start mb-2">
                        <h3 className={`font-label-md text-label-md ${stage.state === "pending" ? "text-on-surface-variant" : stage.state === "active" ? "text-secondary" : "text-on-surface"}`}>{index + 1}. {stage.title}</h3>
                        <span className={`font-label-sm text-label-sm ${stage.state === "pending" ? "text-on-surface-variant" : stage.state === "active" ? "text-secondary" : "text-primary"}`}>{stage.progress}</span>
                      </div>
                      {stage.state !== "pending" && (
                        <div className="w-full bg-surface-container-highest rounded-full h-1.5 mb-2">
                          <div className={`h-1.5 rounded-full ${stage.progressClass}`} style={{ width: stage.progress }}></div>
                        </div>
                      )}
                      <div className="flex justify-between text-on-surface-variant font-label-sm text-label-sm">
                        <span>{stage.eta}</span>
                        <span>{stage.meta}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-container-padding">
            <div className="glass-panel rounded-xl p-6">
              <h2 className="font-headline-md text-headline-md text-on-surface mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">monitoring</span>
                Real-time AI Stats
              </h2>
              <div className="grid grid-cols-2 gap-4">
                {stats.map((stat) => (
                  <div key={stat.title} className="bg-surface-container-highest/50 rounded-lg p-4 border border-outline-variant/20">
                    <div className="font-label-sm text-label-sm text-on-surface-variant mb-1">{stat.title}</div>
                    <div className={`font-display-lg text-display-lg ${stat.title === "Confidence Score" ? "text-on-surface" : "text-primary"}`}>{stat.value}</div>
                    <div className={`font-label-sm text-label-sm mt-1 flex items-center ${stat.title === "GPU Utilization" ? "text-secondary-fixed" : "text-on-surface-variant"}`}>
                      <span className="material-symbols-outlined text-[16px] mr-1">{stat.icon}</span>
                      {stat.detail}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-panel rounded-xl p-6 flex-1 flex flex-col">
              <div className="flex justify-between items-center mb-4">
                <h2 className="font-headline-md text-headline-md text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary">terminal</span>
                  System Logs
                </h2>
                <button className="text-on-surface-variant hover:text-primary transition-colors">
                  <span className="material-symbols-outlined text-sm">open_in_full</span>
                </button>
              </div>
              <div className="bg-surface-container-lowest rounded-lg p-4 font-label-sm text-label-sm text-on-surface-variant font-mono h-48 overflow-y-auto flex flex-col gap-1 border border-outline-variant/20 shadow-inner">
                {logs.map((entry, index) => (
                  <div key={entry} className={`flex gap-2 ${index === logs.length - 1 ? "animate-pulse text-secondary" : ""}`}>
                    <span className="text-outline">14:02:{String(11 + index).padStart(2, "0")}</span>
                    <span className={index === 2 ? "text-secondary" : index === logs.length - 1 ? "text-primary" : "text-primary"}>[INFO]</span>
                    <span>{entry}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
