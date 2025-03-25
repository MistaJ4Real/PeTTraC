#!/usr/bin/env python3
# PeTTraC State Manager
# Provides centralized application state management

import logging
import time
from typing import Dict, Any, Callable, List, Optional, Set, TypeVar, Generic
from datetime import datetime
from event_system import get_event_bus, Event, EventTypes

T = TypeVar('T')

class Observable(Generic[T]):
    """An observable property that notifies observers when its value changes"""
    
    def __init__(self, initial_value: T):
        self._value = initial_value
        self._observers: List[Callable[[T], None]] = []
    
    @property
    def value(self) -> T:
        """Get the current value"""
        return self._value
    
    @value.setter
    def value(self, new_value: T):
        """Set a new value and notify observers"""
        if new_value != self._value:
            old_value = self._value
            self._value = new_value
            self._notify_observers(old_value, new_value)
    
    def observe(self, callback: Callable[[T], None]):
        """Add an observer"""
        if callback not in self._observers:
            self._observers.append(callback)
    
    def unobserve(self, callback: Callable[[T], None]):
        """Remove an observer"""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify_observers(self, old_value: T, new_value: T):
        """Notify all observers of the change"""
        for observer in self._observers:
            try:
                observer(new_value)
            except Exception as e:
                logging.error(f"Error in observer: {e}")


class AppState:
    """Centralized application state"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = AppState()
        return cls._instance
    
    def __init__(self):
        """Initialize application state"""
        self.event_bus = get_event_bus()
        
        # Current screen
        self.current_screen = Observable("desktop")
        self.current_screen.observe(self._on_screen_change)
        
        # Battery state
        self.battery_percentage = Observable(None)
        self.battery_voltage = Observable(None)
        self.is_charging = Observable(False)
        
        # System state
        self.cpu_usage = Observable(0)
        self.memory_usage = Observable(0)
        self.disk_usage = Observable(0)
        self.temperature = Observable(0)
        
        # Settings
        self.brightness = Observable(50)
        self.brightness.observe(self._on_brightness_change)
        
        # Current time
        self.current_time = Observable(datetime.now())
        
        # Debug info
        self.start_time = time.time()
        self.debug_mode = Observable(False)
        self.debug_mode.observe(self._on_debug_mode_change)
        
        # Runtime data
        self.toast_message = Observable(None)
        self.last_update_time = time.time()
    
    def _on_screen_change(self, new_screen: str):
        """Handle screen change"""
        self.event_bus.publish_by_type(EventTypes.SCREEN_CHANGE, {"screen": new_screen})
    
    def _on_brightness_change(self, new_brightness: int):
        """Handle brightness change"""
        self.event_bus.publish_by_type(EventTypes.SETTING_CHANGE, 
                                      {"name": "brightness", "value": new_brightness})
    
    def _on_debug_mode_change(self, debug_enabled: bool):
        """Handle debug mode change"""
        self.event_bus.publish_by_type(EventTypes.SETTING_CHANGE,
                                      {"name": "debug_mode", "value": debug_enabled})
        # Also enable debug mode on the event bus
        self.event_bus.set_debug(debug_enabled)
    
    def update(self):
        """Update time-based state"""
        current_time = time.time()
        self.last_update_time = current_time
        self.current_time.value = datetime.now()
    
    def update_system_stats(self, stats: Dict[str, Any]):
        """Update system statistics"""
        if "cpu" in stats:
            self.cpu_usage.value = stats["cpu"]
        if "memory" in stats:
            self.memory_usage.value = stats["memory"]
        if "disk" in stats:
            self.disk_usage.value = stats["disk"]
        if "temperature" in stats:
            self.temperature.value = stats["temperature"]
    
    def update_battery_status(self, percentage: Optional[int], voltage: Optional[int], charging: bool):
        """Update battery status"""
        if percentage is not None:
            self.battery_percentage.value = percentage
        if voltage is not None:
            self.battery_voltage.value = voltage
        self.is_charging.value = charging
    
    def show_toast(self, message: str, duration: float = 1.0):
        """Show a toast message"""
        self.toast_message.value = (message, duration, time.time())
    
    def is_toast_visible(self) -> bool:
        """Check if a toast is currently visible"""
        if self.toast_message.value is None:
            return False
        
        message, duration, start_time = self.toast_message.value
        return (time.time() - start_time) < duration
    
    def get_uptime(self) -> int:
        """Get application uptime in seconds"""
        return int(time.time() - self.start_time)
    
    def reset_state(self):
        """Reset application state (for testing)"""
        self.current_screen.value = "desktop"
        self.toast_message.value = None


# Convenience function to get app state
def get_app_state():
    """Get the application state instance"""
    return AppState.get_instance() 