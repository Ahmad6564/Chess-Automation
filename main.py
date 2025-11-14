"""
Chess Vision Agent - Main Orchestrator

An autonomous chess-playing agent that combines computer vision (UI-TARS),
chess reasoning (Stockfish), and GUI automation to play chess like a human.
"""

import time
import yaml
import chess
from pathlib import Path
from typing import Optional, Dict

# Import our modules
from vision.capture import BoardCapture
from vision.board_detection import BoardDetector
from vision.piece_recognition import PieceRecognizer
from vision.fen_converter import FENConverter

from engine.stockfish_wrapper import StockfishEngine
from engine.move_validator import MoveValidator

from control.mapping_utils import SquareMapper
from control.move_executor import MoveExecutor
from control.humanizer import Humanizer

from utils.logger import setup_logger, LogContext, log_move, log_vision_result, log_error
from utils.helpers import timer, retry


class ChessAgent:
    """Main chess automation agent."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the chess agent.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Setup logger
        self.logger = setup_logger(
            level=self.config['logging']['level'],
            log_file=self.config['logging']['log_file'],
            console=self.config['logging']['console_output']
        )
        
        self.logger.info("=" * 60)
        self.logger.info("Chess Vision Agent Starting...")
        self.logger.info("=" * 60)
        
        # Initialize components
        self._initialize_components()
        
        # Game state
        self.move_count = 0
        self.game_active = False
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _initialize_components(self):
        """Initialize all agent components."""
        self.logger.info("Initializing components...")
        
        # Vision components
        self.capturer = BoardCapture()
        self.capturer.set_board_region(
            self.config['board_region']['left'],
            self.config['board_region']['top'],
            self.config['board_region']['width'],
            self.config['board_region']['height']
        )
        
        self.detector = BoardDetector(
            target_size=tuple(self.config['vision_model']['target_size'])
        )
        
        self.recognizer = PieceRecognizer(
            model_name=self.config['vision_model']['model_name']
        )
        
        self.fen_converter = FENConverter()
        
        # Engine components
        self.engine = StockfishEngine(
            stockfish_path=self.config['stockfish']['path'],
            skill_level=self.config['stockfish']['skill_level'],
            depth=self.config['stockfish']['depth'],
            time_limit=self.config['stockfish']['time_limit']
        )
        
        self.validator = MoveValidator()
        
        # Control components
        self.mapper = SquareMapper(
            board_bbox=self.config['board_region'],
            orientation=self.config['orientation']
        )
        
        self.executor = MoveExecutor(
            board_bbox=self.config['board_region'],
            orientation=self.config['orientation'],
            use_humanizer=self.config['humanizer']['enabled']
        )
        
        if self.config['humanizer']['enabled']:
            self.humanizer = Humanizer(
                min_delay=self.config['humanizer']['min_delay'],
                max_delay=self.config['humanizer']['max_delay'],
                jitter_pixels=self.config['humanizer']['jitter_pixels'],
                hover_probability=self.config['humanizer']['hover_probability']
            )
            self.humanizer.set_skill_level(self.config['humanizer']['skill_level'])
        
        self.logger.info("All components initialized successfully!")
    
    def capture_and_analyze_board(self) -> str:
        """
        Capture the board and convert to FEN.
        
        Returns:
            FEN string of current position
        """
        with LogContext(self.logger, "Board capture and analysis"):
            # Capture screen
            board_image = self.capturer.capture_board()
            
            # Detect and process board
            processed_board = self.detector.process_board(
                board_image, 
                bbox=self.config['board_region']
            )
            
            # Recognize pieces
            start_time = time.time()
            piece_map = self.recognizer.recognize(processed_board)
            processing_time = time.time() - start_time
            
            log_vision_result(
                self.logger,
                pieces_detected=len(piece_map),
                processing_time=processing_time
            )
            
            # Convert to FEN
            fen = self.fen_converter.piece_map_to_fen(piece_map)
            
            self.logger.info(f"FEN: {fen}")
            
            return fen
    
    def calculate_best_move(self, fen: str) -> str:
        """
        Calculate the best move using Stockfish.
        
        Args:
            fen: Current position FEN
        
        Returns:
            Best move in UCI format
        """
        with LogContext(self.logger, "Move calculation"):
            best_move = self.engine.get_best_move(fen)
            return best_move
    
    def execute_move_on_board(self, move_uci: str) -> bool:
        """
        Execute a move on the physical board.
        
        Args:
            move_uci: Move in UCI format
        
        Returns:
            True if successful
        """
        with LogContext(self.logger, f"Move execution: {move_uci}"):
            success = self.executor.execute_move(
                move_uci,
                drag=(self.config['move_execution']['method'] == 'drag')
            )
            return success
    
    def play_one_move(self):
        """Execute one complete move cycle."""
        self.logger.info(f"\n{'=' * 60}")
        self.logger.info(f"Move {self.move_count + 1}")
        self.logger.info(f"{'=' * 60}")
        
        # Capture and analyze board
        fen_before = self.capture_and_analyze_board()
        
        # Validate position
        if not self.fen_converter.validate_fen(fen_before):
            self.logger.error("Invalid FEN detected! Skipping move.")
            return False
        
        # Sync validator with current position
        self.validator.sync_with_fen(fen_before)
        
        # Check if game is over
        is_over, reason = self.validator.is_game_over()
        if is_over:
            self.logger.info(f"Game Over: {reason}")
            self.game_active = False
            return False
        
        # Calculate best move
        start_time = time.time()
        best_move = self.calculate_best_move(fen_before)
        thinking_time = time.time() - start_time
        
        # Validate move
        is_valid, msg = self.validator.validate_move(best_move)
        if not is_valid:
            self.logger.error(f"Invalid move calculated: {msg}")
            if self.config['error_handling']['abort_on_illegal_move']:
                self.game_active = False
                return False
        
        # Execute move
        success = self.execute_move_on_board(best_move)
        
        if success:
            # Update validator
            self.validator.apply_move(best_move)
            fen_after = self.validator.get_current_fen()
            
            # Log move
            log_move(self.logger, best_move, fen_before, fen_after, thinking_time)
            
            self.move_count += 1
            return True
        else:
            self.logger.error("Move execution failed!")
            return False
    
    def run(self):
        """Main game loop."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("STARTING CHESS AGENT")
        self.logger.info("=" * 60)
        
        self.game_active = True
        max_moves = self.config['game_loop']['max_moves']
        
        try:
            while self.game_active and self.move_count < max_moves:
                # Play our move
                success = self.play_one_move()
                
                if not success or not self.game_active:
                    break
                
                # Wait for opponent's move
                if self.config['game_loop']['opponent_move_detection'] == 'manual':
                    input("\nPress Enter after opponent's move...")
                else:
                    # Auto-detection would go here
                    time.sleep(2)
            
            self.logger.info("\n" + "=" * 60)
            self.logger.info(f"Game ended after {self.move_count} moves")
            self.logger.info("=" * 60)
            
        except KeyboardInterrupt:
            self.logger.info("\nAgent stopped by user")
        except Exception as e:
            log_error(self.logger, e, "Main game loop")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.logger.info("Cleaning up...")
        self.engine.close()
        self.logger.info("Chess Agent shutdown complete")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


