"""
Piece recognition module using Qwen2-VL vision model with quantization.
"""

import torch
import numpy as np
from PIL import Image
from transformers import AutoModelForVision2Seq
from transformers.models.auto import AutoProcessor
from typing import Dict, Optional
import json
import re


class PieceRecognizer:
    """Uses Qwen2-VL model with 4-bit quantization to recognize chess pieces on the board."""
    
    def __init__(self, model_name: str = "Qwen/Qwen2-VL-2B-Instruct", quantization: str = "4bit"):
        """
        Initialize the Qwen2-VL model for piece recognition with quantization.
        
        Args:
            model_name: HuggingFace model identifier
                       Default: Qwen/Qwen2-VL-2B-Instruct (2B parameters, very fast)
            quantization: Quantization mode - "4bit", "8bit", or "none"
                         4-bit is fastest and uses least memory (~1.5GB)
                         8-bit is more accurate but slower (~3GB)
                         none uses full precision (not recommended for CPU)
        """
        self.model_name = model_name
        self.quantization = quantization
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Loading Qwen2-VL model: {model_name}")
        print(f"Device: {self.device} | Quantization: {quantization}")
        
        if quantization in ["4bit", "8bit"]:
            print("First run will download model (~4GB) and may take 2-3 minutes...")
        
        # Load processor
        self.processor = AutoProcessor.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        print("✓ Processor loaded")
        
        # Load model with quantization
        print("Loading quantized model (much faster than full precision)...")
        
        if quantization == "4bit":
            # 4-bit quantization - fastest, ~1.5GB memory
            from transformers import BitsAndBytesConfig
            
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            
            self.model = AutoModelForVision2Seq.from_pretrained(
                model_name,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True
            )
            print("✓ Model loaded with 4-bit quantization (~1.5GB memory)")
            
        elif quantization == "8bit":
            # 8-bit quantization - balanced, ~3GB memory
            from transformers import BitsAndBytesConfig
            
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True
            )
            
            self.model = AutoModelForVision2Seq.from_pretrained(
                model_name,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True
            )
            print("✓ Model loaded with 8-bit quantization (~3GB memory)")
            
        else:
            # No quantization - slowest, most accurate
            self.model = AutoModelForVision2Seq.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            print("✓ Model loaded without quantization (full precision)")
        
        print(f"✓ Qwen2-VL ready for inference!")
        
    def create_prompt(self) -> str:
        """
        Create the prompt for Qwen2-VL to recognize chess pieces.
        
        Returns:
            Formatted prompt string
        """
        prompt = """Analyze this chess board image and identify all pieces.

For each piece, provide its square location (a1-h8), piece type (pawn, knight, bishop, rook, queen, king), and color (white, black).

Return ONLY a JSON object like this:
{"a1": {"piece": "rook", "color": "white"}, "e4": {"piece": "pawn", "color": "black"}}

Use lowercase, algebraic notation, and only include occupied squares."""
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
        text_prompt = self.create_prompt()
        
        # Qwen2VL format: messages with image and text
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": pil_image},
                    {"type": "text", "text": text_prompt}
                ]
            }
        ]
        
        # Process inputs using apply_chat_template
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        
        inputs = self.processor(
            text=[text],
            images=[pil_image],
            return_tensors="pt",
            padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate response
        print("Analyzing board with Qwen2-VL (quantized)...")
        try:
            with torch.no_grad():
                # Generate using the model's generate method
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    do_sample=False,
                )
            
            # Trim input tokens from generated output
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            # Decode response
            response = self.processor.batch_decode(
                generated_ids_trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            
        except Exception as e:
            print(f"Generation error: {e}")
            print("Attempting alternative generation method...")
            # Fallback: use full output
            with torch.no_grad():
                outputs = self.model.generate(**inputs, max_new_tokens=1024)
            response = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            # Try to extract assistant response
            if "assistant" in response.lower():
                parts = response.split("assistant")
                if len(parts) > 1:
                    response = parts[-1].strip()
        
        print(f"Qwen2-VL Response: {response[:200]}...")
        
        # Parse the JSON response
        piece_map = self._parse_response(response)
        
        return piece_map
    
    def _parse_response(self, response: str) -> Dict[str, Dict[str, str]]:
        """
        Parse Qwen2-VL's text response into structured piece data.
        
        Args:
            response: Raw text response from Qwen2-VL
        
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
                    model_name: str = "Qwen/Qwen2-VL-2B-Instruct",
                    quantization: str = "4bit") -> Dict[str, Dict[str, str]]:
    """
    Convenience function to recognize pieces.
    
    Args:
        board_image: Board image as numpy array
        model_name: Qwen2-VL model to use
        quantization: "4bit", "8bit", or "none"
    
    Returns:
        Piece dictionary
    """
    recognizer = PieceRecognizer(model_name, quantization)
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
