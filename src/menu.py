#!/usr/bin/env python3
"""
Menu system for the FPS Bluetooth Game.
Handles main menu, settings menu, and host selection with enhanced GUI.
"""

import pygame
import math
import time
from typing import Dict, Any, List, Optional
from utils import (draw_centered_text, create_button_rect, is_point_in_rect, 
                   create_gradient_surface, clamp, load_image)

class Menu:
    """Menu system for the game."""
    
    def __init__(self, screen: pygame.Surface, settings: Dict[str, Any]):
        """Initialize the menu system with enhanced GUI."""
        self.screen = screen
        self.settings = settings
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Menu state
        self.current_menu = "main"  # main, settings, host_selection, multiplayer_options
        self.selected_option = 0
        self.hosts = []
        self.selected_host = 0
        
        # Button dimensions
        self.button_width = 350
        self.button_height = 70
        self.button_margin = 25
        
        # Colors
        self.background_color = (20, 20, 40)
        self.button_color = (60, 60, 100)
        self.button_hover_color = (80, 80, 120)
        self.button_selected_color = (100, 100, 140)
        self.button_click_color = (120, 120, 160)
        self.text_color = (255, 255, 255)
        self.title_color = (255, 255, 0)
        self.subtitle_color = (200, 200, 200)
        
        # Animation
        self.animation_time = 0
        self.button_animations = {}
        self.hover_effects = {}
        
        # Create animated background
        self.background = self.create_animated_background()
        
        # Menu options
        self.main_menu_options = ["Start Game", "Settings", "Exit"]
        self.multiplayer_options = ["Host Game", "Join Game", "Back"]
        self.settings_options = ["Mouse Sensitivity", "Audio Volume", "Graphics", "Back"]
        
        # Settings sliders
        self.slider_width = 250
        self.slider_height = 25
        self.slider_dragging = None
        
        # Load sounds (if available)
        self.sounds = {}
        self.load_sounds()
        
        # Graphics settings
        self.graphics_options = ["Low", "Medium", "High"]
        self.selected_graphics = 1  # Medium by default
    
    def create_animated_background(self) -> pygame.Surface:
        """Create an animated background with particles."""
        background = create_gradient_surface(
            self.screen_width, self.screen_height,
            (20, 20, 40), (40, 20, 60)
        )
        
        # Add some animated elements
        for i in range(50):
            x = (i * 37) % self.screen_width
            y = (i * 73) % self.screen_height
            color = (100 + i * 3, 150 + i * 2, 255)
            pygame.draw.circle(background, color, (x, y), 2)
        
        return background
    
    def load_sounds(self):
        """Load sound effects for menu interactions."""
        try:
            # Try to load sounds, but don't fail if they don't exist
            self.sounds["hover"] = pygame.mixer.Sound("assets/sounds/hover.wav")
            self.sounds["click"] = pygame.mixer.Sound("assets/sounds/click.wav")
        except:
            # Create silent sounds if files don't exist
            self.sounds["hover"] = None
            self.sounds["click"] = None
    
    def play_sound(self, sound_name: str):
        """Play a sound effect if available."""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except:
                pass
    
    def animate_button(self, button_id: str, is_hovered: bool, is_clicked: bool):
        """Animate button appearance."""
        if button_id not in self.button_animations:
            self.button_animations[button_id] = {"scale": 1.0, "alpha": 255}
        
        anim = self.button_animations[button_id]
        
        if is_hovered:
            anim["scale"] = min(1.1, anim["scale"] + 0.05)
        else:
            anim["scale"] = max(1.0, anim["scale"] - 0.05)
        
        if is_clicked:
            anim["alpha"] = 200
        else:
            anim["alpha"] = min(255, anim["alpha"] + 5)
    
    def draw_animated_button(self, surface: pygame.Surface, text: str, rect: pygame.Rect, 
                           is_hovered: bool, is_clicked: bool, color: tuple):
        """Draw a button with animations and effects."""
        button_id = f"{text}_{rect.x}_{rect.y}"
        
        # Animate button
        self.animate_button(button_id, is_hovered, is_clicked)
        anim = self.button_animations.get(button_id, {"scale": 1.0, "alpha": 255})
        
        # Create button surface with effects
        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Choose color based on state
        if is_clicked:
            button_color = self.button_click_color
        elif is_hovered:
            button_color = self.button_hover_color
        else:
            button_color = color
        
        # Draw button with rounded corners
        pygame.draw.rect(button_surface, button_color, button_surface.get_rect(), border_radius=10)
        
        # Add glow effect for hover
        if is_hovered:
            glow_surface = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*button_color, 100), glow_surface.get_rect(), border_radius=15)
            glow_rect = glow_surface.get_rect(center=button_surface.get_rect().center)
            button_surface.blit(glow_surface, glow_rect)
        
        # Draw text
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, self.text_color)
        text_rect = text_surface.get_rect(center=button_surface.get_rect().center)
        button_surface.blit(text_surface, text_rect)
        
        # Apply scaling and alpha
        if anim["scale"] != 1.0:
            new_width = int(rect.width * anim["scale"])
            new_height = int(rect.height * anim["scale"])
            button_surface = pygame.transform.scale(button_surface, (new_width, new_height))
        
        # Apply to main surface
        final_rect = button_surface.get_rect(center=rect.center)
        surface.blit(button_surface, final_rect)
        
        return final_rect
        
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle menu events and return action."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.play_sound("click")
                return self.handle_click(event.pos)
                
        elif event.type == pygame.KEYDOWN:
            print(f"handle_event: current_menu='{self.current_menu}', key={event.key}")
            if self.current_menu == "main":
                return self.handle_main_menu_key(event.key)
            elif self.current_menu == "multiplayer_options":
                print("Calling handle_multiplayer_key")
                return self.handle_multiplayer_key(event.key)
            elif self.current_menu == "settings":
                return self.handle_settings_key(event.key)
            elif self.current_menu == "host_selection":
                return self.handle_host_selection_key(event.key)
                
        return None
    
    def handle_click(self, pos: tuple) -> Optional[str]:
        """Handle mouse clicks on menu buttons."""
        if self.current_menu == "main":
            return self.handle_main_menu_click(pos)
        elif self.current_menu == "multiplayer_options":
            return self.handle_multiplayer_click(pos)
        elif self.current_menu == "settings":
            return self.handle_settings_click(pos)
        elif self.current_menu == "host_selection":
            return self.handle_host_selection_click(pos)
        return None
    
    def handle_main_menu_click(self, pos: tuple) -> Optional[str]:
        """Handle clicks on main menu buttons."""
        button_y = self.screen_height // 2 - 100
        for i, option in enumerate(self.main_menu_options):
            button_rect = create_button_rect(
                (self.screen_width - self.button_width) // 2,
                button_y + i * (self.button_height + self.button_margin),
                self.button_width,
                self.button_height
            )
            if is_point_in_rect(pos, button_rect):
                if option == "Start Game":
                    self.current_menu = "multiplayer_options"
                    self.selected_option = 0
                    return "multiplayer_options"
                elif option == "Settings":
                    self.current_menu = "settings"
                    self.selected_option = 0
                    return "settings"
                elif option == "Exit":
                    return "exit"
        return None
    
    def handle_main_menu_key(self, key: int) -> Optional[str]:
        """Handle keyboard input for main menu."""
        if key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.main_menu_options)
        elif key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.main_menu_options)
        elif key == pygame.K_RETURN:
            option = self.main_menu_options[self.selected_option]
            if option == "Start Game":
                self.current_menu = "multiplayer_options"
                self.selected_option = 0
                return "show_multiplayer_options"
            elif option == "Settings":
                self.current_menu = "settings"
                return "settings"
            elif option == "Exit":
                return "exit"
        return None
    
    def handle_settings_click(self, pos: tuple) -> Optional[str]:
        """Handle clicks on settings menu."""
        button_y = self.screen_height // 2 - 50
        
        # Mouse sensitivity slider
        slider_x = (self.screen_width - self.slider_width) // 2
        slider_y = button_y + 80
        slider_rect = pygame.Rect(slider_x, slider_y, self.slider_width, self.slider_height)
        
        if is_point_in_rect(pos, slider_rect):
            self.slider_dragging = "sensitivity"
            return None
            
        # Audio volume slider
        volume_slider_y = button_y + 140
        volume_slider_rect = pygame.Rect(slider_x, volume_slider_y, self.slider_width, self.slider_height)
        
        if is_point_in_rect(pos, volume_slider_rect):
            self.slider_dragging = "volume"
            return None
            
        # Back button
        back_button_rect = create_button_rect(
            (self.screen_width - self.button_width) // 2,
            button_y + 200,
            self.button_width,
            self.button_height
        )
        if is_point_in_rect(pos, back_button_rect):
            self.current_menu = "main"
            return "back"
        return None
    
    def handle_settings_key(self, key: int) -> Optional[str]:
        """Handle keyboard input for settings menu."""
        if key == pygame.K_ESCAPE:
            self.current_menu = "main"
            return "back"
        return None
    
    def handle_settings_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle settings menu events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self.handle_settings_click(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.slider_dragging = None
        elif event.type == pygame.MOUSEMOTION and self.slider_dragging:
            self.update_slider(event.pos[0])
        elif event.type == pygame.KEYDOWN:
            return self.handle_settings_key(event.key)
        return None
    
    def update_slider(self, mouse_x: int):
        """Update slider values based on mouse position."""
        slider_x = (self.screen_width - self.slider_width) // 2
        
        if self.slider_dragging == "sensitivity":
            relative_x = clamp(mouse_x - slider_x, 0, self.slider_width)
            self.settings["mouse_sensitivity"] = relative_x / self.slider_width * 0.2
        elif self.slider_dragging == "volume":
            relative_x = clamp(mouse_x - slider_x, 0, self.slider_width)
            self.settings["audio_volume"] = relative_x / self.slider_width
    
    def show_multiplayer_options(self) -> str:
        """Show multiplayer options (Host/Join)."""
        # This would be implemented to show host/join options
        # For now, return host_game as default
        return "host_game"
    
    def handle_multiplayer_click(self, pos: tuple) -> Optional[str]:
        """Handle clicks on multiplayer options menu."""
        button_y = self.screen_height // 2 - 100
        for i, option in enumerate(self.multiplayer_options):
            button_rect = create_button_rect(
                (self.screen_width - self.button_width) // 2,
                button_y + i * (self.button_height + self.button_margin),
                self.button_width,
                self.button_height
            )
            if is_point_in_rect(pos, button_rect):
                if option == "Host Game":
                    return "host_game"
                elif option == "Join Game":
                    return "join_game"
                elif option == "Back":
                    self.current_menu = "main"
                    return "back"
        return None
    
    def handle_multiplayer_key(self, key: int) -> Optional[str]:
        """Handle keyboard input for multiplayer menu."""
        print(f"handle_multiplayer_key called with key: {key}")
        if key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.multiplayer_options)
            print(f"Selected option: {self.selected_option}")
        elif key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.multiplayer_options)
            print(f"Selected option: {self.selected_option}")
        elif key == pygame.K_RETURN:
            option = self.multiplayer_options[self.selected_option]
            print(f"Multiplayer key: selected_option={self.selected_option}, option='{option}'")
            if option == "Host Game":
                print("Returning host_game")
                return "host_game"
            elif option == "Join Game":
                print("Returning join_game")
                return "join_game"
            elif option == "Back":
                print("Returning back")
                self.current_menu = "main"
                return "back"
        elif key == pygame.K_ESCAPE:
            print("Returning back (escape)")
            self.current_menu = "main"
            return "back"
        return None
    
    def show_host_selection(self, hosts: List[str]) -> Optional[str]:
        """Show host selection menu."""
        self.hosts = hosts
        self.current_menu = "host_selection"
        self.selected_host = 0
        return None
    
    def handle_host_selection_click(self, pos: tuple) -> Optional[str]:
        """Handle clicks on host selection menu."""
        button_y = self.screen_height // 2 - 100
        
        for i, host in enumerate(self.hosts):
            button_rect = create_button_rect(
                (self.screen_width - self.button_width) // 2,
                button_y + i * (self.button_height + self.button_margin),
                self.button_width,
                self.button_height
            )
            if is_point_in_rect(pos, button_rect):
                return f"join_host_{i}"
                
        # Back button
        back_button_rect = create_button_rect(
            (self.screen_width - self.button_width) // 2,
            button_y + len(self.hosts) * (self.button_height + self.button_margin),
            self.button_width,
            self.button_height
        )
        if is_point_in_rect(pos, back_button_rect):
            self.current_menu = "main"
            return "back"
        return None
    
    def handle_host_selection_key(self, key: int) -> Optional[str]:
        """Handle keyboard input for host selection."""
        if key == pygame.K_UP:
            self.selected_host = (self.selected_host - 1) % len(self.hosts)
        elif key == pygame.K_DOWN:
            self.selected_host = (self.selected_host + 1) % len(self.hosts)
        elif key == pygame.K_RETURN:
            return f"join_host_{self.selected_host}"
        elif key == pygame.K_ESCAPE:
            self.current_menu = "main"
            return "back"
        return None
    
    def update(self):
        """Update menu animations and effects."""
        pass
    
    def update_settings(self):
        """Update settings menu."""
        pass
    
    def render(self):
        """Render the current menu."""
        if self.current_menu == "main":
            self.render_main_menu()
        elif self.current_menu == "multiplayer_options":
            self.render_multiplayer_menu()
        elif self.current_menu == "settings":
            self.render_settings()
        elif self.current_menu == "host_selection":
            self.render_host_selection()
    
    def render_main_menu(self):
        """Render the main menu with enhanced graphics."""
        # Draw animated background
        self.screen.blit(self.background, (0, 0))
        
        # Add animated particles
        self.animation_time += 0.016  # Assume 60 FPS
        for i in range(20):
            x = (i * 37 + int(self.animation_time * 50)) % self.screen_width
            y = (i * 73 + int(self.animation_time * 30)) % self.screen_height
            alpha = int(128 + 127 * math.sin(self.animation_time + i))
            particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (100, 150, 255, alpha), (2, 2), 2)
            self.screen.blit(particle_surface, (x, y))
        
        # Draw title with glow effect
        title_text = "FPS BLUETOOTH GAME"
        title_rect = pygame.Rect(0, 80, self.screen_width, 120)
        
        # Glow effect
        for i in range(3):
            glow_color = (255, 255, 0, 50 - i * 15)
            glow_surface = pygame.Surface((self.screen_width, 120), pygame.SRCALPHA)
            font = pygame.font.Font(None, 48 + i * 2)
            text_surface = font.render(title_text, True, glow_color)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, 140 + i * 2))
            glow_surface.blit(text_surface, text_rect)
            self.screen.blit(glow_surface, (0, 80))
        
        # Main title
        font = pygame.font.Font(None, 48)
        text_surface = font.render(title_text, True, self.title_color)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 140))
        self.screen.blit(text_surface, text_rect)
        
        # Subtitle
        subtitle_text = "Multiplayer First-Person Shooter"
        font = pygame.font.Font(None, 24)
        text_surface = font.render(subtitle_text, True, self.subtitle_color)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 170))
        self.screen.blit(text_surface, text_rect)
        
        # Draw animated menu options
        button_y = self.screen_height // 2 - 20
        mouse_pos = pygame.mouse.get_pos()
        
        for i, option in enumerate(self.main_menu_options):
            button_rect = create_button_rect(
                (self.screen_width - self.button_width) // 2,
                button_y + i * (self.button_height + self.button_margin),
                self.button_width,
                self.button_height
            )
            
            # Check hover state
            is_hovered = is_point_in_rect(mouse_pos, button_rect)
            is_selected = i == self.selected_option
            
            # Choose button color
            if is_selected:
                color = self.button_selected_color
            else:
                color = self.button_color
            
            # Draw animated button
            self.draw_animated_button(self.screen, option, button_rect, is_hovered, False, color)
            
            # Play hover sound
            if is_hovered and option not in self.hover_effects:
                self.play_sound("hover")
                self.hover_effects[option] = True
            elif not is_hovered and option in self.hover_effects:
                del self.hover_effects[option]
    
    def render_multiplayer_menu(self):
        """Render the multiplayer options menu."""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        title_text = "MULTIPLAYER"
        title_rect = pygame.Rect(0, 100, self.screen_width, 100)
        draw_centered_text(self.screen, title_text, title_rect, 48, self.title_color)
        
        # Draw menu options
        button_y = self.screen_height // 2 - 50
        mouse_pos = pygame.mouse.get_pos()
        
        for i, option in enumerate(self.multiplayer_options):
            button_rect = create_button_rect(
                (self.screen_width - self.button_width) // 2,
                button_y + i * (self.button_height + self.button_margin),
                self.button_width,
                self.button_height
            )
            
            # Check hover state
            is_hovered = is_point_in_rect(mouse_pos, button_rect)
            is_selected = i == self.selected_option
            
            # Choose button color
            if is_selected:
                color = self.button_selected_color
            else:
                color = self.button_color
            
            # Draw animated button
            self.draw_animated_button(self.screen, option, button_rect, is_hovered, False, color)
    
    def render_settings(self):
        """Render the settings menu with enhanced graphics."""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title with glow effect
        title_text = "SETTINGS"
        title_rect = pygame.Rect(0, 80, self.screen_width, 120)
        
        # Glow effect
        for i in range(3):
            glow_color = (255, 255, 0, 50 - i * 15)
            glow_surface = pygame.Surface((self.screen_width, 120), pygame.SRCALPHA)
            font = pygame.font.Font(None, 48 + i * 2)
            text_surface = font.render(title_text, True, glow_color)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, 140 + i * 2))
            glow_surface.blit(text_surface, text_rect)
            self.screen.blit(glow_surface, (0, 80))
        
        # Main title
        font = pygame.font.Font(None, 48)
        text_surface = font.render(title_text, True, self.title_color)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 140))
        self.screen.blit(text_surface, text_rect)
        
        button_y = self.screen_height // 2 - 80
        
        # Draw mouse sensitivity setting
        sensitivity_text = f"Mouse Sensitivity: {self.settings['mouse_sensitivity']:.2f}"
        text_rect = pygame.Rect(0, button_y, self.screen_width, 50)
        draw_centered_text(self.screen, sensitivity_text, text_rect, 24, self.text_color)
        
        # Draw enhanced sensitivity slider
        slider_x = (self.screen_width - self.slider_width) // 2
        slider_y = button_y + 60
        slider_rect = pygame.Rect(slider_x, slider_y, self.slider_width, self.slider_height)
        
        # Slider background with gradient
        pygame.draw.rect(self.screen, (50, 50, 50), slider_rect, border_radius=5)
        pygame.draw.rect(self.screen, (80, 80, 80), slider_rect, 2, border_radius=5)
        
        # Draw slider value with glow
        sensitivity_value = self.settings['mouse_sensitivity'] / 0.2
        value_x = slider_x + int(sensitivity_value * self.slider_width)
        pygame.draw.circle(self.screen, (255, 255, 255), (value_x, slider_y + self.slider_height // 2), 10)
        pygame.draw.circle(self.screen, (100, 150, 255), (value_x, slider_y + self.slider_height // 2), 8)
        
        # Draw audio volume setting
        volume_text = f"Audio Volume: {int(self.settings['audio_volume'] * 100)}%"
        volume_text_rect = pygame.Rect(0, button_y + 120, self.screen_width, 50)
        draw_centered_text(self.screen, volume_text, volume_text_rect, 24, self.text_color)
        
        # Draw enhanced volume slider
        volume_slider_y = button_y + 180
        volume_slider_rect = pygame.Rect(slider_x, volume_slider_y, self.slider_width, self.slider_height)
        
        # Slider background with gradient
        pygame.draw.rect(self.screen, (50, 50, 50), volume_slider_rect, border_radius=5)
        pygame.draw.rect(self.screen, (80, 80, 80), volume_slider_rect, 2, border_radius=5)
        
        # Draw volume slider value with glow
        volume_value_x = slider_x + int(self.settings['audio_volume'] * self.slider_width)
        pygame.draw.circle(self.screen, (255, 255, 255), (volume_value_x, volume_slider_y + self.slider_height // 2), 10)
        pygame.draw.circle(self.screen, (255, 100, 100), (volume_value_x, volume_slider_y + self.slider_height // 2), 8)
        
        # Draw graphics setting
        graphics_text = f"Graphics Quality: {self.graphics_options[self.selected_graphics]}"
        graphics_text_rect = pygame.Rect(0, button_y + 240, self.screen_width, 50)
        draw_centered_text(self.screen, graphics_text, graphics_text_rect, 24, self.text_color)
        
        # Graphics options buttons
        graphics_button_y = button_y + 300
        graphics_button_width = 120
        graphics_button_height = 40
        graphics_button_margin = 20
        
        for i, option in enumerate(self.graphics_options):
            button_rect = create_button_rect(
                (self.screen_width - len(self.graphics_options) * (graphics_button_width + graphics_button_margin)) // 2 + i * (graphics_button_width + graphics_button_margin),
                graphics_button_y,
                graphics_button_width,
                graphics_button_height
            )
            
            # Check if selected
            is_selected = i == self.selected_graphics
            color = self.button_selected_color if is_selected else self.button_color
            
            # Draw button with rounded corners
            pygame.draw.rect(self.screen, color, button_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.text_color, button_rect, 2, border_radius=8)
            draw_centered_text(self.screen, option, button_rect, 20, self.text_color)
        
        # Draw back button with animation
        back_button_rect = create_button_rect(
            (self.screen_width - self.button_width) // 2,
            button_y + 360,
            self.button_width,
            self.button_height
        )
        
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = is_point_in_rect(mouse_pos, back_button_rect)
        self.draw_animated_button(self.screen, "Back", back_button_rect, is_hovered, False, self.button_color)
    
    def render_host_selection(self):
        """Render the host selection menu."""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        title_rect = pygame.Rect(0, 100, self.screen_width, 100)
        draw_centered_text(self.screen, "SELECT HOST", title_rect, 48, self.title_color)
        
        # Draw host options
        button_y = self.screen_height // 2 - 100
        for i, host in enumerate(self.hosts):
            button_rect = create_button_rect(
                (self.screen_width - self.button_width) // 2,
                button_y + i * (self.button_height + self.button_margin),
                self.button_width,
                self.button_height
            )
            
            # Choose button color
            if i == self.selected_host:
                color = self.button_selected_color
            else:
                color = self.button_color
                
            # Draw button
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, self.text_color, button_rect, 2)
            
            # Draw text
            draw_centered_text(self.screen, host, button_rect, 24, self.text_color)
        
        # Draw back button
        back_button_rect = create_button_rect(
            (self.screen_width - self.button_width) // 2,
            button_y + len(self.hosts) * (self.button_height + self.button_margin),
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(self.screen, self.button_color, back_button_rect)
        pygame.draw.rect(self.screen, self.text_color, back_button_rect, 2)
        draw_centered_text(self.screen, "Back", back_button_rect, 32, self.text_color)