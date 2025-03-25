#!/usr/bin/env python3
# PeTTraC Runner Script

import os
import sys
import logging
import subprocess
import json

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import spidev
        import RPi.GPIO
        import numpy
        import gpiozero
        from PIL import Image, ImageDraw, ImageFont
        import psutil
        import smbus2
        
        logging.info("All dependencies are installed")
        return True
    except ImportError as e:
        logging.error(f"Missing dependency: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    logging.info("Installing dependencies...")
    
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Install requirements
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", 
             os.path.join(script_dir, "requirements.txt")],
            check=True
        )
        
        logging.info("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install dependencies: {e}")
        return False

def setup_permissions():
    """Set up required permissions for GPIO and SPI"""
    try:
        # Enable SPI if not already enabled
        if not os.path.exists("/dev/spidev0.0"):
            logging.warning("SPI appears to be disabled. Attempting to enable...")
            
            # Check if running as root
            if os.geteuid() != 0:
                logging.error("This script must be run as root to enable SPI.")
                return False
            
            # Try to enable SPI by modifying config.txt
            with open("/boot/config.txt", "r") as f:
                config = f.read()
            
            if "dtparam=spi=on" not in config:
                with open("/boot/config.txt", "a") as f:
                    f.write("\n# Enable SPI for PeTTraC\ndtparam=spi=on\n")
                
                logging.info("SPI enabled in config.txt. System reboot required.")
                return False
        
        # Enable I2C if not already enabled
        if not os.path.exists("/dev/i2c-1"):
            logging.warning("I2C appears to be disabled. Attempting to enable...")
            
            # Check if running as root
            if os.geteuid() != 0:
                logging.error("This script must be run as root to enable I2C.")
                return False
            
            # Try to enable I2C by modifying config.txt
            with open("/boot/config.txt", "r") as f:
                config = f.read()
            
            if "dtparam=i2c_arm=on" not in config:
                with open("/boot/config.txt", "a") as f:
                    f.write("\n# Enable I2C for PeTTraC\ndtparam=i2c_arm=on\n")
                
                logging.info("I2C enabled in config.txt. System reboot required.")
                return False
                
        # Configure button pull-up resistors
        with open("/boot/config.txt", "r") as f:
            config = f.read()
            
        if "gpio=6,19,5,26,13,21,20,16=pu" not in config:
            with open("/boot/config.txt", "a") as f:
                f.write("\n# Configure GPIO pull-up resistors for PeTTraC buttons\ngpio=6,19,5,26,13,21,20,16=pu\n")
            
            logging.info("GPIO pull-up resistors configured in config.txt. System reboot required.")
            return False
        
        logging.info("Permission setup complete")
        return True
    except Exception as e:
        logging.error(f"Permission setup failed: {e}")
        return False

def setup_config():
    """Initialize the configuration system and create font directory"""
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create fonts directory if it doesn't exist
        fonts_dir = os.path.join(script_dir, "fonts")
        if not os.path.exists(fonts_dir):
            os.makedirs(fonts_dir)
            logging.info(f"Created fonts directory at {fonts_dir}")
        
        # Create default config if it doesn't exist
        config_file = os.path.join(script_dir, "config.json")
        if not os.path.exists(config_file):
            # Import config module to get default values
            sys.path.append(script_dir)
            from config import DEFAULT_CONFIG
            
            # Save default config
            with open(config_file, "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            
            logging.info(f"Created default configuration at {config_file}")
        
        return True
    except Exception as e:
        logging.error(f"Configuration setup failed: {e}")
        return False

def run_app():
    """Run the PeTTraC application"""
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Run the application
        logging.info("Starting PeTTraC application...")
        subprocess.run(
            [sys.executable, os.path.join(script_dir, "app.py")],
            check=True
        )
        
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Application execution failed: {e}")
        return False

def main():
    """Main function"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logging.info("PeTTraC Runner starting")
    
    # Setup configuration
    if not setup_config():
        logging.error("Failed to setup configuration. Exiting.")
        sys.exit(1)
    
    # Check and install dependencies if needed
    if not check_dependencies():
        if not install_dependencies():
            logging.error("Failed to install dependencies. Exiting.")
            sys.exit(1)
    
    # Check and setup permissions
    if not setup_permissions():
        logging.error("Failed to setup required permissions. Exiting.")
        sys.exit(1)
    
    # Copy fonts from example code to fonts directory
    try:
        # Import our fonts module
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(script_dir)
        import fonts
        
        # Install fonts
        fonts.install_fonts()
        logging.info("Fonts installed successfully")
    except Exception as e:
        logging.warning(f"Failed to install fonts: {e}")
    
    # Run the application
    if not run_app():
        logging.error("Application execution failed. Exiting.")
        sys.exit(1)
    
    logging.info("PeTTraC Runner completed successfully")

if __name__ == "__main__":
    main() 