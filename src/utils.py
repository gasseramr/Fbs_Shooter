#!/usr/bin/env python3
"""
Utility functions for the FPS Bluetooth Game.
Handles settings, math operations, and helper functions.
"""

import json
import os
import math
import pygame
from typing import Dict, Any, Tuple

def load_settings() -> Dict[str, Any]:
    """Load game settings from settings.json file."""
    default_settings = {
        "mouse_sensitivity": 0.1,
        "audio_volume": 0.7,
        "fullscreen": False,
        "fov": 60,
        "crosshair_color": (255, 255, 255),
        "crosshair_size": 10
    }
    
    try:
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                # Merge with defaults to ensure all settings exist
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        else:
            return default_settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        return default_settings

def save_settings(settings: Dict[str, Any]) -> None:
    """Save game settings to settings.json file."""
    try:
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(value, max_val))

def distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculate distance between two 2D points."""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def distance_3d(pos1: Tuple[float, float, float], pos2: Tuple[float, float, float]) -> float:
    """Calculate distance between two 3D points."""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 + (pos1[2] - pos2[2])**2)

def normalize_vector(vector: Tuple[float, float]) -> Tuple[float, float]:
    """Normalize a 2D vector."""
    length = math.sqrt(vector[0]**2 + vector[1]**2)
    if length == 0:
        return (0, 0)
    return (vector[0] / length, vector[1] / length)

def rotate_point(point: Tuple[float, float], angle: float) -> Tuple[float, float]:
    """Rotate a 2D point around origin by given angle in radians."""
    x, y = point
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return (x * cos_a - y * sin_a, x * sin_a + y * cos_a)

def angle_between_points(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculate angle between two points in radians."""
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    return math.atan2(dy, dx)

def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * math.pi / 180

def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180 / math.pi

def create_text_surface(text: str, font_size: int = 24, color: Tuple[int, int, int] = (255, 255, 255)) -> pygame.Surface:
    """Create a text surface with given text, font size, and color."""
    font = pygame.font.Font(None, font_size)
    return font.render(text, True, color)

def draw_text(surface: pygame.Surface, text: str, position: Tuple[int, int], 
              font_size: int = 24, color: Tuple[int, int, int] = (255, 255, 255)) -> None:
    """Draw text on a surface at given position."""
    text_surface = create_text_surface(text, font_size, color)
    surface.blit(text_surface, position)

def draw_centered_text(surface: pygame.Surface, text: str, rect: pygame.Rect,
                       font_size: int = 24, color: Tuple[int, int, int] = (255, 255, 255)) -> None:
    """Draw text centered in a rectangle."""
    text_surface = create_text_surface(text, font_size, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def create_button_rect(x: int, y: int, width: int, height: int) -> pygame.Rect:
    """Create a button rectangle."""
    return pygame.Rect(x, y, width, height)

def is_point_in_rect(point: Tuple[int, int], rect: pygame.Rect) -> bool:
    """Check if a point is inside a rectangle."""
    return rect.collidepoint(point)

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between two values."""
    return a + (b - a) * t

def smooth_step(t: float) -> float:
    """Smooth step function for smooth transitions."""
    return t * t * (3 - 2 * t)

def create_gradient_surface(width: int, height: int, color1: Tuple[int, int, int], 
                           color2: Tuple[int, int, int]) -> pygame.Surface:
    """Create a gradient surface."""
    surface = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / height
        r = int(lerp(color1[0], color2[0], ratio))
        g = int(lerp(color1[1], color2[1], ratio))
        b = int(lerp(color1[2], color2[2], ratio))
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    return surface

def load_image(path: str, scale: float = 1.0) -> pygame.Surface:
    """Load and scale an image."""
    try:
        image = pygame.image.load(path)
        if scale != 1.0:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)
        return image
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        # Return a colored surface as fallback
        surface = pygame.Surface((32, 32))
        surface.fill((255, 0, 255))  # Magenta for missing textures
        return surface

def create_crosshair(size: int = 10, color: Tuple[int, int, int] = (255, 255, 255)) -> pygame.Surface:
    """Create a crosshair surface."""
    surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    center = size
    
    # Draw crosshair lines
    pygame.draw.line(surface, color, (center - size//2, center), (center + size//2, center), 2)
    pygame.draw.line(surface, color, (center, center - size//2), (center, center + size//2), 2)
    
    return surface

def format_time(seconds: float) -> str:
    """Format time in MM:SS format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def create_health_bar(width: int, height: int, health_percentage: float, 
                     color: Tuple[int, int, int] = (255, 0, 0)) -> pygame.Surface:
    """Create a health bar surface."""
    surface = pygame.Surface((width, height))
    surface.fill((50, 50, 50))  # Background
    
    # Health bar
    health_width = int(width * health_percentage)
    if health_width > 0:
        health_rect = pygame.Rect(0, 0, health_width, height)
        pygame.draw.rect(surface, color, health_rect)
    
    # Border
    pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 2)
    
    return surface 