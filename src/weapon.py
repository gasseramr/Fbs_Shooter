#!/usr/bin/env python3
"""
Weapon class for the FPS Bluetooth Game.
Handles shooting mechanics, bullet physics, and different weapon types.
"""

import pygame
import math
import random
from typing import List, Tuple, Dict, Any
from utils import distance, angle_between_points, degrees_to_radians

class Bullet:
    """Bullet class for projectile physics."""
    
    def __init__(self, x: float, y: float, z: float, direction: float, 
                 speed: float, damage: int, weapon_type: str, owner_id: str):
        """Initialize bullet with position, direction, and properties."""
        self.x = x
        self.y = y
        self.z = z
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.weapon_type = weapon_type
        self.owner_id = owner_id
        
        # Physics
        self.velocity_x = math.cos(direction) * speed
        self.velocity_y = math.sin(direction) * speed
        self.velocity_z = 0
        self.gravity = 0  # No gravity for bullets in this game
        
        # Life
        self.lifetime = 3.0  # Seconds
        self.age = 0
        
        # Size
        self.radius = 0.1
        
    def update(self, dt: float):
        """Update bullet position and age."""
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.z += self.velocity_z * dt
        
        self.age += dt
        
    def is_dead(self) -> bool:
        """Check if bullet should be removed."""
        return self.age >= self.lifetime
    
    def get_position(self) -> Tuple[float, float, float]:
        """Get bullet position."""
        return (self.x, self.y, self.z)
    
    def check_collision(self, player_x: float, player_y: float, player_z: float, 
                       player_radius: float) -> bool:
        """Check if bullet hits a player."""
        distance_2d = distance((self.x, self.y), (player_x, player_y))
        distance_3d = math.sqrt(distance_2d**2 + (self.z - player_z)**2)
        return distance_3d <= player_radius + self.radius
    
    def check_wall_collision(self, walls: List[Tuple[float, float, float, float]]) -> bool:
        """Check if bullet hits a wall."""
        for wall in walls:
            x1, y1, x2, y2 = wall
            
            # Simple line-circle intersection
            if self.line_circle_intersection(x1, y1, x2, y2, self.x, self.y, self.radius):
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
            
        t = max(0, min(1, (fx * dx + fy * dy) / line_length_sq))
        
        # Closest point on line to circle center
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # Distance from circle center to closest point
        distance_sq = (cx - closest_x) ** 2 + (cy - closest_y) ** 2
        
        return distance_sq <= radius * radius

class Weapon:
    """Base weapon class."""
    
    def __init__(self, weapon_type: str):
        """Initialize weapon with type."""
        self.weapon_type = weapon_type
        self.owner_id = ""
        
        # Weapon properties
        self.damage = 25
        self.bullet_speed = 50.0
        self.fire_rate = 0.5  # Seconds between shots
        self.last_shot_time = 0
        
        # Ammo
        self.current_ammo = 30
        self.max_ammo = 30
        self.total_ammo = 90
        
        # Accuracy
        self.spread = 0.0  # Radians
        self.recoil = 0.0
        
        # Effects
        self.muzzle_flash_duration = 0.1
        self.muzzle_flash_time = 0
        
    def can_shoot(self, current_time: float) -> bool:
        """Check if weapon can shoot."""
        return (current_time - self.last_shot_time >= self.fire_rate and 
                self.current_ammo > 0)
    
    def shoot(self, x: float, y: float, z: float, direction: float, 
              current_time: float) -> List[Bullet]:
        """Shoot weapon and return list of bullets."""
        if not self.can_shoot(current_time):
            return []
        
        self.last_shot_time = current_time
        self.current_ammo -= 1
        self.muzzle_flash_time = current_time
        
        # Calculate spread
        spread_angle = random.uniform(-self.spread, self.spread)
        final_direction = direction + spread_angle
        
        # Create bullet
        bullet = Bullet(x, y, z, final_direction, self.bullet_speed, 
                       self.damage, self.weapon_type, self.owner_id)
        
        return [bullet]
    
    def reload(self):
        """Reload weapon."""
        if self.total_ammo > 0:
            ammo_needed = self.max_ammo - self.current_ammo
            ammo_to_add = min(ammo_needed, self.total_ammo)
            self.current_ammo += ammo_to_add
            self.total_ammo -= ammo_to_add
    
    def add_ammo(self, amount: int):
        """Add ammo to weapon."""
        self.total_ammo += amount
    
    def get_ammo_percentage(self) -> float:
        """Get ammo as percentage."""
        return self.current_ammo / self.max_ammo if self.max_ammo > 0 else 0
    
    def is_muzzle_flash_active(self, current_time: float) -> bool:
        """Check if muzzle flash should be visible."""
        return current_time - self.muzzle_flash_time < self.muzzle_flash_duration