def setup_board_region():
    """Interactive setup to define board region by clicking."""
    from pynput import mouse
    
    print("\n" + "=" * 60)
    print("BOARD REGION SETUP")
    print("=" * 60)
    print("Click on the CENTER of the chessboard...")
    print("The coordinates will be saved to config.yaml")
    
    coords = {'x': 0, 'y': 0}
    
    def on_click(x, y, button, pressed):
        if pressed:
            coords['x'] = x
            coords['y'] = y
            print(f"\nCenter coordinates captured: X={x}, Y={y}")
            return False
    
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    
    # Ask for board size
    try:
        board_size = int(input("\nEnter board size in pixels (default 800): ") or "800")
    except ValueError:
        board_size = 800
    
    # Calculate region
    half_size = board_size // 2
    region = {
        'left': coords['x'] - half_size,
        'top': coords['y'] - half_size,
        'width': board_size,
        'height': board_size
    }
    
    print(f"\nBoard region: {region}")
    
    # Update config
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        config['board_region'] = region
        
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print("✓ Config updated successfully!")
        print(f"Board region set to: {region}")
    except Exception as e:
        print(f"Error updating config: {e}")
    
    return region


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Chess Vision Agent')
    parser.add_argument('--setup', action='store_true', 
                       help='Run board region setup')
    parser.add_argument('--config', default='config.yaml',
                       help='Path to config file')
    
    args = parser.parse_args()
    
    if args.setup:
        setup_board_region()
    else:
        with ChessAgent(args.config) as agent:
            agent.run()


if __name__ == "__main__":
    main()
 
 