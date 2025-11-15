import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./Home.css";

const Home = () => {
  const { user } = useAuth();

  return (
    <div className="home-container">
      <div className="home-content">
        <div className="hero-section">
          <div className="hero-badge">
            <span className="badge-icon">⚡</span>
            <span>Powered by Kubernetes & FastAPI</span>
          </div>
          <h1 className="hero-title">TempShell</h1>
          <p className="hero-subtitle">
            Secure, Isolated, Temporary Shell Environments
          </p>
          <p className="hero-description">
            Run commands in isolated Kubernetes pods with enterprise-grade
            security. No installation required, just login and start coding.
          </p>

          <div className="hero-buttons">
            {user ? (
              <Link to="/shell" className="hero-btn btn-primary">
                <span className="btn-icon">▶</span>
                Open Terminal
              </Link>
            ) : (
              <>
                <Link to="/signup" className="hero-btn btn-primary">
                  <span className="btn-icon">🚀</span>
                  Get Started
                </Link>
                <Link to="/login" className="hero-btn btn-secondary">
                  <span className="btn-icon">🔐</span>
                  Login
                </Link>
              </>
            )}
          </div>
        </div>

        <div className="features-section">
          <h2 className="section-title">Why Choose TempShell?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">🔒</div>
              </div>
              <h3 className="feature-title">Secure by Design</h3>
              <p className="feature-description">
                NIST-compliant security with JWT authentication and bcrypt
                password hashing
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">🏝️</div>
              </div>
              <h3 className="feature-title">Complete Isolation</h3>
              <p className="feature-description">
                Each user gets their own Kubernetes pod with strict resource
                limits
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">⚡</div>
              </div>
              <h3 className="feature-title">Fast & Efficient</h3>
              <p className="feature-description">
                Powered by FastAPI and React for lightning-fast performance
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">🎯</div>
              </div>
              <h3 className="feature-title">Easy to Use</h3>
              <p className="feature-description">
                Simple web interface - no setup required, just login and start
              </p>
            </div>
          </div>
        </div>

        <div className="tech-section">
          <h2 className="section-title">Built With Modern Technology</h2>
          <div className="tech-grid">
            <div className="tech-item">
              <div className="tech-logo">🐍</div>
              <div className="tech-name">FastAPI</div>
            </div>
            <div className="tech-item">
              <div className="tech-logo">⚛️</div>
              <div className="tech-name">React</div>
            </div>
            <div className="tech-item">
              <div className="tech-logo">☸️</div>
              <div className="tech-name">Kubernetes</div>
            </div>
            <div className="tech-item">
              <div className="tech-logo">🐳</div>
              <div className="tech-name">Docker</div>
            </div>
            <div className="tech-item">
              <div className="tech-logo">🗄️</div>
              <div className="tech-name">MySQL</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
