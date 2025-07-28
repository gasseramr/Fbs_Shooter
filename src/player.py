#!/usr/bin/env python3
"""
Player class for the FPS Bluetooth Game.
Handles player movement, health, shooting, and collision detection.
"""

import pygame
import math
from typing import Tuple, List, Dict, Any
from utils import (clamp, distance, normalize_vector, rotate_point, 
                   degrees_to_radians, radians_to_degrees)

class Player:
    """Player class with movement, health, and shooting mechanics."""
    
    def __init__(self, x: float, y: float, player_id: str = "player1"):
        """Initialize player with position and ID."""
        self.x = x
        self.y = y
        self.z = 0  # Height (for jumping)
        self.player_id = player_id
        
        # Movement
        self.rotation = 0  # Rotation in radians
        self.speed = 5.0
        self.jump_speed = 8.0
        self.gravity = 20.0
        self.velocity_z = 0
        self.on_ground = True
        
        # Health and combat
        self.max_health = 100
        self.health = self.max_health
        self.armor = 0
        self.max_armor = 100
        
        # Weapon
        self.current_weapon = "pistol"
        self.ammo = {"pistol": 30, "rifle": 90, "shotgun": 8}
        self.max_ammo = {"pistol": 30, "rifle": 90, "shotgun": 8}
        
        # Input state
        self.keys_pressed = set()
        self.mouse_dx = 0
        self.mouse_dy = 0
        
        # Collision
        self.radius = 0.5  # Player collision radius
        
        # Animation
        self.last_shot_time = 0
        self.shot_cooldown = 0.5  # Seconds between shots
        
    def handle_input(self, keys: List[bool], mouse_dx: float, mouse_dy: float):
        """Handle keyboard and mouse input."""
        # Update keys pressed
        self.keys_pressed.clear()
        if keys[pygame.K_w]:
            self.keys_pressed.add('w')
        if keys[pygame.K_s]:
            self.keys_pressed.add('s')
        if keys[pygame.K_a]:
            self.keys_pressed.add('a')
        if keys[pygame.K_d]:
            self.keys_pressed.add('d')
        if keys[pygame.K_SPACE]:
            self.keys_pressed.add('space')
            
        # Update mouse movement
        self.mouse_dx = mouse_dx
        self.mouse_dy = mouse_dy
    
    def update(self, dt: float, walls: List[Tuple[float, float, float, float]]):
        """Update player position and state."""
        # Handle rotation (mouse look)
        sensitivity = 0.002  # This should come from settings
        self.rotation -= self.mouse_dx * sensitivity
        self.rotation = self.rotation % (2 * math.pi)
        
        # Calculate movement direction
        move_x, move_y = 0, 0
        
        if 'w' in self.keys_pressed:
            move_x += math.cos(self.rotation)
            move_y += math.sin(self.rotation)
        if 's' in self.keys_pressed:
            move_x -= math.cos(self.rotation)
            move_y -= math.sin(self.rotation)
        if 'a' in self.keys_pressed:
            move_x += math.cos(self.rotation - math.pi/2)
            move_y += math.sin(self.rotation - math.pi/2)
        if 'd' in self.keys_pressed:
            move_x += math.cos(self.rotation + math.pi/2)
            move_y += math.sin(self.rotation + math.pi/2)
        
        # Normalize movement vector
        if move_x != 0 or move_y != 0:
            length = math.sqrt(move_x**2 + move_y**2)
            move_x /= length
            move_y /= length
        
        # Apply movement
        new_x = self.x + move_x * self.speed * dt
        new_y = self.y + move_y * self.speed * dt
        
        # Check collision with walls
        if not self.check_wall_collision(new_x, new_y, walls):
            self.x = new_x
            self.y = new_y
        
        # Handle jumping
        if 'space' in self.keys_pressed and self.on_ground:
            self.velocity_z = self.jump_speed
            self.on_ground = False
        
        # Apply gravity
        if not self.on_ground:
            self.velocity_z -= self.gravity * dt
            self.z += self.velocity_z * dt
            
            if self.z <= 0:
                self.z = 0
                self.velocity_z = 0
                self.on_ground = True
        
        # Reset mouse movement
        self.mouse_dx = 0
        self.mouse_dy = 0
    
    def check_wall_collision(self, new_x: float, new_y: float, walls: List[Tuple[float, float, float, float]]) -> bool:
        """Check if new position collides with walls."""
        for wall in walls:
            x1, y1, x2, y2 = wall
            
            # Check if player circle intersects with wall line segment
            if self.line_circle_intersection(x1, y1, x2, y2, new_x, new_y, self.radius):
                return True
        return False
    
    def line_circle_intersection(self, x1: float, y1: float, x2: float, y2: float, 
                                cx: float, cy: float, radius: float) -> bool:
        """Check if a line segment intersects with a circle."""
        # Vector from line start to end
        dx = x2 - x1
        dy = y2 - y1
        
        # Vector from line start to circle center
        fx = cx - x1
        fy = cy - y1
        
        # Project circle center onto line
        line_length_sq = dx * dx + dy * dy
        if line_length_sq == 0:
            return False
            
        t = clamp((fx * dx + fy * dy) / line_length_sq, 0, 1)
        
        # Closest point on line to circle center
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # Distance from circle center to closest point
        distance_sq = (cx - closest_x) ** 2 + (cy - closest_y) ** 2
        
        return distance_sq <= radius * radius
    
    def shoot(self, current_time: float) -> bool:
        """Attempt to shoot weapon. Returns True if shot was fired."""
        if current_time - self.last_shot_time < self.shot_cooldown:
            return False
            
        if self.ammo[self.current_weapon] <= 0:
            return False
            
        self.ammo[self.current_weapon] -= 1
        self.last_shot_time = current_time
        return True
    
    def take_damage(self, damage: int, damage_type: str = "bullet"):
        """Take damage and update health."""
        if damage_type == "bullet" and self.armor > 0:
            # Armor absorbs some damage
            absorbed = min(damage // 2, self.armor)
            self.armor -= absorbed
            damage -= absorbed
            
        self.health = max(0, self.health - damage)
    
    def heal(self, amount: int):
        """Heal the player."""
        self.health = min(self.max_health, self.health + amount)
    
    def add_armor(self, amount: int):
        """Add armor to the player."""
        self.armor = min(self.max_armor, self.armor + amount)
    
    def add_ammo(self, weapon: str, amount: int):
        """Add ammo for a specific weapon."""
        if weapon in self.ammo:
            self.ammo[weapon] = min(self.max_ammo[weapon], self.ammo[weapon] + amount)
    
    def switch_weapon(self, weapon: str):
        """Switch to a different weapon."""
        if weapon in self.ammo:
            self.current_weapon = weapon
    
    def is_alive(self) -> bool:
        """Check if player is alive."""
        return self.health > 0
    
    def get_position(self) -> Tuple[float, float, float]:
        """Get player position."""
        return (self.x, self.y, self.z)
    
    def get_rotation(self) -> float:
        """Get player rotation in radians."""
        return self.rotation
    
    def get_health_percentage(self) -> float:
        """Get player health as percentage."""
        return self.health / self.max_health
    
    def get_armor_percentage(self) -> float:
        """Get player armor as percentage."""
        return self.armor / self.max_armor if self.max_armor > 0 else 0
    
    def get_ammo_percentage(self) -> float:
        """Get current weapon ammo as percentage."""
        weapon = self.current_weapon
        if weapon in self.ammo and weapon in self.max_ammo:
            return self.ammo[weapon] / self.max_ammo[weapon]
        return 0
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Get player state for network transmission."""
        return {
            "id": self.player_id,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "rotation": self.rotation,
            "health": self.health,
            "armor": self.armor,
            "current_weapon": self.current_weapon,
            "ammo": self.ammo.copy()
        }
    
    def set_state_from_dict(self, state: Dict[str, Any]):
        """Set player state from network data."""
        if "x" in state:
            self.x = state["x"]
        if "y" in state:
            self.y = state["y"]
        if "z" in state:
            self.z = state["z"]
        if "rotation" in state:
            self.rotation = state["rotation"]
        if "health" in state:
            self.health = state["health"]
        if "armor" in state:
            self.armor = state["armor"]
        if "current_weapon" in state:
            self.current_weapon = state["current_weapon"]
        if "ammo" in state:
            self.ammo = state["ammo"].copy()
    
    def reset(self, x: float, y: float):
        """Reset player to spawn position."""
        self.x = x
        self.y = y
        self.z = 0
        self.velocity_z = 0
        self.on_ground = True
        self.health = self.max_health
        self.armor = 0
        self.ammo = self.max_ammo.copy() 