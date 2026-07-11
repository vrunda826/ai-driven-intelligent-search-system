/** @type {import('tailwindcss').Config} */

export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "secondary-fixed": "#7df4ff",
        "primary-fixed-dim": "#b7c4ff",
        outline: "#8d90a2",
        "surface-container-lowest": "#060e20",
        "on-tertiary-fixed": "#0b1c30",
        "on-tertiary": "#213145",
        surface: "#0b1326",
        "outline-variant": "#434656",
        "on-tertiary-container": "#d6e6ff",
        "secondary-fixed-dim": "#00dbe9",
        "primary-fixed": "#dde1ff",
        primary: "#b7c4ff",
        "on-surface": "#dae2fd",
        "on-secondary-container": "#00686f",
        background: "#0b1326",
        "on-primary": "#002682",
        "secondary-container": "#00eefc",
        "surface-variant": "#2d3449",
        "surface-container": "#171f33",
        "tertiary-fixed-dim": "#b7c8e1",
        "surface-bright": "#31394d",
        "surface-tint": "#b7c4ff",
        "surface-container-low": "#131b2e",
        "on-tertiary-fixed-variant": "#38485d",
        "on-primary-fixed": "#001452",
        "on-error": "#690005",
        error: "#ffb4ab",
        "surface-container-highest": "#2d3449",
        "on-secondary-fixed-variant": "#004f54",
        "on-secondary-fixed": "#002022",
        "inverse-surface": "#dae2fd",
        "surface-dim": "#0b1326",
        "on-primary-fixed-variant": "#0038b6",
        secondary: "#d3fbff",
        "on-error-container": "#ffdad6",
        "error-container": "#93000a",
        "primary-container": "#0052ff",
        "tertiary-container": "#57677e",
        "on-surface-variant": "#c3c5d9",
        "tertiary-fixed": "#d3e4fe",
        tertiary: "#b7c8e1",
        "surface-container-high": "#222a3d",
        "inverse-primary": "#004ced",
        "on-secondary": "#00363a",
        "on-background": "#dae2fd"
      },
      borderRadius: {
        DEFAULT: "0.125rem",
        lg: "0.25rem",
        xl: "0.5rem",
        full: "0.75rem"
      },
      spacing: {
        gutter: "16px",
        "video-grid-gap": "8px",
        unit: "4px",
        "container-padding": "24px",
        "sidebar-width": "280px"
      },
      fontFamily: {
        "headline-lg-mobile": ["Inter"],
        "headline-lg": ["Inter"],
        "body-sm": ["Inter"],
        "body-md": ["Inter"],
        "label-md": ["JetBrains Mono"],
        "display-lg": ["Inter"],
        "label-sm": ["JetBrains Mono"],
        "body-lg": ["Inter"],
        "headline-md": ["Inter"]
      },
      fontSize: {
        "headline-lg-mobile": ["24px", { lineHeight: "32px", fontWeight: "600" }],
        "headline-lg": ["32px", { lineHeight: "40px", letterSpacing: "-0.01em", fontWeight: "600" }],
        "body-sm": ["14px", { lineHeight: "20px", fontWeight: "400" }],
        "body-md": ["16px", { lineHeight: "24px", fontWeight: "400" }],
        "label-md": ["14px", { lineHeight: "20px", letterSpacing: "0.05em", fontWeight: "500" }],
        "display-lg": ["48px", { lineHeight: "56px", letterSpacing: "-0.02em", fontWeight: "700" }],
        "label-sm": ["12px", { lineHeight: "16px", letterSpacing: "0.05em", fontWeight: "500" }],
        "body-lg": ["18px", { lineHeight: "28px", fontWeight: "400" }],
        "headline-md": ["24px", { lineHeight: "32px", fontWeight: "600" }]
      }
    }
  },
  plugins: []
};