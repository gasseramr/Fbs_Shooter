#!/usr/bin/env python3
"""
Bluetooth manager for the FPS Bluetooth Game.
Handles multiplayer connectivity, host/join functionality, and data synchronization.
"""

import json
import threading
import time
from typing import Dict, List, Any, Optional, Tuple
from player import Player

try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    print("Warning: PyBluez not available. Multiplayer will be disabled.")
    BLUETOOTH_AVAILABLE = False

class BluetoothManager:
    """Manages Bluetooth connections for multiplayer."""
    
    def __init__(self):
        """Initialize Bluetooth manager."""
        self.is_host = False
        self.is_client = False
        self.connected = False
        
        # Host properties
        self.host_socket = None
        self.client_sockets = []
        self.host_thread = None
        self.running = False
        
        # Client properties
        self.client_socket = None
        self.client_thread = None
        
        # Game data
        self.players = {}
        self.local_player_id = "player1"
        self.game_data = {}
        
        # Network settings
        self.port = 1
        self.buffer_size = 1024
        self.update_rate = 60  # Hz
        
        # Message types
        self.MSG_PLAYER_UPDATE = "player_update"
        self.MSG_PLAYER_JOIN = "player_join"
        self.MSG_PLAYER_LEAVE = "player_leave"
        self.MSG_SHOT_FIRED = "shot_fired"
        self.MSG_PLAYER_HIT = "player_hit"
        self.MSG_GAME_STATE = "game_state"
        
    def start_hosting(self) -> bool:
        """Start hosting a multiplayer game."""
        if not BLUETOOTH_AVAILABLE:
            print("Bluetooth not available")
            return False
            
        try:
            # Create server socket
            self.host_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.host_socket.bind(("", self.port))
            self.host_socket.listen(1)
            
            self.is_host = True
            self.running = True
            
            # Start host thread
            self.host_thread = threading.Thread(target=self._host_loop)
            self.host_thread.daemon = True
            self.host_thread.start()
            
            print(f"Hosting game on port {self.port}")
            return True
            
        except Exception as e:
            print(f"Error starting host: {e}")
            return False
    
    def _host_loop(self):
        """Main loop for hosting."""
        while self.running:
            try:
                # Accept new connections
                client_socket, address = self.host_socket.accept()
                print(f"Client connected: {address}")
                
                # Add client to list
                self.client_sockets.append(client_socket)
                
                # Start client handler thread
                client_thread = threading.Thread(
                    target=self._handle_client, 
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Host error: {e}")
                break
    
    def _handle_client(self, client_socket, address):
        """Handle individual client connection."""
        try:
            while self.running:
                # Receive data from client
                data = client_socket.recv(self.buffer_size)
                if not data:
                    break
                
                # Parse message
                message = json.loads(data.decode('utf-8'))
                self._process_message(message, client_socket)
                
        except Exception as e:
            print(f"Client handler error: {e}")
        finally:
            # Remove client
            if client_socket in self.client_sockets:
                self.client_sockets.remove(client_socket)
            client_socket.close()
            print(f"Client disconnected: {address}")
    
    def discover_hosts(self) -> List[str]:
        """Discover available hosts."""
        if not BLUETOOTH_AVAILABLE:
            return []
            
        hosts = []
        try:
            nearby_devices = bluetooth.discover_devices(lookup_names=True)
            for addr, name in nearby_devices:
                if "FPS_Game" in name or "FPS" in name:
                    hosts.append(f"{name} ({addr})")
        except Exception as e:
            print(f"Error discovering hosts: {e}")
        
        return hosts
    
    def join_game(self, host_info: str) -> bool:
        """Join a hosted game."""
        if not BLUETOOTH_AVAILABLE:
            print("Bluetooth not available")
            return False
            
        try:
            # Extract address from host info
            addr = host_info.split("(")[-1].split(")")[0]
            
            # Connect to host
            self.client_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.client_socket.connect((addr, self.port))
            
            self.is_client = True
            self.connected = True
            
            # Start client thread
            self.client_thread = threading.Thread(target=self._client_loop)
            self.client_thread.daemon = True
            self.client_thread.start()
            
            print(f"Connected to host: {host_info}")
            return True
            
        except Exception as e:
            print(f"Error joining game: {e}")
            return False
    
    def _client_loop(self):
        """Main loop for client."""
        try:
            while self.connected:
                # Receive data from host
                data = self.client_socket.recv(self.buffer_size)
                if not data:
                    break
                
                # Parse message
                message = json.loads(data.decode('utf-8'))
                self._process_message(message)
                
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            self.connected = False
            if self.client_socket:
                self.client_socket.close()
    
    def _process_message(self, message: Dict[str, Any], sender_socket=None):
        """Process incoming network message."""
        msg_type = message.get("type")
        
        if msg_type == self.MSG_PLAYER_UPDATE:
            self._handle_player_update(message)
        elif msg_type == self.MSG_PLAYER_JOIN:
            self._handle_player_join(message)
        elif msg_type == self.MSG_PLAYER_LEAVE:
            self._handle_player_leave(message)
        elif msg_type == self.MSG_SHOT_FIRED:
            self._handle_shot_fired(message)
        elif msg_type == self.MSG_PLAYER_HIT:
            self._handle_player_hit(message)
        elif msg_type == self.MSG_GAME_STATE:
            self._handle_game_state(message)
    
    def _handle_player_update(self, message: Dict[str, Any]):
        """Handle player position/state update."""
        player_id = message.get("player_id")
        player_data = message.get("data", {})
        
        if player_id != self.local_player_id:
            # Update remote player
            if player_id not in self.players:
                self.players[player_id] = Player(0, 0, player_id)
            
            self.players[player_id].set_state_from_dict(player_data)
    
    def _handle_player_join(self, message: Dict[str, Any]):
        """Handle new player joining."""
        player_id = message.get("player_id")
        if player_id not in self.players:
            self.players[player_id] = Player(0, 0, player_id)
    
    def _handle_player_leave(self, message: Dict[str, Any]):
        """Handle player leaving."""
        player_id = message.get("player_id")
        if player_id in self.players:
            del self.players[player_id]
    
    def _handle_shot_fired(self, message: Dict[str, Any]):
        """Handle shot fired by another player."""
        # This would be handled by the game manager
        pass
    
    def _handle_player_hit(self, message: Dict[str, Any]):
        """Handle player being hit."""
        # This would be handled by the game manager
        pass
    
    def _handle_game_state(self, message: Dict[str, Any]):
        """Handle game state update."""
        self.game_data = message.get("data", {})
    
    def send_message(self, message: Dict[str, Any]):
        """Send message to connected peers."""
        if not self.connected and not self.is_host:
            return
        
        try:
            data = json.dumps(message).encode('utf-8')
            
            if self.is_host:
                # Send to all clients
                for client_socket in self.client_sockets:
                    try:
                        client_socket.send(data)
                    except:
                        pass
            elif self.is_client and self.client_socket:
                # Send to host
                self.client_socket.send(data)
                
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def send_player_update(self, player: Player):
        """Send player state update."""
        message = {
            "type": self.MSG_PLAYER_UPDATE,
            "player_id": player.player_id,
            "data": player.get_state_dict()
        }
        self.send_message(message)
    
    def send_shot_fired(self, x: float, y: float, z: float, direction: float, weapon: str):
        """Send shot fired event."""
        message = {
            "type": self.MSG_SHOT_FIRED,
            "player_id": self.local_player_id,
            "x": x,
            "y": y,
            "z": z,
            "direction": direction,
            "weapon": weapon
        }
        self.send_message(message)
    
    def send_player_hit(self, target_id: str, damage: int):
        """Send player hit event."""
        message = {
            "type": self.MSG_PLAYER_HIT,
            "attacker_id": self.local_player_id,
            "target_id": target_id,
            "damage": damage
        }
        self.send_message(message)
    
    def get_remote_players(self) -> List[Player]:
        """Get list of remote players."""
        return list(self.players.values())
    
    def is_connected(self) -> bool:
        """Check if connected to multiplayer."""
        return self.connected or self.is_host
    
    def get_connection_status(self) -> str:
        """Get connection status string."""
        if self.is_host:
            return f"Hosting ({len(self.client_sockets)} clients)"
        elif self.is_client and self.connected:
            return "Connected"
        else:
            return "Disconnected"
    
    def cleanup(self):
        """Clean up Bluetooth connections."""
        self.running = False
        self.connected = False
        
        # Close host socket
        if self.host_socket:
            self.host_socket.close()
            self.host_socket = None
        
        # Close client sockets
        for client_socket in self.client_sockets:
            try:
                client_socket.close()
            except:
                pass
        self.client_sockets.clear()
        
        # Close client socket
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        
        # Wait for threads to finish
        if self.host_thread and self.host_thread.is_alive():
            self.host_thread.join(timeout=1.0)
        
        if self.client_thread and self.client_thread.is_alive():
            self.client_thread.join(timeout=1.0)
        
        print("Bluetooth manager cleaned up")

# Fallback class when Bluetooth is not available
class MockBluetoothManager:
    """Mock Bluetooth manager for when PyBluez is not available."""
    
    def __init__(self):
        self.is_host = False
        self.is_client = False
        self.connected = False
        self.players = {}
        self.local_player_id = "player1"
        self.game_data = {}
    
    def start_hosting(self) -> bool:
        print("Bluetooth not available - cannot host")
        return False
    
    def discover_hosts(self) -> List[str]:
        print("Bluetooth not available - cannot discover hosts")
        return []
    
    def join_game(self, host_info: str) -> bool:
        print("Bluetooth not available - cannot join game")
        return False
    
    def send_message(self, message: Dict[str, Any]):
        pass
    
    def send_player_update(self, player: Player):
        pass
    
    def send_shot_fired(self, x: float, y: float, z: float, direction: float, weapon: str):
        pass
    
    def send_player_hit(self, target_id: str, damage: int):
        pass
    
    def get_remote_players(self) -> List[Player]:
        return []
    
    def is_connected(self) -> bool:
        return False
    
    def get_connection_status(self) -> str:
        return "Bluetooth not available"
    
    def cleanup(self):
        pass

# Use appropriate manager based on Bluetooth availability
if BLUETOOTH_AVAILABLE:
    BluetoothManager = BluetoothManager
else:
    BluetoothManager = MockBluetoothManager 