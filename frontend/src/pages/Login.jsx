import React, { useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../services/api";
import { saveAuthSession } from "../utils/auth";

export default function Login() {
  const formRef = useRef(null);
  const btnRef = useRef(null);
  const spinnerRef = useRef(null);
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    const btn = btnRef.current;
    const spinner = spinnerRef.current;
    const btnText = btn?.querySelector("#btn-text");
    const btnIcon = btn?.querySelector("#btn-icon");
    const formData = new FormData(formRef.current);

    setError("");
    setIsLoading(true);
    btn?.classList.add("pointer-events-none");
    btnText?.classList.add("opacity-0", "-translate-y-4");
    btnIcon?.classList.add("opacity-0", "translate-x-4");
    spinner?.classList.remove("opacity-0");
    btn?.closest(".glass-panel")?.classList.add("ring-1", "ring-primary-container", "shadow-[0_0_30px_rgba(0,82,255,0.2)]");

    try {
      const result = await login({
        username: formData.get("username")?.toString() || "",
        password: formData.get("password")?.toString() || "",
      });

      if (result.success) {
        saveAuthSession({ token: result.token, user: result.user });
        navigate("/dashboard");
      } else {
        setError(result.error || "Authentication failed.");
      }
    } catch (err) {
      setError(err?.response?.data?.error || "Authentication failed. Try admin / password");
    } finally {
      setIsLoading(false);
      btn?.classList.remove("pointer-events-none");
      btnText?.classList.remove("opacity-0", "-translate-y-4");
      btnIcon?.classList.remove("opacity-0", "translate-x-4");
      spinner?.classList.add("opacity-0");
      btn?.closest(".glass-panel")?.classList.remove("ring-1", "ring-primary-container", "shadow-[0_0_30px_rgba(0,82,255,0.2)]");
      formRef.current?.reset();
    }
  }

  return (
    <div className="min-h-screen w-full flex bg-surface text-on-surface font-body-md">
      <div className="hidden lg:flex w-1/2 relative bg-surface-container-lowest border-r border-outline-variant/30 flex-col justify-end p-12 overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-50 z-0"></div>
        <div className="absolute inset-0 z-10 opacity-70 mix-blend-screen pointer-events-none"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-surface-container-lowest via-surface-container-lowest/50 to-transparent z-10"></div>
        <div className="absolute inset-0 bg-gradient-to-r from-surface-container-lowest via-transparent to-surface-container-lowest/20 z-10"></div>
        <div className="relative z-20 max-w-lg mb-8">
          <div className="flex items-center gap-3 mb-6">
            <span className="material-symbols-outlined text-primary text-4xl" style={{ fontVariationSettings: "'FILL' 1" }}>policy</span>
            <h1 className="font-display-lg text-display-lg text-on-surface tracking-tighter">SENTINEL<span className="text-primary-container">.OS</span></h1>
          </div>
          <div className="border-l-2 border-primary-container pl-6 py-2">
            <h2 className="font-headline-md text-headline-md text-on-surface mb-2">Urban Intelligence Grid</h2>
            <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed">Predictive threat modeling and multi-spectrum forensic analysis for municipal enforcement. Secure gateway connection established.</p>
          </div>
        </div>
        <div className="relative z-20 flex items-center gap-4 font-label-sm text-label-sm text-outline uppercase tracking-widest mt-auto">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-secondary-container animate-pulse"></span>
            <span>Node: Alpha-7</span>
          </div>
          <span className="text-outline-variant">|</span>
          <span>Encryption: AES-256</span>
          <span className="text-outline-variant">|</span>
          <span>Status: Optimal</span>
        </div>
      </div>

      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-12 bg-surface relative z-30">
        <div className="w-full max-w-[440px] glass-panel border border-outline-variant/50 rounded-xl shadow-[0_8px_32px_rgba(0,0,0,0.4)] relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary-container/50 to-transparent"></div>
          <div className="p-8 sm:p-10">
            <div className="text-center mb-10">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-surface-container border border-outline-variant mb-6 relative">
                <div className="absolute inset-0 rounded-full border border-primary-container/30 scale-110 animate-pulse"></div>
                <span className="material-symbols-outlined text-primary text-3xl">admin_panel_settings</span>
              </div>
              <h2 className="font-headline-lg text-headline-lg text-on-surface mb-2">Operator Gateway</h2>
              <p className="font-body-sm text-body-sm text-on-surface-variant">Provide forensic credentials to authenticate.</p>
            </div>

            <form className="space-y-6" id="auth-form" ref={formRef} onSubmit={handleSubmit}>
              <div className="space-y-2">
                <label className="font-label-sm text-label-sm text-on-surface block uppercase tracking-wider" htmlFor="username">Operator ID</label>
                <div className="relative group/input">
                  <span className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-outline group-focus-within/input:text-primary transition-colors">
                    <span className="material-symbols-outlined text-[20px]">badge</span>
                  </span>
                  <input autoComplete="username" className="w-full bg-surface-container-high border border-outline-variant text-on-surface font-label-md text-label-md rounded-lg pl-12 pr-4 py-3.5 focus-scan placeholder-outline/50 transition-all shadow-inner" id="username" name="username" placeholder="OP-XXXX" required type="text" />
                </div>
              </div>

              <div className="space-y-2">
                <label className="font-label-sm text-label-sm text-on-surface block uppercase tracking-wider" htmlFor="password">Passcode</label>
                <div className="relative group/input">
                  <span className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-outline group-focus-within/input:text-primary transition-colors">
                    <span className="material-symbols-outlined text-[20px]">key</span>
                  </span>
                  <input autoComplete="current-password" className="w-full bg-surface-container-high border border-outline-variant text-on-surface font-label-md text-label-md rounded-lg pl-12 pr-4 py-3.5 focus-scan placeholder-outline/50 transition-all shadow-inner tracking-widest" id="password" name="password" placeholder="••••••••" required type="password" />
                </div>
              </div>

              <div className="flex items-center justify-between pt-2">
                <label className="flex items-center gap-3 cursor-pointer group/check">
                  <div className="relative flex items-center">
                    <input className="peer w-5 h-5 rounded border-outline-variant bg-surface-container-high text-primary-container focus:ring-primary-container focus:ring-offset-surface focus:ring-offset-2 transition-all cursor-pointer" type="checkbox" />
                  </div>
                  <span className="font-body-sm text-body-sm text-on-surface-variant group-hover/check:text-on-surface transition-colors">Retain Session</span>
                </label>
                <a className="font-label-sm text-label-sm text-primary hover:text-primary-fixed transition-colors underline-offset-4 hover:underline" href="#">Forgot Passcode?</a>
              </div>

              {error ? <div className="rounded-lg border border-error/30 bg-error/10 p-3 text-sm text-error">{error}</div> : null}

              <div className="pt-4">
                <button ref={btnRef} id="submit-btn" type="submit" disabled={isLoading} className="w-full relative overflow-hidden group/btn bg-gradient-to-b from-[#0052FF] to-[#0041CC] border border-[#0052FF]/50 text-on-primary-container font-label-md text-label-md uppercase tracking-wider py-4 rounded-lg flex items-center justify-center gap-2 transition-all hover:shadow-[0_0_20px_rgba(0,82,255,0.4)] active:scale-[0.98] disabled:opacity-75">
                  <span id="btn-text" className="relative z-10 transition-transform duration-300">{isLoading ? "Authenticating..." : "Initialize Access"}</span>
                  <span id="btn-icon" className="material-symbols-outlined text-[20px] relative z-10 transition-transform duration-300 group-hover/btn:translate-x-1">login</span>
                  <div id="btn-spinner" ref={spinnerRef} className="absolute inset-0 flex items-center justify-center bg-[#0041CC] opacity-0 pointer-events-none transition-opacity duration-300">
                    <svg className="animate-spin h-6 w-6 text-on-primary-container" fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" fill="currentColor"></path>
                    </svg>
                  </div>
                </button>
              </div>
            </form>

            <div className="mt-10 pt-6 border-t border-outline-variant/30">
              <div className="flex items-start gap-3 bg-error-container/10 border border-error-container/30 rounded-lg p-4">
                <span className="material-symbols-outlined text-error text-[20px] mt-0.5">gavel</span>
                <p className="font-label-sm text-label-sm text-error/90 leading-tight">Authorized Personnel Only. All access is logged, monitored, and subject to forensic auditing.</p>
              </div>
              <div className="mt-6 flex flex-col gap-3">
                <Link to="/dashboard" className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary-container px-4 py-2 text-sm text-on-primary-container transition-colors">
                  <span className="material-symbols-outlined text-[18px]">sensor_occupied</span>
                  Open Dashboard
                </Link>
                <Link to="/" className="inline-flex items-center gap-2 text-sm text-primary hover:text-primary-fixed transition-colors">
                  <span className="material-symbols-outlined text-[18px]">arrow_back</span>
                  Back to Home
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
