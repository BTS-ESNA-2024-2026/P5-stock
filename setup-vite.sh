#!/bin/bash

# Build and serve script for Flask + Vite development

echo "=== Flask + Vite Development Setup ==="
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Please run this script from the project root"
    exit 1
fi

# Kill any existing Flask or Vite processes
echo "Cleaning up existing processes..."
pkill -f "flask run" || true
pkill -f "vite" || true
sleep 1

# Build the frontend
echo "Building Vite frontend..."
cd frontend
pnpm build
cd ..

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To run the application:"
echo "1. For production (Flask serves built frontend):"
echo "   flask --app src run"
echo ""
echo "2. For development with hot reload:"
echo "   Terminal 1: cd frontend && pnpm dev"
echo "   Terminal 2: flask --app src run --debug"
echo ""
echo "The frontend dev server will run on http://localhost:5173/"
echo "The Flask backend will run on http://localhost:5000/"
