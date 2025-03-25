#!/usr/bin/env python3
# PeTTraC Event System
# Provides a decoupled way for components to communicate

import logging
from typing import Dict, List, Callable, Any, Optional, Set

class Event:
    """Base event class that can carry data"""
    
    def __init__(self, event_type: str, data: Optional[Dict[str, Any]] = None):
        self.event_type = event_type
        self.data = data or {}
        self.handled = False
        
    def __str__(self):
        return f"Event({self.event_type}, {self.data})"
    
    def mark_handled(self):
        """Mark event as handled to prevent further processing"""
        self.handled = True


class EventBus:
    """Central event bus for publishing and subscribing to events"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of EventBus"""
        if cls._instance is None:
            cls._instance = EventBus()
        return cls._instance
    
    def __init__(self):
        """Initialize the event bus with empty listeners"""
        self.listeners: Dict[str, List[Callable[[Event], None]]] = {}
        self.processed_events = 0
        self.debug_mode = False
        
    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """Subscribe to an event type with a callback function"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        
        if callback not in self.listeners[event_type]:
            self.listeners[event_type].append(callback)
            if self.debug_mode:
                logging.debug(f"Subscribed to {event_type}: {callback.__qualname__}")
    
    def unsubscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """Unsubscribe from an event type"""
        if event_type in self.listeners and callback in self.listeners[event_type]:
            self.listeners[event_type].remove(callback)
            if self.debug_mode:
                logging.debug(f"Unsubscribed from {event_type}: {callback.__qualname__}")
    
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers"""
        event_type = event.event_type
        
        if event_type in self.listeners:
            if self.debug_mode:
                logging.debug(f"Publishing {event}")
            
            # Create a copy of listeners to avoid issues if a callback unsubscribes during iteration
            listeners = self.listeners[event_type].copy()
            
            for callback in listeners:
                if not event.handled:  # Only call if not handled
                    try:
                        callback(event)
                        self.processed_events += 1
                    except Exception as e:
                        logging.error(f"Error in event handler {callback.__qualname__} for {event_type}: {e}")
    
    def publish_by_type(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Publish an event by type with optional data"""
        event = Event(event_type, data)
        self.publish(event)
    
    def set_debug(self, enabled: bool) -> None:
        """Enable or disable debug mode"""
        self.debug_mode = enabled
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            "listeners": {k: len(v) for k, v in self.listeners.items()},
            "processed_events": self.processed_events
        }


# Standard events used in the application
class EventTypes:
    """Standard event types used in the application"""
    
    # Button events
    BUTTON_PRESS = "button_press"
    BUTTON_RELEASE = "button_release"
    BUTTON_HOLD = "button_hold"
    
    # UI events
    UI_REFRESH = "ui_refresh"
    SCREEN_CHANGE = "screen_change"
    THEME_CHANGE = "theme_change"
    
    # System events
    BATTERY_LOW = "battery_low"
    BATTERY_CRITICAL = "battery_critical"
    SYSTEM_SHUTDOWN = "system_shutdown"
    
    # Settings events
    SETTING_CHANGE = "setting_change"
    CONFIG_SAVE = "config_save"


# Convenience function to get the event bus
def get_event_bus():
    """Get the global event bus instance"""
    return EventBus.get_instance() 