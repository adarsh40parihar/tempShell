import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import {
  Terminal,
  Trash2,
  ChevronRight,
  Circle,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import "./Shell.css";

const Shell = () => {
  const [command, setCommand] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [commandHistory, setCommandHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [cwd, setCwd] = useState("/workspace");

  const terminalRef = useRef(null);
  const inputRef = useRef(null);
  const { API_URL, user } = useAuth();

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [history]);

  useEffect(() => {
    if (!loading && inputRef.current) inputRef.current.focus();
  }, [loading]);

  useEffect(() => {
    setHistory([
      { type: "system", content: `TempShell v2.0  —  Isolated Alpine Linux environment` },
      { type: "system", content: `Session started for ${user?.username ?? "user"}. Type a command to begin.` },
      { type: "system", content: `─────────────────────────────────────────────` },
    ]);
  }, [user]);

  const executeCommand = async (e) => {
    e.preventDefault();
    const trimmed = command.trim();
    if (!trimmed || loading) return;

    setLoading(true);
    setCommandHistory((prev) => [...prev, trimmed]);
    setHistoryIndex(-1);

    // Show the typed command immediately
    setHistory((prev) => [
      ...prev.filter((h) => h.type !== "welcome"),
      { type: "input", content: trimmed, cwd },
    ]);

    try {
      const res = await axios.post(`${API_URL}/api/shell/execute`, {
        command: trimmed,
      });

      const output = res.data?.output ?? "";
      const newCwd = res.data?.cwd ?? cwd;   // update path from backend
      setCwd(newCwd);

      setHistory((prev) => [
        ...prev,
        { type: "output", content: output, exit_code: res.data?.exit_code },
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
      if (!commandHistory.length) return;
      const idx = Math.min(historyIndex + 1, commandHistory.length - 1);
      setHistoryIndex(idx);
      setCommand(commandHistory[commandHistory.length - 1 - idx]);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (historyIndex <= 0) {
        setHistoryIndex(-1);
        setCommand("");
      } else {
        const idx = historyIndex - 1;
        setHistoryIndex(idx);
        setCommand(commandHistory[commandHistory.length - 1 - idx]);
      }
    }
  };

  return (
    <div className="shell-page" onClick={() => inputRef.current?.focus()}>
      <div className="shell-wrapper">

        {/* Terminal card */}
        <div className="terminal-card">

          {/* Title bar — mimics macOS window */}
          <div className="terminal-titlebar">
            <div className="titlebar-dots">
              <span className="dot dot-red" />
              <span className="dot dot-yellow" />
              <span className="dot dot-green" />
            </div>
            <div className="titlebar-label">
              <Terminal size={13} className="titlebar-icon" />
              <span>shell — {user?.username ?? "user"}@tempshell</span>
            </div>
            <button
              className="titlebar-clear"
              onClick={(e) => { e.stopPropagation(); setHistory([]); }}
              title="Clear terminal"
            >
              <Trash2 size={13} />
              Clear
            </button>
          </div>

          {/* Output area */}
          <div className="terminal-body" ref={terminalRef}>
            {history.map((entry, i) => (
              <div key={i} className={`term-line term-${entry.type}`}>
                {entry.type === "input" && (
                  <div className="term-input-row">
                    <span className="term-path">{entry.cwd ?? "/workspace"}</span>
                    <ChevronRight size={12} className="term-chevron" />
                    <span className="term-cmd">{entry.content}</span>
                  </div>
                )}
                {entry.type === "output" && (
                  <pre className="term-output">{entry.content}</pre>
                )}
                {entry.type === "error" && (
                  <div className="term-error-row">
                    <AlertCircle size={13} />
                    <pre>{entry.content}</pre>
                  </div>
                )}
                {entry.type === "system" && (
                  <div className="term-system">{entry.content}</div>
                )}
              </div>
            ))}

            {loading && (
              <div className="term-line term-loading">
                <Loader2 size={13} className="spin" />
                <span>running…</span>
              </div>
            )}
          </div>

          {/* Input row */}
          <form className="terminal-inputbar" onSubmit={executeCommand}>
            <span className="input-path">{cwd}</span>
            <ChevronRight size={13} className="input-chevron" />
            <input
              ref={inputRef}
              type="text"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="type a command…"
              className="terminal-input"
              disabled={loading}
              autoFocus
              spellCheck={false}
              autoCapitalize="none"
              autoComplete="off"
            />
            <button
              type="submit"
              disabled={loading || !command.trim()}
              className="input-run-btn"
            >
              {loading ? <Loader2 size={14} className="spin" /> : <ChevronRight size={14} />}
            </button>
          </form>
        </div>

        {/* Status bar */}
        <div className="shell-statusbar">
          <div className="status-left">
            <Circle size={7} fill="var(--accent)" className="status-dot" />
            <span>Connected</span>
            <span className="status-sep">·</span>
            <span className="status-muted">Alpine Linux · Docker isolated</span>
          </div>
          <div className="status-right">
            <span className="status-muted">↑↓ history</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Shell;
