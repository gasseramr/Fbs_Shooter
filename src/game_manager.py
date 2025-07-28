#!/usr/bin/env python3
"""
Game manager for the FPS Bluetooth Game.
Controls game states, rendering, and coordinates all game components.
"""

import pygame
import math
import time
from typing import Dict, List, Any, Tuple
from player import Player
from weapon import WeaponManager, Bullet
from bluetooth_manager import BluetoothManager
from utils import (create_health_bar, create_crosshair, draw_text, 
                   format_time, clamp, distance)

class GameManager:
    """Manages the main game logic and rendering."""
    
    def __init__(self, screen: pygame.Surface, settings: Dict[str, Any]):
        """Initialize game manager."""
        self.screen = screen
        self.settings = settings
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Game state
        self.game_state = "menu"  # menu, playing, paused, game_over
        self.game_start_time = 0
        self.game_time = 0
        
        # Players
        self.local_player = Player(5, 5, "player1")
        self.remote_players = []
        self.all_players = [self.local_player]
        
        # Weapon system
        self.weapon_manager = WeaponManager()
        
        # Bluetooth
        self.bluetooth_manager = BluetoothManager()
        
        # Game world
        self.walls = self.create_default_map()
        self.spawn_points = [(5, 5), (15, 15), (5, 15), (15, 5)]
        
        # Rendering
        self.fov = 60  # Field of view in degrees
        self.ray_count = 200
        self.max_distance = 20
        
        # HUD
        self.crosshair = create_crosshair(10, (255, 255, 255))
        self.health_bar_width = 200
        self.health_bar_height = 20
        
        # Mouse
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        # Game settings
        self.mouse_sensitivity = settings.get("mouse_sensitivity", 0.1)
        
    def create_default_map(self) -> List[Tuple[float, float, float, float]]:
        """Create a default map with walls."""
        walls = [
            # Outer walls
            (0, 0, 20, 0),    # Bottom
            (0, 0, 0, 20),    # Left
            (20, 0, 20, 20),  # Right
            (0, 20, 20, 20),  # Top
            
            # Inner obstacles
            (5, 5, 8, 5),     # Horizontal wall 1
            (5, 5, 5, 8),     # Vertical wall 1
            (12, 12, 15, 12), # Horizontal wall 2
            (12, 12, 12, 15), # Vertical wall 2
            
            # Center structure
            (8, 8, 12, 8),    # Center horizontal
            (8, 8, 8, 12),    # Center vertical
            (12, 8, 12, 12),  # Center right
            (8, 12, 12, 12),  # Center bottom
        ]
        return walls
    
    def start_new_game(self):
        """Start a new single-player game."""
        self.game_state = "playing"
        self.game_start_time = time.time()
        self.local_player.reset(5, 5)
        self.weapon_manager.clear_bullets()
        self.remote_players = []
        self.all_players = [self.local_player]
        
        # Reset mouse
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
    
    def start_multiplayer_game(self, is_host: bool):
        """Start a multiplayer game."""
        self.game_state = "playing"
        self.game_start_time = time.time()
        self.local_player.reset(5, 5)
        self.weapon_manager.clear_bullets()
        
        if is_host:
            self.bluetooth_manager.start_hosting()
        # Client connection is handled in main.py
        
        # Reset mouse
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
    
    def handle_event(self, event: pygame.event.Event):
        """Handle game events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.handle_shoot()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.weapon_manager.reload_current_weapon()
            elif event.key == pygame.K_1:
                self.weapon_manager.switch_weapon("pistol")
            elif event.key == pygame.K_2:
                self.weapon_manager.switch_weapon("rifle")
            elif event.key == pygame.K_3:
                self.weapon_manager.switch_weapon("shotgun")
    
    def handle_shoot(self):
        """Handle shooting input."""
        if self.game_state != "playing":
            return
        
        current_time = time.time()
        weapon = self.weapon_manager.get_current_weapon()
        
        if weapon.can_shoot(current_time):
            # Get player position and direction
            x, y, z = self.local_player.get_position()
            direction = self.local_player.get_rotation()
            
            # Create bullets
            bullets = self.weapon_manager.shoot(x, y, z, direction, current_time, 
                                              self.local_player.player_id)
            
            # Send shot to other players if multiplayer
            if self.bluetooth_manager.is_connected():
                self.bluetooth_manager.send_shot_fired(x, y, z, direction, 
                                                     weapon.weapon_type)
    
    def update(self):
        """Update game logic."""
        if self.game_state != "playing":
            return
        
        current_time = time.time()
        dt = 1.0 / 60.0  # Assume 60 FPS
        
        # Update game time
        self.game_time = current_time - self.game_start_time
        
        # Handle input
        keys = pygame.key.get_pressed()
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        
        # Update local player
        self.local_player.handle_input(keys, mouse_dx, mouse_dy)
        self.local_player.update(dt, self.walls)
        
        # Update weapon manager
        self.weapon_manager.update_bullets(dt, self.walls)
        
        # Check bullet hits
        hits = self.weapon_manager.check_player_hits(self.all_players)
        for bullet, player in hits:
            player.take_damage(bullet.damage)
            
            # Send hit to other players if multiplayer
            if self.bluetooth_manager.is_connected():
                self.bluetooth_manager.send_player_hit(player.player_id, bullet.damage)
        
        # Update remote players
        self.remote_players = self.bluetooth_manager.get_remote_players()
        self.all_players = [self.local_player] + self.remote_players
        
        # Send player update if multiplayer
        if self.bluetooth_manager.is_connected():
            self.bluetooth_manager.send_player_update(self.local_player)
        
        # Check for game over
        if not self.local_player.is_alive():
            self.game_state = "game_over"
    
    def render(self):
        """Render the game."""
        if self.game_state == "playing":
            self.render_3d_world()
            self.render_hud()
        elif self.game_state == "game_over":
            self.render_game_over()
    
    def render_3d_world(self):
        """Render the 3D world using raycasting."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Draw sky (top half)
        sky_color = (100, 150, 255)
        pygame.draw.rect(self.screen, sky_color, (0, 0, self.screen_width, self.screen_height // 2))
        
        # Draw floor (bottom half)
        floor_color = (50, 50, 50)
        pygame.draw.rect(self.screen, floor_color, (0, self.screen_height // 2, 
                                                   self.screen_width, self.screen_height // 2))
        
        # Raycasting
        player_x, player_y, player_z = self.local_player.get_position()
        player_rotation = self.local_player.get_rotation()
        
        fov_radians = math.radians(self.fov)
        ray_angle_step = fov_radians / self.ray_count
        
        for i in range(self.ray_count):
            ray_angle = player_rotation - fov_radians / 2 + i * ray_angle_step
            
            # Cast ray
            distance = self.cast_ray(player_x, player_y, ray_angle)
            
            # Calculate wall height
            wall_height = self.calculate_wall_height(distance)
            
            # Draw wall slice
            wall_x = i * (self.screen_width // self.ray_count)
            wall_width = self.screen_width // self.ray_count
            
            # Wall color based on distance
            color_intensity = max(0, 255 - distance * 10)
            wall_color = (color_intensity, color_intensity // 2, 0)
            
            wall_rect = pygame.Rect(wall_x, (self.screen_height - wall_height) // 2, 
                                   wall_width, wall_height)
            pygame.draw.rect(self.screen, wall_color, wall_rect)
    
    def cast_ray(self, start_x: float, start_y: float, angle: float) -> float:
        """Cast a ray and return distance to wall."""
        ray_x = start_x
        ray_y = start_y
        ray_step = 0.1
        
        for distance in range(int(self.max_distance * 10)):
            ray_x += math.cos(angle) * ray_step
            ray_y += math.sin(angle) * ray_step
            
            # Check collision with walls
            for wall in self.walls:
                x1, y1, x2, y2 = wall
                if self.point_line_distance(ray_x, ray_y, x1, y1, x2, y2) < 0.1:
                    return distance * ray_step
        
        return self.max_distance
    
    def point_line_distance(self, px: float, py: float, x1: float, y1: float, 
                           x2: float, y2: float) -> float:
        """Calculate distance from point to line segment."""
        # Vector from line start to end
        dx = x2 - x1
        dy = y2 - y1
        
        # Vector from line start to point
        fx = px - x1
        fy = py - y1
        
        # Project point onto line
        line_length_sq = dx * dx + dy * dy
        if line_length_sq == 0:
            return distance((px, py), (x1, y1))
        
        t = clamp((fx * dx + fy * dy) / line_length_sq, 0, 1)
        
        # Closest point on line
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        return distance((px, py), (closest_x, closest_y))
    
    def calculate_wall_height(self, distance: float) -> int:
        """Calculate wall height based on distance."""
        if distance <= 0:
            return self.screen_height
        
        # Perspective projection
        wall_height = (self.screen_height * 0.5) / (distance + 0.1)
        return int(wall_height)
    
    def render_hud(self):
        """Render heads-up display."""
        # Health bar
        health_percentage = self.local_player.get_health_percentage()
        health_bar = create_health_bar(self.health_bar_width, self.health_bar_height, 
                                     health_percentage)
        self.screen.blit(health_bar, (20, 20))
        
        # Health text
        health_text = f"Health: {self.local_player.health}/{self.local_player.max_health}"
        draw_text(self.screen, health_text, (20, 50), 16)
        
        # Ammo
        weapon = self.weapon_manager.get_current_weapon()
        ammo_text = f"Ammo: {weapon.current_ammo}/{weapon.max_ammo}"
        draw_text(self.screen, ammo_text, (20, 80), 16)
        
        # Weapon name
        weapon_text = f"Weapon: {weapon.weapon_type.upper()}"
        draw_text(self.screen, weapon_text, (20, 110), 16)
        
        # Game time
        time_text = f"Time: {format_time(self.game_time)}"
        draw_text(self.screen, time_text, (self.screen_width - 150, 20), 16)
        
        # Connection status
        if self.bluetooth_manager.is_connected():
            status_text = f"Status: {self.bluetooth_manager.get_connection_status()}"
            draw_text(self.screen, status_text, (20, self.screen_height - 40), 16)
        
        # Crosshair
        crosshair_x = (self.screen_width - self.crosshair.get_width()) // 2
        crosshair_y = (self.screen_height - self.crosshair.get_height()) // 2
        self.screen.blit(self.crosshair, (crosshair_x, crosshair_y))
    
    def render_game_over(self):
        """Render game over screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = "GAME OVER"
        font = pygame.font.Font(None, 72)
        text_surface = font.render(game_over_text, True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(text_surface, text_rect)
        
        # Final score/time
        final_time = format_time(self.game_time)
        time_text = f"Survival Time: {final_time}"
        font = pygame.font.Font(None, 36)
        text_surface = font.render(time_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        self.screen.blit(text_surface, text_rect)
        
        # Instructions
        instructions = "Press ESC to return to menu"
        font = pygame.font.Font(None, 24)
        text_surface = font.render(instructions, True, (200, 200, 200))
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 100))
        self.screen.blit(text_surface, text_rect)
    
    def is_game_over(self) -> bool:
        """Check if game is over."""
        return self.game_state == "game_over"
    
    def pause_game(self):
        """Pause the game."""
        if self.game_state == "playing":
            self.game_state = "paused"
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
    
    def resume_game(self):
        """Resume the game."""
        if self.game_state == "paused":
            self.game_state = "playing"
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
    
    def cleanup(self):
        """Clean up game resources."""
        self.bluetooth_manager.cleanup()
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False) 