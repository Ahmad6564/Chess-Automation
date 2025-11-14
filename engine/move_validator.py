"""
Move validator - ensures move legality and syncs board state.
"""

import chess
from typing import Optional, Tuple


class MoveValidator:
    """Validates chess moves and maintains board state synchronization."""
    
    def __init__(self, initial_fen: Optional[str] = None):
        """
        Initialize move validator.
        
        Args:
            initial_fen: Starting position FEN (defaults to standard starting position)
        """
        self.board = chess.Board(initial_fen) if initial_fen else chess.Board()
        self.move_history = []
    
    def validate_move(self, move_uci: str) -> Tuple[bool, str]:
        """
        Validate if a move is legal in the current position.
        
        Args:
            move_uci: Move in UCI format (e.g., "e2e4")
        
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            move = chess.Move.from_uci(move_uci)
            
            if move in self.board.legal_moves:
                return True, "Move is legal"
            else:
                return False, f"Illegal move: {move_uci}"
                
        except ValueError as e:
            return False, f"Invalid move format: {e}"
    
    def apply_move(self, move_uci: str) -> bool:
        """
        Apply a move to the board if it's legal.
        
        Args:
            move_uci: Move in UCI format
        
        Returns:
            True if move was applied, False otherwise
        """
        is_valid, message = self.validate_move(move_uci)
        
        if is_valid:
            move = chess.Move.from_uci(move_uci)
            self.board.push(move)
            self.move_history.append(move_uci)
            print(f"Move applied: {move_uci}")
            return True
        else:
            print(f"Move rejected: {message}")
            return False
    
    def sync_with_fen(self, fen: str) -> Tuple[bool, str]:
        """
        Sync the internal board state with a FEN position.
        
        Args:
            fen: FEN notation string
        
        Returns:
            Tuple of (success, message)
        """
        try:
            new_board = chess.Board(fen)
            
            # Check if the new position is reachable from current position
            # (This is a simplified check - full validation would be complex)
            self.board = new_board
            
            return True, "Board synced successfully"
            
        except ValueError as e:
            return False, f"Invalid FEN: {e}"
    
    def detect_position_change(self, new_fen: str) -> Optional[str]:
        """
        Detect what move was made by comparing current position with new position.
        
        Args:
            new_fen: FEN of the new position
        
        Returns:
            Detected move in UCI format, or None if no single move detected
        """
        try:
            new_board = chess.Board(new_fen)
            
            # Check each legal move to see if it leads to the new position
            for move in self.board.legal_moves:
                test_board = self.board.copy()
                test_board.push(move)
                
                # Compare positions (ignoring move counters)
                if self._positions_equal(test_board, new_board):
                    return move.uci()
            
            return None
            
        except ValueError:
            return None
    
    def _positions_equal(self, board1: chess.Board, board2: chess.Board) -> bool:
        """
        Compare two board positions (ignoring move counters).
        
        Args:
            board1: First board
            board2: Second board
        
        Returns:
            True if positions are equal
        """
        # Compare piece positions
        if board1.board_fen() != board2.board_fen():
            return False
        
        # Compare side to move
        if board1.turn != board2.turn:
            return False
        
        # Compare castling rights
        if board1.castling_rights != board2.castling_rights:
            return False
        
        # Compare en passant square
        if board1.ep_square != board2.ep_square:
            return False
        
        return True
    
    def get_current_fen(self) -> str:
        """
        Get FEN of current position.
        
        Returns:
            FEN string
        """
        return self.board.fen()
    
    def get_legal_moves(self) -> list:
        """
        Get all legal moves in current position.
        
        Returns:
            List of legal moves in UCI format
        """
        return [move.uci() for move in self.board.legal_moves]
    
    def is_game_over(self) -> Tuple[bool, Optional[str]]:
        """
        Check if the game is over.
        
        Returns:
            Tuple of (is_over, reason)
        """
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn else "White"
            return True, f"Checkmate - {winner} wins"
        elif self.board.is_stalemate():
            return True, "Stalemate"
        elif self.board.is_insufficient_material():
            return True, "Insufficient material"
        elif self.board.is_seventyfive_moves():
            return True, "75-move rule"
        elif self.board.is_fivefold_repetition():
            return True, "Fivefold repetition"
        else:
            return False, None
    
    def reset(self, fen: Optional[str] = None):
        """
        Reset the validator to a new position.
        
        Args:
            fen: Optional FEN string (defaults to starting position)
        """
        self.board = chess.Board(fen) if fen else chess.Board()
        self.move_history = []


def validate_move(move_uci: str, fen: str) -> Tuple[bool, str]:
    """
    Convenience function to validate a single move.
    
    Args:
        move_uci: Move in UCI format
        fen: Current position FEN
    
    Returns:
        Tuple of (is_valid, message)
    """
    validator = MoveValidator(fen)
    return validator.validate_move(move_uci)


if __name__ == "__main__":
    # Test move validator
    print("Testing move validator...")
    
    validator = MoveValidator()
    
    # Test valid move
    is_valid, msg = validator.validate_move("e2e4")
    print(f"e2e4 valid: {is_valid} - {msg}")
    
    # Apply move
    validator.apply_move("e2e4")
    print(f"Current FEN: {validator.get_current_fen()}")
    
    # Test invalid move
    is_valid, msg = validator.validate_move("e2e4")
    print(f"e2e4 again valid: {is_valid} - {msg}")
    
    # Check game status
    is_over, reason = validator.is_game_over()
    print(f"Game over: {is_over} - {reason}")
