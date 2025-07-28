#!/usr/bin/env python3
"""
Test script for the FPS Bluetooth Game.
This script tests the basic components to ensure everything is working.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        import pygame
        print("✅ Pygame imported successfully")
    except ImportError as e:
        print(f"❌ Pygame import failed: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        from utils import load_settings, save_settings
        print("✅ Utils module imported successfully")
    except ImportError as e:
        print(f"❌ Utils import failed: {e}")
        return False
    
    try:
        from player import Player
        print("✅ Player module imported successfully")
    except ImportError as e:
        print(f"❌ Player import failed: {e}")
        return False
    
    try:
        from weapon import WeaponManager
        print("✅ Weapon module imported successfully")
    except ImportError as e:
        print(f"❌ Weapon import failed: {e}")
        return False
    
    try:
        from bluetooth_manager import BluetoothManager
        print("✅ Bluetooth manager imported successfully")
    except ImportError as e:
        print(f"❌ Bluetooth manager import failed: {e}")
        return False
    
    try:
        from menu import Menu
        print("✅ Menu module imported successfully")
    except ImportError as e:
        print(f"❌ Menu import failed: {e}")
        return False
    
    try:
        from game_manager import GameManager
        print("✅ Game manager imported successfully")
    except ImportError as e:
        print(f"❌ Game manager import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic game functionality."""
    print("\nTesting basic functionality...")
    
    try:
        # Test settings
        from utils import load_settings
        settings = load_settings()
        print("✅ Settings loaded successfully")
        
        # Test player creation
        from player import Player
        player = Player(5, 5)
        print("✅ Player created successfully")
        
        # Test weapon manager
        from weapon import WeaponManager
        weapon_manager = WeaponManager()
        print("✅ Weapon manager created successfully")
        
        # Test bluetooth manager
        from bluetooth_manager import BluetoothManager
        bt_manager = BluetoothManager()
        print("✅ Bluetooth manager created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_pygame_initialization():
    """Test Pygame initialization."""
    print("\nTesting Pygame initialization...")
    
    try:
        import pygame
        pygame.init()
        print("✅ Pygame initialized successfully")
        
        # Create a small test window
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("FPS Game Test")
        print("✅ Test window created successfully")
        
        # Clean up
        pygame.quit()
        print("✅ Pygame cleaned up successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Pygame initialization failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=== FPS Bluetooth Game Test Suite ===\n")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check your installation.")
        return False
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality tests failed.")
        return False
    
    # Test Pygame
    if not test_pygame_initialization():
        print("\n❌ Pygame tests failed.")
        return False
    
    print("\n🎉 All tests passed! The game should be ready to run.")
    print("\nTo run the game:")
    print("python src/main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 