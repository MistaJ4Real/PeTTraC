#!/usr/bin/env python3
# PeTTraC Hardware Interface

import os
import sys
import time
import spidev
import logging
import numpy as np
from gpiozero import DigitalInputDevice, DigitalOutputDevice, PWMOutputDevice
import psutil

# Import configuration
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
config = get_config()

# Set log level from configuration
log_level = config.get("system", "log_level")
if log_level:
    numeric_level = getattr(logging, log_level.upper(), None)
    if isinstance(numeric_level, int):
        logging.getLogger().setLevel(numeric_level)

# GPIO Pin Definitions
KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

# LCD Constants
LCD_RST_PIN    = 27
LCD_DC_PIN     = 25
LCD_BL_PIN     = 24

# PiSugar I2C address
PISUGAR_I2C_ADDR = 0x57

class RaspberryPi:
    def __init__(self, spi=spidev.SpiDev(0,0), spi_freq=40000000, 
                 rst=LCD_RST_PIN, dc=LCD_DC_PIN, bl=LCD_BL_PIN, 
                 bl_freq=1000, i2c=None, i2c_freq=100000):
        self.np = np
        self.INPUT = False
        self.OUTPUT = True
        self.SPEED = spi_freq
        self.BL_freq = bl_freq

        # Initialize GPIO
        self.GPIO_RST_PIN = self.gpio_mode(rst, self.OUTPUT)
        self.GPIO_DC_PIN = self.gpio_mode(dc, self.OUTPUT)
        self.GPIO_BL_PIN = self.gpio_pwm(bl)
        self.bl_DutyCycle(config.get("display", "brightness"))  # Set brightness from config
        
        # Button setup
        self.GPIO_KEY_UP_PIN = self.gpio_mode(KEY_UP_PIN, self.INPUT, True, None)
        self.GPIO_KEY_DOWN_PIN = self.gpio_mode(KEY_DOWN_PIN, self.INPUT, True, None)
        self.GPIO_KEY_LEFT_PIN = self.gpio_mode(KEY_LEFT_PIN, self.INPUT, True, None)
        self.GPIO_KEY_RIGHT_PIN = self.gpio_mode(KEY_RIGHT_PIN, self.INPUT, True, None)
        self.GPIO_KEY_PRESS_PIN = self.gpio_mode(KEY_PRESS_PIN, self.INPUT, True, None)
        self.GPIO_KEY1_PIN = self.gpio_mode(KEY1_PIN, self.INPUT, True, None)
        self.GPIO_KEY2_PIN = self.gpio_mode(KEY2_PIN, self.INPUT, True, None)
        self.GPIO_KEY3_PIN = self.gpio_mode(KEY3_PIN, self.INPUT, True, None)

        # Initialize SPI
        self.SPI = spi
        if self.SPI is not None:
            self.SPI.max_speed_hz = spi_freq
            self.SPI.mode = 0b00
            
        # Button state tracking
        self.button_states = {
            'up': False,
            'down': False,
            'left': False,
            'right': False,
            'press': False,
            'key1': False,
            'key2': False,
            'key3': False
        }
        
        # Button callback functions
        self.button_callbacks = {
            'up': None,
            'down': None,
            'left': None,
            'right': None,
            'press': None,
            'key1': None,
            'key2': None,
            'key3': None
        }
        
        # Time-based debounce for buttons
        self.last_button_press_time = {button: 0 for button in self.button_states.keys()}
        self.button_debounce_ms = 100  # Minimum ms between button presses

    def gpio_mode(self, pin, mode, pull_up=None, active_state=True):
        if mode:
            return DigitalOutputDevice(pin, active_high=True, initial_value=False)
        else:
            return DigitalInputDevice(pin, pull_up=pull_up, active_state=active_state)

    def digital_write(self, pin, value):
        if value:
            pin.on()
        else:
            pin.off()

    def digital_read(self, pin):
        return pin.value

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def gpio_pwm(self, pin):
        return PWMOutputDevice(pin, frequency=self.BL_freq)

    def spi_writebyte(self, data):
        if self.SPI is not None:
            self.SPI.writebytes(data)

    def bl_DutyCycle(self, duty):
        # Ensure duty cycle is within valid range
        duty = max(0, min(100, duty))
        self.GPIO_BL_PIN.value = duty / 100
        
    def bl_Frequency(self, freq):  # Hz
        self.GPIO_BL_PIN.frequency = freq
           
    def module_init(self):
        if self.SPI is not None:
            self.SPI.max_speed_hz = self.SPEED        
            self.SPI.mode = 0b00     
        return 0

    def module_exit(self):
        logging.debug("SPI and GPIO cleanup...")
        if self.SPI is not None:
            self.SPI.close()
        
        self.digital_write(self.GPIO_RST_PIN, 1)
        self.digital_write(self.GPIO_DC_PIN, 0)   
        self.GPIO_BL_PIN.close()
        time.sleep(0.001)
        
    def update_button_states(self):
        """Update all button states and trigger callbacks if registered"""
        current_time = int(time.time() * 1000)  # Current time in ms
        
        new_states = {
            'up': not self.digital_read(self.GPIO_KEY_UP_PIN),
            'down': not self.digital_read(self.GPIO_KEY_DOWN_PIN),
            'left': not self.digital_read(self.GPIO_KEY_LEFT_PIN),
            'right': not self.digital_read(self.GPIO_KEY_RIGHT_PIN),
            'press': not self.digital_read(self.GPIO_KEY_PRESS_PIN),
            'key1': not self.digital_read(self.GPIO_KEY1_PIN),
            'key2': not self.digital_read(self.GPIO_KEY2_PIN),
            'key3': not self.digital_read(self.GPIO_KEY3_PIN)
        }
        
        # Check for button state changes and execute callbacks with debounce
        for key, state in new_states.items():
            if state and not self.button_states[key]:  # Button was just pressed
                # Check if enough time has passed since last press (debounce)
                if current_time - self.last_button_press_time[key] > self.button_debounce_ms:
                    self.last_button_press_time[key] = current_time
                    
                    # Execute callback if registered
                    if self.button_callbacks[key]:
                        self.button_callbacks[key]()
            
        # Update states
        self.button_states = new_states
        
        return self.button_states
        
    def register_button_callback(self, button, callback_func):
        """Register a callback function for a button press"""
        if button in self.button_callbacks:
            self.button_callbacks[button] = callback_func
            return True
        return False


