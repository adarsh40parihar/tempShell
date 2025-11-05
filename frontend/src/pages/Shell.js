import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { useAuth } from "../contexts/AuthContext";
import "./Shell.css";

const Shell = () => {
  const [command, setCommand] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [commandHistory, setCommandHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  const terminalRef = useRef(null);
  const inputRef = useRef(null);

  const { API_URL } = useAuth();

  // Auto-scroll terminal on new output
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [history]);

  // Auto-focus input after loading completes
  useEffect(() => {
    if (!loading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [loading]);

  // Initial welcome messages (hidden after first command)
  useEffect(() => {
    setHistory([
      { type: "welcome", content: "Welcome to TempShell." },
      {
        type: "welcome",
        content: "Your commands run in an isolated Kubernetes environment.",
      },
      { type: "welcome", content: 'Type "help" to get started.' },
    ]);
  }, []);

  const executeCommand = async (e) => {
    e.preventDefault();
    const trimmed = command.trim();
    if (!trimmed || loading) return;

    setLoading(true);

    // Add to local command history for navigation
    setCommandHistory((prev) => [...prev, trimmed]);
    setHistoryIndex(-1);

    // Remove welcome lines on first command and show the input line
    setHistory((prev) => [
      ...prev.filter((h) => h.type !== "welcome"),
      { type: "input", content: trimmed },
    ]);

    try {
      const res = await axios.post(`${API_URL}/api/v1/shell/execute`, {
        command: trimmed,
      });

      setHistory((prev) => [
        ...prev,
        {
          type: "output",
          content: res.data?.output ?? "",
          exit_code: res.data?.exit_code,
        },
      ]);
    } catch (error) {
      setHistory((prev) => [
        ...prev,
        {
          type: "error",
          content:
            error.response?.data?.detail ||
            "Command execution failed. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
      setCommand("");
      if (inputRef.current) inputRef.current.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "ArrowUp") {
      e.preventDefault();
      if (commandHistory.length === 0) return;
      const newIndex = Math.min(historyIndex + 1, commandHistory.length - 1);
      setHistoryIndex(newIndex);
      setCommand(commandHistory[commandHistory.length - 1 - newIndex]);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (historyIndex <= 0) {
        setHistoryIndex(-1);
        setCommand("");
      } else {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setCommand(commandHistory[commandHistory.length - 1 - newIndex]);
      }
    }
  };

  const clearTerminal = () => setHistory([]);

  const focusInput = () => {
    if (inputRef.current && !loading) {
      inputRef.current.focus();
    }
  };

  return (
    <div className="shell-container" onClick={focusInput}>
      <div className="shell-content">
        <div className="terminal-window">
          <div className="terminal-header">
            <div className="terminal-title">
              <span className="terminal-icon">⚡</span>
              <span>Terminal</span>
            </div>
            <button
              onClick={clearTerminal}
              className="clear-btn"
              title="Clear terminal"
              type="button"
            >
              <span>🗑️</span>
              <span>Clear</span>
            </button>
          </div>

          <div className="shell-terminal" ref={terminalRef}>
            {history.map((entry, index) => (
              <div
                key={index}
                className={`terminal-line terminal-${entry.type}`}
              >
                {entry.type === "input" && (
                  <div className="terminal-command">
                    <span className="terminal-prompt">$</span>
                    <span className="command-text">{entry.content}</span>
                  </div>
                )}

                {entry.type === "output" && (
                  <div className="terminal-output">
                    <pre>{entry.content}</pre>
                  </div>
                )}

                {entry.type === "error" && (
                  <div className="terminal-error">
                    <span className="error-icon">✖</span>
                    <pre>{entry.content}</pre>
                  </div>
                )}

                {entry.type === "system" && (
                  <div className="terminal-system">{entry.content}</div>
                )}

                {entry.type === "welcome" && (
                  <div className="terminal-welcome">{entry.content}</div>
                )}
              </div>
            ))}

            {loading && (
              <div className="terminal-line terminal-loading">
                <div className="loading-indicator">
                  <div className="spinner"></div>
                  <span>Executing command...</span>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={executeCommand} className="command-input-container">
            <div className="input-wrapper">
              <span className="prompt-label">$</span>
              <input
                ref={inputRef}
                type="text"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type a command... (↑/↓ for history)"
                className="command-input"
                disabled={loading}
                autoFocus
              />
            </div>
            <button
              type="submit"
              disabled={loading || !command.trim()}
              className="execute-btn"
            >
              {loading ? "Executing..." : "Execute"}
            </button>
          </form>
        </div>

        <div className="shell-footer">
          <span className="footer-status">
            <span className="status-dot"></span>
            Connected to Kubernetes Pod
          </span>
          <span className="footer-hint">
            💡 Pro tip: Use arrow keys to navigate history
          </span>
        </div>
      </div>
    </div>
  );
};

export default Shell;
