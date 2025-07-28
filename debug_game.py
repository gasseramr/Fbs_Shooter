#!/usr/bin/env python3
"""
Debug script for the FPS Bluetooth Game.
This script helps identify and fix issues with mouse input and button handling.
"""

import pygame
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_mouse_capture():
    """Test mouse capture functionality."""
    print("=== Testing Mouse Capture ===")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Mouse Capture Test")
    clock = pygame.time.Clock()
    
    print("Window created. Testing mouse capture...")
    
    # Test mouse grab
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    print("✅ Mouse grabbed and hidden")
    
    # Test mouse position reset
    pygame.mouse.set_pos(400, 300)
    print("✅ Mouse position reset to center")
    
    # Test mouse movement
    running = True
    frame_count = 0
    
    while running and frame_count < 300:  # Run for 5 seconds at 60 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEMOTION:
                print(f"Mouse movement: {event.rel}")
        
        # Get relative mouse movement
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        if mouse_dx != 0 or mouse_dy != 0:
            print(f"Mouse relative movement: ({mouse_dx}, {mouse_dy})")
        
        screen.fill((0, 0, 0))
        
        # Draw instructions
        font = pygame.font.Font(None, 36)
        text = font.render("Move mouse to test capture", True, (255, 255, 255))
        text_rect = text.get_rect(center=(400, 200))
        screen.blit(text, text_rect)
        
        text2 = font.render("Press ESC to exit", True, (255, 255, 255))
        text_rect2 = text2.get_rect(center=(400, 250))
        screen.blit(text2, text_rect2)
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1
    
    # Release mouse
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    print("✅ Mouse released")
    
    pygame.quit()
    print("Mouse capture test completed!")

def test_button_click():
    """Test button click functionality."""
    print("\n=== Testing Button Click ===")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Button Click Test")
    clock = pygame.time.Clock()
    
    # Create a simple button
    button_rect = pygame.Rect(300, 250, 200, 50)
    button_color = (100, 100, 100)
    button_hover_color = (150, 150, 150)
    
    running = True
    mouse_pos = (0, 0)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if button_rect.collidepoint(event.pos):
                        print("✅ Button clicked!")
                        running = False
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
        
        screen.fill((0, 0, 0))
        
        # Draw button
        color = button_hover_color if button_rect.collidepoint(mouse_pos) else button_color
        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)
        
        # Draw button text
        font = pygame.font.Font(None, 36)
        text = font.render("Click Me!", True, (255, 255, 255))
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)
        
        # Draw instructions
        font2 = pygame.font.Font(None, 24)
        text2 = font2.render("Hover and click the button", True, (255, 255, 255))
        text_rect2 = text2.get_rect(center=(400, 350))
        screen.blit(text2, text_rect2)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("Button click test completed!")

def test_menu_components():
    """Test menu components."""
    print("\n=== Testing Menu Components ===")
    
    try:
        from menu import Menu
        from utils import load_settings
        
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Menu Test")
        
        settings = load_settings()
        menu = Menu(screen, settings)
        
        print("✅ Menu created successfully")
        
        # Test menu rendering
        menu.render()
        print("✅ Menu rendered successfully")
        
        pygame.quit()
        print("Menu component test completed!")
        
    except Exception as e:
        print(f"❌ Menu test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all debug tests."""
    print("=== FPS Game Debug Suite ===\n")
    
    # Test mouse capture
    test_mouse_capture()
    
    # Test button clicks
    test_button_click()
    
    # Test menu components
    test_menu_components()
    
    print("\n🎉 All debug tests completed!")
    print("\nNow try running the main game:")
    print("python src/main.py")

if __name__ == "__main__":
    main() 