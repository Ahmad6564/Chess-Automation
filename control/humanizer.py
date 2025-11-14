"""
Humanizer module - adds human-like behavior to chess moves.
"""

import random
import time
from typing import Tuple


class Humanizer:
    """Adds human-like delays and randomization to chess moves."""
    
    def __init__(self, 
                 min_delay: float = 1.0,
                 max_delay: float = 3.5,
                 jitter_pixels: int = 3,
                 hover_probability: float = 0.3):
        """
        Initialize humanizer.
        
        Args:
            min_delay: Minimum delay before move (seconds)
            max_delay: Maximum delay before move (seconds)
            jitter_pixels: Maximum pixel jitter to add to coordinates
            hover_probability: Probability of hovering before clicking (0-1)
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.jitter_pixels = jitter_pixels
        self.hover_probability = hover_probability
        
        # Movement duration ranges
        self.min_move_duration = 0.3
        self.max_move_duration = 0.7
        
    def pre_move_delay(self):
        """Add a delay before making a move (thinking time)."""
        delay = self.random_delay(self.min_delay, self.max_delay)
        print(f"Thinking... ({delay:.2f}s)")
        time.sleep(delay)
    
    def post_move_delay(self):
        """Add a small delay after making a move."""
        delay = self.random_delay(0.1, 0.5)
        time.sleep(delay)
    
    def random_delay(self, min_time: float, max_time: float) -> float:
        """
        Generate a random delay with slight variance.
        
        Args:
            min_time: Minimum delay
            max_time: Maximum delay
        
        Returns:
            Random delay time
        """
        # Use triangular distribution for more natural variation
        # (more likely to be in the middle range)
        mode = (min_time + max_time) / 2
        return random.triangular(min_time, max_time, mode)
    
    def add_pixel_jitter(self, x: int, y: int) -> Tuple[int, int]:
        """
        Add small random jitter to pixel coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            Tuple of jittered (x, y) coordinates
        """
        jitter_x = random.randint(-self.jitter_pixels, self.jitter_pixels)
        jitter_y = random.randint(-self.jitter_pixels, self.jitter_pixels)
        
        return x + jitter_x, y + jitter_y
    
    def get_move_duration(self) -> float:
        """
        Get a randomized mouse movement duration.
        
        Returns:
            Movement duration in seconds
        """
        return self.random_delay(self.min_move_duration, self.max_move_duration)
    
    def should_hover(self) -> bool:
        """
        Determine if the cursor should hover before clicking.
        
        Returns:
            True if should hover
        """
        return random.random() < self.hover_probability
    
    def occasional_pause(self, probability: float = 0.1):
        """
        Occasionally add a longer pause (simulating distraction).
        
        Args:
            probability: Probability of pausing (0-1)
        """
        if random.random() < probability:
            pause_time = self.random_delay(0.5, 2.0)
            print(f"Brief pause... ({pause_time:.2f}s)")
            time.sleep(pause_time)
    
    def vary_thinking_time(self, position_complexity: float = 0.5) -> float:
        """
        Vary thinking time based on position complexity.
        
        Args:
            position_complexity: Complexity factor 0-1 (0=simple, 1=complex)
        
        Returns:
            Adjusted thinking time
        """
        # More complex positions get more thinking time
        base_time = self.random_delay(self.min_delay, self.max_delay)
        complexity_factor = 1.0 + (position_complexity * 2.0)  # 1x to 3x multiplier
        
        return base_time * complexity_factor
    
    def simulate_mouse_drift(self) -> Tuple[int, int]:
        """
        Generate small random drift coordinates (simulating imperfect mouse control).
        
        Returns:
            Tuple of (dx, dy) drift values
        """
        drift_x = random.gauss(0, self.jitter_pixels / 2)
        drift_y = random.gauss(0, self.jitter_pixels / 2)
        
        return int(drift_x), int(drift_y)
    
    def set_delay_range(self, min_delay: float, max_delay: float):
        """
        Update the delay range.
        
        Args:
            min_delay: New minimum delay
            max_delay: New maximum delay
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
    
    def set_skill_level(self, skill_level: int):
        """
        Adjust humanizer settings based on skill level.
        Higher skill = faster, more precise movements.
        
        Args:
            skill_level: Skill level 1-10
        """
        if skill_level < 1:
            skill_level = 1
        if skill_level > 10:
            skill_level = 10
        
        # Adjust delays (lower skill = slower thinking)
        self.min_delay = 3.0 - (skill_level * 0.2)  # 2.8s to 1.0s
        self.max_delay = 6.0 - (skill_level * 0.3)  # 5.7s to 3.0s
        
        # Adjust jitter (lower skill = less precise)
        self.jitter_pixels = 8 - skill_level  # 7 to -2 (clamp at 1)
        self.jitter_pixels = max(1, self.jitter_pixels)
        
        print(f"Skill level set to {skill_level}")
        print(f"Delays: {self.min_delay:.1f}s - {self.max_delay:.1f}s")
        print(f"Jitter: {self.jitter_pixels}px")


def add_human_delay(min_time: float = 1.0, max_time: float = 3.5):
    """
    Convenience function to add a human-like delay.
    
    Args:
        min_time: Minimum delay
        max_time: Maximum delay
    """
    humanizer = Humanizer(min_time, max_time)
    humanizer.pre_move_delay()


if __name__ == "__main__":
    # Test humanizer
    print("Testing humanizer...")
    
    humanizer = Humanizer()
    
    # Test delays
    print("Testing thinking delay...")
    humanizer.pre_move_delay()
    
    # Test jitter
    original_coords = (500, 500)
    jittered = humanizer.add_pixel_jitter(*original_coords)
    print(f"Original: {original_coords}, Jittered: {jittered}")
    
    # Test skill levels
    for skill in [1, 5, 10]:
        print(f"\n--- Skill Level {skill} ---")
        humanizer.set_skill_level(skill)
        humanizer.pre_move_delay()
