
import {
  Crosshair,
  Camera,
  Search,
  Bell,
} from "lucide-react";

import FeatureCard from "./FeatureCard";

export default function Features() {

  const features = [

    {
      icon: <Crosshair size={30}/>,
      title: "Real Time Tracking",
      description:
        "Track any person or vehicle across multiple CCTV cameras."
    },

    {
      icon: <Camera size={30}/>,
      title: "Multi Camera AI",
      description:
        "Connect unlimited CCTV cameras into one intelligent system."
    },

    {
      icon: <Search size={30}/>,
      title: "Natural Language Search",
      description:
        "Search using queries like 'red shirt person near gate'."
    },

    {
      icon: <Bell size={30}/>,
      title: "Instant Alerts",
      description:
        "Receive real-time AI alerts for suspicious activity."
    }

  ];

  return (

    <section
      id="features"
      className="py-24 bg-slate-950"
    >

      <div className="max-w-7xl mx-auto px-6">

        <h2 className="text-5xl font-bold text-center">

          Smart CCTV Features

        </h2>

        <p className="text-center text-gray-400 mt-5 mb-16">

          Artificial Intelligence powered surveillance platform.

        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">

          {features.map((item,index)=>(

            <FeatureCard
              key={index}
              {...item}
            />

          ))}

        </div>

      </div>

    </section>

  );

}