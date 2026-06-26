import React from "react";
import { Terminal } from "lucide-react";
import "./Footer.css";

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <Terminal size={13} className="footer-icon" />
          <span>TempShell</span>
        </div>
        <p className="footer-copy">
          © {new Date().getFullYear()} TempShell. All rights reserved.
        </p>
      </div>
    </footer>
  );
}

export default Footer;
