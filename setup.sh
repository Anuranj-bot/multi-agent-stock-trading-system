#!/bin/bash

echo "======================================"
echo " Trading Agents AI Setup Script"
echo "======================================"



echo "Creating virtual environment..."
python3 -m venv venv


echo "Activating virtual environment..."
source venv/bin/activate


echo "Upgrading pip..."
pip install --upgrade pip


echo "Installing Python dependencies..."
pip install -r requirements.txt


if ! command -v ollama &> /dev/null
then
    echo "Ollama is not installed."
    echo "Please install from: https://ollama.com/download"
else
    echo "Pulling LLaMA3 model..."
    ollama pull llama3
fi

echo ""
echo "======================================"
echo " Setup Complete!"
echo "======================================"
echo ""
echo "To activate environment in future:"
echo "source venv/bin/activate"