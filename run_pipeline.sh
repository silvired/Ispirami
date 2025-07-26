#!/bin/bash

# Pipeline execution script for ispirami
echo "Starting ispirami pipeline..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed or not in PATH"
    exit 1
fi

# Check if required files exist
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found"
    exit 1
fi

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing requirements from requirements.txt..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install requirements"
        exit 1
    fi
    echo "Requirements installed successfully."
else
    echo "Warning: requirements.txt not found, skipping dependency installation."
fi

# Run the main pipeline
echo "Executing main.py..."
python3 main.py

if [ $? -eq 0 ]; then
    echo "Pipeline completed successfully!"
else
    echo "Pipeline failed with exit code $?"
    exit 1
fi 