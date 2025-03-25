#!/bin/bash
# PeTTraC Installation Script
# This script installs the PeTTraC system on a Raspberry Pi

# Display colorful text
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored status messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to ask yes/no question with default
ask_yes_no() {
    local prompt=$1
    local default=$2
    local response
    
    if [ "$default" = "Y" ]; then
        prompt="$prompt [Y/n]"
    else
        prompt="$prompt [y/N]"
    fi
    
    read -p "$prompt " response
    
    if [ -z "$response" ]; then
        response=$default
    fi
    
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to check if running as root
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        print_error "This script must be run as root (with sudo)"
        exit 1
    fi
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_DIR="/opt/pettrac"

# Display welcome message
clear
echo "====================================================="
echo "        PeTTraC Installation Script v1.0.0           "
echo "====================================================="
echo
echo "This script will install the PeTTraC system on your Raspberry Pi."
echo "Make sure your Raspberry Pi is connected to the internet."
echo
echo "The installation will:"
echo "  1. Install required dependencies"
echo "  2. Enable SPI and I2C interfaces"
echo "  3. Copy PeTTraC files to $INSTALL_DIR"
echo "  4. Set up auto-start (optional)"
echo

# Confirm installation
if ! ask_yes_no "Do you want to continue with the installation?" "Y"; then
    print_status "Installation canceled."
    exit 0
fi

# Check if running as root
check_root

# Create installation directory
print_status "Creating installation directory..."
mkdir -p $INSTALL_DIR
if [ $? -ne 0 ]; then
    print_error "Failed to create installation directory."
    exit 1
fi

# Create font directory
print_status "Creating fonts directory..."
mkdir -p $INSTALL_DIR/fonts
if [ $? -ne 0 ]; then
    print_warning "Failed to create fonts directory."
fi

# Copy PeTTraC files
print_status "Copying PeTTraC files..."
cp -r $SCRIPT_DIR/* $INSTALL_DIR/
if [ $? -ne 0 ]; then
    print_error "Failed to copy PeTTraC files."
    exit 1
fi
print_success "Files copied successfully."

# Update package lists
print_status "Updating package lists..."
apt-get update
if [ $? -ne 0 ]; then
    print_error "Failed to update package lists."
    exit 1
fi

# Install Python and pip if not already installed
print_status "Installing Python and pip..."
apt-get install -y python3 python3-pip
if [ $? -ne 0 ]; then
    print_error "Failed to install Python and pip."
    exit 1
fi

# Install dependencies
print_status "Installing PeTTraC dependencies..."
python3 -m pip install -r $INSTALL_DIR/requirements.txt
if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies."
    exit 1
fi
print_success "Dependencies installed successfully."

# Install additional required packages
print_status "Installing additional system packages..."
apt-get install -y python3-smbus i2c-tools
if [ $? -ne 0 ]; then
    print_warning "Failed to install some system packages. Some features may not work."
fi

# Enable SPI and I2C interfaces
print_status "Enabling SPI and I2C interfaces..."
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" >> /boot/config.txt
    print_success "SPI interface enabled."
else
    print_status "SPI interface already enabled."
fi

if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "dtparam=i2c_arm=on" >> /boot/config.txt
    print_success "I2C interface enabled."
else
    print_status "I2C interface already enabled."
fi

# Configure pull-up resistors for buttons
if ! grep -q "gpio=6,19,5,26,13,21,20,16=pu" /boot/config.txt; then
    echo "gpio=6,19,5,26,13,21,20,16=pu" >> /boot/config.txt
    print_success "GPIO pull-up resistors configured."
else
    print_status "GPIO pull-up resistors already configured."
fi

# Make scripts executable
print_status "Making scripts executable..."
chmod +x $INSTALL_DIR/pettrac_app.py
chmod +x $INSTALL_DIR/run_pettrac.py
if [ $? -ne 0 ]; then
    print_warning "Failed to make scripts executable."
fi

# Copy fonts from example code if available
print_status "Installing fonts..."
if [ -d "$INSTALL_DIR/HardWare_Specs_Info_Wiring/1.3inch_LCD_HAT_Example_code/python/Font" ]; then
    cp $INSTALL_DIR/HardWare_Specs_Info_Wiring/1.3inch_LCD_HAT_Example_code/python/Font/*.ttf $INSTALL_DIR/fonts/
    print_success "Fonts installed."
else
    print_warning "Font directory not found. Default fonts will be used."
fi

# Create or update config.json if needed
if [ ! -f "$INSTALL_DIR/config.json" ]; then
    print_status "Creating default configuration..."
    # Run Python to create default config
    python3 -c "import sys; sys.path.append('$INSTALL_DIR'); from config import get_config; get_config()" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_success "Default configuration created."
    else
        print_warning "Failed to create default configuration."
    fi
fi

# Create desktop shortcut
print_status "Creating desktop shortcut..."
cat > /home/pi/Desktop/PeTTraC.desktop << EOL
[Desktop Entry]
Type=Application
Name=PeTTraC
Comment=PeTTraC System
Exec=sudo python3 $INSTALL_DIR/run_pettrac.py
Icon=$INSTALL_DIR/icon.png
Terminal=true
Categories=Utility;
EOL

chmod +x /home/pi/Desktop/PeTTraC.desktop
chown pi:pi /home/pi/Desktop/PeTTraC.desktop

# Create icon file (a simple placeholder if no icon is available)
if [ ! -f "$INSTALL_DIR/icon.png" ]; then
    print_status "Creating placeholder icon..."
    cat > $INSTALL_DIR/icon.png << EOL
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAPLSURBVHhe7ZpNSBRhGMffj80sDRIrqEOHoEOXOgR1CdKgQxB0KKiDdCmCPqCgS0EHCQK7dAi6CB2kDnWwo3QoCIKCiCjoEBRERBBERERs/p/ZZ3Zmdt8ZZ3fffWf3feDn7Mw7M+/M/7/vzjvvjDMqFAqFQqHIfyLdh+7Mz8+XisXiHsUbiN3oBrKDvD7XTH6BT4OEJ6Ojow+CIJADQAJfIr+A54DHcCN5nXrVZmZmJj05OVnxJhYArCwWCgU4wrgEXIM38JYJXnIGRIbIUPQGbHhcggdG+DNkz/T09CCJKwPcRAofkZYhLTnMAc/tZYXwhE+Cnyuv3QQs3eoD/l/wLPQWl28TsQNrLdTXwS+g24R3qsrKykp0bGwsaXt0RZLwcQXcCO/FNqyJ4WVUgXPxUjQaPdXqwgvMPGKM2JKVSY2urq4xypJNAkS3+uDVHvwbCT7e6QuvwPoYjQyK9XVpJWVRV4Cv1UdVWZHgHZ0ifJmtW7e+hc+JtVpZhVMCyJ5eZFUZGZbYiMZvJfj+Thd+bm5uBP4KD2+8tcpXQWUKsKUXuZtPhvDWi4WN7ORFTslOI51mzo9jHfArPIlvMPb2pQQQXOTdCb+FLITw70Rkp+4qYFoKHxMTE7fhDcL7fteVAL9WH5Sh8Pfu3bsO/wbhJWGRaqbBtdVHg1D4e/fuXYM3C29Sy51AzqsPylD4+/fvX+Fh1wqvUi0BUqsPRXgLrLxA+KvwbRE+Ti0JkFQf7S58XDMFnFYf7S68j2YS0JGtPtpNMwSkVh/tLrxPmAQsq9VHuwvvY5EAWa0+FN5B/QRIrT7aXXgfiwSofPWhXvWmQeF9XD+OWrW/vz/FtVYf3wqFwkmFNwnr9SWA1+pDt8t7Bv9E4c2ESwJEVx829eYOPCfDPcN/gu+6FaKBJxAuCRBdffhw3y+i0Og5+C8SvJXzzCcWi73pdSVA2uqDjdInk70JXMav4Qr/FV5uxfnCRl9fX+D1WPVXgtP4yaSUOPjGqSN8M3DSuElNTS8EQshxlwS0HdQVrfCsK5Sli90Gx8dHjO/3lHR3d49TdoLPF10LgXJ2gBPYdwR5wXXwLPTGJgHO9/oMOvmFfMuEuAQ/RL6I/2V48YxKVa/KGvyjDH2rjxr5r4JzZMRJcG/Fqnqrz2D+Vz64x3h8EfuC1gY5m94O7wef8dltG36DjJDyKnOH8QByjuALZdJyh+8a/Yf5CbuE5f5G4VpWKBQKhUKhyCN6ev4Bdsfa9Dv1p1sAAAAASUVORK5CYII=
EOL
    base64 -d $INSTALL_DIR/icon.png > $INSTALL_DIR/icon.png.tmp
    mv $INSTALL_DIR/icon.png.tmp $INSTALL_DIR/icon.png
fi

# Option to set up auto-start
if ask_yes_no "Do you want PeTTraC to start automatically at boot?" "Y"; then
    print_status "Setting up auto-start..."
    
    # Create systemd service
    cat > /etc/systemd/system/pettrac.service << EOL
[Unit]
Description=PeTTraC System
After=multi-user.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 $INSTALL_DIR/run_pettrac.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL

    # Enable and start service
    systemctl enable pettrac.service
    if [ $? -ne 0 ]; then
        print_error "Failed to enable auto-start service."
    else
        print_success "Auto-start service enabled."
    fi
fi

# Check if reboot is needed
REBOOT_NEEDED=0
if grep -q "^dtparam=spi=on" /boot/config.txt && ! [ -e /dev/spidev0.0 ]; then
    REBOOT_NEEDED=1
fi

if grep -q "^dtparam=i2c_arm=on" /boot/config.txt && ! [ -e /dev/i2c-1 ]; then
    REBOOT_NEEDED=1
fi

# Success message
echo
echo "====================================================="
print_success "PeTTraC has been successfully installed!"
echo
echo "Installation details:"
echo "  - PeTTraC files installed in $INSTALL_DIR"
echo "  - Fonts copied to $INSTALL_DIR/fonts"
echo "  - Configuration created in $INSTALL_DIR/config.json"
echo "  - Desktop shortcut created"
if ask_yes_no "Do you want to launch PeTTraC now?" "Y"; then
    if [ $REBOOT_NEEDED -eq 1 ]; then
        print_warning "System needs to reboot for hardware changes to take effect."
        if ask_yes_no "Do you want to reboot now?" "Y"; then
            print_status "Rebooting system..."
            reboot
        fi
    else
        print_status "Launching PeTTraC..."
        python3 $INSTALL_DIR/run_pettrac.py &
    fi
elif [ $REBOOT_NEEDED -eq 1 ]; then
    print_warning "System needs to reboot for hardware changes to take effect."
    if ask_yes_no "Do you want to reboot now?" "Y"; then
        print_status "Rebooting system..."
        reboot
    fi
fi

print_status "You can start PeTTraC by double-clicking the desktop shortcut or by running 'sudo python3 $INSTALL_DIR/run_pettrac.py'"
echo
echo "Thank you for installing PeTTraC!"
echo "=====================================================" 