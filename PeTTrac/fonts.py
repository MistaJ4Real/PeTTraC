#!/usr/bin/env python3
# PeTTraC Font Management

import os
import logging
import shutil
from PIL import ImageFont

# Directories to search for fonts
FONT_DIRS = [
    # Custom directory (will be created during installation)
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts"),
    
    # Original example code directory (for backward compatibility)
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                "HardWare_Specs_Info_Wiring/1.3inch_LCD_HAT_Example_code/python/Font"),
    
    # System font directories for Raspberry Pi OS
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype",
    "/usr/share/fonts"
]

# Default font files to look for
DEFAULT_FONT_FILES = {
    "regular": ["Font01.ttf", "DejaVuSans.ttf", "FreeSans.ttf"],
    "mono": ["Font02.ttf", "DejaVuSansMono.ttf", "FreeMono.ttf"],
    "bold": ["Font01.ttf", "DejaVuSans-Bold.ttf", "FreeSansBold.ttf"]
}

# Singleton font manager
_font_manager = None

class FontManager:
    """Manages fonts for PeTTraC UI"""
    
    def __init__(self):
        """Initialize font manager"""
        self.fonts = {}
        self.default_font = None
        self.font_paths = {}
        
        # Find available fonts
        self._find_fonts()
        
        # Initialize default fonts
        self._init_default_fonts()
    
    def _find_fonts(self):
        """Find available fonts in common directories"""
        # Check for font directories
        for font_dir in FONT_DIRS:
            if os.path.exists(font_dir) and os.path.isdir(font_dir):
                logging.debug(f"Found font directory: {font_dir}")
                
                # Check for font files
                for font_type, font_files in DEFAULT_FONT_FILES.items():
                    if font_type not in self.font_paths:
                        for font_file in font_files:
                            font_path = os.path.join(font_dir, font_file)
                            if os.path.exists(font_path):
                                logging.debug(f"Found font: {font_path}")
                                self.font_paths[font_type] = font_path
                                break
    
    def _init_default_fonts(self):
        """Initialize default fonts with different sizes"""
        # Default sizes for common uses
        sizes = {
            "small": 12,
            "medium": 16,
            "large": 20,
            "title": 24
        }
        
        # Create default fonts
        for size_name, size in sizes.items():
            for font_type in DEFAULT_FONT_FILES.keys():
                self._load_font(f"{font_type}_{size_name}", font_type, size)
    
    def _load_font(self, font_key, font_type, size):
        """Load a font with fallback to default"""
        try:
            if font_type in self.font_paths:
                # Load font from found path
                self.fonts[font_key] = ImageFont.truetype(self.font_paths[font_type], size)
                return
        except Exception as e:
            logging.warning(f"Error loading font {font_type} size {size}: {e}")
        
        # Fallback to default
        logging.debug(f"Using default font for {font_key}")
        self.fonts[font_key] = ImageFont.load_default()
    
    def get_font(self, type_name="regular", size_name="medium"):
        """Get a font by type and size name"""
        font_key = f"{type_name}_{size_name}"
        
        if font_key in self.fonts:
            return self.fonts[font_key]
        
        # If not found, try to load it
        font_type = type_name if type_name in DEFAULT_FONT_FILES else "regular"
        
        # Map size name to pixel size
        size_map = {
            "small": 12,
            "medium": 16, 
            "large": 20,
            "title": 24
        }
        size = size_map.get(size_name, 16)
        
        # Load and return
        self._load_font(font_key, font_type, size)
        return self.fonts[font_key]
    
    def get_font_by_size(self, size, type_name="regular"):
        """Get a font by exact pixel size"""
        font_key = f"{type_name}_{size}"
        
        if font_key in self.fonts:
            return self.fonts[font_key]
        
        # If not found, load it
        font_type = type_name if type_name in DEFAULT_FONT_FILES else "regular"
        self._load_font(font_key, font_type, size)
        return self.fonts[font_key]
    
    def install_fonts(self, dest_dir=None):
        """Install fonts from example code to main folder for better accessibility"""
        if dest_dir is None:
            dest_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
        
        # Create destination directory if needed
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        # Copy fonts from original directory if available
        orig_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                              "HardWare_Specs_Info_Wiring/1.3inch_LCD_HAT_Example_code/python/Font")
        
        if os.path.exists(orig_dir):
            for font_file in os.listdir(orig_dir):
                if font_file.endswith('.ttf'):
                    src_path = os.path.join(orig_dir, font_file)
                    dst_path = os.path.join(dest_dir, font_file)
                    
                    if not os.path.exists(dst_path):
                        try:
                            shutil.copy2(src_path, dst_path)
                            logging.info(f"Copied font {font_file} to {dest_dir}")
                        except Exception as e:
                            logging.error(f"Error copying font {font_file}: {e}")
        
        # Refresh font paths
        self._find_fonts()
        return os.path.exists(dest_dir)

def get_font_manager():
    """Get or create the singleton font manager instance"""
    global _font_manager
    
    if _font_manager is None:
        _font_manager = FontManager()
    
    return _font_manager

def install_fonts():
    """Install fonts to the dedicated fonts directory"""
    font_manager = get_font_manager()
    return font_manager.install_fonts()

def get_font(type_name="regular", size_name="medium"):
    """Convenience function to get a font by type and size name"""
    font_manager = get_font_manager()
    return font_manager.get_font(type_name, size_name)

def get_font_by_size(size, type_name="regular"):
    """Convenience function to get a font by exact pixel size"""
    font_manager = get_font_manager()
    return font_manager.get_font_by_size(size, type_name) 