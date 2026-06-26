import React from "react";
import { Link } from "react-router-dom";
import { Terminal, Shield, Zap, Box, ArrowRight } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import "./Home.css";

const features = [
  {
    icon: <Shield size={18} />,
    title: "Fully Isolated",
    desc: "Each session runs inside its own Docker container — your workspace is completely private.",
  },
  {
    icon: <Zap size={18} />,
    title: "Instant Sessions",
    desc: "Containers spin up in milliseconds. No waiting, no setup — just run commands.",
  },
  {
    icon: <Box size={18} />,
    title: "Persistent Workspace",
    desc: "Your files in /workspace survive across sessions. Come back anytime.",
  },
];

const Home = () => {
  const { user } = useAuth();

  return (
    <div className="home">
      {/* Hero */}
      <section className="hero">
        <div className="hero-badge">
          <Terminal size={12} />
          <span>Secure Shell Environment</span>
        </div>

        <h1 className="hero-title">
          A terminal that lives<br />
          <span className="hero-accent">in the cloud.</span>
        </h1>

        <p className="hero-sub">
          Run shell commands inside isolated Docker containers — instantly,
          securely, from your browser.
        </p>

        <div className="hero-actions">
          {user ? (
            <Link to="/shell" className="btn-primary">
              <Terminal size={15} />
              Open Terminal
              <ArrowRight size={14} className="btn-arrow" />
            </Link>
          ) : (
            <>
              <Link to="/signup" className="btn-primary">
                Get Started
                <ArrowRight size={14} className="btn-arrow" />
              </Link>
              <Link to="/login" className="btn-ghost">
                Sign in
              </Link>
            </>
          )}
        </div>

        {/* Mini terminal preview */}
        <div className="hero-terminal">
          <div className="ht-bar">
            <span className="dot dot-red" />
            <span className="dot dot-yellow" />
            <span className="dot dot-green" />
          </div>
          <div className="ht-body">
            <div className="ht-line">
              <span className="ht-path">/workspace</span>
              <span className="ht-chevron">›</span>
              <span className="ht-cmd">echo "Hello, World!"</span>
            </div>
            <div className="ht-output">Hello, World!</div>
            <div className="ht-line">
              <span className="ht-path">/workspace</span>
              <span className="ht-chevron">›</span>
              <span className="ht-cmd">ls -la</span>
            </div>
            <div className="ht-output">total 4{"\n"}drwxr-xr-x  notes.txt  project/</div>
            <div className="ht-line">
              <span className="ht-path">/workspace</span>
              <span className="ht-chevron ht-blink">_</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features">
        {features.map((f, i) => (
          <div key={i} className="feature-card">
            <div className="feature-icon">{f.icon}</div>
            <h3 className="feature-title">{f.title}</h3>
            <p className="feature-desc">{f.desc}</p>
          </div>
        ))}
      </section>
    </div>
  );
};

export default Home;
