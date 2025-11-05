import React from 'react';
import './Footer.css';

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <div className="footer-brand">
            <span className="footer-logo">🐚</span>
            <span className="footer-brand-name">TempShell</span>
          </div>
          <p className="footer-tagline">
            Secure, isolated shell environments in the cloud
          </p>
          <div className="footer-social">
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="social-link">
              <span>⚡</span>
            </a>
            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="social-link">
              <span>🚀</span>
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="social-link">
              <span>💼</span>
            </a>
          </div>
        </div>

        <div className="footer-section">
          <h3 className="footer-title">Product</h3>
          <ul className="footer-links">
            <li><a href="#features">Features</a></li>
            <li><a href="#pricing">Pricing</a></li>
            <li><a href="#docs">Documentation</a></li>
            <li><a href="#changelog">Changelog</a></li>
          </ul>
        </div>

        <div className="footer-section">
          <h3 className="footer-title">Resources</h3>
          <ul className="footer-links">
            <li><a href="#tutorials">Tutorials</a></li>
            <li><a href="#api">API Reference</a></li>
            <li><a href="#support">Support</a></li>
            <li><a href="#status">System Status</a></li>
          </ul>
        </div>

        <div className="footer-section">
          <h3 className="footer-title">Company</h3>
          <ul className="footer-links">
            <li><a href="#about">About Us</a></li>
            <li><a href="#blog">Blog</a></li>
            <li><a href="#careers">Careers</a></li>
            <li><a href="#contact">Contact</a></li>
          </ul>
        </div>

        <div className="footer-section">
          <h3 className="footer-title">Legal</h3>
          <ul className="footer-links">
            <li><a href="#privacy">Privacy Policy</a></li>
            <li><a href="#terms">Terms of Service</a></li>
            <li><a href="#security">Security</a></li>
            <li><a href="#compliance">Compliance</a></li>
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <div className="footer-bottom-content">
          <p className="copyright">
            © {currentYear} TempShell. All rights reserved.
          </p>
          <div className="footer-badges">
            <span className="badge">
              <span className="badge-icon">🔒</span>
              NIST Compliant
            </span>
            <span className="badge">
              <span className="badge-icon">☸️</span>
              Kubernetes Powered
            </span>
            <span className="badge">
              <span className="badge-icon">⚡</span>
              99.9% Uptime
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
