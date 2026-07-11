export default function AnimatedBackground() {
  return (
    <div className="absolute inset-0 opacity-40 overflow-hidden">

      <svg
        viewBox="0 0 600 400"
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
      >

        <rect width="600" height="400" fill="#0b1326" />

        {/* Horizontal Grid */}

        {[40,80,120,160,200,240,280,320,360].map((y)=>(
          <line
            key={y}
            x1="0"
            y1={y}
            x2="600"
            y2={y}
            stroke="#1e293b"
            strokeWidth="0.5"
          />
        ))}

        {/* Vertical Grid */}

        {[40,80,120,160,200,240,280,320,360,400,440,480,520,560].map((x)=>(
          <line
            key={x}
            x1={x}
            y1="0"
            x2={x}
            y2="400"
            stroke="#1e293b"
            strokeWidth="0.5"
          />
        ))}

        {/* Camera */}

        <g transform="translate(150 100)">

          <path
            d="M20 100 L280 100 L260 160 L40 160 Z"
            fill="#31394d"
            stroke="#2563eb"
            strokeWidth="2"
          />

          <circle
            cx="150"
            cy="130"
            r="25"
            fill="#0b1326"
            stroke="#2563eb"
            strokeWidth="2"
          >

            <animate
              attributeName="opacity"
              values="0.5;1;0.5"
              dur="3s"
              repeatCount="indefinite"
            />

          </circle>

          <circle
            cx="150"
            cy="130"
            r="8"
            fill="red"
          >

            <animate
              attributeName="opacity"
              values="1;0;1"
              dur="1s"
              repeatCount="indefinite"
            />

          </circle>

        </g>

        {/* Scanner */}

        <path
          d="M300 230 L100 400 L500 400 Z"
          fill="url(#beam)"
          opacity=".3"
        >

          <animateTransform
            attributeName="transform"
            type="translate"
            from="-50 0"
            to="50 0"
            dur="4s"
            repeatCount="indefinite"
          />

        </path>

        {/* Detection Box */}

        <rect
          x="400"
          y="250"
          width="60"
          height="60"
          fill="none"
          stroke="#2563eb"
        >

          <animate
            attributeName="x"
            values="400;420;400"
            dur="5s"
            repeatCount="indefinite"
          />

        </rect>

        <text
          x="400"
          y="245"
          fill="#3b82f6"
          fontSize="10"
        >
          OBJECT 01
        </text>

        <rect
          x="100"
          y="300"
          width="80"
          height="80"
          fill="none"
          stroke="#2563eb"
        >

          <animate
            attributeName="y"
            values="300;280;300"
            dur="6s"
            repeatCount="indefinite"
          />

        </rect>

        <text
          x="100"
          y="295"
          fill="#3b82f6"
          fontSize="10"
        >
          OBJECT 02
        </text>

        <defs>

          <linearGradient
            id="beam"
            x1="300"
            y1="230"
            x2="300"
            y2="400"
          >

            <stop offset="0%" stopColor="#2563eb"/>

            <stop
              offset="100%"
              stopColor="#2563eb"
              stopOpacity="0"
            />

          </linearGradient>

        </defs>

      </svg>

      <div className="absolute inset-0 bg-gradient-to-b from-slate-900/40 via-slate-950/70 to-slate-950"></div>

    </div>
  );
}