class Pistol(Weapon):
    """Pistol weapon class."""
    
    def __init__(self):
        """Initialize pistol."""
        super().__init__("pistol")
        self.damage = 25
        self.bullet_speed = 40.0
        self.fire_rate = 0.5
        self.spread = 0.05
        self.current_ammo = 12
        self.max_ammo = 12
        self.total_ammo = 48

class Rifle(Weapon):
    """Rifle weapon class."""
    
    def __init__(self):
        """Initialize rifle."""
        super().__init__("rifle")
        self.damage = 35
        self.bullet_speed = 60.0
        self.fire_rate = 0.1
        self.spread = 0.02
        self.current_ammo = 30
        self.max_ammo = 30
        self.total_ammo = 90

class Shotgun(Weapon):
    """Shotgun weapon class."""
    
    def __init__(self):
        """Initialize shotgun."""
        super().__init__("shotgun")
        self.damage = 15  # Per pellet
        self.bullet_speed = 35.0
        self.fire_rate = 1.0
        self.spread = 0.3
        self.current_ammo = 8
        self.max_ammo = 8
        self.total_ammo = 24
        self.pellet_count = 8
    
    def shoot(self, x: float, y: float, z: float, direction: float, 
              current_time: float) -> List[Bullet]:
        """Shoot shotgun with multiple pellets."""
        if not self.can_shoot(current_time):
            return []
        
        self.last_shot_time = current_time
        self.current_ammo -= 1
        self.muzzle_flash_time = current_time
        
        bullets = []
        
        # Create multiple pellets
        for _ in range(self.pellet_count):
            spread_angle = random.uniform(-self.spread, self.spread)
            final_direction = direction + spread_angle
            
            bullet = Bullet(x, y, z, final_direction, self.bullet_speed, 
                           self.damage, self.weapon_type, self.owner_id)
            bullets.append(bullet)
        
        return bullets

class WeaponManager:
    """Manages all weapons and bullets in the game."""
    
    def __init__(self):
        """Initialize weapon manager."""
        self.weapons = {
            "pistol": Pistol(),
            "rifle": Rifle(),
            "shotgun": Shotgun()
        }
        self.bullets = []
        self.current_weapon = "pistol"
        
    def get_current_weapon(self) -> Weapon:
        """Get the currently equipped weapon."""
        return self.weapons[self.current_weapon]
    
    def switch_weapon(self, weapon_type: str):
        """Switch to a different weapon."""
        if weapon_type in self.weapons:
            self.current_weapon = weapon_type
    
    def shoot(self, x: float, y: float, z: float, direction: float, 
              current_time: float, owner_id: str) -> List[Bullet]:
        """Shoot current weapon and return new bullets."""
        weapon = self.get_current_weapon()
        weapon.owner_id = owner_id
        
        new_bullets = weapon.shoot(x, y, z, direction, current_time)
        self.bullets.extend(new_bullets)
        
        return new_bullets
    
    def update_bullets(self, dt: float, walls: List[Tuple[float, float, float, float]]):
        """Update all bullets and remove dead ones."""
        dead_bullets = []
        
        for bullet in self.bullets:
            bullet.update(dt)
            
            # Check if bullet is dead
            if bullet.is_dead() or bullet.check_wall_collision(walls):
                dead_bullets.append(bullet)
        
        # Remove dead bullets
        for bullet in dead_bullets:
            self.bullets.remove(bullet)
    
    def check_player_hits(self, players: List[Any]) -> List[Tuple[Bullet, Any]]:
        """Check if bullets hit players and return hit pairs."""
        hits = []
        
        for bullet in self.bullets:
            for player in players:
                if player.player_id != bullet.owner_id:  # Don't hit self
                    if bullet.check_collision(player.x, player.y, player.z, player.radius):
                        hits.append((bullet, player))
                        # Remove bullet after hit
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        break
        
        return hits
    
    def add_weapon(self, weapon_type: str, ammo: int = 0):
        """Add ammo to a weapon."""
        if weapon_type in self.weapons:
            self.weapons[weapon_type].add_ammo(ammo)
    
    def reload_current_weapon(self):
        """Reload the current weapon."""
        weapon = self.get_current_weapon()
        weapon.reload()
    
    def get_bullets(self) -> List[Bullet]:
        """Get all active bullets."""
        return self.bullets.copy()
    
    def clear_bullets(self):
        """Clear all bullets."""
        self.bullets.clear() 