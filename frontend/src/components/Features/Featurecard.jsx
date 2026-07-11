export default function FeatureCard({
  icon,
  title,
  description,
}) {
  return (
    <div className="bg-slate-900/60 border border-slate-700 rounded-xl p-6 hover:border-blue-500 transition">

      <div className="w-14 h-14 rounded-lg bg-blue-500/20 flex items-center justify-center mb-5">

        {icon}

      </div>

      <h3 className="text-xl font-semibold mb-3">

        {title}

      </h3>

      <p className="text-gray-400">

        {description}

      </p>

    </div>
  );
}