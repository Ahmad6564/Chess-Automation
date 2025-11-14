"""
FEN converter module - converts piece positions to FEN notation.
"""

import chess
from typing import Dict, Optional


class FENConverter:
    """Converts detected piece positions to FEN notation."""
    
    # Piece symbols mapping
    PIECE_SYMBOLS = {
        ('pawn', 'white'): 'P',
        ('pawn', 'black'): 'p',
        ('knight', 'white'): 'N',
        ('knight', 'black'): 'n',
        ('bishop', 'white'): 'B',
        ('bishop', 'black'): 'b',
        ('rook', 'white'): 'R',
        ('rook', 'black'): 'r',
        ('queen', 'white'): 'Q',
        ('queen', 'black'): 'q',
        ('king', 'white'): 'K',
        ('king', 'black'): 'k'
    }
    
    def __init__(self):
        """Initialize FEN converter."""
        self.board = chess.Board()
    
    def piece_map_to_fen(self, piece_map: Dict[str, Dict[str, str]], 
                         side_to_move: str = 'white',
                         castling_rights: str = 'KQkq',
                         en_passant: str = '-',
                         halfmove_clock: int = 0,
                         fullmove_number: int = 1) -> str:
        """
        Convert piece map to FEN notation.
        
        Args:
            piece_map: Dictionary of pieces {"e2": {"piece": "pawn", "color": "white"}}
            side_to_move: 'white' or 'black' (w or b)
            castling_rights: Castling availability (KQkq, -, etc.)
            en_passant: En passant target square or '-'
            halfmove_clock: Halfmove clock for 50-move rule
            fullmove_number: Fullmove number
        
        Returns:
            FEN string
        """
        # Create 8x8 board representation
        board_array = [[None for _ in range(8)] for _ in range(8)]
        
        # Fill board with pieces
        for square, piece_info in piece_map.items():
            try:
                # Convert algebraic notation to array indices
                col = ord(square[0]) - ord('a')  # a-h -> 0-7
                row = 8 - int(square[1])  # 1-8 -> 7-0 (reversed for FEN)
                
                if 0 <= col < 8 and 0 <= row < 8:
                    piece_type = piece_info['piece'].lower()
                    color = piece_info['color'].lower()
                    
                    # Get piece symbol
                    piece_symbol = self.PIECE_SYMBOLS.get((piece_type, color))
                    if piece_symbol:
                        board_array[row][col] = piece_symbol
            except (KeyError, ValueError, IndexError) as e:
                print(f"Warning: Invalid square or piece info for {square}: {e}")
                continue
        
        # Convert board array to FEN position string
        fen_rows = []
        for row in board_array:
            fen_row = ""
            empty_count = 0
            
            for piece in row:
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    fen_row += piece
            
            if empty_count > 0:
                fen_row += str(empty_count)
            
            fen_rows.append(fen_row)
        
        position = "/".join(fen_rows)
        
        # Convert side to move
        side = 'w' if side_to_move.lower() == 'white' else 'b'
        
        # Build complete FEN string
        fen = f"{position} {side} {castling_rights} {en_passant} {halfmove_clock} {fullmove_number}"
        
        return fen
    
    def validate_fen(self, fen: str) -> bool:
        """
        Validate FEN string using python-chess.
        
        Args:
            fen: FEN string to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            board = chess.Board(fen)
            return board.is_valid()
        except ValueError:
            return False
    
    def get_board_from_fen(self, fen: str) -> Optional[chess.Board]:
        """
        Create a python-chess Board object from FEN.
        
        Args:
            fen: FEN string
        
        Returns:
            chess.Board object or None if invalid
        """
        try:
            return chess.Board(fen)
        except ValueError as e:
            print(f"Invalid FEN: {e}")
            return None
    
    def detect_orientation(self, piece_map: Dict[str, Dict[str, str]]) -> str:
        """
        Detect board orientation based on piece positions.
        
        Args:
            piece_map: Dictionary of detected pieces
        
        Returns:
            'white' if white is at bottom, 'black' if black is at bottom
        """
        # Check if there are more white pieces in lower rows (6-8) or upper rows (1-3)
        white_bottom_count = 0
        white_top_count = 0
        
        for square, piece_info in piece_map.items():
            if piece_info['color'].lower() == 'white':
                row = int(square[1])
                if row <= 2:
                    white_bottom_count += 1
                elif row >= 7:
                    white_top_count += 1
        
        return 'white' if white_bottom_count > white_top_count else 'black'


def to_fen(piece_map: Dict[str, Dict[str, str]], 
           side_to_move: str = 'white',
           **kwargs) -> str:
    """
    Convenience function to convert piece map to FEN.
    
    Args:
        piece_map: Dictionary of pieces
        side_to_move: Side to move ('white' or 'black')
        **kwargs: Additional FEN parameters
    
    Returns:
        FEN string
    """
    converter = FENConverter()
    return converter.piece_map_to_fen(piece_map, side_to_move, **kwargs)


if __name__ == "__main__":
    # Test FEN conversion
    print("Testing FEN converter...")
    
    # Starting position piece map
    test_pieces = {
        'a1': {'piece': 'rook', 'color': 'white'},
        'b1': {'piece': 'knight', 'color': 'white'},
        'c1': {'piece': 'bishop', 'color': 'white'},
        'd1': {'piece': 'queen', 'color': 'white'},
        'e1': {'piece': 'king', 'color': 'white'},
        'f1': {'piece': 'bishop', 'color': 'white'},
        'g1': {'piece': 'knight', 'color': 'white'},
        'h1': {'piece': 'rook', 'color': 'white'},
        'a2': {'piece': 'pawn', 'color': 'white'},
        'b2': {'piece': 'pawn', 'color': 'white'},
        'e2': {'piece': 'pawn', 'color': 'white'},
        'e4': {'piece': 'pawn', 'color': 'white'},
    }
    
    converter = FENConverter()
    fen = converter.piece_map_to_fen(test_pieces)
    print(f"Generated FEN: {fen}")
    print(f"Valid: {converter.validate_fen(fen)}")
