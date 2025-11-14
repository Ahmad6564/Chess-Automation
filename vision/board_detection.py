"""
Board detection module for identifying and cropping the chessboard region.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Dict
from PIL import Image


class BoardDetector:
    """Detects and crops the chessboard from an image."""
    
    def __init__(self, target_size: Tuple[int, int] = (512, 512)):
        """
        Initialize board detector.
        
        Args:
            target_size: Target size to resize the board to (width, height)
        """
        self.target_size = target_size
        
    def detect_board_edges(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect board edges using edge detection and contour finding.
        
        Args:
            image: Input image as numpy array
        
        Returns:
            Coordinates of board corners or None if not found
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find the largest square/rectangular contour
        max_area = 0
        best_contour = None
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > max_area and area > 10000:  # Minimum area threshold
                # Approximate the contour
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                
                # Check if it's roughly square (4 corners)
                if len(approx) == 4:
                    max_area = area
                    best_contour = approx
        
        return best_contour
    
    def crop_board(self, image: np.ndarray, corners: Optional[np.ndarray] = None,
                   bbox: Optional[Dict] = None) -> np.ndarray:
        """
        Crop the board from the image.
        
        Args:
            image: Input image
            corners: Corner coordinates (4 points) if detected
            bbox: Bounding box dict with 'left', 'top', 'width', 'height'
        
        Returns:
            Cropped board image
        """
        if bbox is not None:
            # Use provided bounding box
            x, y, w, h = bbox['left'], bbox['top'], bbox['width'], bbox['height']
            cropped = image[y:y+h, x:x+w]
        elif corners is not None:
            # Use detected corners for perspective transform
            corners = corners.reshape(4, 2)
            
            # Order points: top-left, top-right, bottom-right, bottom-left
            rect = self._order_points(corners)
            
            # Perform perspective transform
            cropped = self._four_point_transform(image, rect)
        else:
            # Return original if no cropping info
            cropped = image
        
        return cropped
    
    def _order_points(self, pts: np.ndarray) -> np.ndarray:
        """Order points in clockwise order starting from top-left."""
        rect = np.zeros((4, 2), dtype=np.float32)
        
        # Sum and diff to find corners
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # Top-left
        rect[2] = pts[np.argmax(s)]  # Bottom-right
        
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # Top-right
        rect[3] = pts[np.argmax(diff)]  # Bottom-left
        
        return rect
    
    def _four_point_transform(self, image: np.ndarray, rect: np.ndarray) -> np.ndarray:
        """Apply perspective transform to get top-down view."""
        (tl, tr, br, bl) = rect
        
        # Compute width
        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = max(int(widthA), int(widthB))
        
        # Compute height
        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = max(int(heightA), int(heightB))
        
        # Destination points
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype=np.float32)
        
        # Compute perspective transform matrix
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        
        return warped
    
    def normalize_board(self, board_image: np.ndarray) -> np.ndarray:
        """
        Normalize board image to target size.
        
        Args:
            board_image: Cropped board image
        
        Returns:
            Normalized board image
        """
        # Resize to target size
        resized = cv2.resize(board_image, self.target_size, interpolation=cv2.INTER_LINEAR)
        return resized
    
    def process_board(self, image: np.ndarray, bbox: Optional[Dict] = None) -> np.ndarray:
        """
        Complete pipeline: detect, crop, and normalize board.
        
        Args:
            image: Input image
            bbox: Optional bounding box
        
        Returns:
            Processed board image ready for model input
        """
        if bbox is None:
            # Try to detect board automatically
            corners = self.detect_board_edges(image)
            cropped = self.crop_board(image, corners=corners)
        else:
            cropped = self.crop_board(image, bbox=bbox)
        
        # Normalize size
        normalized = self.normalize_board(cropped)
        
        return normalized


def detect_board(image: np.ndarray, bbox: Optional[Dict] = None) -> np.ndarray:
    """
    Convenience function to detect and process board.
    
    Args:
        image: Input image
        bbox: Optional bounding box
    
    Returns:
        Processed board image
    """
    detector = BoardDetector()
    return detector.process_board(image, bbox)


def crop_board(image: np.ndarray, bbox: Dict) -> np.ndarray:
    """
    Crop board using bounding box.
    
    Args:
        image: Input image
        bbox: Bounding box dictionary
    
    Returns:
        Cropped board image
    """
    detector = BoardDetector()
    return detector.crop_board(image, bbox=bbox)


if __name__ == "__main__":
    # Test board detection
    print("Testing board detection...")
    test_image = np.zeros((800, 800, 3), dtype=np.uint8)
    detector = BoardDetector()
    processed = detector.normalize_board(test_image)
    print(f"Processed board shape: {processed.shape}")
