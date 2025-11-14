"""
Quick test script to verify all components are working.
"""

import sys
from pathlib import Path

def test_imports():
    """Test if all modules can be imported."""
    print("Testing imports...")
    
    try:
        print("  ✓ Vision module...")
        from vision import capture, board_detection, piece_recognition, fen_converter
        
        print("  ✓ Engine module...")
        from engine import stockfish_wrapper, move_validator
        
        print("  ✓ Control module...")
        from control import mapping_utils, move_executor, humanizer
        
        print("  ✓ Utils module...")
        from utils import logger, helpers
        
        print("\n✅ All imports successful!\n")
        return True
    except ImportError as e:
        print(f"\n❌ Import error: {e}\n")
        return False


def test_dependencies():
    """Test if all dependencies are installed."""
    print("Testing dependencies...")
    
    dependencies = [
        ('numpy', 'numpy'),
        ('PIL', 'pillow'),
        ('cv2', 'opencv-python'),
        ('yaml', 'pyyaml'),
        ('chess', 'python-chess'),
        ('mss', 'mss'),
        ('pyautogui', 'pyautogui'),
        ('pynput', 'pynput'),
        ('torch', 'torch'),
        ('transformers', 'transformers'),
    ]
    
    missing = []
    
    for module, package in dependencies:
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}\n")
        return False
    else:
        print("\n✅ All dependencies installed!\n")
        return True


def test_config():
    """Test if config file exists and is valid."""
    print("Testing configuration...")
    
    config_path = Path('config.yaml')
    
    if not config_path.exists():
        print("  ✗ config.yaml not found")
        print("\n❌ Configuration file missing!\n")
        return False
    
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        required_keys = ['board_region', 'stockfish', 'vision_model', 'humanizer']
        for key in required_keys:
            if key in config:
                print(f"  ✓ {key}")
            else:
                print(f"  ✗ {key} - MISSING")
                return False
        
        print("\n✅ Configuration valid!\n")
        return True
    except Exception as e:
        print(f"\n❌ Config error: {e}\n")
        return False


def test_stockfish():
    """Test Stockfish installation."""
    print("Testing Stockfish...")
    
    try:
        from engine.stockfish_wrapper import StockfishEngine
        
        engine = StockfishEngine()
        engine.close()
        
        print("  ✓ Stockfish found and working")
        print("\n✅ Stockfish ready!\n")
        return True
    except FileNotFoundError:
        print("  ✗ Stockfish not found")
        print("\n❌ Stockfish not installed!")
        print("Download from: https://stockfishchess.org/download/\n")
        return False
    except Exception as e:
        print(f"\n❌ Stockfish error: {e}\n")
        return False


def test_vision():
    """Test basic vision components."""
    print("Testing vision components...")
    
    try:
        import numpy as np
        from vision.capture import BoardCapture
        from vision.board_detection import BoardDetector
        
        # Test capture
        capturer = BoardCapture()
        print("  ✓ Board capture initialized")
        
        # Test detector
        detector = BoardDetector()
        test_image = np.zeros((800, 800, 3), dtype=np.uint8)
        processed = detector.normalize_board(test_image)
        print("  ✓ Board detector working")
        
        print("\n✅ Vision components ready!\n")
        return True
    except Exception as e:
        print(f"\n❌ Vision error: {e}\n")
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("CHESS VISION AGENT - SYSTEM TEST")
    print("=" * 60 + "\n")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Stockfish", test_stockfish),
        ("Vision Components", test_vision),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}\n")
            results.append((name, False))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYou're ready to run the chess agent!")
        print("\nNext steps:")
        print("1. Run setup: python main.py --setup")
        print("2. Run agent: python main.py\n")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease fix the issues above before running the agent.\n")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
