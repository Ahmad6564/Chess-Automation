"""
Piece recognition module using Hugging Face Inference API.
No local model loading required - uses cloud inference.
"""
from PIL import Image
import numpy as np
import requests
import json
import base64
import io
from typing import Dict, Optional
import os
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PieceRecognizer:
    """Uses Hugging Face Inference API to recognize chess pieces."""
    
    def __init__(self, model_name: str = "Qwen/Qwen2-VL-2B-Instruct", api_token: Optional[str] = None):
        """
        Initialize the Hugging Face API client.
        
        Args:
            model_name: HuggingFace model identifier
            api_token: HF API token (or set HF_API_TOKEN environment variable)
        """
        self.model_name = model_name
        
        # Get API token from parameter or environment
        self.api_token = api_token or os.getenv("HF_API_TOKEN")
        if not self.api_token:
            raise ValueError(
                "Hugging Face API token required! Set HF_API_TOKEN environment variable or pass api_token parameter.\n"
                "Get your token from: https://huggingface.co/settings/tokens"
            )
        
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        
        logger.info(f"Initialized HF Inference API client for {model_name}")
        logger.info("No local model download required - using cloud inference")
    
    def create_prompt(self) -> str:
        """Create the chess piece recognition prompt."""
        return """Analyze this chess board image and identify all pieces.

For each piece, provide its square location (a1-h8), piece type (pawn, knight, bishop, rook, queen, king), and color (white, black).

Return ONLY a JSON object like this:
{"a1": {"piece": "rook", "color": "white"}, "e4": {"piece": "pawn", "color": "black"}}

Use lowercase, algebraic notation, and only include occupied squares."""
    
    def recognize(self, board_image: np.ndarray) -> Dict[str, Dict[str, str]]:
        """
        Recognize pieces using HF Inference API.
        
        Args:
            board_image: Board image as numpy array (H, W, 3)
        
        Returns:
            Dictionary mapping squares to piece info
            Example: {"e2": {"piece": "pawn", "color": "white"}}
        """
        logger.info("Recognizing pieces via Hugging Face API...")
        
        # Convert numpy array to PIL Image
        if isinstance(board_image, np.ndarray):
            image = Image.fromarray(board_image)
        else:
            image = board_image
        
        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Prepare the request payload
        prompt = self.create_prompt()
        
        # For vision models, send image as base64
        payload = {
            "inputs": {
                "image": img_base64,
                "question": prompt
            },
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.1,  # Low temperature for consistent outputs
            }
        }
        
        try:
            # Make API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 503:
                logger.warning("Model is loading, retrying in 20 seconds...")
                import time
                time.sleep(20)
                response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract text from response (format depends on model)
            if isinstance(result, list) and len(result) > 0:
                text_response = result[0].get("generated_text", "")
            elif isinstance(result, dict):
                text_response = result.get("generated_text", result.get("answer", ""))
            else:
                text_response = str(result)
            
            logger.info(f"API Response: {text_response[:200]}...")
            
            # Parse the JSON response
            pieces = self._parse_response(text_response)
            logger.info(f"Detected {len(pieces)} pieces on board")
            
            return pieces
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return {}
    
    def _parse_response(self, response: str) -> Dict[str, Dict[str, str]]:
        """Parse the model's response into piece dictionary."""
        try:
            # Try to find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                pieces = json.loads(json_str)
                
                # Validate format
                if isinstance(pieces, dict):
                    return pieces
            
            logger.warning("Could not parse JSON from response, trying text parsing")
            return self._parse_text_response(response)
            
        except json.JSONDecodeError:
            logger.warning("JSON parsing failed, trying text parsing")
            return self._parse_text_response(response)
    
    def _parse_text_response(self, response: str) -> Dict[str, Dict[str, str]]:
        """Fallback text parser if JSON parsing fails."""
        pieces = {}
        lines = response.lower().split('\n')
        
        for line in lines:
            # Look for patterns like "e4: white pawn" or "a1: black rook"
            for square in ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8',
                          'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8',
                          'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8',
                          'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8',
                          'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8',
                          'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8',
                          'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8',
                          'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8']:
                if square in line:
                    for color in ['white', 'black']:
                        if color in line:
                            for piece in ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']:
                                if piece in line:
                                    pieces[square] = {"piece": piece, "color": color}
                                    break
        
        return pieces


def recognize_pieces(board_image: np.ndarray, 
                    model_name: str = "Qwen/Qwen2-VL-2B-Instruct",
                    api_token: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """
    Convenience function to recognize pieces via HF API.
    
    Args:
        board_image: Board image as numpy array
        model_name: Qwen2-VL model to use
        api_token: HF API token
    
    Returns:
        Piece dictionary
    """
    recognizer = PieceRecognizer(model_name, api_token)
    return recognizer.recognize(board_image)


if __name__ == "__main__":
    # Test piece recognition
    print("Testing HF API piece recognition...")
    print("Set HF_API_TOKEN environment variable to test")
    print("Get token from: https://huggingface.co/settings/tokens")
