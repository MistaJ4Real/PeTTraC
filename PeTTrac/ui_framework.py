#!/usr/bin/env python3
# PeTTraC UI Framework
# Provides a component-based architecture for UI elements

import logging
from typing import List, Tuple, Dict, Any, Optional, Callable
from PIL import Image, ImageDraw, ImageFont
from config import get_config
import fonts
from event_system import get_event_bus, Event, EventTypes

# Get configuration for default values
config = get_config()

class Point:
    """Simple point class for positions"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"

class Rect:
    """Rectangle class for layouts"""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def __repr__(self):
        return f"Rect({self.x}, {self.y}, {self.width}, {self.height})"
    
    def contains(self, point: Point) -> bool:
        """Check if the rectangle contains the point"""
        return (
            point.x >= self.x and 
            point.x < self.x + self.width and
            point.y >= self.y and
            point.y < self.y + self.height
        )
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        """Convert to tuple for PIL drawing"""
        return (self.x, self.y, self.x + self.width, self.y + self.height)

class ThemeManager:
    """Manages UI themes"""
    
    # Theme definitions
    THEMES = {
        "default": {
            "background": "BLACK",
            "text": "WHITE",
            "title": "WHITE",
            "highlight": "BLUE",
            "accent1": "CYAN",
            "accent2": "GREEN",
            "warning": "YELLOW",
            "error": "RED",
            "menu_bg": "BLUE",
            "menu_item": "WHITE",
            "menu_selected_bg": "GRAY",
            "menu_selected_text": "WHITE"
        },
        "dark": {
            "background": "BLACK",
            "text": "LIGHTGRAY",
            "title": "WHITE",
            "highlight": "PURPLE",
            "accent1": "CYAN",
            "accent2": "GREEN",
            "warning": "ORANGE",
            "error": "RED",
            "menu_bg": "DARKBLUE",
            "menu_item": "LIGHTGRAY",
            "menu_selected_bg": "PURPLE",
            "menu_selected_text": "WHITE"
        },
        "light": {
            "background": "WHITE",
            "text": "BLACK",
            "title": "BLACK",
            "highlight": "BLUE",
            "accent1": "DARKBLUE",
            "accent2": "DARKGREEN",
            "warning": "ORANGE",
            "error": "RED",
            "menu_bg": "LIGHTGRAY",
            "menu_item": "BLACK",
            "menu_selected_bg": "BLUE",
            "menu_selected_text": "WHITE"
        },
        "blue": {
            "background": "NAVY",
            "text": "WHITE",
            "title": "CYAN",
            "highlight": "CYAN",
            "accent1": "LIGHTBLUE",
            "accent2": "GREEN",
            "warning": "YELLOW",
            "error": "RED",
            "menu_bg": "DARKBLUE",
            "menu_item": "WHITE",
            "menu_selected_bg": "CYAN",
            "menu_selected_text": "BLACK"
        }
    }
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance
    
    def __init__(self):
        """Initialize theme manager"""
        self.current_theme = config.get("display", "theme") or "default"
        self.event_bus = get_event_bus()
        
        # Subscribe to theme change events
        self.event_bus.subscribe(EventTypes.THEME_CHANGE, self._handle_theme_change)
    
    def _handle_theme_change(self, event: Event):
        """Handle theme change event"""
        if "theme" in event.data:
            self.set_theme(event.data["theme"])
    
    def get_color(self, element: str) -> str:
        """Get color for a UI element based on the current theme"""
        theme = self.THEMES.get(self.current_theme, self.THEMES["default"])
        return theme.get(element, "WHITE")
    
    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme"""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            config.set("display", "theme", theme_name)
            return True
        return False
    
    def get_current_theme(self) -> str:
        """Get the current theme name"""
        return self.current_theme
    
    def get_available_themes(self) -> List[str]:
        """Get list of available themes"""
        return list(self.THEMES.keys())

# Convenience function to get theme manager
def get_theme_manager():
    """Get the theme manager instance"""
    return ThemeManager.get_instance()

