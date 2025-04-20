#!/bin/bash

echo "HomeFinder - Real Estate Property Scraper"
echo "========================================"
echo

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Please install Python 3."
    exit 1
fi

echo "Checking for virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

echo "Installing requirements..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install requirements."
    exit 1
fi

echo
echo "Choose the application mode:"
echo "1. Command-line interface"
echo "2. Web interface"
echo

read -p "Enter your choice (1 or 2): " mode

if [ "$mode" = "1" ]; then
    echo
    echo "Starting command-line interface..."
    echo
    python app.py "$@"
elif [ "$mode" = "2" ]; then
    echo
    echo "Starting web interface..."
    echo
    echo "Web app will be available at http://localhost:5000"
    echo "Press Ctrl+C to exit"
    echo
    python web_app.py
else
    echo
    echo "Invalid choice. Please enter 1 or 2."
    exit 1
fi

deactivate
