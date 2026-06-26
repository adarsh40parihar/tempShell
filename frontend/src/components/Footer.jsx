import React from 'react';
import './Footer.css';

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-content">
        <p className="copyright">© {currentYear} TempShell. All rights reserved.</p>
        <div className="footer-links">
          <a href="#privacy">Privacy</a>
          <span className="separator">•</span>
          <a href="#terms">Terms</a>
          <span className="separator">•</span>
          <a href="#security">Security</a>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
