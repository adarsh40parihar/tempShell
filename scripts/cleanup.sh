#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}╔════════════════════════════════════════╗${NC}"
echo -e "${RED}║   TempShell Cleanup Script            ║${NC}"
echo -e "${RED}╚════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}⚠️  This will delete all TempShell resources${NC}"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${BLUE}Cleanup cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}🧹 Cleaning up TempShell deployment...${NC}"

# Delete namespace (this will delete everything in it)
echo -e "${BLUE}Deleting namespace and all resources...${NC}"
kubectl delete namespace tempshell --ignore-not-found=true

echo -e "${YELLOW}⏳ Waiting for namespace deletion...${NC}"
kubectl wait --for=delete namespace/tempshell --timeout=60s 2>/dev/null || true

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Cleanup Complete! ✨               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}All TempShell resources have been removed${NC}"
