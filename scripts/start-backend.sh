#!/bin/bash

echo "🚀 Starting TempShell Local Development Environment"
echo "=================================================="
echo ""

# Check if MySQL container is running
if ! docker ps | grep -q tempshell-mysql; then
    echo "❌ MySQL container not running!"
    echo "Please run: docker run -d --name tempshell-mysql -e MYSQL_ROOT_PASSWORD=your_password -e MYSQL_DATABASE=tempshell -e MYSQL_USER=tempshell_user -e MYSQL_PASSWORD=your_password -p 3307:3306 mysql:8.0"
    exit 1
fi

echo "✅ MySQL container is running"
echo ""

# Start backend
cd "$(dirname "$0")/../backend"
echo "🖥️  Starting Backend on http://localhost:8000..."
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
