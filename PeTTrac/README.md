# PeTTraC System

## Installation Instructions

### Option 1: Double-Click Installation (Recommended)

1. Copy the entire PeTTraC folder to your Raspberry Pi (via USB drive or other method)
2. On the Raspberry Pi, navigate to the PeTTraC folder
3. Right-click on `install_pettrac.sh` and select "Run in Terminal" or double-click it
4. When prompted, enter your password (the script needs to run with sudo privileges)
5. Follow the on-screen instructions to complete the installation

### Option 2: Manual Installation

If the double-click installation doesn't work, you can install manually:

1. Copy the PeTTraC folder to your Raspberry Pi
2. Open a terminal and navigate to the PeTTraC folder:
   ```
   cd /path/to/PeTTraC
   ```
3. Run the installation script with sudo:
   ```
   sudo bash install_pettrac.sh
   ```
4. Follow the on-screen instructions

## Starting PeTTraC

After installation, you can start PeTTraC in one of these ways:

- Double-click the PeTTraC icon on the Desktop
- Run the command: `sudo python3 /opt/pettrac/run_pettrac.py`
- If you enabled auto-start during installation, PeTTraC will start automatically when the Raspberry Pi boots

## Requirements

- Raspberry Pi with Raspberry Pi OS (Bullseye or newer recommended)
- 1.3-inch LCD HAT connected to the Raspberry Pi
- PiSugar3 battery module (optional)
- Internet connection for dependency installation

## Hardware Connections

Ensure your LCD HAT and PiSugar3 are properly connected to the Raspberry Pi according to their respective documentation. The installation script will configure the necessary interfaces (SPI and I2C).

## Troubleshooting

- If the LCD doesn't display anything, ensure SPI is enabled and reboot your Raspberry Pi
- If the battery status doesn't show, ensure I2C is enabled and the PiSugar3 is properly connected
- For other issues, check the logs by running: `journalctl -u pettrac.service` (if auto-start is enabled) 