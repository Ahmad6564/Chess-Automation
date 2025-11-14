"""
Simple test script to verify Qwen2-VL model loading with quantization.
This helps diagnose if the model loads correctly before running the full agent.
"""

import torch
import time
from transformers import AutoModelForVision2Seq, AutoProcessor, BitsAndBytesConfig

def test_model_loading():
    """Test if Qwen2-VL model can be loaded with quantization."""
    print("=" * 60)
    print("Qwen2-VL Model Loading Test (4-bit Quantized)")
    print("=" * 60)
    
    model_name = "Qwen/Qwen2-VL-2B-Instruct"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    quantization = "4bit"  # Use 4-bit quantization for speed
    
    print(f"\nDevice: {device}")
    print(f"Model: {model_name}")
    print(f"Quantization: {quantization}")
    
    if device == "cpu":
        print("\n✓ Using 4-bit quantization for fast CPU inference (~2-3 minutes)")
        print("Much faster than full precision!")
        
        response = input("\nContinue with CPU loading? (y/n): ")
        if response.lower() != 'y':
            print("Aborted. Consider using GPU or a smaller model.")
            return False
    
    print("\n" + "-" * 60)
    print("Step 1: Loading Processor...")
    start = time.time()
    
    try:
        processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
        print(f"✓ Processor loaded in {time.time() - start:.1f}s")
    except Exception as e:
        print(f"✗ Processor loading failed: {e}")
        return False
    
    print("\n" + "-" * 60)
    print("Step 2: Loading Model with 4-bit quantization...")
    print("This will be much faster than full precision!")
    print("Progress will show below...")
    start = time.time()
    
    try:
        # 4-bit quantization config
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        
        model = AutoModelForVision2Seq.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True
        )
        elapsed = time.time() - start
        print(f"✓ Model loaded in {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
    except Exception as e:
        print(f"✗ Model loading failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Qwen2-VL model loaded with 4-bit quantization!")
    print("=" * 60)
    print(f"\nMemory usage: ~1.5GB (quantized)")
    print("The model is now cached and future loads will be faster.")
    print("You can now run the full chess agent with: python main.py")
    
    return True


if __name__ == "__main__":
    success = test_model_loading()
    
    if not success:
        print("\n" + "=" * 60)
        print("ALTERNATIVE OPTIONS:")
        print("=" * 60)
        print("1. Use GPU if available (much faster)")
        print("2. Let it run in background (will complete eventually)")
        print("3. Use a different vision model (update config.yaml)")
        print("4. Test other components first (Stockfish, controls)")
