# FPS Bluetooth Multiplayer Game

A desktop first-person shooter game with Bluetooth-based multiplayer connectivity built in Python using Pygame.

## Features

- **3D FPS Gameplay**: First-person shooter with mouse-look and WASD movement
- **Bluetooth Multiplayer**: Host or join games over Bluetooth
- **Main Menu**: Start, Settings, and Exit options
- **Settings Menu**: Adjust mouse sensitivity and audio volume
- **HUD**: Health bar, ammo count, crosshair, and game timer
- **Collision Detection**: Prevent walking through walls
- **Health System**: Player health decreases when shot

## Installation

1. **Install Python 3.8+** if not already installed
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **For Windows users**: You may need to install PyBluez manually:
   ```bash
   pip install pybluez
   ```

## How to Run

1. **Navigate to the project directory**:
   ```bash
   cd fps_bluetooth_game
   ```

2. **Run the game**:
   ```bash
   python src/main.py
   ```

## Controls

- **WASD**: Move forward, left, backward, right
- **Space**: Jump
- **Mouse**: Look around
- **Left Click**: Shoot
- **ESC**: Pause/Return to menu

## Multiplayer Setup

### Hosting a Game
1. Select "Start Game" from the main menu
2. Choose "Host Game"
3. Wait for other players to join

### Joining a Game
1. Select "Start Game" from the main menu
2. Choose "Join Game"
3. Select an available host from the list

## Project Structure

```
fps_bluetooth_game/
│
├── assets/               # Textures, sounds, and game assets
│   ├── textures/        # Wall textures and UI elements
│   ├── sounds/          # Sound effects and music
│   └── maps/           # Game map data
│
├── src/
│   ├── main.py           # Entry point: menu + game loop
│   ├── player.py         # Player movement, health, shooting
│   ├── weapon.py         # Shooting mechanics, bullets
│   ├── bluetooth_manager.py # Bluetooth host/join logic
│   ├── game_manager.py   # Controls game states (menu, play, game over)
│   ├── menu.py           # Start menu and settings
│   └── utils.py          # Helper functions
│
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── LICENSE              # Project license
```

## Game Features

### Main Menu
- Start Game (Host or Join via Bluetooth)
- Settings (audio, mouse sensitivity)
- Exit Game

### FPS Gameplay
- 3D environment with raycasting engine
- Player movement and collision detection
- Shooting mechanics with bullet physics
- Health and ammo systems
- Real-time multiplayer synchronization

### Settings
- Mouse sensitivity adjustment
- Audio volume control
- Settings persistence (saved to settings.json)

## Troubleshooting

### Bluetooth Issues
- Ensure Bluetooth is enabled on your device
- Make sure devices are paired before starting the game
- Check firewall settings for Bluetooth connections

### Performance Issues
- Lower mouse sensitivity in settings
- Close other applications to free up resources
- Update graphics drivers

## Development

This project uses:
- **Pygame**: Graphics, input, and main game loop
- **PyBluez**: Bluetooth communication for multiplayer
- **PyOpenGL**: 3D rendering (optional)
- **NumPy**: Mathematical operations for 3D calculations

## License

This project is licensed under the MIT License - see the LICENSE file for details. 