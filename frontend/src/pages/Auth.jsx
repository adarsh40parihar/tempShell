import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { User, Mail, Lock, Eye, EyeOff } from "lucide-react";
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
    // Keep UI in sync with route: /login -> login, /signup -> signup
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
      // Switch to login form and show success message
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
        <div className="gradient-orb orb-3"></div>
      </div>

      <div className="auth-wrapper">
        <div className={`auth-box ${isLogin ? "login-mode" : "signup-mode"}`}>
          {/* Left Panel - Decorative */}
          <div className="auth-panel decorative-panel" style={{ flex: 0.55 }}>
            <div className="panel-content">
              <div className="logo-section">
                <span className="logo-icon">⚡</span>
                <h1 className="logo-text">TempShell</h1>
              </div>
              <h2 className="panel-title">
                {isLogin ? "Welcome Back!" : "Join Us Today!"}
              </h2>
              <p className="panel-description">
                {isLogin
                  ? "Enter your credentials to access your secure terminal environment"
                  : "Create your account and start using powerful cloud-based shell terminals"}
              </p>
              <div className="decorative-elements">
                <div className="deco-circle"></div>
                <div className="deco-square"></div>
                <div className="deco-triangle"></div>
              </div>
            </div>
          </div>

          {/* Right Panel - Forms */}
          <div className="auth-panel form-panel">
            <div className="form-container">
              {/* Login Form */}
              <div className={`form-content ${isLogin ? "active" : ""}`}>
                <h2 className="form-title">Login</h2>
                <p className="form-subtitle">Access your account</p>

                {error && isLogin && (
                  <div className="error-alert">
                    <span className="error-icon">⚠</span>
                    <span>{error}</span>
                  </div>
                )}

                <form onSubmit={handleLoginSubmit} className="auth-form">
                  <div className="input-group">
                    <label htmlFor="login-username">Username</label>
                    <div className="input-wrapper">
                      <User className="input-icon" size={18} />
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
                      <Lock className="input-icon" size={18} />
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
                        aria-label={
                          showPassword ? "Hide password" : "Show password"
                        }
                      >
                        {showPassword ? (
                          <Eye size={18} />
                        ) : (
                          <EyeOff size={18} />
                        )}
                      </button>
                    </div>
                  </div>
{/* 
                  <div className="forgot-password-wrapper">
                    <a href="#" className="forgot-password-link">
                      Forgot Password?
                    </a>
                  </div> */}

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
                    <button
                      type="button"
                      className="toggle-link"
                      onClick={toggleForm}
                    >
                      Sign up
                    </button>
                  </p>
                </div>
              </div>

              {/* Signup Form */}
              <div className={`form-content ${!isLogin ? "active" : ""}`}>
                <h2 className="form-title">Create Account</h2>
                <p className="form-subtitle"></p>

                {error && !isLogin && (
                  <div className="error-alert">
                    <span className="error-icon">⚠</span>
                    <span>{error}</span>
                  </div>
                )}

                <form onSubmit={handleSignupSubmit} className="auth-form">
                  <div className="input-group">
                    <label htmlFor="signup-username">Username</label>
                    <div className="input-wrapper">
                      <User className="input-icon" size={18} />
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
                      <Mail className="input-icon" size={18} />
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
                      <Lock className="input-icon" size={18} />
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
                        aria-label={
                          showPassword ? "Hide password" : "Show password"
                        }
                      >
                        {showPassword ? (
                          <Eye size={18} />
                        ) : (
                          <EyeOff size={18} />
                        )}
                      </button>
                    </div>
                    {/* <small className="input-hint">
                      8+ chars with uppercase, lowercase, number & special char
                    </small> */}
                  </div>

                  <div className="input-group">
                    <label htmlFor="confirm-password">Confirm Password</label>
                    <div className="input-wrapper">
                      <Lock className="input-icon" size={18} />
                      <input
                        type={showConfirmPassword ? "text" : "password"}
                        id="confirm-password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                        disabled={loading}
                        placeholder="Re-enter your password"
                        autoComplete="new-password"
                      />
                      <button
                        type="button"
                        className="toggle-password"
                        onClick={() =>
                          setShowConfirmPassword(!showConfirmPassword)
                        }
                        aria-label={
                          showConfirmPassword
                            ? "Hide password"
                            : "Show password"
                        }
                      >
                        {showConfirmPassword ? (
                          <Eye size={18} />
                        ) : (
                          <EyeOff size={18} />
                        )}
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
                        <span className="spinner"></span> Creating Account...
                      </>
                    ) : (
                      <>Sign Up</>
                    )}
                  </button>
                </form>

                <div className="form-footer">
                  <p>
                    Already have an account?{" "}
                    <button
                      type="button"
                      className="toggle-link"
                      onClick={toggleForm}
                    >
                      Login
                    </button>
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

export default Auth;
