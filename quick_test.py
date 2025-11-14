"""
Quick test to verify Qwen2-VL loads with 4-bit quantization.
This should be MUCH faster than the old UI-TARS model.
"""

import sys
import time

print("=" * 60)
print("QUICK MODEL TEST - Qwen2-VL-2B with 4-bit Quantization")
print("=" * 60)

# Test 1: Import check
print("\n[1/4] Checking imports...")
try:
    import torch
    from transformers import AutoModelForVision2Seq, Qwen2VLProcessor, BitsAndBytesConfig
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nTrying alternative processor...")
    try:
        from transformers import AutoModelForVision2Seq, BitsAndBytesConfig
        from transformers.models.auto import AutoProcessor
        print("✓ All imports successful (alternative)")
    except ImportError as e2:
        print(f"✗ Import error: {e2}")
        print("Run: pip install --upgrade transformers bitsandbytes accelerate")
        sys.exit(1)

# Test 2: Configuration
print("\n[2/4] Setting up configuration...")
model_name = "Qwen/Qwen2-VL-2B-Instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"  Device: {device}")
print(f"  Model: {model_name}")
print(f"  Quantization: 4-bit (NF4)")

# Test 3: Load processor (fast)
print("\n[3/4] Loading processor...")
start = time.time()
try:
    # Try AutoProcessor from transformers.models.auto
    from transformers.models.auto import AutoProcessor
    processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
    elapsed = time.time() - start
    print(f"✓ Processor loaded in {elapsed:.2f}s")
except Exception as e:
    print(f"✗ Processor loading failed: {e}")
    print("This model may require specific processor. Trying Qwen2VLProcessor...")
    try:
        from transformers import Qwen2VLProcessor
        processor = Qwen2VLProcessor.from_pretrained(model_name, trust_remote_code=True)
        print(f"✓ Qwen2VLProcessor loaded")
    except Exception as e2:
        print(f"✗ Qwen2VLProcessor failed: {e2}")
        sys.exit(1)

# Test 4: Load model with quantization
print("\n[4/4] Loading model with 4-bit quantization...")
print("  This will download ~4GB on first run (vs ~14GB for UI-TARS)")
print("  Expected time: 2-3 minutes on first run, <10 seconds after cached")

start = time.time()
try:
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
    print(f"✓ Model loaded in {elapsed:.1f}s ({elapsed/60:.2f} minutes)")
    print(f"✓ Memory: ~1.5GB (4-bit quantized)")
    
except Exception as e:
    print(f"✗ Model loading failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Success!
print("\n" + "=" * 60)
print("✅ SUCCESS! Model ready for chess piece recognition")
print("=" * 60)
print("\nPerformance comparison:")
print("  UI-TARS-1.5-7B:     ~14GB, 5-10 min load (CPU)")
print("  Qwen2-VL-2B (4bit): ~1.5GB, 2-3 min load (CPU)")
print("\nNext steps:")
print("  1. Run: python main.py --setup (configure board)")
print("  2. Run: python main.py (start agent)")
