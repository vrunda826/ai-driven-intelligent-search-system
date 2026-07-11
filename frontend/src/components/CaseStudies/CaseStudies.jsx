import { ArrowRight } from "lucide-react";

const studies = [
  {
    tag: "Crisis Management",
    title: "Major Event Security",
    description:
      "Secured a metropolitan marathon with 50,000+ participants using AI surveillance and real-time threat detection.",
  },
  {
    tag: "Forensic Analysis",
    title: "Cold Case Resolution",
    description:
      "Processed years of CCTV footage to identify suspects using AI-powered forensic search.",
  },
  {
    tag: "Public Safety",
    title: "Missing Person Recovery",
    description:
      "Tracked a missing child across multiple cameras and recovered them safely within minutes.",
  },
];

function CaseStudies() {
  return (
    <section
      id="case-studies"
      className="bg-slate-900 py-24"
    >
      <div className="max-w-7xl mx-auto px-6">

        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold">
            Case Studies
          </h2>

          <p className="mt-5 text-gray-400">
            Real deployments of our AI CCTV platform.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">

          {studies.map((item) => (
            <div
              key={item.title}
              className="rounded-xl border border-slate-700 bg-slate-950 p-8 hover:border-blue-500 transition"
            >
              <span className="inline-block px-3 py-1 rounded bg-blue-500/20 text-blue-400 text-sm">
                {item.tag}
              </span>

              <h3 className="text-2xl font-semibold mt-6">
                {item.title}
              </h3>

              <p className="text-gray-400 mt-4">
                {item.description}
              </p>

              <button className="flex items-center gap-2 mt-8 text-blue-400 hover:text-blue-300">
                Read More
                <ArrowRight size={18} />
              </button>
            </div>
          ))}

        </div>
      </div>
    </section>
  );
}

export default CaseStudies;