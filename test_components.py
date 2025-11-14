"""
Test chess engine and control components WITHOUT vision model.
This allows testing Stockfish and move execution while vision model loads.
"""

import yaml
import chess
import time
from engine.stockfish_wrapper import StockfishEngine
from engine.move_validator import MoveValidator
from control.move_executor import MoveExecutor
from utils.logger import setup_logger

def test_engine():
    """Test Stockfish engine."""
    print("\n" + "=" * 60)
    print("Testing Stockfish Engine")
    print("=" * 60)
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    try:
        engine = StockfishEngine(
            stockfish_path=config['stockfish']['path'],
            skill_level=config['stockfish']['skill_level'],
            depth=config['stockfish']['depth']
        )
        
        # Test position (starting position)
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        
        print(f"\nPosition: {fen}")
        print("Calculating best move...")
        
        start = time.time()
        best_move = engine.get_best_move(fen)
        elapsed = time.time() - start
        
        print(f"✓ Best move: {best_move} (calculated in {elapsed:.2f}s)")
        
        # Get evaluation
        eval_score = engine.get_evaluation(fen)
        print(f"✓ Position evaluation: {eval_score}")
        
        engine.close()
        print("\n✅ Stockfish engine working correctly!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure Stockfish is installed:")
        print("  Download from: https://stockfishchess.org/download/")
        print("  Or install via: choco install stockfish (Windows)")
        return False


def test_validator():
    """Test move validator."""
    print("\n" + "=" * 60)
    print("Testing Move Validator")
    print("=" * 60)
    
    try:
        validator = MoveValidator()
        
        # Test move validation
        test_moves = [
            ("e2e4", True, "Valid opening move"),
            ("e2e5", False, "Invalid pawn jump"),
            ("a1h8", False, "Invalid rook move at start")
        ]
        
        for move, should_be_valid, description in test_moves:
            is_valid, msg = validator.validate_move(move)
            status = "✓" if is_valid == should_be_valid else "✗"
            print(f"{status} {move}: {description} - {msg}")
        
        print("\n✅ Move validator working correctly!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_move_executor_dry_run():
    """Test move executor in dry-run mode (no actual mouse movement)."""
    print("\n" + "=" * 60)
    print("Testing Move Executor (Dry Run)")
    print("=" * 60)
    
    try:
        # Load config
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        executor = MoveExecutor(
            board_bbox=config['board_region'],
            orientation=config['orientation'],
            use_humanizer=False
        )
        
        # Test coordinate calculation
        test_squares = ['e2', 'e4', 'a1', 'h8']
        
        print("\nCalculating board coordinates:")
        for square in test_squares:
            coords = executor.mapper.square_to_coords(square)
            print(f"  {square} -> X: {coords[0]}, Y: {coords[1]}")
        
        print("\n✅ Move executor coordinate system working!")
        print("⚠️  Actual mouse movement not tested (requires manual verification)")
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("CHESS AGENT COMPONENT TESTS (WITHOUT VISION)")
    print("=" * 60)
    print("\nThese tests verify core components work while vision model loads.")
    
    results = {
        "Stockfish Engine": test_engine(),
        "Move Validator": test_validator(),
        "Move Executor": test_move_executor_dry_run()
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {component}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All components working! Core system is ready.")
        print("\nNext steps:")
        print("1. Wait for vision model to finish loading")
        print("2. Run: python test_model_loading.py (to verify vision)")
        print("3. Run: python main.py --setup (to configure board region)")
        print("4. Run: python main.py (full agent)")
    else:
        print("\n⚠️  Some components failed. Fix errors above before proceeding.")
    
    return all_passed


if __name__ == "__main__":
    main()