class ST7789(RaspberryPi):
    """ST7789 LCD Display Driver"""
    
    width = 240
    height = 240
    
    def __init__(self, spi=spidev.SpiDev(0,0), spi_freq=40000000, 
                 rst=LCD_RST_PIN, dc=LCD_DC_PIN, bl=LCD_BL_PIN, 
                 bl_freq=1000, rotation=None):
        """Initialize the display with optional rotation"""
        super().__init__(spi, spi_freq, rst, dc, bl, bl_freq)
        
        # Set rotation from config if not specified
        if rotation is None:
            self.rotation = config.get("display", "rotation")
        else:
            self.rotation = rotation
            
        # Default to 0 if config returns None
        if self.rotation is None:
            self.rotation = 0
    
    def command(self, cmd):
        """Send command to display"""
        self.digital_write(self.GPIO_DC_PIN, False)
        self.spi_writebyte([cmd])
        
    def data(self, val):
        """Send data to display"""
        self.digital_write(self.GPIO_DC_PIN, True)
        self.spi_writebyte([val])

    def reset(self):
        """Reset the display"""
        self.digital_write(self.GPIO_RST_PIN, True)
        time.sleep(0.01)
        self.digital_write(self.GPIO_RST_PIN, False)
        time.sleep(0.01)
        self.digital_write(self.GPIO_RST_PIN, True)
        time.sleep(0.01)
        
    def Init(self):
        """Initialize display"""  
        self.module_init()
        self.reset()

        # Default commands for display init
        self.command(0x36)  # Memory Access Control
        
        # Set rotation using MADCTL register
        # MADCTL bits:
        # - MY (Row Address Order): 0x80
        # - MX (Column Address Order): 0x40
        # - MV (Row/Column Exchange): 0x20
        # - RGB/BGR Order: 0x08 (0=RGB, 1=BGR)
        rotation_values = {
            0: 0x70,    # 0 degrees (default)
            90: 0x10,   # 90 degrees
            180: 0xC0,  # 180 degrees
            270: 0xA0   # 270 degrees
        }
        # Use the value for the specified rotation or default to 0
        madctl = rotation_values.get(self.rotation, 0x70)
        self.data(madctl)

        self.command(0x3A)  # Interface Pixel Format
        self.data(0x05)     # 16 bits per pixel

        self.command(0xB2)
        self.data(0x0C)
        self.data(0x0C)
        self.data(0x00)
        self.data(0x33)
        self.data(0x33)

        self.command(0xB7)
        self.data(0x35) 

        self.command(0xBB)
        self.data(0x19)

        self.command(0xC0)
        self.data(0x2C)

        self.command(0xC2)
        self.data(0x01)

        self.command(0xC3)
        self.data(0x12)   

        self.command(0xC4)
        self.data(0x20)

        self.command(0xC6)
        self.data(0x0F) 

        self.command(0xD0)
        self.data(0xA4)
        self.data(0xA1)

        self.command(0xE0)
        self.data(0xD0)
        self.data(0x04)
        self.data(0x0D)
        self.data(0x11)
        self.data(0x13)
        self.data(0x2B)
        self.data(0x3F)
        self.data(0x54)
        self.data(0x4C)
        self.data(0x18)
        self.data(0x0D)
        self.data(0x0B)
        self.data(0x1F)
        self.data(0x23)

        self.command(0xE1)
        self.data(0xD0)
        self.data(0x04)
        self.data(0x0C)
        self.data(0x11)
        self.data(0x13)
        self.data(0x2C)
        self.data(0x3F)
        self.data(0x44)
        self.data(0x51)
        self.data(0x2F)
        self.data(0x1F)
        self.data(0x1F)
        self.data(0x20)
        self.data(0x23)
        
        self.command(0x21)  # Display inversion on
        self.command(0x11)  # Sleep out
        self.command(0x29)  # Display on
        
        logging.info(f"Display initialized with rotation: {self.rotation} degrees")
  
    def SetWindows(self, Xstart, Ystart, Xend, Yend):
        """Set the display window area"""
        # Set the X coordinates
        self.command(0x2A)
        self.data(0x00)               # Set the horizontal starting point to the high octet
        self.data(Xstart & 0xff)      # Set the horizontal starting point to the low octet
        self.data(0x00)               # Set the horizontal end to the high octet
        self.data((Xend - 1) & 0xff)  # Set the horizontal end to the low octet 
        
        # Set the Y coordinates
        self.command(0x2B)
        self.data(0x00)
        self.data((Ystart & 0xff))
        self.data(0x00)
        self.data((Yend - 1) & 0xff)

        # Write to RAM
        self.command(0x2C) 
        
    def ShowImage(self, image):
        """Display an image on the LCD"""
        # Check image dimensions
        imwidth, imheight = image.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError('Image must be same dimensions as display ({0}x{1}).'
                             .format(self.width, self.height))
        
        # Apply rotation if needed
        if self.rotation and self.rotation % 360 != 0:
            # PIL rotates counterclockwise, so we use negative value
            # Also, PIL's rotate parameter is the opposite of our rotation
            rot_degrees = {
                90: 270, 
                180: 180, 
                270: 90
            }.get(self.rotation)
            
            if rot_degrees:
                image = image.rotate(rot_degrees, expand=True)
        
        # Convert image data to display format
        img = self.np.asarray(image)
        pix = self.np.zeros((self.width, self.height, 2), dtype=self.np.uint8)
        pix[...,[0]] = self.np.add(self.np.bitwise_and(img[...,[0]], 0xF8), 
                                   self.np.right_shift(img[...,[1]], 5))
        pix[...,[1]] = self.np.add(self.np.bitwise_and(self.np.left_shift(img[...,[1]], 3), 0xE0), 
                                   self.np.right_shift(img[...,[2]], 3))
        pix = pix.flatten().tolist()
        
        # Send data to display
        self.SetWindows(0, 0, self.width, self.height)
        self.digital_write(self.GPIO_DC_PIN, True)
        for i in range(0, len(pix), 4096):
            self.spi_writebyte(pix[i:i+4096])
    
    def set_rotation(self, rotation):
        """Set display rotation (0, 90, 180, or 270 degrees)"""
        # Store current rotation
        if rotation in (0, 90, 180, 270):
            self.rotation = rotation
            # Update configuration
            config.set("display", "rotation", rotation)
            # Reinitialize display with new rotation
            self.Init()
            return True
        return False
        
    def clear(self):
        """Clear the display"""
        _buffer = [0xff] * (self.width * self.height * 2)
        self.SetWindows(0, 0, self.width, self.height)
        self.digital_write(self.GPIO_DC_PIN, True)
        for i in range(0, len(_buffer), 4096):
            self.spi_writebyte(_buffer[i:i+4096])
        
    def set_brightness(self, brightness):
        """Set backlight brightness (0-100)"""
        brightness = max(0, min(100, brightness))
        self.bl_DutyCycle(brightness)
        # Update configuration
        config.set("display", "brightness", brightness)
        return brightness


