import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./Home.css";

const Home = () => {
  const { user } = useAuth();

  return (
    <div className="home-container">
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="badge-dot"></span>
            <span>Secure Shell Environment</span>
          </div>

          <h1 className="hero-title">Temp<span className="title-accent">Shell</span></h1>

          <p className="hero-subtitle">
            Execute commands in isolated environments instantly
          </p>

          <p className="hero-description">
            A secure, simple platform for running shell commands with complete isolation.
            No setup required—just login and start executing commands.
          </p>

          <div className="hero-actions">
            {user ? (
              <Link to="/shell" className="btn btn-primary btn-lg">
                <span>▶</span>
                Open Terminal
              </Link>
            ) : (
              <>
                <Link to="/signup" className="btn btn-primary btn-lg">
                  <span>🚀</span>
                  Get Started
                </Link>
                <Link to="/login" className="btn btn-secondary btn-lg">
                  <span>🔐</span>
                  Sign In
                </Link>
              </>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
