import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./Auth.css";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const result = await login(username, password);

    if (result.success) {
      navigate("/shell");
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  return (
    <div className="auth-page">
      <div className="auth-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
      </div>

      <div className="auth-wrapper">
        <div className="auth-box login-mode">
          {/* Left Panel - Decorative */}
          <div className="auth-panel decorative-panel" style={{ flex: 0.55 }}>
            <div className="panel-content">
              <div className="logo-section">
                <span className="logo-icon">⚡</span>
                <h1 className="logo-text">TempShell</h1>
              </div>
              <h2 className="panel-title">Welcome Back!</h2>
              <p className="panel-description">
                Enter your credentials to access your secure terminal
                environment
              </p>
              <div className="decorative-elements">
                <div className="deco-circle"></div>
                <div className="deco-square"></div>
                <div className="deco-triangle"></div>
              </div>
            </div>
          </div>

          {/* Right Panel - Form */}
          <div className="auth-panel form-panel">
            <div className="form-container">
              <div className="form-content active">
                <h2 className="form-title">Login</h2>
                <p className="form-subtitle">Access your account</p>

                {error && (
                  <div className="error-alert">
                    <span className="error-icon">⚠</span>
                    <span>{error}</span>
                  </div>
                )}

                <form onSubmit={handleSubmit} className="auth-form">
                  <div className="input-group">
                    <label htmlFor="username">Username</label>
                    <div className="input-wrapper">
                      <span className="input-icon">👤</span>
                      <input
                        type="text"
                        id="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                        disabled={loading}
                        placeholder="Enter your username"
                        autoComplete="username"
                      />
                    </div>
                  </div>

                  <div className="input-group">
                    <label htmlFor="password">Password</label>
                    <div className="input-wrapper">
                      <span className="input-icon">🔒</span>
                      <input
                        type={showPassword ? "text" : "password"}
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        disabled={loading}
                        placeholder="Enter your password"
                        autoComplete="current-password"
                      />
                      <button
                        type="button"
                        className="toggle-password"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? "👁️" : "👁️‍🗨️"}
                      </button>
                    </div>
                  </div>

                  <button
                    type="submit"
                    className="submit-btn"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner"></span> Logging in...
                      </>
                    ) : (
                      <>Login</>
                    )}
                  </button>
                </form>

                <div className="form-footer">
                  <p>
                    Don't have an account?{" "}
                    <Link to="/signup" className="toggle-link">
                      Sign up
                    </Link>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
