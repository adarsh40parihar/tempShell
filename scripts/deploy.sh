#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   TempShell Deployment Script         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if minikube is running
echo -e "${YELLOW}🔍 Checking Minikube status...${NC}"
if ! minikube status > /dev/null 2>&1; then
    echo -e "${YELLOW}📦 Minikube is not running. Starting Minikube...${NC}"
    minikube start --cpus=4 --memory=8192
    echo -e "${GREEN}✅ Minikube started successfully${NC}"
else
    echo -e "${GREEN}✅ Minikube is already running${NC}"
fi

# Configure to use Minikube's Docker daemon
echo -e "${YELLOW}🔧 Configuring Docker to use Minikube's daemon...${NC}"
eval $(minikube docker-env)
echo -e "${GREEN}✅ Docker configured${NC}"

# Build Backend Image
echo ""
echo -e "${BLUE}📦 Building Backend Docker Image...${NC}"
cd backend
docker build -t tempshell-backend:latest .
echo -e "${GREEN}✅ Backend image built successfully${NC}"
cd ..

# Build Frontend Image
echo ""
echo -e "${BLUE}📦 Building Frontend Docker Image...${NC}"
cd frontend
docker build -t tempshell-frontend:latest .
echo -e "${GREEN}✅ Frontend image built successfully${NC}"
cd ..

# Create namespace
echo ""
echo -e "${BLUE}🔧 Creating Kubernetes namespace...${NC}"
kubectl apply -f k8s/namespace.yaml
echo -e "${GREEN}✅ Namespace created${NC}"

# Apply RBAC
echo ""
echo -e "${BLUE}🔐 Applying RBAC configuration...${NC}"
kubectl apply -f k8s/rbac.yaml
echo -e "${GREEN}✅ RBAC configured${NC}"

# Check if secrets need to be generated
echo ""
echo -e "${YELLOW}🔑 Checking secrets configuration...${NC}"
if grep -q "CHANGE_ME" k8s/secret.yaml; then
    echo -e "${RED}⚠️  WARNING: Secrets contain default values!${NC}"
    echo -e "${YELLOW}Generating secure secrets...${NC}"
    
    # Generate SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32)
    DB_PASSWORD=$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9' | head -c 32)
    
    # Create temporary secret file
    cat > k8s/secret-generated.yaml <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: tempshell-secret
  namespace: tempshell
type: Opaque
stringData:
  SECRET_KEY: "${SECRET_KEY}"
  DB_HOST: "mysql-service"
  DB_USER: "tempshell_user"
  DB_PASSWORD: "${DB_PASSWORD}"
  DB_NAME: "tempshell"
EOF
    
    kubectl apply -f k8s/secret-generated.yaml
    echo -e "${GREEN}✅ Generated and applied secure secrets${NC}"
    rm k8s/secret-generated.yaml
else
    kubectl apply -f k8s/secret.yaml
    echo -e "${GREEN}✅ Secrets applied${NC}"
fi

# Create ConfigMap
echo ""
echo -e "${BLUE}⚙️  Creating ConfigMap...${NC}"
kubectl apply -f k8s/configmap.yaml
echo -e "${GREEN}✅ ConfigMap created${NC}"

# Deploy MySQL
echo ""
echo -e "${BLUE}🗄️  Deploying MySQL...${NC}"
kubectl apply -f k8s/mysql-deployment.yaml
echo -e "${YELLOW}⏳ Waiting for MySQL to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=mysql -n tempshell --timeout=300s
echo -e "${GREEN}✅ MySQL is ready${NC}"

# Deploy Backend
echo ""
echo -e "${BLUE}🖥️  Deploying Backend...${NC}"
kubectl apply -f k8s/backend-deployment.yaml
echo -e "${YELLOW}⏳ Waiting for Backend to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=tempshell-backend -n tempshell --timeout=300s
echo -e "${GREEN}✅ Backend is ready${NC}"

# Deploy Frontend
echo ""
echo -e "${BLUE}🌐 Deploying Frontend...${NC}"
kubectl apply -f k8s/frontend-deployment.yaml
echo -e "${YELLOW}⏳ Waiting for Frontend to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=tempshell-frontend -n tempshell --timeout=300s
echo -e "${GREEN}✅ Frontend is ready${NC}"

# Get service URLs
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Deployment Completed! 🎉          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📊 Deployment Summary:${NC}"
kubectl get pods -n tempshell
echo ""
echo -e "${BLUE}🌐 Access URLs:${NC}"
echo -e "${GREEN}Frontend:${NC} $(minikube service tempshell-frontend-service -n tempshell --url)"
echo -e "${GREEN}Backend:${NC}  $(minikube service tempshell-backend-service -n tempshell --url)"
echo ""
echo -e "${YELLOW}💡 Useful Commands:${NC}"
echo -e "  ${BLUE}View all resources:${NC}     kubectl get all -n tempshell"
echo -e "  ${BLUE}Backend logs:${NC}           kubectl logs -f deployment/tempshell-backend -n tempshell"
echo -e "  ${BLUE}Frontend logs:${NC}          kubectl logs -f deployment/tempshell-frontend -n tempshell"
echo -e "  ${BLUE}MySQL logs:${NC}             kubectl logs -f deployment/mysql -n tempshell"
echo -e "  ${BLUE}Open Frontend in browser:${NC} minikube service tempshell-frontend-service -n tempshell"
echo ""
echo -e "${GREEN}✨ TempShell is now running! ✨${NC}"
