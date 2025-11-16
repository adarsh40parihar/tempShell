#!/bin/bash

set -e

echo "=== TempShell Deployment Script ==="
echo ""

# Check if minikube is running
echo "Checking Minikube status..."
if ! minikube status > /dev/null 2>&1; then
    echo "Minikube is not running. Starting Minikube..."
    minikube start --cpus=4 --memory=8192
    echo "Minikube started successfully"
else
    echo "Minikube is already running"
fi

# Configure to use Minikube's Docker daemon
echo "Configuring Docker to use Minikube's daemon..."
eval $(minikube docker-env)
echo "Docker configured"

# Build Backend Image
echo ""
echo "Building Backend Docker Image..."
cd backend
docker build -t tempshell-backend:latest .
echo "Backend image built successfully"
cd ..

# Build Frontend Image
echo ""
echo "Building Frontend Docker Image..."
cd frontend
docker build -t tempshell-frontend:latest .
echo "Frontend image built successfully"
cd ..

# Create namespace
echo ""
echo "Creating Kubernetes namespace..."
kubectl apply -f k8s/namespace.yaml
echo "Namespace created"

# Apply RBAC
echo ""
echo "Applying RBAC configuration..."
kubectl apply -f k8s/rbac.yaml
echo "RBAC configured"

# Check if secrets need to be generated
echo ""
echo "Checking secrets configuration..."
if grep -q "CHANGE_ME" k8s/secret.yaml; then
    echo "WARNING: Secrets contain default values!"
    echo "Generating secure secrets..."
    
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
    echo "Generated and applied secure secrets"
    rm k8s/secret-generated.yaml
else
    kubectl apply -f k8s/secret.yaml
    echo "Secrets applied"
fi

# Create ConfigMap
echo ""
echo "Creating ConfigMap..."
kubectl apply -f k8s/configmap.yaml
echo "ConfigMap created"

# Deploy MySQL
echo ""
echo "Deploying MySQL..."
kubectl apply -f k8s/mysql-deployment.yaml
echo "Waiting for MySQL to be ready..."
kubectl wait --for=condition=ready pod -l app=mysql -n tempshell --timeout=300s
echo "MySQL is ready"

# Deploy Backend
echo ""
echo "Deploying Backend..."
kubectl apply -f k8s/backend-deployment.yaml
echo "Waiting for Backend to be ready..."
kubectl wait --for=condition=ready pod -l app=tempshell-backend -n tempshell --timeout=300s
echo "Backend is ready"

# Deploy Frontend
echo ""
echo "Deploying Frontend..."
kubectl apply -f k8s/frontend-deployment.yaml
echo "Waiting for Frontend to be ready..."
kubectl wait --for=condition=ready pod -l app=tempshell-frontend -n tempshell --timeout=300s
echo "Frontend is ready"

# Get service URLs
echo ""
echo "=== Deployment Completed ==="
echo ""
echo "Deployment Summary:"

kubectl get pods -n tempshell

echo ""
#echo "Access URLs:"
#echo "Frontend: $(minikube service tempshell-frontend-service -n tempshell --url)"
#echo "Backend:  $(minikube service tempshell-backend-service -n tempshell --url)"
#echo ""
echo "Useful Commands:"
echo "  View all resources:     kubectl get all -n tempshell"
echo "  Backend logs:           kubectl logs -f deployment/tempshell-backend -n tempshell"
echo "  Frontend logs:          kubectl logs -f deployment/tempshell-frontend -n tempshell"
echo "  MySQL logs:             kubectl logs -f deployment/mysql -n tempshell"
echo "  Open Frontend:          minikube service tempshell-frontend-service -n tempshell"
echo ""
echo "TempShell is now running!"
echo ""
echo "Starting the server"

minikube service tempshell-frontend-service -n tempshell

