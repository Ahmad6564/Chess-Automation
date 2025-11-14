"""
Move executor - physically executes chess moves via mouse automation.
"""

import pyautogui
import time
from typing import Tuple, Dict, Optional
from .mapping_utils import SquareMapper
from .humanizer import Humanizer


class MoveExecutor:
    """Executes chess moves using mouse automation."""
    
    def __init__(self, 
                 board_bbox: Dict[str, int],
                 orientation: str = 'white',
                 use_humanizer: bool = True):
        """
        Initialize move executor.
        
        Args:
            board_bbox: Board bounding box dictionary
            orientation: Board orientation ('white' or 'black')
            use_humanizer: Whether to use human-like behavior
        """
        self.mapper = SquareMapper(board_bbox, orientation)
        self.humanizer = Humanizer() if use_humanizer else None
        
        # PyAutoGUI settings
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    
    def execute_move(self, move_uci: str, drag: bool = True) -> bool:
        """
        Execute a chess move.
        
        Args:
            move_uci: Move in UCI format (e.g., 'e2e4')
            drag: If True, drag piece; if False, click from and to
        
        Returns:
            True if execution succeeded
        """
        try:
            # Get coordinates
            from_coords, to_coords = self.mapper.get_move_coordinates(move_uci)
            
            print(f"Executing move: {move_uci}")
            print(f"From {from_coords} to {to_coords}")
            
            # Add pre-move delay
            if self.humanizer:
                self.humanizer.pre_move_delay()
            
            if drag:
                self._drag_piece(from_coords, to_coords)
            else:
                self._click_move(from_coords, to_coords)
            
            # Add post-move delay
            if self.humanizer:
                self.humanizer.post_move_delay()
            
            print(f"Move {move_uci} executed successfully")
            return True
            
        except Exception as e:
            print(f"Error executing move: {e}")
            return False
    
    def _drag_piece(self, from_coords: Tuple[int, int], to_coords: Tuple[int, int]):
        """
        Drag a piece from one square to another.
        
        Args:
            from_coords: Starting (x, y) coordinates
            to_coords: Ending (x, y) coordinates
        """
        from_x, from_y = from_coords
        to_x, to_y = to_coords
        
        # Add humanizer jitter if enabled
        if self.humanizer:
            from_x, from_y = self.humanizer.add_pixel_jitter(from_x, from_y)
            to_x, to_y = self.humanizer.add_pixel_jitter(to_x, to_y)
        
        # Move to starting position with human-like curve
        duration = self.humanizer.get_move_duration() if self.humanizer else 0.3
        
        # Optional: hover before clicking
        if self.humanizer and self.humanizer.should_hover():
            hover_x = from_x + pyautogui.random.randint(-20, 20)
            hover_y = from_y + pyautogui.random.randint(-20, 20)
            pyautogui.moveTo(hover_x, hover_y, duration=duration * 0.5)
            time.sleep(0.1)
        
        # Move to piece
        pyautogui.moveTo(from_x, from_y, duration=duration)
        time.sleep(0.05)
        
        # Drag to destination
        pyautogui.drag(to_x - from_x, to_y - from_y, 
                      duration=duration * 1.2, 
                      button='left')
        
        time.sleep(0.1)
    
    def _click_move(self, from_coords: Tuple[int, int], to_coords: Tuple[int, int]):
        """
        Execute move by clicking from square then to square.
        
        Args:
            from_coords: Starting (x, y) coordinates
            to_coords: Ending (x, y) coordinates
        """
        from_x, from_y = from_coords
        to_x, to_y = to_coords
        
        # Add humanizer jitter if enabled
        if self.humanizer:
            from_x, from_y = self.humanizer.add_pixel_jitter(from_x, from_y)
            to_x, to_y = self.humanizer.add_pixel_jitter(to_x, to_y)
        
        duration = self.humanizer.get_move_duration() if self.humanizer else 0.3
        
        # Click source square
        pyautogui.moveTo(from_x, from_y, duration=duration)
        time.sleep(0.05)
        pyautogui.click()
        
        # Small delay
        time.sleep(0.1 + (self.humanizer.random_delay(0.05, 0.15) if self.humanizer else 0))
        
        # Click destination square
        pyautogui.moveTo(to_x, to_y, duration=duration)
        time.sleep(0.05)
        pyautogui.click()
        
        time.sleep(0.1)
    
    def click_square(self, square: str):
        """
        Click on a specific square.
        
        Args:
            square: Chess square notation (e.g., 'e4')
        """
        x, y = self.mapper.square_to_pixels(square)
        
        if self.humanizer:
            x, y = self.humanizer.add_pixel_jitter(x, y)
            duration = self.humanizer.get_move_duration()
        else:
            duration = 0.3
        
        pyautogui.moveTo(x, y, duration=duration)
        time.sleep(0.05)
        pyautogui.click()
    
    def verify_move_visual(self, move_uci: str, 
                          capture_func=None,
                          compare_func=None) -> bool:
        """
        Verify that a move was executed correctly (placeholder).
        
        Args:
            move_uci: Move that was executed
            capture_func: Function to capture current board state
            compare_func: Function to compare before/after states
        
        Returns:
            True if move appears successful
        """
        # This is a placeholder for visual verification
        # In a complete implementation, this would:
        # 1. Capture the board before/after
        # 2. Detect if the piece moved correctly
        # 3. Return success/failure
        
        print("Visual verification not yet implemented")
        return True


def execute_move(move_uci: str, 
                board_bbox: Dict[str, int],
                orientation: str = 'white',
                drag: bool = True) -> bool:
    """
    Convenience function to execute a move.
    
    Args:
        move_uci: Move in UCI format
        board_bbox: Board bounding box
        orientation: Board orientation
        drag: Whether to drag or click
    
    Returns:
        True if successful
    """
    executor = MoveExecutor(board_bbox, orientation)
    return executor.execute_move(move_uci, drag)


if __name__ == "__main__":
    # Test move executor
    print("Testing move executor...")
    print("WARNING: This will move your mouse!")
    print("Move mouse to top-left corner to abort")
    
    time.sleep(3)
    
    # Example board
    test_bbox = {
        'left': 100,
        'top': 100,
        'width': 800,
        'height': 800
    }
    
    executor = MoveExecutor(test_bbox, orientation='white')
    
    # Test move (will move mouse but won't affect anything without a chess board)
    # executor.execute_move('e2e4', drag=True)
    print("Test complete (execution commented out for safety)")
