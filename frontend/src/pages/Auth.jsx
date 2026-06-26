import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./Auth.css";

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Login form state
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Signup form state
  const [signupUsername, setSignupUsername] = useState("");
  const [signupEmail, setSignupEmail] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login, signup } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  React.useEffect(() => {
    setIsLogin(location.pathname !== "/signup");
  }, [location.pathname]);

  const toggleForm = () => {
    setIsLogin(!isLogin);
    setError("");
    setShowPassword(false);
    setShowConfirmPassword(false);
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const result = await login(loginUsername, loginPassword);

    if (result.success) {
      navigate("/shell");
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (signupPassword !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (signupPassword.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    if (signupPassword.length > 72) {
      setError("Password cannot be longer than 72 characters");
      return;
    }

    const passwordBytes = new TextEncoder().encode(signupPassword);
    if (passwordBytes.length > 72) {
      setError("Password is too long (max 72 bytes in UTF-8)");
      return;
    }

    if (!/[A-Z]/.test(signupPassword)) {
      setError("Password must contain at least one uppercase letter");
      return;
    }
    if (!/[a-z]/.test(signupPassword)) {
      setError("Password must contain at least one lowercase letter");
      return;
    }
    if (!/[0-9]/.test(signupPassword)) {
      setError("Password must contain at least one digit");
      return;
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(signupPassword)) {
      setError("Password must contain at least one special character");
      return;
    }

    setLoading(true);

    const result = await signup(signupUsername, signupPassword, signupEmail);

    if (result.success) {
      setIsLogin(true);
      setLoginUsername(signupUsername);
      setError("");
      alert("Account created successfully! Please login.");
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
      </div>

      <div className="auth-wrapper">
        <div className="auth-box">
          {/* Login Form */}
          {isLogin && (
            <div className="form-content active">
              <div className="form-header">
                <h1 className="form-title">Welcome Back</h1>
                <p className="form-subtitle">Access your secure terminal</p>
              </div>

              {error && (
                <div className="error-alert">
                  <span className="error-icon">⚠</span>
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleLoginSubmit} className="auth-form">
                <div className="input-group">
                  <label htmlFor="login-username">Username</label>
                  <div className="input-wrapper">
                    <span className="input-icon">👤</span>
                    <input
                      type="text"
                      id="login-username"
                      value={loginUsername}
                      onChange={(e) => setLoginUsername(e.target.value)}
                      required
                      disabled={loading}
                      placeholder="Enter your username"
                      autoComplete="username"
                    />
                  </div>
                </div>

                <div className="input-group">
                  <label htmlFor="login-password">Password</label>
                  <div className="input-wrapper">
                    <span className="input-icon">🔒</span>
                    <input
                      type={showPassword ? "text" : "password"}
                      id="login-password"
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
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

                <button type="submit" className="submit-btn" disabled={loading}>
                  {loading ? (
                    <>
                      <span className="spinner"></span> Logging in...
                    </>
                  ) : (
                    "Login"
                  )}
                </button>
              </form>

              <div className="form-footer">
                <p>
                  Don't have an account?{" "}
                  <button type="button" className="toggle-link" onClick={toggleForm}>
                    Sign up
                  </button>
                </p>
              </div>
            </div>
          )}

          {/* Signup Form */}
          {!isLogin && (
            <div className="form-content active">
              <div className="form-header">
                <h1 className="form-title">Create Account</h1>
                <p className="form-subtitle">Join TempShell</p>
              </div>

              {error && (
                <div className="error-alert">
                  <span className="error-icon">⚠</span>
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSignupSubmit} className="auth-form">
                <div className="input-group">
                  <label htmlFor="signup-username">Username</label>
                  <div className="input-wrapper">
                    <span className="input-icon">👤</span>
                    <input
                      type="text"
                      id="signup-username"
                      value={signupUsername}
                      onChange={(e) => setSignupUsername(e.target.value)}
                      required
                      disabled={loading}
                      placeholder="Choose a username"
                      autoComplete="username"
                      minLength={3}
                      maxLength={63}
                      pattern="[A-Za-z0-9_]+"
                    />
                  </div>
                </div>

                <div className="input-group">
                  <label htmlFor="signup-email">Email</label>
                  <div className="input-wrapper">
                    <span className="input-icon">📧</span>
                    <input
                      type="email"
                      id="signup-email"
                      value={signupEmail}
                      onChange={(e) => setSignupEmail(e.target.value)}
                      required
                      disabled={loading}
                      placeholder="your.email@example.com"
                      autoComplete="email"
                    />
                  </div>
                </div>

                <div className="input-group">
                  <label htmlFor="signup-password">Password</label>
                  <div className="input-wrapper">
                    <span className="input-icon">🔒</span>
                    <input
                      type={showPassword ? "text" : "password"}
                      id="signup-password"
                      value={signupPassword}
                      onChange={(e) => setSignupPassword(e.target.value)}
                      required
                      disabled={loading}
                      placeholder="Create a strong password"
                      autoComplete="new-password"
                      minLength={8}
                      maxLength={72}
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

                <div className="input-group">
                  <label htmlFor="confirm-password">Confirm Password</label>
                  <div className="input-wrapper">
                    <span className="input-icon">🔒</span>
                    <input
                      type={showConfirmPassword ? "text" : "password"}
                      id="confirm-password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                      disabled={loading}
                      placeholder="Confirm your password"
                      autoComplete="new-password"
                    />
                    <button
                      type="button"
                      className="toggle-password"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? "👁️" : "👁️‍🗨️"}
                    </button>
                  </div>
                </div>

                <button type="submit" className="submit-btn" disabled={loading}>
                  {loading ? (
                    <>
                      <span className="spinner"></span> Creating Account...
                    </>
                  ) : (
                    "Sign Up"
                  )}
                </button>
              </form>

              <div className="form-footer">
                <p>
                  Already have an account?{" "}
                  <button type="button" className="toggle-link" onClick={toggleForm}>
                    Login
                  </button>
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Auth;
