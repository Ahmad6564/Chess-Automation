"""
Mapping utilities for converting chess squares to pixel coordinates.
"""

from typing import Tuple, Dict, Optional


class SquareMapper:
    """Maps chess board squares to pixel coordinates."""
    
    def __init__(self, 
                 board_bbox: Dict[str, int],
                 orientation: str = 'white'):
        """
        Initialize square mapper.
        
        Args:
            board_bbox: Dictionary with 'left', 'top', 'width', 'height'
            orientation: 'white' if white is at bottom, 'black' if black is at bottom
        """
        self.left = board_bbox['left']
        self.top = board_bbox['top']
        self.width = board_bbox['width']
        self.height = board_bbox['height']
        self.orientation = orientation.lower()
        
        # Calculate square dimensions
        self.square_width = self.width / 8
        self.square_height = self.height / 8
    
    def square_to_pixels(self, square: str) -> Tuple[int, int]:
        """
        Convert chess square to pixel coordinates (center of square).
        
        Args:
            square: Chess square notation (e.g., 'e2', 'd4')
        
        Returns:
            Tuple of (x, y) pixel coordinates
        """
        if len(square) != 2:
            raise ValueError(f"Invalid square notation: {square}")
        
        col = square[0].lower()
        row = square[1]
        
        if col not in 'abcdefgh' or row not in '12345678':
            raise ValueError(f"Invalid square notation: {square}")
        
        # Convert to indices
        col_idx = ord(col) - ord('a')  # 0-7
        row_idx = int(row) - 1  # 0-7
        
        # Adjust for orientation
        if self.orientation == 'white':
            # White at bottom: a1 is bottom-left
            pixel_col = col_idx
            pixel_row = 7 - row_idx  # Flip vertically
        else:
            # Black at bottom: a8 is bottom-left
            pixel_col = 7 - col_idx  # Flip horizontally
            pixel_row = row_idx
        
        # Calculate pixel coordinates (center of square)
        x = int(self.left + (pixel_col + 0.5) * self.square_width)
        y = int(self.top + (pixel_row + 0.5) * self.square_height)
        
        return x, y
    
    def get_move_coordinates(self, move_uci: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Get pixel coordinates for a move.
        
        Args:
            move_uci: Move in UCI format (e.g., 'e2e4')
        
        Returns:
            Tuple of ((from_x, from_y), (to_x, to_y))
        """
        if len(move_uci) < 4:
            raise ValueError(f"Invalid move UCI: {move_uci}")
        
        from_square = move_uci[:2]
        to_square = move_uci[2:4]
        
        from_coords = self.square_to_pixels(from_square)
        to_coords = self.square_to_pixels(to_square)
        
        return from_coords, to_coords
    
    def pixels_to_square(self, x: int, y: int) -> str:
        """
        Convert pixel coordinates to chess square.
        
        Args:
            x: X pixel coordinate
            y: Y pixel coordinate
        
        Returns:
            Chess square notation (e.g., 'e4')
        """
        # Calculate which square the pixel is in
        col_idx = int((x - self.left) / self.square_width)
        row_idx = int((y - self.top) / self.square_height)
        
        # Clamp to valid range
        col_idx = max(0, min(7, col_idx))
        row_idx = max(0, min(7, row_idx))
        
        # Adjust for orientation
        if self.orientation == 'white':
            col = chr(ord('a') + col_idx)
            row = str(8 - row_idx)
        else:
            col = chr(ord('a') + (7 - col_idx))
            row = str(row_idx + 1)
        
        return f"{col}{row}"
    
    def get_square_bbox(self, square: str) -> Dict[str, int]:
        """
        Get bounding box for a specific square.
        
        Args:
            square: Chess square notation
        
        Returns:
            Dictionary with 'left', 'top', 'width', 'height'
        """
        center_x, center_y = self.square_to_pixels(square)
        
        left = int(center_x - self.square_width / 2)
        top = int(center_y - self.square_height / 2)
        
        return {
            'left': left,
            'top': top,
            'width': int(self.square_width),
            'height': int(self.square_height)
        }


def get_square_pixels(square: str, 
                     board_bbox: Dict[str, int],
                     orientation: str = 'white') -> Tuple[int, int]:
    """
    Convenience function to get pixel coordinates for a square.
    
    Args:
        square: Chess square notation
        board_bbox: Board bounding box
        orientation: Board orientation
    
    Returns:
        Tuple of (x, y) pixel coordinates
    """
    mapper = SquareMapper(board_bbox, orientation)
    return mapper.square_to_pixels(square)


if __name__ == "__main__":
    # Test square mapper
    print("Testing square mapper...")
    
    # Example board bounding box
    test_bbox = {
        'left': 100,
        'top': 100,
        'width': 800,
        'height': 800
    }
    
    mapper = SquareMapper(test_bbox, orientation='white')
    
    # Test square to pixels
    e2_coords = mapper.square_to_pixels('e2')
    print(f"e2 coordinates: {e2_coords}")
    
    e4_coords = mapper.square_to_pixels('e4')
    print(f"e4 coordinates: {e4_coords}")
    
    # Test move coordinates
    from_coords, to_coords = mapper.get_move_coordinates('e2e4')
    print(f"Move e2e4: {from_coords} -> {to_coords}")
    
    # Test pixels to square
    square = mapper.pixels_to_square(e4_coords[0], e4_coords[1])
    print(f"Pixels {e4_coords} -> square: {square}")
