import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./Navbar.css";

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">⚡</span>
          <span className="logo-text">TempShell</span>
        </Link>

        <div className="nav-menu">
          {user ? (
            <>
              <Link to="/shell" className="nav-link">
                <span className="nav-link-icon">▶</span>
                <span>Terminal</span>
              </Link>
              <div className="nav-user">
                <span className="user-icon">👤</span>
                <span className="user-name">{user.username}</span>
              </div>
              <button onClick={handleLogout} className="nav-btn logout-btn">
                <span className="btn-icon">🚪</span>
                <span>Logout</span>
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">
                <span>Login</span>
              </Link>
              <Link to="/signup" className="nav-btn signup-btn">
                <span>Sign Up</span>
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
