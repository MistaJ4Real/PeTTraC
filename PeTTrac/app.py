#!/usr/bin/env python3
# PeTTraC Main Application
# Orchestrates the components of the PeTTraC system

import os
import sys
import logging
import time
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw

# Import our framework components
from event_system import get_event_bus, Event, EventTypes
from state_manager import get_app_state
from hardware_abstraction import get_hardware_manager
from ui_framework import Screen, Rect
from screens import get_screen
from config import get_config
import fonts

# Configure logging
config = get_config()
log_level = config.get("system", "log_level") or "INFO"
numeric_level = getattr(logging, log_level.upper(), None)
logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240
UPDATE_INTERVAL = 0.05  # 50ms refresh rate (20fps)

class PeTTraCApplication:
    """Main application class"""
    
    def __init__(self):
        """Initialize application"""
        logging.info("Initializing PeTTraC application")
        
        # Initialize fonts
        fonts.install_fonts()
        
        # Get framework components
        self.event_bus = get_event_bus()
        self.app_state = get_app_state()
        self.hardware = get_hardware_manager()
        
        # Debug mode
        self.debug_mode = config.get("system", "debug_mode") or False
        self.event_bus.set_debug(self.debug_mode)
        self.app_state.debug_mode.value = self.debug_mode
        
        # Create render surface
        self.image = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), "BLACK")
        self.canvas = ImageDraw.Draw(self.image)
        
        # Set up screens
        self.screens: Dict[str, Screen] = {}
        self.current_screen: Optional[Screen] = None
        self.load_screen(config.get("system", "default_screen") or "desktop")
        
        # Application state
        self.running = False
        self.last_update_time = time.time()
        self.frame_count = 0
        self.fps = 0
        
        # Subscribe to events
        self.event_bus.subscribe(EventTypes.SCREEN_CHANGE, self._on_screen_change)
        
        logging.info("PeTTraC application initialized")
    
    def load_screen(self, screen_name: str):
        """Load and activate a screen by name"""
        # Deactivate current screen if any
        if self.current_screen:
            self.current_screen.deactivate()
        
        # Create screen if not already cached
        if screen_name not in self.screens:
            self.screens[screen_name] = get_screen(screen_name)
        
        # Set current screen
        self.current_screen = self.screens[screen_name]
        
        # Activate the screen
        self.current_screen.activate()
        
        logging.info(f"Loaded screen: {screen_name}")
    
    def _on_screen_change(self, event: Event):
        """Handle screen change events"""
        new_screen = event.data.get("screen")
        if new_screen and new_screen != self.app_state.current_screen.value:
            self.load_screen(new_screen)
    
    def render(self):
        """Render the current screen to the display"""
        # Clear the canvas
        self.canvas.rectangle((0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT), fill="BLACK")
        
        # Render current screen
        if self.current_screen:
            self.current_screen.draw(self.canvas)
        
        # Render toast message if any
        self._render_toast()
        
        # Send to hardware
        self.hardware.render_to_display(self.image)
        
        # Update frame stats
        self.frame_count += 1
        current_time = time.time()
        time_diff = current_time - self.last_update_time
        
        # Update FPS every second
        if time_diff >= 1.0:
            self.fps = self.frame_count / time_diff
            self.frame_count = 0
            self.last_update_time = current_time
    
    def _render_toast(self):
        """Render toast message if active"""
        if not self.app_state.is_toast_visible():
            return
            
        message, duration, start_time = self.app_state.toast_message.value
        
        # Create a toast message
        toast_height = 40
        toast_y = (DISPLAY_HEIGHT - toast_height) // 2
        
        # Draw toast background
        self.canvas.rectangle(
            (10, toast_y, DISPLAY_WIDTH - 10, toast_y + toast_height), 
            fill="BLUE", 
            outline="CYAN"
        )
        
        # Draw toast text
        font = fonts.get_font("bold", "medium")
        text_width = font.getlength(message)
        text_x = (DISPLAY_WIDTH - text_width) // 2
        self.canvas.text(
            (text_x, toast_y + 10), 
            message, 
            fill="WHITE", 
            font=font
        )
    
    def update(self):
        """Update application state"""
        # Update hardware (poll buttons, update battery, etc.)
        self.hardware.update()
        
        # Update app state
        self.app_state.update()
        
        # Update current screen
        if self.current_screen:
            self.current_screen.update()
    
    def run(self):
        """Main application loop"""
        self.running = True
        
        try:
            logging.info("Starting PeTTraC application main loop")
            
            while self.running:
                loop_start = time.time()
                
                # Update state
                self.update()
                
                # Render
                self.render()
                
                # Calculate sleep time to maintain consistent frame rate
                elapsed = time.time() - loop_start
                sleep_time = max(0, UPDATE_INTERVAL - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            logging.info("Application interrupted by user")
        except Exception as e:
            logging.error(f"Unhandled exception in main loop: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean up resources and exit"""
        logging.info("Shutting down PeTTraC application")
        self.running = False
        
        # Clean up hardware
        self.hardware.shutdown()
        
        logging.info("PeTTraC application shut down successfully")


def main():
    """Application entry point"""
    try:
        app = PeTTraCApplication()
        app.run()
        return 0
    except Exception as e:
        logging.error(f"Critical error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 