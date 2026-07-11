import { Search, Bell, Radar } from "lucide-react";

export default function Navbar() {
  return (
    <header className="fixed top-0 left-0 w-full z-50 border-b border-slate-700 bg-slate-950/80 backdrop-blur-xl">

      <div className="max-w-7xl mx-auto h-20 flex justify-between items-center px-6">

        <div className="flex items-center gap-3">

          <Radar size={34} className="text-blue-500" />

          <h1 className="text-2xl font-bold text-blue-400">
            Smart CCTV Search
          </h1>

        </div>

        <nav className="hidden md:flex items-center gap-10">

          <a href="#features">Features</a>

          <a href="#technology">Technology</a>

          <a href="#case-studies">Case Studies</a>

        </nav>

        <div className="flex gap-5 items-center">

          <Search className="cursor-pointer" />

          <Bell className="cursor-pointer" />

          <button className="bg-blue-600 hover:bg-blue-700 px-5 py-2 rounded-lg">
            Contact
          </button>

        </div>

      </div>

    </header>
  );
}