#!/bin/bash

# TradeFly Backend - Quick Start Script
# This script sets up and runs the TradeFly trading signal backend

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════"
echo "   TradeFly Backend - Quick Start"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo ""
    echo "Please create .env file first:"
    echo "  cp .env.example .env"
    echo "  nano .env  # Add your API keys"
    echo ""
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate venv
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Run the backend
echo "═══════════════════════════════════════════════════════════"
echo "🚀 Starting TradeFly Backend..."
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Backend will:"
echo "  • Scan 8 tickers every 60 seconds"
echo "  • Detect trading patterns (VWAP, EMA, ORB)"
echo "  • Analyze with GPT-5 Expert System"
echo "  • Save HIGH/MEDIUM signals to Supabase"
echo "  • Your iOS app will fetch them automatically"
echo ""
echo "Press Ctrl+C to stop"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""

# Run main.py
python main.py
