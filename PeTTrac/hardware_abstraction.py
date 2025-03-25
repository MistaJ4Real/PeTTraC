#!/usr/bin/env python3
# PeTTraC Hardware Abstraction Layer
# Provides an interface between the hardware and the application framework

import logging
import time
from typing import Dict, Any, Optional, List, Callable

# Import hardware interfaces
from hardware_interface import initialize_hardware, ST7789, BatteryManager
from event_system import get_event_bus, Event, EventTypes
from state_manager import get_app_state
from config import get_config

class HardwareManager:
    """Manages hardware components and interfaces with the application"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = HardwareManager()
        return cls._instance
    
    def __init__(self):
        """Initialize hardware manager"""
        self.event_bus = get_event_bus()
        self.app_state = get_app_state()
        self.config = get_config()
        
        self.display = None
        self.battery = None
        self.hw_initialized = False
        
        # Button mapping for event conversion
        self.button_mapping = {
            'up': 'up',
            'down': 'down',
            'left': 'left',
            'right': 'right',
            'press': 'press',
            'key1': 'key1',
            'key2': 'key2',
            'key3': 'key3',
        }
        
        # Subscribe to settings events
        self.event_bus.subscribe(EventTypes.SETTING_CHANGE, self._handle_setting_change)
        
        # Initialize hardware
        self.initialize()
    
    def initialize(self) -> bool:
        """Initialize hardware components"""
        try:
            # Initialize hardware
            hw = initialize_hardware()
            self.display = hw['display']
            self.battery = hw['battery']
            
            # Set brightness from app state
            brightness = self.app_state.brightness.value
            if brightness is not None:
                self.display.bl_DutyCycle(brightness)
            
            # Set up button handlers
            self._setup_button_handlers()
            
            self.hw_initialized = True
            logging.info("Hardware initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize hardware: {e}")
            self.hw_initialized = False
            return False
    
    def _setup_button_handlers(self):
        """Set up button handlers to convert hardware events to framework events"""
        # Dictionary to track button states to detect changes
        self.button_states = {name: False for name in self.button_mapping.keys()}
        
    def update(self):
        """Update hardware state and poll for events"""
        if not self.hw_initialized:
            return
        
        try:
            # Update button states and publish events on changes
            new_states = self.display.update_button_states()
            
            # Convert hardware button states to events
            for hw_name, app_name in self.button_mapping.items():
                new_state = new_states.get(hw_name, False)
                old_state = self.button_states.get(hw_name, False)
                
                # Button was just pressed
                if new_state and not old_state:
                    self.event_bus.publish_by_type(
                        EventTypes.BUTTON_PRESS, 
                        {"button": app_name}
                    )
                # Button was just released
                elif not new_state and old_state:
                    self.event_bus.publish_by_type(
                        EventTypes.BUTTON_RELEASE, 
                        {"button": app_name}
                    )
                
                # Update state
                self.button_states[hw_name] = new_state
            
            # Get battery status
            if self.battery:
                percentage = self.battery.get_battery_percentage()
                voltage = self.battery.get_battery_voltage()
                charging = self.battery.is_charging()
                
                # Update app state
                self.app_state.update_battery_status(percentage, voltage, charging)
                
                # Get system stats
                stats = self.battery.get_system_stats()
                self.app_state.update_system_stats(stats)
        except Exception as e:
            logging.error(f"Error updating hardware state: {e}")
    
    def render_to_display(self, image):
        """Render an image to the physical display"""
        if not self.hw_initialized or not self.display:
            return False
        
        try:
            self.display.ShowImage(image)
            return True
        except Exception as e:
            logging.error(f"Error rendering to display: {e}")
            return False
    
    def _handle_setting_change(self, event: Event):
        """Handle settings change events"""
        setting_name = event.data.get("name")
        value = event.data.get("value")
        
        if setting_name == "brightness" and value is not None:
            self._set_brightness(value)
        elif setting_name == "rotation" and value is not None:
            self._set_rotation(value)
    
    def _set_brightness(self, brightness: int):
        """Set display brightness"""
        if not self.hw_initialized or not self.display:
            return
        
        try:
            brightness = max(0, min(100, brightness))
            self.display.bl_DutyCycle(brightness)
            # Save to config
            self.config.set("display", "brightness", brightness)
            logging.info(f"Brightness set to {brightness}%")
        except Exception as e:
            logging.error(f"Error setting brightness: {e}")
    
    def _set_rotation(self, rotation: int):
        """Set display rotation"""
        if not self.hw_initialized or not self.display:
            return
        
        try:
            if rotation in (0, 90, 180, 270):
                self.display.set_rotation(rotation)
                # Save to config
                self.config.set("display", "rotation", rotation)
                logging.info(f"Rotation set to {rotation} degrees")
        except Exception as e:
            logging.error(f"Error setting rotation: {e}")
    
    def shutdown(self):
        """Clean up hardware resources"""
        if not self.hw_initialized:
            return
            
        try:
            if self.display:
                self.display.clear()
                self.display.module_exit()
            logging.info("Hardware resources cleaned up")
        except Exception as e:
            logging.error(f"Error shutting down hardware: {e}")


# Convenience function to get hardware manager
def get_hardware_manager():
    """Get the hardware manager instance"""
    return HardwareManager.get_instance() 