#!/bin/bash
# List Everything in Specific Namespace (tempshell)
kubectl get all -n tempshell
set -e

echo "=== TempShell Cleanup Script ==="
echo ""

echo "WARNING: This will delete all TempShell resources"
read -p "Are you sure you want to continue? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""
echo "Checking if minikube is running..."
if ! minikube status > /dev/null 2>&1; then
    echo "ERROR: Minikube is not running. Please start minikube first."
    echo "Run: minikube start"
    exit 1
fi

echo "Cleaning up TempShell deployment..."

# Delete namespace (this will delete everything in it)
echo "Deleting namespace and all resources..."
kubectl delete namespace tempshell --ignore-not-found=true

echo "Waiting for namespace deletion..."
kubectl wait --for=delete namespace/tempshell --timeout=60s 2>/dev/null || true

echo ""
echo "=== Cleanup Complete ==="
echo "All TempShell resources have been removed"

# List Everything in All Namespaces
kubectl get all --all-namespaces