class BatteryManager:
    """Manages PiSugar3 battery via I2C"""
    
    def __init__(self, i2c_address=PISUGAR_I2C_ADDR):
        # Use SMBus for I2C communication
        try:
            import smbus2
            self.bus = smbus2.SMBus(1)  # Use I2C bus 1
            self.i2c_address = i2c_address
            self.initialized = True
            
            # Get battery settings from config
            self.low_warning = config.get("battery", "low_warning")
            self.critical_warning = config.get("battery", "critical_warning")
            self.auto_shutdown = config.get("battery", "auto_shutdown")
            
            # Set default values if not in config
            if self.low_warning is None:
                self.low_warning = 20
            if self.critical_warning is None:
                self.critical_warning = 10
            if self.auto_shutdown is None:
                self.auto_shutdown = 5
                
            logging.info(f"Battery manager initialized with I2C address: 0x{i2c_address:02x}")
        except Exception as e:
            logging.error(f"Failed to initialize battery manager: {e}")
            self.initialized = False
            self.low_warning = 20
            self.critical_warning = 10
            self.auto_shutdown = 5
    
    def get_battery_voltage(self):
        """Get battery voltage in millivolts"""
        if not self.initialized:
            return None
        
        try:
            # Read high and low bytes (0x22 and 0x23)
            high_byte = self.bus.read_byte_data(self.i2c_address, 0x22)
            low_byte = self.bus.read_byte_data(self.i2c_address, 0x23)
            
            # Combine bytes to get voltage in mV
            voltage_mv = (high_byte << 8) | low_byte
            return voltage_mv
        except Exception as e:
            logging.error(f"Error reading battery voltage: {e}")
            return None
    
    def get_battery_percentage(self):
        """Get battery percentage (0-100%)"""
        if not self.initialized:
            return None
        
        try:
            # Read percentage from register 0x2A
            percentage = self.bus.read_byte_data(self.i2c_address, 0x2A)
            
            # Check for low battery
            if percentage <= self.auto_shutdown:
                logging.critical(f"Battery critically low ({percentage}%)! System will shutdown.")
                self._trigger_auto_shutdown()
            elif percentage <= self.critical_warning:
                logging.critical(f"Battery critically low ({percentage}%)!")
            elif percentage <= self.low_warning:
                logging.warning(f"Battery low ({percentage}%)!")
                
            return percentage
        except Exception as e:
            logging.error(f"Error reading battery percentage: {e}")
            return None
    
    def is_charging(self):
        """Check if battery is charging"""
        if not self.initialized:
            return None
        
        try:
            # Read status register at 0x02
            status = self.bus.read_byte_data(self.i2c_address, 0x02)
            
            # Bit 7 indicates if external power is connected
            return bool(status & (1 << 7))
        except Exception as e:
            logging.error(f"Error checking charging status: {e}")
            return None
    
    def _trigger_auto_shutdown(self):
        """Trigger system shutdown due to low battery"""
        if config.get("battery", "auto_shutdown") > 0:
            logging.critical("Initiating automatic shutdown due to critically low battery!")
            try:
                # Attempt to shutdown gracefully
                import subprocess
                subprocess.run(["sudo", "shutdown", "-h", "now"])
            except Exception as e:
                logging.error(f"Failed to initiate shutdown: {e}")
            
    def get_system_stats(self):
        """Get system statistics (CPU, memory)"""
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            temperature = self._get_cpu_temperature()
            disk_usage = psutil.disk_usage('/').percent
            
            return {
                'cpu': cpu,
                'memory': memory,
                'temperature': temperature,
                'disk': disk_usage
            }
        except Exception as e:
            logging.error(f"Error getting system stats: {e}")
            return {'cpu': 0, 'memory': 0, 'temperature': 0, 'disk': 0}
    
    def _get_cpu_temperature(self):
        """Get CPU temperature"""
        try:
            # This works on Raspberry Pi
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read()) / 1000.0
            return temp
        except:
            # Return 0 if unable to read temperature
            return 0


# Helper function to initialize hardware components
def initialize_hardware():
    """Initialize all hardware components"""
    try:
        # Initialize display with rotation from config
        rotation = config.get("display", "rotation")
        display = ST7789(rotation=rotation)
        display.Init()
        display.clear()
        
        # Set brightness from config
        brightness = config.get("display", "brightness")
        if brightness is not None:
            display.bl_DutyCycle(brightness)
        else:
            display.bl_DutyCycle(50)  # Default to 50% if not specified
        
        # Initialize battery manager
        battery = BatteryManager()
        
        logging.info("Hardware initialization complete")
        return {
            'display': display,
            'battery': battery
        }
    except Exception as e:
        logging.error(f"Hardware initialization failed: {e}")
        raise 