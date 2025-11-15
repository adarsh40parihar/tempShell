import React, { createContext, useState, useContext, useEffect } from "react";
import axios from "axios";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Use empty string for relative URLs (proxied through nginx)
  const API_URL = process.env.REACT_APP_API_URL || "";

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      const username = localStorage.getItem("username");
      setUser({ username, token });
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API_URL}/api/v1/auth/login`, {
        username,
        password,
      });

      const { access_token, refresh_token } = response.data;

      localStorage.setItem("access_token", access_token);
      localStorage.setItem("refresh_token", refresh_token);
      localStorage.setItem("username", username);
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;

      setUser({ username, token: access_token });
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error:
          error.response?.data?.detail || "Login failed. Please try again.",
      };
    }
  };

  const signup = async (username, password, email) => {
    try {
      await axios.post(`${API_URL}/api/v1/auth/signup`, {
        username,
        password,
        email,
      });
      return { success: true };
    } catch (error) {
      let errorMessage = "Signup failed. Please try again.";

      if (error.response?.data?.detail) {
        // Handle both string and array of validation errors
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMessage = detail.map((err) => err.msg || err.message).join(", ");
        } else if (typeof detail === "string") {
          errorMessage = detail;
        } else if (typeof detail === "object") {
          errorMessage = JSON.stringify(detail);
        }
      }

      return {
        success: false,
        error: errorMessage,
      };
    }
  };

  const logout = async () => {
    try {
      await axios.delete(`${API_URL}/api/v1/shell/terminate`);
    } catch (error) {
      console.error("Error terminating shell:", error);
    }

    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("username");
    delete axios.defaults.headers.common["Authorization"];
    setUser(null);
  };

  const value = {
    user,
    login,
    signup,
    logout,
    loading,
    API_URL,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
