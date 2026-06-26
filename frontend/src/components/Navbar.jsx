import React from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Terminal, User, LogOut, LogIn, UserPlus } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import "./Navbar.css";

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header className="navbar">
      <div className="navbar-inner">
        {/* Logo */}
        <Link to="/" className="navbar-logo">
          <div className="logo-mark">
            <Terminal size={16} strokeWidth={2.5} />
          </div>
          <span className="logo-text">TempShell</span>
        </Link>

        {/* Right side */}
        <nav className="navbar-nav">
          {user ? (
            <>
              <Link
                to="/shell"
                className={`nav-pill ${isActive("/shell") ? "nav-pill--active" : ""}`}
              >
                <Terminal size={14} />
                Terminal
              </Link>

              <div className="nav-divider" />

              <div className="nav-user">
                <div className="user-avatar">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <span className="user-name">{user.username}</span>
              </div>

              <button onClick={handleLogout} className="nav-logout">
                <LogOut size={14} />
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className={`nav-pill ${isActive("/login") ? "nav-pill--active" : ""}`}
              >
                <LogIn size={14} />
                Login
              </Link>
              <Link to="/signup" className="nav-cta">
                <UserPlus size={14} />
                Sign Up
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Navbar;
