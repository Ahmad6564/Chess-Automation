"""
Stockfish chess engine wrapper for move calculation.
"""

import chess
import chess.engine
from typing import Optional, Dict, Any
import os
from pathlib import Path


class StockfishEngine:
    """Wrapper for Stockfish chess engine."""
    
    def __init__(self, 
                 stockfish_path: Optional[str] = None,
                 skill_level: int = 20,
                 depth: int = 15,
                 time_limit: float = 1.0):
        """
        Initialize Stockfish engine.
        
        Args:
            stockfish_path: Path to Stockfish executable
                           If None, will try to find it in common locations
            skill_level: Skill level 0-20 (20 is strongest)
            depth: Search depth for move calculation
            time_limit: Time limit in seconds for move calculation
        """
        self.stockfish_path = stockfish_path or self._find_stockfish()
        self.skill_level = skill_level
        self.depth = depth
        self.time_limit = time_limit
        self.engine = None
        self.board = chess.Board()
        
        # Initialize engine
        self._initialize_engine()
    
    def _find_stockfish(self) -> str:
        """
        Try to find Stockfish executable in common locations.
        
        Returns:
            Path to Stockfish executable
        
        Raises:
            FileNotFoundError: If Stockfish not found
        """
        # Common paths to check
        possible_paths = [
            "stockfish",  # In PATH
            "stockfish.exe",  # Windows in PATH
            r"C:\Program Files\Stockfish\stockfish.exe",
            r"C:\Stockfish\stockfish.exe",
            "/usr/local/bin/stockfish",  # Linux/Mac
            "/usr/bin/stockfish",
            str(Path.home() / "stockfish" / "stockfish.exe"),
            "./stockfish.exe",
            "./stockfish",
        ]
        
        for path in possible_paths:
            if os.path.exists(path) or self._is_in_path(path):
                print(f"Found Stockfish at: {path}")
                return path
        
        raise FileNotFoundError(
            "Stockfish executable not found. Please install Stockfish and provide the path."
            "\nDownload from: https://stockfishchess.org/download/"
        )
    
    def _is_in_path(self, executable: str) -> bool:
        """Check if executable is in system PATH."""
        try:
            import subprocess
            result = subprocess.run([executable, "--help"], 
                                  capture_output=True, 
                                  timeout=2)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _initialize_engine(self):
        """Initialize the Stockfish engine with configured settings."""
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
            
            # Configure engine options
            self.engine.configure({
                "Skill Level": self.skill_level,
                "Threads": 2,
                "Hash": 256,  # MB
            })
            
            print(f"Stockfish initialized successfully (Skill Level: {self.skill_level})")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Stockfish: {e}")
    
    def set_position(self, fen: str):
        """
        Set the board position from FEN string.
        
        Args:
            fen: FEN notation string
        """
        try:
            self.board = chess.Board(fen)
            print(f"Position set: {fen}")
        except ValueError as e:
            raise ValueError(f"Invalid FEN string: {e}")
    
    def get_best_move(self, 
                      fen: Optional[str] = None,
                      depth: Optional[int] = None,
                      time_limit: Optional[float] = None) -> str:
        """
        Calculate the best move for the current position.
        
        Args:
            fen: Optional FEN string (if None, uses current board)
            depth: Optional search depth (if None, uses configured depth)
            time_limit: Optional time limit (if None, uses configured time)
        
        Returns:
            Best move in UCI format (e.g., "e2e4")
        """
        if fen:
            self.set_position(fen)
        
        # Use provided parameters or defaults
        search_depth = depth or self.depth
        search_time = time_limit or self.time_limit
        
        # Calculate best move
        try:
            result = self.engine.play(
                self.board,
                chess.engine.Limit(depth=search_depth, time=search_time)
            )
            
            move_uci = result.move.uci()
            print(f"Best move: {move_uci}")
            return move_uci
            
        except Exception as e:
            raise RuntimeError(f"Error calculating move: {e}")
    
    def get_evaluation(self, fen: Optional[str] = None) -> Dict[str, Any]:
        """
        Get position evaluation.
        
        Args:
            fen: Optional FEN string
        
        Returns:
            Dictionary with evaluation info (score, mate distance, etc.)
        """
        if fen:
            self.set_position(fen)
        
        info = self.engine.analyse(
            self.board,
            chess.engine.Limit(depth=self.depth)
        )
        
        eval_dict = {
            "score": info["score"].white().score(mate_score=10000) if info.get("score") else None,
            "depth": info.get("depth"),
            "nodes": info.get("nodes"),
            "time": info.get("time"),
        }
        
        return eval_dict
    
    def make_move(self, move_uci: str):
        """
        Make a move on the internal board.
        
        Args:
            move_uci: Move in UCI format (e.g., "e2e4")
        """
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                print(f"Move made: {move_uci}")
            else:
                raise ValueError(f"Illegal move: {move_uci}")
        except ValueError as e:
            raise ValueError(f"Invalid move format: {e}")
    
    def get_legal_moves(self) -> list:
        """
        Get all legal moves for current position.
        
        Returns:
            List of legal moves in UCI format
        """
        return [move.uci() for move in self.board.legal_moves]
    
    def reset_board(self):
        """Reset board to starting position."""
        self.board = chess.Board()
    
    def close(self):
        """Close the engine."""
        if self.engine:
            self.engine.quit()
            print("Stockfish engine closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def get_best_move(fen: str, 
                  stockfish_path: Optional[str] = None,
                  depth: int = 15) -> str:
    """
    Convenience function to get best move for a position.
    
    Args:
        fen: FEN notation string
        stockfish_path: Path to Stockfish executable
        depth: Search depth
    
    Returns:
        Best move in UCI format
    """
    with StockfishEngine(stockfish_path, depth=depth) as engine:
        return engine.get_best_move(fen)


if __name__ == "__main__":
    # Test Stockfish wrapper
    print("Testing Stockfish wrapper...")
    
    try:
        with StockfishEngine() as engine:
            # Test starting position
            starting_fen = chess.STARTING_FEN
            best_move = engine.get_best_move(starting_fen)
            print(f"Best opening move: {best_move}")
            
            # Get evaluation
            eval_info = engine.get_evaluation()
            print(f"Evaluation: {eval_info}")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Stockfish is installed!")
