"""
Update all markdown files to use Qwen2-VL-2B-Instruct with quantization.
"""

import re

# Define replacements
replacements = [
    # Model names
    ("UI-TARS-1.5-7B", "Qwen2-VL-2B-Instruct"),
    ("ByteDance-Seed/UI-TARS-1.5-7B", "Qwen/Qwen2-VL-2B-Instruct"),
    ("UI-TARS 1.5-7B", "Qwen2-VL-2B-Instruct"),
    ("UI-TARS-7B", "Qwen2-VL-2B"),
    ("UI-TARS model", "Qwen2-VL model"),
    ("UI-TARS Model", "Qwen2-VL Model"),
    ("UI-TARS", "Qwen2-VL"),
    
    # Parameter counts
    ("7B parameters", "2B parameters with 4-bit quantization"),
    ("7B parameter", "2B parameter with 4-bit quantization"),
    ("7B efficient", "2B quantized"),
    
    # Model descriptions
    ("~14GB model", "~4GB model (quantized)"),
    ("efficient 7B", "efficient 2B quantized"),
    
    # Technical details
    ("7 checkpoint shards", "model shards with 4-bit quantization"),
]

# Files to update
files = [
    "README.md",
    "SETUP.md",
    "QUICKSTART.md",
    "PROJECT_SUMMARY.md",
    "MODEL_UPDATE.md"
]

print("=" * 60)
print("Updating Documentation: UI-TARS → Qwen2-VL-2B-Instruct")
print("=" * 60)

for filename in files:
    try:
        print(f"\nProcessing {filename}...")
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = 0
        
        # Apply replacements
        for old_text, new_text in replacements:
            if old_text in content:
                count = content.count(old_text)
                content = content.replace(old_text, new_text)
                changes += count
                if count > 0:
                    print(f"  ✓ Replaced '{old_text}' ({count} times)")
        
        # Write back if changes were made
        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Updated {filename} ({changes} changes)")
        else:
            print(f"  ⏭️  No changes needed for {filename}")
            
    except Exception as e:
        print(f"  ❌ Error updating {filename}: {e}")

print("\n" + "=" * 60)
print("✅ Documentation update complete!")
print("=" * 60)
print("\nAll files now reference: Qwen/Qwen2-VL-2B-Instruct")
print("Key changes:")
print("  - Model: UI-TARS-1.5-7B → Qwen2-VL-2B-Instruct")
print("  - Parameters: 7B → 2B with 4-bit quantization")
print("  - Memory: ~14GB → ~4GB (quantized)")
print("  - Speed: Much faster inference on CPU")
