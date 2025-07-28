# FPS Bluetooth Game - Complete Project Structure

## Project Overview
A desktop first-person shooter game with Bluetooth multiplayer connectivity built in Python using Pygame.

## Complete File Structure

```
fps_bluetooth_game/
│
├── assets/                    # Game assets directory
│   ├── textures/             # Wall textures and UI elements
│   ├── sounds/               # Sound effects and music
│   └── maps/                 # Game map data
│
├── src/                      # Source code directory
│   ├── main.py               # Entry point: menu + game loop
│   ├── player.py             # Player movement, health, shooting
│   ├── weapon.py             # Shooting mechanics, bullets
│   ├── bluetooth_manager.py  # Bluetooth host/join logic
│   ├── game_manager.py       # Controls game states (menu, play, game over)
│   ├── menu.py               # Start menu and settings (Enhanced GUI)
│   └── utils.py              # Helper functions
│
├── requirements.txt           # Python dependencies
├── README.md                 # Project description and setup
├── LICENSE                   # MIT License
└── PROJECT_STRUCTURE.md      # This file
```

## File Descriptions

### Core Files

#### `main.py` - Entry Point
- **Purpose**: Main game loop and state management
- **Features**:
  - Initializes Pygame and game components
  - Handles game states (menu, game, settings)
  - Manages event handling and rendering
  - Coordinates all game managers

#### `player.py` - Player System
- **Purpose**: Player movement, health, and combat mechanics
- **Features**:
  - WASD movement with collision detection
  - Mouse-look rotation
  - Health and armor system
  - Jump mechanics with gravity
  - Network state synchronization

#### `weapon.py` - Weapon System
- **Purpose**: Shooting mechanics and bullet physics
- **Features**:
  - Multiple weapon types (Pistol, Rifle, Shotgun)
  - Bullet physics and collision detection
  - Ammo management
  - Weapon switching (1, 2, 3 keys)
  - Reload mechanics (R key)

#### `bluetooth_manager.py` - Multiplayer System
- **Purpose**: Bluetooth connectivity for multiplayer
- **Features**:
  - Host/Join game functionality
  - Device discovery
  - Real-time data synchronization
  - Fallback for when Bluetooth is unavailable
  - JSON-based message protocol

#### `game_manager.py` - Game Logic
- **Purpose**: Main game controller and 3D rendering
- **Features**:
  - Raycasting 3D engine (Doom-style)
  - Game world management
  - HUD rendering (health, ammo, crosshair)
  - Game over handling
  - Multiplayer coordination

#### `menu.py` - Enhanced GUI System
- **Purpose**: Complete menu system with modern UI
- **Features**:
  - Animated background with particles
  - Glow effects and hover animations
  - Sound effects for interactions
  - Multiplayer options menu
  - Settings with sliders and graphics options
  - Rounded buttons with visual feedback

#### `utils.py` - Utility Functions
- **Purpose**: Helper functions and settings management
- **Features**:
  - Settings loading/saving (JSON)
  - Math utilities (distance, rotation, etc.)
  - Text rendering helpers
  - Image loading with fallbacks
  - Crosshair and health bar creation

### Configuration Files

#### `requirements.txt`
```
pygame==2.5.2
pybluez==0.23
pyopengl==3.1.7
numpy==1.24.3
```

#### `README.md`
- Complete project documentation
- Installation instructions
- Usage guide
- Troubleshooting section

#### `LICENSE`
- MIT License for open source distribution

## Enhanced GUI Features

### Main Menu
- **Animated Background**: Particle effects and gradient
- **Glow Effects**: Title with multiple glow layers
- **Hover Animations**: Buttons scale and glow on hover
- **Sound Effects**: Click and hover sounds
- **Smooth Transitions**: Between menu states

### Settings Menu
- **Enhanced Sliders**: Rounded corners and glow effects
- **Graphics Options**: Low/Medium/High quality settings
- **Real-time Updates**: Settings apply immediately
- **Visual Feedback**: Clear indication of current values

### Multiplayer Menu
- **Host/Join Options**: Clear separation of multiplayer modes
- **Connection Status**: Real-time status display
- **Device Discovery**: Automatic host discovery

## Game Features

### FPS Gameplay
- **3D Raycasting Engine**: Doom-style pseudo-3D rendering
- **WASD Movement**: Smooth player movement
- **Mouse Look**: 360-degree camera rotation
- **Jump Mechanics**: Space bar for jumping
- **Collision Detection**: Prevents walking through walls

### Combat System
- **Multiple Weapons**: Pistol, Rifle, Shotgun
- **Bullet Physics**: Realistic projectile movement
- **Damage System**: Health and armor mechanics
- **Ammo Management**: Limited ammo with reload system

### Multiplayer
- **Bluetooth Connectivity**: Local multiplayer
- **Host/Join System**: Easy game setup
- **Real-time Sync**: Player positions and actions
- **Fallback Mode**: Works without Bluetooth

### HUD Elements
- **Health Bar**: Visual health indicator
- **Ammo Counter**: Current weapon ammo
- **Crosshair**: Aiming assistance
- **Game Timer**: Survival time tracking
- **Connection Status**: Multiplayer status

## Installation and Usage

### Prerequisites
- Python 3.8+
- Windows 10/11 (for Bluetooth support)
- Bluetooth adapter (for multiplayer)

### Installation
```bash
# Clone or download the project
cd fps_bluetooth_game

# Install dependencies
pip install -r requirements.txt

# Run the game
python src/main.py
```

### Controls
- **WASD**: Move
- **Mouse**: Look around
- **Left Click**: Shoot
- **Space**: Jump
- **R**: Reload
- **1/2/3**: Switch weapons
- **ESC**: Pause/Return to menu

## Technical Implementation

### Architecture
- **Modular Design**: Each component is self-contained
- **Event-Driven**: Pygame event system
- **State Management**: Clear game state transitions
- **Network Layer**: Abstracted Bluetooth communication

### Performance
- **60 FPS Target**: Smooth gameplay
- **Optimized Rendering**: Efficient raycasting
- **Memory Management**: Proper resource cleanup
- **Error Handling**: Graceful fallbacks

### Extensibility
- **Easy to Add Weapons**: Weapon class system
- **Map Editor Ready**: Modular map system
- **Sound System**: Extensible audio framework
- **Settings System**: Configurable options

## Future Enhancements
- Texture mapping for walls
- Sound effects and music
- More weapon types
- Different game modes
- Map editor
- Scoreboard system
- Bot AI for single-player

This project provides a complete, playable FPS game with modern GUI and multiplayer capabilities, ready for further development and customization. 