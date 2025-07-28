#!/usr/bin/env python3
"""
FPS Bluetooth Multiplayer Game - Main Entry Point
Handles the main game loop, state management, and initialization.
"""

import pygame
import sys
import os
from game_manager import GameManager
from menu import Menu
from bluetooth_manager import BluetoothManager
from utils import load_settings, save_settings

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
GAME_TITLE = "FPS Bluetooth Game"

class Game:
    """Main game class that handles the game loop and state management."""
    
    def __init__(self):
        """Initialize the game with screen, clock, and managers."""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        
        # Load settings
        self.settings = load_settings()
        
        # Initialize managers
        self.game_manager = GameManager(self.screen, self.settings)
        self.menu = Menu(self.screen, self.settings)
        self.bluetooth_manager = BluetoothManager()
        
        # Game state
        self.running = True
        self.current_state = "menu"  # menu, game, settings, multiplayer_options
        
        # Mouse state tracking
        self.mouse_grabbed = False
        
    def handle_events(self):
        """Handle all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
                
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed: {event.key}")
                if event.key == pygame.K_ESCAPE:
                    if self.current_state == "game":
                        self.exit_game_mode()
                    elif self.current_state == "settings":
                        self.current_state = "menu"
                    elif self.current_state == "multiplayer_options":
                        self.current_state = "menu"
                        
            # Handle events based on current state
            if self.current_state == "menu":
                action = self.menu.handle_event(event)
                print(f"Menu action: {action}")
                if action in ("multiplayer_options", "show_multiplayer_options"):
                    self.current_state = "multiplayer_options"
                    print("Switched to multiplayer options")
                elif action == "settings":
                    self.current_state = "settings"
                    print("Switched to settings")
                elif action == "exit":
                    self.running = False
                    
            elif self.current_state == "multiplayer_options":
                action = self.menu.handle_event(event)
                print(f"Multiplayer action: {action}")
                if action == "host_game":
                    print("Starting host game...")
                    self.start_game_mode(True)
                elif action == "join_game":
                    print("Starting join game...")
                    self.start_game_mode(False)
                elif action == "back":
                    self.current_state = "menu"
                    
            elif self.current_state == "settings":
                action = self.menu.handle_settings_event(event)
                print(f"Settings action: {action}")
                if action == "back":
                    self.current_state = "menu"
                    save_settings(self.settings)
                    
            elif self.current_state == "game":
                self.game_manager.handle_event(event)
    
    def start_game_mode(self, is_host: bool):
        """Start the game mode with proper mouse handling."""
        print(f"Starting game mode (host: {is_host})")
        
        # Set game state
        self.current_state = "game"
        
        # Start the game
        if is_host:
            self.game_manager.start_multiplayer_game(True)
        else:
            self.game_manager.start_new_game()
        
        # Grab mouse for FPS controls
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        self.mouse_grabbed = True
        
        # Reset mouse position to center
        pygame.mouse.set_pos(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        print("Game started! Mouse should be captured.")
    
    def exit_game_mode(self):
        """Exit game mode and return to menu."""
        print("Exiting game mode...")
        
        # Release mouse
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        self.mouse_grabbed = False
        
        # Return to menu
        self.current_state = "menu"
        
        print("Returned to menu. Mouse should be visible.")
    
    def update(self):
        """Update game logic based on current state."""
        if self.current_state == "menu":
            self.menu.update()
        elif self.current_state == "multiplayer_options":
            self.menu.update()
        elif self.current_state == "settings":
            self.menu.update_settings()
        elif self.current_state == "game":
            self.game_manager.update()
            
            # Check if game is over
            if self.game_manager.is_game_over():
                self.exit_game_mode()
    
    def render(self):
        """Render the current game state."""
        self.screen.fill((0, 0, 0))  # Clear screen with black
        
        if self.current_state == "menu":
            self.menu.render()
        elif self.current_state == "multiplayer_options":
            self.menu.render()
        elif self.current_state == "settings":
            self.menu.render_settings()
        elif self.current_state == "game":
            self.game_manager.render()
            
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        print("Starting FPS Bluetooth Game...")
        print("Controls: WASD to move, Mouse to look, Left Click to shoot, ESC to pause")
        print("Menu: Use mouse to navigate, or arrow keys + Enter")
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources before exiting."""
        print("Cleaning up...")
        
        # Release mouse if still grabbed
        if self.mouse_grabbed:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        
        self.bluetooth_manager.cleanup()
        save_settings(self.settings)
        pygame.quit()
        sys.exit()

def main():
    """Main entry point for the game."""
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
        pygame.quit()
        sys.exit()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main() 