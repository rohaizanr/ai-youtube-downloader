#!/bin/bash

# YouTube Downloader Automation - macOS Setup Script
# This script sets up the Python virtual environment and installs all dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Welcome message
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    YouTube Downloader Automation                     ║"
echo "║                         macOS Setup Script                          ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python 3 is installed
print_status "Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python 3 found: $PYTHON_VERSION"
else
    print_error "Python 3 is not installed!"
    print_status "Please install Python 3 from https://www.python.org/downloads/"
    print_status "Or install via Homebrew: brew install python"
    exit 1
fi

# Check Python version (require 3.8+)
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 8 ]]; then
    print_error "Python 3.8+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if ffmpeg is installed
print_status "Checking ffmpeg installation..."
if command_exists ffmpeg; then
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n1 | cut -d' ' -f3)
    print_success "ffmpeg found: $FFMPEG_VERSION"
else
    print_warning "ffmpeg not found. Installing via Homebrew..."
    
    # Check if Homebrew is installed
    if command_exists brew; then
        print_status "Installing ffmpeg..."
        brew install ffmpeg
        print_success "ffmpeg installed successfully"
    else
        print_error "Homebrew is not installed!"
        print_status "Please install Homebrew first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        print_status "Then run this script again, or manually install ffmpeg"
        print_warning "Continuing without ffmpeg (some features may not work)..."
    fi
fi

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

print_status "Project directory: $PROJECT_DIR"

# Create virtual environment
print_status "Creating Python virtual environment..."
cd "$PROJECT_DIR"

if [[ -d "venv" ]]; then
    print_warning "Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv
print_success "Virtual environment created"

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip
print_success "pip upgraded"

# Install requirements
print_status "Installing Python dependencies..."
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
    print_success "Dependencies installed successfully"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p downloads logs config
print_success "Directories created"

# Create a simple activation script
print_status "Creating activation script..."
cat > activate_env.sh << 'EOF'
#!/bin/bash
# Activation script for YouTube Downloader Automation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"

echo "YouTube Downloader Automation environment activated!"
echo "To run the application:"
echo "  python src/main.py                    # Interactive mode"
echo "  python src/main.py -q 'search term'  # Batch mode"
echo ""
echo "To deactivate: deactivate"
EOF

chmod +x activate_env.sh
print_success "Activation script created: activate_env.sh"

# Create run script
print_status "Creating run script..."
cat > run_downloader.sh << 'EOF'
#!/bin/bash
# Run script for YouTube Downloader Automation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Run the application
python src/main.py "$@"
EOF

chmod +x run_downloader.sh
print_success "Run script created: run_downloader.sh"

# Test the installation
print_status "Testing installation..."
python -c "
try:
    import yt_dlp
    import youtubesearchpython
    import rich
    import yaml
    print('✓ All main dependencies imported successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
    exit(1)
"

if [[ $? -eq 0 ]]; then
    print_success "Installation test passed"
else
    print_error "Installation test failed"
    exit 1
fi

# Final setup complete message
echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                        Setup Complete! 🎉                          ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
print_success "YouTube Downloader Automation is ready to use!"
echo ""
echo "Quick Start:"
echo "  1. Activate the environment: source activate_env.sh"
echo "  2. Run interactively:        python src/main.py"
echo "  3. Or use the run script:    ./run_downloader.sh"
echo ""
echo "Batch mode examples:"
echo "  ./run_downloader.sh -q 'funny cats' -n 5"
echo "  ./run_downloader.sh -q 'python tutorials' -n 3"
echo ""
print_status "Check README.md for detailed usage instructions"
echo ""

# Deactivate virtual environment
deactivate