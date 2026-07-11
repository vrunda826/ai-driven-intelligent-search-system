import {
  Shield,
  Github,
  Linkedin,
  Mail,
} from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-black border-t border-slate-800">

      <div className="max-w-7xl mx-auto px-6 py-14">

        <div className="grid md:grid-cols-4 gap-10">

          <div className="md:col-span-2">

            <div className="flex items-center gap-3">

              <Shield className="text-blue-500" />

              <h2 className="text-2xl font-bold">
                Smart CCTV Search
              </h2>

            </div>

            <p className="mt-5 text-gray-400 max-w-md">
              AI Powered CCTV Search Platform capable of searching
              people, vehicles and events using natural language.
            </p>

          </div>

          <div>

            <h4 className="font-semibold mb-4">
              Product
            </h4>

            <ul className="space-y-3 text-gray-400">

              <li>Dashboard</li>
              <li>Search</li>
              <li>Reports</li>
              <li>Analytics</li>

            </ul>

          </div>

          <div>

            <h4 className="font-semibold mb-4">
              Contact
            </h4>

            <div className="space-y-3">

              <div className="flex gap-3">
                <Mail size={18} />
                support@smartcctv.ai
              </div>

              <div className="flex gap-3">
                <Github size={18} />
                Github
              </div>

              <div className="flex gap-3">
                <Linkedin size={18} />
                LinkedIn
              </div>

            </div>

          </div>

        </div>

        <hr className="border-slate-800 my-10"/>

        <p className="text-center text-gray-500">
          © 2026 Smart CCTV Search. All Rights Reserved.
        </p>

      </div>

    </footer>
  );
}