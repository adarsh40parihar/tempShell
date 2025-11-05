# TempShell - Secure Temporary Shell Environment

A modern, secure web-based temporary shell service built with FastAPI, React, and Kubernetes. Each user gets their own isolated Kubernetes pod with strict resource limits and NIST-compliant security.

## 🌟 Features

- **🔒 Enterprise Security**: NIST-compliant authentication with JWT tokens, bcrypt password hashing, and input validation
- **🏝️ Complete Isolation**: Each user gets an isolated Kubernetes pod with strict resource limits
- **⚡ Modern Stack**: FastAPI backend + React frontend for blazing-fast performance
- **🎯 DevOps Ready**: Kubernetes manifests with ConfigMaps, Secrets, RBAC, and resource limits
- **📊 Production Ready**: Health checks, logging, monitoring, and automated deployment scripts

## 🚀 Quick Start

### 1. Deploy to Minikube

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Deploy everything
./scripts/deploy.sh
```

### 2. Access the Application

```bash
# Open frontend in browser
minikube service tempshell-frontend-service -n tempshell
```

See full documentation below for configuration, development, and troubleshooting.
