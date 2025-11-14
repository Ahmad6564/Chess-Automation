"""
Piece recognition module using LLaVA vision model.
"""

import torch
import numpy as np
from PIL import Image
from transformers import AutoProcessor, LlavaForConditionalGeneration
from typing import Dict, Optional
import json
import re


class PieceRecognizer:
    """Uses LLaVA model to recognize chess pieces on the board."""
    
    def __init__(self, model_name: str = "llava-hf/llava-v1.6-mistral-7b-hf"):
        """
        Initialize the LLaVA model for piece recognition.
        
        Args:
            model_name: HuggingFace model identifier
                       Options: 
                       - llava-hf/llava-v1.6-mistral-7b-hf (smaller, faster)
                       - llava-hf/llava-v1.6-34b-hf (larger, more accurate)
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading LLaVA model: {model_name} on {self.device}...")
        
        # Load model and processor
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = LlavaForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            low_cpu_mem_usage=True,
            device_map="auto" if self.device == "cuda" else None
        )
        
        if self.device == "cpu":
            self.model = self.model.to(self.device)
        
        print("Model loaded successfully!")
        
    def create_prompt(self) -> str:
        """
        Create the prompt for LLaVA to recognize chess pieces.
        
        Returns:
            Formatted prompt string
        """
        prompt = """USER: <image>
You are analyzing a chess board image. The board has 8 rows (1-8) and 8 columns (a-h).
Please identify all chess pieces and their positions.

For each piece, provide:
- Square location (e.g., e2, d4)
- Piece type (pawn, knight, bishop, rook, queen, king)
- Color (white or black)

Return the information in JSON format like this:
{
  "a1": {"piece": "rook", "color": "white"},
  "b1": {"piece": "knight", "color": "white"},
  "e4": {"piece": "pawn", "color": "black"}
}

Only include squares that have pieces. Use lowercase for all values.
ASSISTANT:"""
        return prompt
    
    def recognize(self, board_image: np.ndarray) -> Dict[str, Dict[str, str]]:
        """
        Recognize all pieces on the board.
        
        Args:
            board_image: Numpy array of the board image (RGB)
        
        Returns:
            Dictionary mapping squares to piece info
            Format: {"e2": {"piece": "pawn", "color": "white"}, ...}
        """
        # Convert numpy array to PIL Image
        if isinstance(board_image, np.ndarray):
            pil_image = Image.fromarray(board_image)
        else:
            pil_image = board_image
        
        # Create prompt
        prompt = self.create_prompt()
        
        # Process inputs
        inputs = self.processor(text=prompt, images=pil_image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate response
        print("Analyzing board with LLaVA...")
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=1024,
                do_sample=False,
                temperature=0.2,
            )
        
        # Decode response
        response = self.processor.decode(outputs[0], skip_special_tokens=True)
        
        # Extract the assistant's response
        if "ASSISTANT:" in response:
            response = response.split("ASSISTANT:")[-1].strip()
        
        print(f"LLaVA Response: {response[:200]}...")
        
        # Parse the JSON response
        piece_map = self._parse_response(response)
        
        return piece_map
    
    def _parse_response(self, response: str) -> Dict[str, Dict[str, str]]:
        """
        Parse LLaVA's text response into structured piece data.
        
        Args:
            response: Raw text response from LLaVA
        
        Returns:
            Parsed piece dictionary
        """
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                piece_map = json.loads(json_str)
                return piece_map
            else:
                print("Warning: Could not find JSON in response")
                return self._parse_text_response(response)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self._parse_text_response(response)
    
    def _parse_text_response(self, response: str) -> Dict[str, Dict[str, str]]:
        """
        Fallback parser for non-JSON responses.
        
        Args:
            response: Text response
        
        Returns:
            Best-effort parsed piece dictionary
        """
        piece_map = {}
        
        # Look for patterns like "e2: white pawn" or "e2 - white pawn"
        patterns = [
            r'([a-h][1-8]):\s*\{?"piece":\s*"(\w+)",\s*"color":\s*"(\w+)"\}?',
            r'([a-h][1-8]):\s*(\w+)\s+(\w+)',
            r'([a-h][1-8])\s*[-:]\s*(\w+)\s+(\w+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, response, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 3:
                    square = match.group(1).lower()
                    if 'piece' in pattern:
                        piece = match.group(2).lower()
                        color = match.group(3).lower()
                    else:
                        color = match.group(2).lower()
                        piece = match.group(3).lower()
                    
                    piece_map[square] = {"piece": piece, "color": color}
        
        return piece_map


def recognize_pieces(board_image: np.ndarray, 
                    model_name: str = "llava-hf/llava-v1.6-mistral-7b-hf") -> Dict[str, Dict[str, str]]:
    """
    Convenience function to recognize pieces.
    
    Args:
        board_image: Board image as numpy array
        model_name: LLaVA model to use
    
    Returns:
        Piece dictionary
    """
    recognizer = PieceRecognizer(model_name)
    return recognizer.recognize(board_image)


if __name__ == "__main__":
    # Test piece recognition
    print("Testing piece recognition...")
    # Create a dummy image for testing
    test_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    
    # Note: This will only work with a real chess board image
    # recognizer = PieceRecognizer()
    # pieces = recognizer.recognize(test_image)
    # print(f"Detected pieces: {pieces}")
    print("Test setup complete. Use with real chess board images.")
