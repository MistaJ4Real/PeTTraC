#!/usr/bin/env python3
# PeTTraC Screen Implementations
# Contains UI screens based on the component framework

import logging
import time
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from ui_framework import Screen, Container, Label, Button, ProgressBar, Rect, Point
from ui_framework import get_theme_manager
from state_manager import get_app_state
from event_system import get_event_bus, Event, EventTypes
import fonts

# Constants
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 240

class DesktopScreen(Screen):
    """Main desktop/home screen"""
    
    def __init__(self):
        super().__init__(Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.name = "desktop"
        self.app_state = get_app_state()
        self.theme_manager = get_theme_manager()
        self.event_bus = get_event_bus()
        
        # Create UI components
        self.setup_ui()
        
        # Subscribe to events
        self.event_bus.subscribe(EventTypes.BUTTON_PRESS, self._on_button_press)
    
    def setup_ui(self):
        """Set up UI components"""
        # Clock and date
        self.time_label = Label(
            Rect(10, 10, 150, 30),
            datetime.now().strftime("%H:%M:%S"),
            font_type="bold",
            font_size="large"
        )
        self.add_child(self.time_label)
        
        self.date_label = Label(
            Rect(10, 35, 150, 20),
            datetime.now().strftime("%Y-%m-%d"),
            font_size="medium"
        )
        self.add_child(self.date_label)
        
        # Battery info
        self.battery_label = Label(
            Rect(SCREEN_WIDTH - 50, 10, 50, 20),
            "N/A",
            font_size="small",
            align="right"
        )
        self.add_child(self.battery_label)
        
        # System stats
        self.cpu_label = Label(
            Rect(10, 60, 100, 16),
            "CPU: 0%",
            font_size="small",
            color=self.theme_manager.get_color("accent1")
        )
        self.add_child(self.cpu_label)
        
        self.memory_label = Label(
            Rect(10, 75, 100, 16),
            "MEM: 0%",
            font_size="small",
            color=self.theme_manager.get_color("accent1")
        )
        self.add_child(self.memory_label)
        
        # App grid
        self.create_app_grid()
        
        # Navigation hint
        self.hint_label = Label(
            Rect(10, SCREEN_HEIGHT - 20, SCREEN_WIDTH - 20, 20),
            "KEY1: Menu | KEY2: Bright | KEY3: Theme",
            font_size="small",
            color=self.theme_manager.get_color("highlight")
        )
        self.add_child(self.hint_label)
        
        # Observe state changes
        self.app_state.current_time.observe(self._on_time_change)
        self.app_state.battery_percentage.observe(self._on_battery_change)
        self.app_state.is_charging.observe(self._on_charging_change)
        self.app_state.cpu_usage.observe(self._on_cpu_change)
        self.app_state.memory_usage.observe(self._on_memory_change)
    
    def create_app_grid(self):
        """Create app grid with buttons"""
        self.app_container = Container(
            Rect(20, 100, 200, 110)
        )
        self.add_child(self.app_container)
        
        # App icons
        app_icons = [
            {"name": "Files", "color": self.theme_manager.get_color("highlight"), "action": self._files_action},
            {"name": "Camera", "color": self.theme_manager.get_color("accent2"), "action": self._camera_action},
            {"name": "Tools", "color": self.theme_manager.get_color("accent1"), "action": self._tools_action},
            {"name": "Settings", "color": self.theme_manager.get_color("text"), "action": self._settings_action}
        ]
        
        grid_x = 10
        grid_y = 0
        spacing = 55
        
        for i, icon in enumerate(app_icons):
            col = i % 2
            row = i // 2
            
            x = grid_x + col * spacing
            y = grid_y + row * spacing
            
            button = Button(
                Rect(x, y, 40, 40),
                icon["name"],
                action=icon["action"],
                bg_color=icon["color"]
            )
            self.app_container.add_child(button)
    
    def _files_action(self):
        """Handle Files app button press"""
        self.app_state.show_toast("Files app not implemented", 1.0)
    
    def _camera_action(self):
        """Handle Camera app button press"""
        self.app_state.show_toast("Camera app not implemented", 1.0)
    
    def _tools_action(self):
        """Handle Tools app button press"""
        self.app_state.show_toast("Tools app not implemented", 1.0)
    
    def _settings_action(self):
        """Handle Settings app button press"""
        self.app_state.current_screen.value = "settings"
    
    def _on_time_change(self, current_time):
        """Handle time change"""
        self.time_label.set_text(current_time.strftime("%H:%M:%S"))
        self.date_label.set_text(current_time.strftime("%Y-%m-%d"))
    
    def _on_battery_change(self, percentage):
        """Handle battery percentage change"""
        if percentage is not None:
            # Set color based on battery level
            if percentage <= 10:
                color = self.theme_manager.get_color("error")
            elif percentage <= 30:
                color = self.theme_manager.get_color("warning")
            else:
                color = self.theme_manager.get_color("text")
                
            self.battery_label.color = color
            self.battery_label.set_text(f"{percentage}%")
    
    def _on_charging_change(self, is_charging):
        """Handle charging state change"""
        if is_charging:
            # Add charging indicator to battery label
            current_text = self.battery_label.text
            if not current_text.startswith("⚡"):
                self.battery_label.set_text(f"⚡{current_text}")
        else:
            # Remove charging indicator
            current_text = self.battery_label.text
            if current_text.startswith("⚡"):
                self.battery_label.set_text(current_text[1:])
    
    def _on_cpu_change(self, cpu_usage):
        """Handle CPU usage change"""
        self.cpu_label.set_text(f"CPU: {cpu_usage}%")
    
    def _on_memory_change(self, memory_usage):
        """Handle memory usage change"""
        self.memory_label.set_text(f"MEM: {memory_usage}%")
    
    def _on_button_press(self, event: Event):
        """Handle button press events"""
        button = event.data.get("button")
        
        if button == "key1":
            # Show menu screen
            self.app_state.current_screen.value = "menu"
        elif button == "key2":
            # Toggle brightness
            current_brightness = self.app_state.brightness.value
            new_brightness = 100 if current_brightness < 75 else 50
            self.app_state.brightness.value = new_brightness
            self.app_state.show_toast(f"Brightness: {new_brightness}%")
        elif button == "key3":
            # Cycle through themes
            themes = self.theme_manager.get_available_themes()
            current_idx = themes.index(self.theme_manager.get_current_theme())
            next_idx = (current_idx + 1) % len(themes)
            next_theme = themes[next_idx]
            self.theme_manager.set_theme(next_theme)
            self.app_state.show_toast(f"Theme: {next_theme}")
    
    def update(self):
        """Update screen state"""
        pass
    
    def activate(self):
        """Called when screen becomes active"""
        # Make sure theme is correct
        self.hint_label.color = self.theme_manager.get_color("highlight")
        self.cpu_label.color = self.theme_manager.get_color("accent1")
        self.memory_label.color = self.theme_manager.get_color("accent1")
    
    def deactivate(self):
        """Called when screen is no longer active"""
        pass


class MenuScreen(Screen):
    """Menu screen with navigation options"""
    
    def __init__(self):
        super().__init__(Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.name = "menu"
        self.app_state = get_app_state()
        self.theme_manager = get_theme_manager()
        self.event_bus = get_event_bus()
        
        # Menu options and current selection
        self.menu_items = ["System Info", "Battery", "Settings", "About"]
        self.selected_item = 0
        
        # Create UI components
        self.setup_ui()
        
        # Subscribe to events
        self.event_bus.subscribe(EventTypes.BUTTON_PRESS, self._on_button_press)
    
    def setup_ui(self):
        """Set up UI components"""
        # Header
        header_bg = Container(
            Rect(0, 0, SCREEN_WIDTH, 30),
            bg_color=self.theme_manager.get_color("menu_bg")
        )
        self.add_child(header_bg)
        
        title_label = Label(
            Rect(0, 5, SCREEN_WIDTH, 20),
            "MENU",
            font_type="bold",
            font_size="large",
            color=self.theme_manager.get_color("menu_item"),
            align="center"
        )
        self.add_child(title_label)
        
        # Menu items
        self.menu_container = Container(
            Rect(10, 40, SCREEN_WIDTH - 20, 160)
        )
        self.add_child(self.menu_container)
        
        # Create menu buttons
        self.menu_buttons = []
        for i, item in enumerate(self.menu_items):
            btn = Button(
                Rect(0, i * 40, SCREEN_WIDTH - 20, 30),
                item,
                action=lambda idx=i: self._on_menu_select(idx),
                bg_color=self.theme_manager.get_color("menu_selected_bg") if i == self.selected_item else None,
                text_color=self.theme_manager.get_color("menu_selected_text") if i == self.selected_item else self.theme_manager.get_color("menu_item")
            )
            self.menu_container.add_child(btn)
            self.menu_buttons.append(btn)
        
        # Navigation hint
        hint_label = Label(
            Rect(10, SCREEN_HEIGHT - 20, SCREEN_WIDTH - 20, 20),
            "◀ Back    ▲▼ Navigate    ● Select",
            font_size="small",
            color=self.theme_manager.get_color("highlight")
        )
        self.add_child(hint_label)
    
    def update_selection(self):
        """Update the visual selection state"""
        for i, btn in enumerate(self.menu_buttons):
            if i == self.selected_item:
                btn.bg_color = self.theme_manager.get_color("menu_selected_bg")
                btn.text_color = self.theme_manager.get_color("menu_selected_text")
            else:
                btn.bg_color = None
                btn.text_color = self.theme_manager.get_color("menu_item")
    
    def _on_menu_select(self, index):
        """Handle menu item selection"""
        selected = self.menu_items[index]
        
        if selected == "System Info":
            self.app_state.current_screen.value = "system_info"
        elif selected == "Battery":
            self.app_state.current_screen.value = "battery"
        elif selected == "Settings":
            self.app_state.current_screen.value = "settings"
        elif selected == "About":
            self.app_state.current_screen.value = "about"
    
    def _on_button_press(self, event: Event):
        """Handle button press events"""
        button = event.data.get("button")
        
        if button == "up":
            self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            self.update_selection()
        elif button == "down":
            self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            self.update_selection()
        elif button == "press":
            self._on_menu_select(self.selected_item)
        elif button == "left":
            self.app_state.current_screen.value = "desktop"
        elif button == "key1":
            self.app_state.current_screen.value = "desktop"
    
    def activate(self):
        """Called when screen becomes active"""
        # Update colors from theme
        self.bg_color = self.theme_manager.get_color("background")
        self.update_selection()
        
        for child in self.children:
            if isinstance(child, Container) and child.rect.y == 0:
                child.bg_color = self.theme_manager.get_color("menu_bg")
    
    def deactivate(self):
        """Called when screen is no longer active"""
        pass


class SystemInfoScreen(Screen):
    """System info screen showing CPU, memory, and disk usage"""
    
    def __init__(self):
        super().__init__(Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.name = "system_info"
        self.app_state = get_app_state()
        self.theme_manager = get_theme_manager()
        self.event_bus = get_event_bus()
        
        # Create UI components
        self.setup_ui()
        
        # Subscribe to events
        self.event_bus.subscribe(EventTypes.BUTTON_PRESS, self._on_button_press)
    
    def setup_ui(self):
        """Set up UI components"""
        # Header
        header_bg = Container(
            Rect(0, 0, SCREEN_WIDTH, 30),
            bg_color=self.theme_manager.get_color("accent2")
        )
        self.add_child(header_bg)
        
        title_label = Label(
            Rect(0, 5, SCREEN_WIDTH, 20),
            "SYSTEM INFO",
            font_type="bold",
            font_size="large",
            color=self.theme_manager.get_color("background"),
            align="center"
        )
        self.add_child(title_label)
        
        # CPU usage
        self.cpu_label = Label(
            Rect(10, 40, SCREEN_WIDTH - 20, 20),
            "CPU Usage: 0%",
            color=self.theme_manager.get_color("text")
        )
        self.add_child(self.cpu_label)
        
        self.cpu_bar = ProgressBar(
            Rect(10, 65, SCREEN_WIDTH - 20, 10),
            value=0,
            color=self.theme_manager.get_color("error")
        )
        self.add_child(self.cpu_bar)
        
        # Memory usage
        self.memory_label = Label(
            Rect(10, 90, SCREEN_WIDTH - 20, 20),
            "Memory Usage: 0%",
            color=self.theme_manager.get_color("text")
        )
        self.add_child(self.memory_label)
        
        self.memory_bar = ProgressBar(
            Rect(10, 115, SCREEN_WIDTH - 20, 10),
            value=0,
            color=self.theme_manager.get_color("highlight")
        )
        self.add_child(self.memory_bar)
        
        # Disk usage
        self.disk_label = Label(
            Rect(10, 140, SCREEN_WIDTH - 20, 20),
            "Storage: 0% used",
            color=self.theme_manager.get_color("text")
        )
        self.add_child(self.disk_label)
        
        self.disk_bar = ProgressBar(
            Rect(10, 165, SCREEN_WIDTH - 20, 10),
            value=0,
            color=self.theme_manager.get_color("accent2")
        )
        self.add_child(self.disk_bar)
        
        # Temperature
        self.temp_label = Label(
            Rect(10, 190, SCREEN_WIDTH - 20, 20),
            "Temperature: 0.0°C",
            color=self.theme_manager.get_color("text")
        )
        self.add_child(self.temp_label)
        
        # Navigation hint
        hint_label = Label(
            Rect(10, SCREEN_HEIGHT - 20, SCREEN_WIDTH - 20, 20),
            "◀ Back",
            font_size="small",
            color=self.theme_manager.get_color("highlight")
        )
        self.add_child(hint_label)
        
        # Observe state changes
        self.app_state.cpu_usage.observe(self._on_cpu_change)
        self.app_state.memory_usage.observe(self._on_memory_change)
        self.app_state.disk_usage.observe(self._on_disk_change)
        self.app_state.temperature.observe(self._on_temperature_change)
    
    def _on_cpu_change(self, cpu_usage):
        """Handle CPU usage change"""
        self.cpu_label.set_text(f"CPU Usage: {cpu_usage}%")
        self.cpu_bar.value = cpu_usage / 100
    
    def _on_memory_change(self, memory_usage):
        """Handle memory usage change"""
        self.memory_label.set_text(f"Memory Usage: {memory_usage}%")
        self.memory_bar.value = memory_usage / 100
    
    def _on_disk_change(self, disk_usage):
        """Handle disk usage change"""
        self.disk_label.set_text(f"Storage: {disk_usage}% used")
        self.disk_bar.value = disk_usage / 100
    
    def _on_temperature_change(self, temperature):
        """Handle temperature change"""
        self.temp_label.set_text(f"Temperature: {temperature:.1f}°C")
    
    def _on_button_press(self, event: Event):
        """Handle button press events"""
        button = event.data.get("button")
        
        if button in ("left", "key1"):
            self.app_state.current_screen.value = "menu"
    
    def update(self):
        """Update screen state"""
        pass
    
    def activate(self):
        """Called when screen becomes active"""
        pass
    
    def deactivate(self):
        """Called when screen is no longer active"""
        pass


class BatteryScreen(Screen):
    """Battery information screen"""
    
    def __init__(self):
        super().__init__(Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.name = "battery"
        self.app_state = get_app_state()
        self.theme_manager = get_theme_manager()
        self.event_bus = get_event_bus()
        
        # Create UI components
        self.setup_ui()
        
        # Subscribe to events
        self.event_bus.subscribe(EventTypes.BUTTON_PRESS, self._on_button_press)
    
    def setup_ui(self):
        """Set up UI components"""
        # Header
        header_bg = Container(
            Rect(0, 0, SCREEN_WIDTH, 30),
            bg_color=self.theme_manager.get_color("warning")
        )
        self.add_child(header_bg)
        
        title_label = Label(
            Rect(0, 5, SCREEN_WIDTH, 20),
            "BATTERY",
            font_type="bold",
            font_size="large",
            color=self.theme_manager.get_color("background"),
            align="center"
        )
        self.add_child(title_label)
        
        # Large percentage display
        self.percentage_label = Label(
            Rect(0, 60, SCREEN_WIDTH, 30),
            "0%",
            font_type="bold",
            font_size="large",
            color=self.theme_manager.get_color("text"),
            align="center"
        )
        self.add_child(self.percentage_label)
        
        # Battery container (for custom drawing)
        self.battery_container = Container(
            Rect(70, 90, 100, 50)
        )
        self.add_child(self.battery_container)
        
        # Charging indicator
        self.charging_label = Label(
            Rect(0, 100, SCREEN_WIDTH, 20),
            "⚡ Charging",
            color=self.theme_manager.get_color("warning"),
            align="center"
        )
        self.charging_label.visible = False
        self.add_child(self.charging_label)
        
        # Voltage information
        self.voltage_label = Label(
            Rect(0, 140, SCREEN_WIDTH, 20),
            "Voltage: 0.00V",
            color=self.theme_manager.get_color("text"),
            align="center"
        )
        self.add_child(self.voltage_label)
        
        # Warning thresholds
        self.low_warning_label = Label(
            Rect(35, 170, SCREEN_WIDTH - 70, 20),
            "Low Warning: 20%",
            color=self.theme_manager.get_color("warning")
        )
        self.add_child(self.low_warning_label)
        
        self.critical_label = Label(
            Rect(35, 190, SCREEN_WIDTH - 70, 20),
            "Critical: 10%",
            color=self.theme_manager.get_color("error")
        )
        self.add_child(self.critical_label)
        
        self.shutdown_label = Label(
            Rect(35, 210, SCREEN_WIDTH - 70, 20),
            "Auto Shutdown: 5%",
            font_type="bold",
            color=self.theme_manager.get_color("error")
        )
        self.add_child(self.shutdown_label)
        
        # Navigation hint
        hint_label = Label(
            Rect(10, SCREEN_HEIGHT - 20, SCREEN_WIDTH - 20, 20),
            "◀ Back",
            font_size="small",
            color=self.theme_manager.get_color("highlight")
        )
        self.add_child(hint_label)
        
        # Observe state changes
        self.app_state.battery_percentage.observe(self._on_battery_change)
        self.app_state.battery_voltage.observe(self._on_voltage_change)
        self.app_state.is_charging.observe(self._on_charging_change)
    
    def _on_battery_change(self, percentage):
        """Handle battery percentage change"""
        if percentage is not None:
            self.percentage_label.set_text(f"{percentage}%")
            
            # Update battery_container's custom draw method
            def draw_battery(canvas, rect):
                x, y = rect.x, rect.y
                width, height = 50, 25
                
                # Set color based on battery level
                if percentage > 75:
                    fill_color = self.theme_manager.get_color("accent2")
                elif percentage > 30:
                    fill_color = self.theme_manager.get_color("warning")
                else:
                    fill_color = self.theme_manager.get_color("error")
                
                # Draw battery outline
                canvas.rectangle((x, y, x + width, y + height), 
                               outline=self.theme_manager.get_color("text"), width=2)
                canvas.rectangle((x + width, y + 7, x + width + 5, y + height - 7), 
                               fill=self.theme_manager.get_color("text"))
                
                # Draw battery fill level
                fill_width = int((percentage / 100) * (width - 4))
                canvas.rectangle((x + 2, y + 2, x + 2 + fill_width, y + height - 2), 
                               fill=fill_color)
            
            self.battery_container.custom_draw = draw_battery
    
    def _on_voltage_change(self, voltage):
        """Handle voltage change"""
        if voltage is not None:
            self.voltage_label.set_text(f"Voltage: {voltage/1000:.2f}V")
    
    def _on_charging_change(self, is_charging):
        """Handle charging state change"""
        self.charging_label.visible = is_charging
    
    def _on_button_press(self, event: Event):
        """Handle button press events"""
        button = event.data.get("button")
        
        if button in ("left", "key1"):
            self.app_state.current_screen.value = "menu"
    
    def update(self):
        """Update screen state"""
        pass
    
    def activate(self):
        """Called when screen becomes active"""
        pass
    
    def deactivate(self):
        """Called when screen is no longer active"""
        pass


class SettingsScreen(Screen):
    """Settings screen for app configuration"""
    
    def __init__(self):
        super().__init__(Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.name = "settings"
        self.app_state = get_app_state()
        self.theme_manager = get_theme_manager()
        self.event_bus = get_event_bus()
        self.config = get_config()
        
        # Settings options
        self.settings = [
            {"name": "Brightness", "value": self.app_state.brightness.value, "min": 0, "max": 100, "step": 5},
            {"name": "Rotation", "value": self.config.get("display", "rotation"), "options": [0, 90, 180, 270]},
            {"name": "Theme", "value": self.theme_manager.get_current_theme(), "options": self.theme_manager.get_available_themes()},
            {"name": "Debug Mode", "value": "ON" if self.app_state.debug_mode.value else "OFF", "options": ["ON", "OFF"]},
            {"name": "Back to Menu", "action": "back_to_menu"}
        ]
        self.selected_item = 0
        
        # Create UI components
        self.setup_ui()
        
        # Subscribe to events
        self.event_bus.subscribe(EventTypes.BUTTON_PRESS, self._on_button_press)
    
    def setup_ui(self):
        """Set up UI components"""
        # Header
        header_bg = Container(
            Rect(0, 0, SCREEN_WIDTH, 30),
            bg_color=self.theme_manager.get_color("menu_bg")
        )
        self.add_child(header_bg)
        
        title_label = Label(
            Rect(0, 5, SCREEN_WIDTH, 20),
            "SETTINGS",
            font_type="bold",
            font_size="large",
            color=self.theme_manager.get_color("text"),
            align="center"
        )
        self.add_child(title_label)
        
        # Settings container
        self.settings_container = Container(
            Rect(5, 40, SCREEN_WIDTH - 10, 170)
        )
        self.add_child(self.settings_container)
        
        # Create settings items
        self.setting_labels = []
        self.value_labels = []
        
        for i, setting in enumerate(self.settings):
            # Setting name
            setting_label = Label(
                Rect(15, i * 35, 150, 20),
                setting["name"],
                color=self.theme_manager.get_color("text")
            )
            self.settings_container.add_child(setting_label)
            self.setting_labels.append(setting_label)
            
            # Setting value
            value_text = str(setting.get("value", ""))
            if i == self.selected_item:
                value_text = f"◀ {value_text} ▶"
                
            value_label = Label(
                Rect(170, i * 35, SCREEN_WIDTH - 180, 20),
                value_text,
                color=self.theme_manager.get_color("accent1"),
                align="right"
            )
            self.settings_container.add_child(value_label)
            self.value_labels.append(value_label)
        
        # Highlight for selected item
        self.selection_highlight = Container(
            Rect(5, 35 + (self.selected_item * 35), SCREEN_WIDTH - 10, 30),
            bg_color=self.theme_manager.get_color("menu_selected_bg")
        )
        self.settings_container.add_child(self.selection_highlight)
        
        # Make sure highlight is behind labels
        self.settings_container.children.insert(0, self.settings_container.children.pop())
        
        # Navigation hint
        self.hint_label = Label(
            Rect(10, SCREEN_HEIGHT - 20, SCREEN_WIDTH - 20, 20),
            "◀ Back    ◀▶ Change Value    ● Select",
            font_size="small",
            color=self.theme_manager.get_color("highlight")
        )
        self.add_child(self.hint_label)
    
    def update_selection(self):
        """Update the visual selection state"""
        # Move highlight
        self.selection_highlight.rect.y = 35 + (self.selected_item * 35)
        
        # Update value text and arrows
        for i, label in enumerate(self.value_labels):
            value_text = str(self.settings[i].get("value", ""))
            if i == self.selected_item:
                if "action" not in self.settings[i]:
                    value_text = f"◀ {value_text} ▶"
            label.set_text(value_text)
        
        # Update navigation hint
        if self.selected_item == len(self.settings) - 1:  # "Back to Menu" item
            self.hint_label.set_text("◀ Back    ● Return to Menu")
        else:
            self.hint_label.set_text("◀ Back    ◀▶ Change Value    ● Select")
    
    def _adjust_setting(self, direction):
        """Adjust the selected setting value in the given direction"""
        setting = self.settings[self.selected_item]
        
        if "action" in setting:
            # This is an action button, not a value to adjust
            return
            
        # Different handling based on setting type
        if "options" in setting:
            # This is a selection from options
            options = setting["options"]
            current_idx = options.index(setting["value"]) if setting["value"] in options else 0
            new_idx = (current_idx + direction) % len(options)
            setting["value"] = options[new_idx]
            
        elif "min" in setting and "max" in setting:
            # This is a numeric value with min/max
            step = setting.get("step", 1)
            new_value = setting["value"] + (step * direction)
            setting["value"] = max(setting["min"], min(setting["max"], new_value))
        
        # Apply the setting
        self._apply_setting(setting["name"], setting["value"])
        
        # Update the display
        self.update_selection()
    
    def _apply_setting(self, name, value):
        """Apply a setting change"""
        if name == "Brightness":
            self.app_state.brightness.value = value
            self.event_bus.publish_by_type(EventTypes.SETTING_CHANGE, {"name": "brightness", "value": value})
            
        elif name == "Rotation":
            self.config.set("display", "rotation", value)
            self.event_bus.publish_by_type(EventTypes.SETTING_CHANGE, {"name": "rotation", "value": value})
            
        elif name == "Theme":
            self.theme_manager.set_theme(value)
            self.config.set("display", "theme", value)
            
        elif name == "Debug Mode":
            debug_value = (value == "ON")
            self.app_state.debug_mode.value = debug_value
            self.config.set("system", "debug_mode", debug_value)
            self.event_bus.set_debug(debug_value)
    
    def _on_button_press(self, event: Event):
        """Handle button press events"""
        button = event.data.get("button")
        
        if button == "up":
            self.selected_item = (self.selected_item - 1) % len(self.settings)
            self.update_selection()
            
        elif button == "down":
            self.selected_item = (self.selected_item + 1) % len(self.settings)
            self.update_selection()
            
        elif button == "left":
            if self.selected_item == len(self.settings) - 1:  # "Back to Menu" item
                self.app_state.current_screen.value = "menu"
            else:
                self._adjust_setting(-1)
                
        elif button == "right":
            if self.selected_item < len(self.settings) - 1:  # Not on "Back to Menu"
                self._adjust_setting(1)
                
        elif button == "press":
            if self.selected_item == len(self.settings) - 1:  # "Back to Menu" item
                self.app_state.current_screen.value = "menu"
            
        elif button == "key1":
            self.app_state.current_screen.value = "menu"
    
    def update(self):
        """Update screen state"""
        pass
    
    def activate(self):
        """Called when screen becomes active"""
        # Refresh settings values from app state
        self.settings[0]["value"] = self.app_state.brightness.value
        self.settings[1]["value"] = self.config.get("display", "rotation")
        self.settings[2]["value"] = self.theme_manager.get_current_theme()
        self.settings[3]["value"] = "ON" if self.app_state.debug_mode.value else "OFF"
        
        # Update colors from theme
        self.selection_highlight.bg_color = self.theme_manager.get_color("menu_selected_bg")
        header_bg = self.children[0]
        if isinstance(header_bg, Container):
            header_bg.bg_color = self.theme_manager.get_color("menu_bg")
        
        # Update selection display
        self.update_selection()
    
    def deactivate(self):
        """Called when screen is no longer active"""
        pass


class AboutScreen(Screen):
    """About screen with app information"""
    
    def __init__(self):
        super().__init__(Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.name = "about"
        self.app_state = get_app_state()
        self.theme_manager = get_theme_manager()
        self.event_bus = get_event_bus()
        
        # Create UI components
        self.setup_ui()
        
        # Subscribe to events
        self.event_bus.subscribe(EventTypes.BUTTON_PRESS, self._on_button_press)
    
    def setup_ui(self):
        """Set up UI components"""
        # Header with special color
        theme = self.theme_manager.get_current_theme()
        title_color = {"default": "PURPLE", "dark": "PURPLE", "light": "PURPLE", "blue": "CYAN"}.get(theme, "PURPLE")
        
        header_bg = Container(
            Rect(0, 0, SCREEN_WIDTH, 30),
            bg_color=title_color
        )
        self.add_child(header_bg)
        
        title_label = Label(
            Rect(0, 5, SCREEN_WIDTH, 20),
            "ABOUT",
            font_type="bold",
            font_size="large",
            color=self.theme_manager.get_color("background"),
            align="center"
        )
        self.add_child(title_label)
        
        # App information
        app_name_label = Label(
            Rect(30, 50, SCREEN_WIDTH - 60, 30),
            "PeTTraC System",
            font_type="bold",
            font_size="large",
            color=self.theme_manager.get_color("text")
        )
        self.add_child(app_name_label)
        
        version_label = Label(
            Rect(30, 80, SCREEN_WIDTH - 60, 20),
            "Version 1.0.0",
            color=self.theme_manager.get_color("highlight")
        )
        self.add_child(version_label)
        
        project_label = Label(
            Rect(30, 110, SCREEN_WIDTH - 60, 20),
            "Part of CERBERUS Project",
            color=self.theme_manager.get_color("accent2")
        )
        self.add_child(project_label)
        
        copyright_label = Label(
            Rect(30, 140, SCREEN_WIDTH - 60, 20),
            "© 2025",
            color=self.theme_manager.get_color("accent1")
        )
        self.add_child(copyright_label)
        
        # Decorative line
        self.decor_line = Container(
            Rect(30, 170, 180, 2),
            bg_color=self.theme_manager.get_color("highlight")
        )
        self.add_child(self.decor_line)
        
        # System information
        import sys
        python_label = Label(
            Rect(30, 180, SCREEN_WIDTH - 60, 20),
            f"Python {sys.version_info.major}.{sys.version_info.minor}",
            font_size="small",
            color=self.theme_manager.get_color("text")
        )
        self.add_child(python_label)
        
        # Try to get Raspberry Pi model
        pi_model = "Unknown hardware"
        try:
            with open('/proc/device-tree/model', 'r') as f:
                pi_model = f.read().strip('\0')
        except:
            pass
            
        hardware_label = Label(
            Rect(30, 200, SCREEN_WIDTH - 60, 20),
            pi_model,
            font_size="small",
            color=self.theme_manager.get_color("text")
        )
        self.add_child(hardware_label)
        
        # Navigation hint
        hint_label = Label(
            Rect(10, SCREEN_HEIGHT - 20, SCREEN_WIDTH - 20, 20),
            "◀ Back",
            font_size="small",
            color=self.theme_manager.get_color("highlight")
        )
        self.add_child(hint_label)
    
    def _on_button_press(self, event: Event):
        """Handle button press events"""
        button = event.data.get("button")
        
        if button in ("left", "key1"):
            self.app_state.current_screen.value = "menu"
    
    def update(self):
        """Update screen state"""
        pass
    
    def activate(self):
        """Called when screen becomes active"""
        # Update colors from theme
        theme = self.theme_manager.get_current_theme()
        title_color = {"default": "PURPLE", "dark": "PURPLE", "light": "PURPLE", "blue": "CYAN"}.get(theme, "PURPLE")
        
        header_bg = self.children[0]
        if isinstance(header_bg, Container):
            header_bg.bg_color = title_color
            
        self.decor_line.bg_color = self.theme_manager.get_color("highlight")
    
    def deactivate(self):
        """Called when screen is no longer active"""
        pass


# Dictionary of available screens
SCREENS = {
    "desktop": DesktopScreen,
    "menu": MenuScreen,
    "system_info": SystemInfoScreen,
    "battery": BatteryScreen,
    "settings": SettingsScreen,
    "about": AboutScreen,
}

def get_screen(name: str) -> Screen:
    """Get a screen by name"""
    if name in SCREENS:
        return SCREENS[name]()
    else:
        logging.error(f"Screen '{name}' not found")
        return DesktopScreen()  # Default 