class UIComponent:
    """Base class for all UI components"""
    
    def __init__(self, rect: Optional[Rect] = None):
        self.rect = rect
        self.visible = True
        self.parent = None
        self.children: List[UIComponent] = []
        self.theme_manager = get_theme_manager()
        self.event_bus = get_event_bus()
    
    def draw(self, canvas: ImageDraw.ImageDraw):
        """Draw the component and its children"""
        if not self.visible:
            return
        
        # Draw self first
        self.draw_component(canvas)
        
        # Then draw children
        for child in self.children:
            child.draw(canvas)
    
    def draw_component(self, canvas: ImageDraw.ImageDraw):
        """Draw just this component (override in subclasses)"""
        pass
    
    def add_child(self, child: 'UIComponent'):
        """Add a child component"""
        self.children.append(child)
        child.parent = self
        return child
    
    def remove_child(self, child: 'UIComponent'):
        """Remove a child component"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
    
    def set_rect(self, rect: Rect):
        """Set component rectangle"""
        self.rect = rect
    
    def set_visible(self, visible: bool):
        """Set component visibility"""
        self.visible = visible
    
    def handle_event(self, event: Event) -> bool:
        """Handle an event (returns True if handled)"""
        # Let children handle the event first (in reverse order for z-order)
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        
        # Then handle the event ourselves
        return self.on_event(event)
    
    def on_event(self, event: Event) -> bool:
        """Handle event (override in subclasses)"""
        return False
    
    def get_absolute_rect(self) -> Rect:
        """Get the absolute rectangle accounting for parent offsets"""
        if not self.rect:
            return Rect(0, 0, 0, 0)
            
        if not self.parent:
            return self.rect
            
        parent_rect = self.parent.get_absolute_rect()
        return Rect(
            parent_rect.x + self.rect.x,
            parent_rect.y + self.rect.y,
            self.rect.width,
            self.rect.height
        )

class Container(UIComponent):
    """A container for other components"""
    
    def __init__(self, rect: Rect, bg_color: Optional[str] = None):
        super().__init__(rect)
        self.bg_color = bg_color
    
    def draw_component(self, canvas: ImageDraw.ImageDraw):
        """Draw container background if color is specified"""
        if self.bg_color:
            canvas.rectangle(self.rect.to_tuple(), fill=self.bg_color)

class Label(UIComponent):
    """Text label component"""
    
    def __init__(self, rect: Rect, text: str, font_type: str = "regular", 
                 font_size: str = "medium", color: Optional[str] = None, 
                 align: str = "left"):
        super().__init__(rect)
        self.text = text
        self.font_type = font_type
        self.font_size = font_size
        self.color = color
        self.align = align
        self.font = fonts.get_font(font_type, font_size)
    
    def draw_component(self, canvas: ImageDraw.ImageDraw):
        """Draw the label text"""
        if not self.color:
            self.color = self.theme_manager.get_color("text")
            
        # Calculate text position based on alignment
        text_width = self.font.getlength(self.text)
        x = self.rect.x
        
        if self.align == "center":
            x = self.rect.x + (self.rect.width - text_width) // 2
        elif self.align == "right":
            x = self.rect.x + self.rect.width - text_width
            
        canvas.text((x, self.rect.y), self.text, fill=self.color, font=self.font)
    
    def set_text(self, text: str):
        """Set the label text"""
        self.text = text

class Button(UIComponent):
    """Interactive button component"""
    
    def __init__(self, rect: Rect, text: str, action: Optional[Callable[[], None]] = None,
                font_type: str = "regular", font_size: str = "medium", 
                bg_color: Optional[str] = None, text_color: Optional[str] = None,
                highlight_color: Optional[str] = None):
        super().__init__(rect)
        self.text = text
        self.action = action
        self.font_type = font_type
        self.font_size = font_size
        self.font = fonts.get_font(font_type, font_size)
        self.bg_color = bg_color
        self.text_color = text_color
        self.highlight_color = highlight_color
        self.pressed = False
    
    def draw_component(self, canvas: ImageDraw.ImageDraw):
        """Draw the button"""
        # Get colors if not specified
        if not self.bg_color:
            self.bg_color = self.theme_manager.get_color("menu_bg")
        
        if not self.text_color:
            self.text_color = self.theme_manager.get_color("menu_item")
            
        if not self.highlight_color:
            self.highlight_color = self.theme_manager.get_color("highlight")
        
        # Draw button background
        canvas.rectangle(self.rect.to_tuple(), 
                        fill=self.bg_color,
                        outline=self.highlight_color if self.pressed else None)
        
        # Draw button text
        text_width = self.font.getlength(self.text)
        x = self.rect.x + (self.rect.width - text_width) // 2
        y = self.rect.y + (self.rect.height - self.font.size) // 2
        canvas.text((x, y), self.text, fill=self.text_color, font=self.font)
    
    def on_event(self, event: Event) -> bool:
        """Handle button events"""
        if event.event_type == EventTypes.BUTTON_PRESS:
            btn_name = event.data.get("button")
            btn_pos = event.data.get("position")
            
            # Check if this was a touch event
            if btn_pos:
                point = Point(btn_pos[0], btn_pos[1])
                if self.get_absolute_rect().contains(point):
                    self.pressed = True
                    return True
            
            # Or check if this was a specific button targeting this component
            elif btn_name and event.data.get("target") == self:
                self.pressed = True
                return True
                
        elif event.event_type == EventTypes.BUTTON_RELEASE:
            if self.pressed:
                self.pressed = False
                if self.action:
                    self.action()
                return True
                
        return False

class ProgressBar(UIComponent):
    """Progress bar component"""
    
    def __init__(self, rect: Rect, value: float, max_value: float = 100.0,
                bg_color: Optional[str] = None, fill_color: Optional[str] = None,
                border_color: Optional[str] = None):
        super().__init__(rect)
        self.value = value
        self.max_value = max_value
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.border_color = border_color
    
    def draw_component(self, canvas: ImageDraw.ImageDraw):
        """Draw the progress bar"""
        # Get colors if not specified
        if not self.bg_color:
            self.bg_color = self.theme_manager.get_color("background")
        
        if not self.fill_color:
            self.fill_color = self.theme_manager.get_color("accent1")
            
        if not self.border_color:
            self.border_color = self.theme_manager.get_color("text")
        
        # Draw background
        canvas.rectangle(self.rect.to_tuple(), fill=self.bg_color, outline=self.border_color)
        
        # Calculate fill width based on value
        fill_width = int((self.value / self.max_value) * (self.rect.width - 2))
        if fill_width > 0:
            fill_rect = Rect(self.rect.x + 1, self.rect.y + 1, fill_width, self.rect.height - 2)
            canvas.rectangle(fill_rect.to_tuple(), fill=self.fill_color)
    
    def set_value(self, value: float):
        """Set the current value"""
        self.value = max(0, min(value, self.max_value))

class Screen(Container):
    """Base class for full application screens"""
    
    def __init__(self, rect: Rect):
        # Always use theme background color
        bg_color = get_theme_manager().get_color("background")
        super().__init__(rect, bg_color)
        self.name = "screen"
    
    def activate(self):
        """Called when the screen becomes active"""
        pass
    
    def deactivate(self):
        """Called when the screen is no longer active"""
        pass
    
    def update(self):
        """Update screen state - called periodically"""
        pass 