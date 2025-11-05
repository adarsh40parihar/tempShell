#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   TempShell - View Logs                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

echo "Select component to view logs:"
echo "1) Backend"
echo "2) Frontend"
echo "3) MySQL"
echo "4) All"
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo -e "${GREEN}Showing Backend logs:${NC}"
        kubectl logs -f deployment/tempshell-backend -n tempshell
        ;;
    2)
        echo -e "${GREEN}Showing Frontend logs:${NC}"
        kubectl logs -f deployment/tempshell-frontend -n tempshell
        ;;
    3)
        echo -e "${GREEN}Showing MySQL logs:${NC}"
        kubectl logs -f deployment/mysql -n tempshell
        ;;
    4)
        echo -e "${GREEN}Showing all pods:${NC}"
        kubectl get pods -n tempshell
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
