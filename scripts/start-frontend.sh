#!/bin/bash

echo "🌐 Starting TempShell Frontend"
echo "=================================================="
echo ""

cd "$(dirname "$0")/../frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "🚀 Starting Frontend on http://localhost:3000..."
echo "   The browser will open automatically"
echo ""
npm start
