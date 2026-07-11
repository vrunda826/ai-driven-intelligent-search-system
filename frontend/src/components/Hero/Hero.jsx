import { useNavigate } from "react-router-dom";
import AnimatedBackground from "./AnimatedBackground";

export default function Hero() {
  const navigate = useNavigate();
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden pt-24">
      <AnimatedBackground />

      <div className="relative z-10 max-w-7xl mx-auto grid lg:grid-cols-[1.15fr_0.85fr] gap-16 px-6 items-center">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full bg-slate-900/60 px-5 py-2 border border-slate-700">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
            System Active
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mt-8 leading-tight">
            AI-powered
            <span className="block text-blue-500">forensic CCTV search</span>
          </h1>

          <p className="mt-8 text-gray-300 text-lg max-w-2xl">
            Rapidly search people, vehicles, and events across citywide camera networks with multilingual natural-language queries and live workflow automation.
          </p>

          <div className="flex flex-wrap gap-5 mt-10">
            <button onClick={() => navigate("/login")} className="bg-blue-600 hover:bg-blue-700 px-8 py-4 rounded-lg text-center font-semibold transition-transform hover:-translate-y-0.5">
              Try Demo
            </button>
            <button onClick={() => navigate("/analysis-workflow")} className="border border-slate-600 hover:border-blue-400 px-8 py-4 rounded-lg text-center transition-colors">
              View Workflow
            </button>
          </div>

          <div className="mt-10 grid sm:grid-cols-3 gap-4 text-sm text-slate-300">
            <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
              <div className="text-2xl font-semibold text-white">12k+</div>
              <div className="mt-1 text-slate-400">events indexed daily</div>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
              <div className="text-2xl font-semibold text-white">94.2%</div>
              <div className="mt-1 text-slate-400">model confidence</div>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
              <div className="text-2xl font-semibold text-white">24/7</div>
              <div className="mt-1 text-slate-400">autonomous monitoring</div>
            </div>
          </div>
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-2xl shadow-blue-950/30">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="text-sm text-blue-400">Live mission board</div>
              <div className="text-xl font-semibold text-white">Case queue overview</div>
            </div>
            <div className="rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 text-xs text-blue-300">ACTIVE</div>
          </div>
          <div className="space-y-3">
            {[
              ["Vehicle search", "12 matches", "bg-blue-500/20 text-blue-300"],
              ["Person of interest", "4 matches", "bg-cyan-500/20 text-cyan-300"],
              ["Suspicious package", "2 alerts", "bg-orange-500/20 text-orange-300"],
            ].map(([title, meta, cls]) => (
              <div key={title} className="rounded-xl border border-slate-800 bg-slate-950/70 p-4 flex items-center justify-between">
                <div>
                  <div className="font-medium text-white">{title}</div>
                  <div className="text-sm text-slate-400">{meta}</div>
                </div>
                <span className={`rounded-full px-2.5 py-1 text-xs ${cls}`}>Ready</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}