"""
Screen capture module for capturing the chessboard from screen or browser.
"""

import mss
import numpy as np
from PIL import Image
from typing import Optional, Tuple, Dict
import yaml
import os


class BoardCapture:
    """Handles screen capture of the chessboard."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the board capture system.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.board_region = self.config.get('board_region', None)
        self.sct = None
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def set_board_region(self, left: int, top: int, width: int, height: int):
        """
        Manually set the board region coordinates.
        
        Args:
            left: X coordinate of top-left corner
            top: Y coordinate of top-left corner
            width: Width of the board region
            height: Height of the board region
        """
        self.board_region = {
            "left": left,
            "top": top,
            "width": width,
            "height": height
        }
        
    def capture_screen(self, region: Optional[Dict] = None) -> np.ndarray:
        """
        Capture the screen or a specific region.
        
        Args:
            region: Dictionary with 'left', 'top', 'width', 'height' keys
                   If None, uses the configured board_region
        
        Returns:
            Numpy array of the captured image (RGB format)
        """
        with mss.mss() as sct:
            if region is None:
                region = self.board_region
            
            if region is None:
                # Capture entire primary monitor
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
            else:
                screenshot = sct.grab(region)
            
            # Convert to numpy array (RGB)
            img = np.array(screenshot)
            # mss returns BGRA, convert to RGB
            img = img[:, :, :3][:, :, ::-1]
            
            return img
    
    def capture_board(self) -> np.ndarray:
        """
        Capture the chessboard using the configured region.
        
        Returns:
            Numpy array of the board image
        """
        return self.capture_screen(self.board_region)
    
    def save_capture(self, image: np.ndarray, filepath: str = "board_capture.png"):
        """
        Save captured image to file.
        
        Args:
            image: Image array to save
            filepath: Path where to save the image
        """
        img_pil = Image.fromarray(image)
        img_pil.save(filepath)
        print(f"Captured board saved to {filepath}")


def capture_board(region: Optional[Dict] = None) -> np.ndarray:
    """
    Convenience function to capture the chessboard.
    
    Args:
        region: Optional region dictionary
    
    Returns:
        Numpy array of captured board
    """
    capturer = BoardCapture()
    return capturer.capture_screen(region)


if __name__ == "__main__":
    # Test the capture functionality
    print("Testing board capture...")
    capturer = BoardCapture()
    
    # Capture and save
    board_img = capturer.capture_board()
    capturer.save_capture(board_img, "test_capture.png")
    print(f"Captured image shape: {board_img.shape}")
