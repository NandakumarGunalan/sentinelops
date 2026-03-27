#!/bin/bash

echo "🧪 Testing SentinelOps Demo Setup"
echo "=================================="
echo ""

# Test Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION"
else
    echo "❌ Python 3 not found"
    exit 1
fi

# Test Node
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node $NODE_VERSION"
else
    echo "❌ Node.js not found"
    exit 1
fi

# Test npm
echo "Checking npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm $NPM_VERSION"
else
    echo "❌ npm not found"
    exit 1
fi

echo ""
echo "✅ All prerequisites installed!"
echo ""
echo "Next steps:"
echo "1. Run: ./start-demo.sh"
echo "2. Open: http://localhost:5173"
echo "3. Select an alert and click 'Start Investigation'"
