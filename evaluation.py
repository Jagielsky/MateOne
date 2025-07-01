import chess

# Piece values
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Piece-square tables for positional evaluation
# These tables give bonuses for pieces on better squares
PAWN_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

KING_TABLE_MIDDLEGAME = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20
]

KING_TABLE_ENDGAME = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]

PIECE_SQUARE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE_MIDDLEGAME
}

def get_piece_square_value(piece_type, square, is_white, is_endgame=False):
    """Get the positional value for a piece on a specific square"""
    table = PIECE_SQUARE_TABLES[piece_type]
    
    # Use endgame table for king if in endgame
    if piece_type == chess.KING and is_endgame:
        table = KING_TABLE_ENDGAME
    
    # For white pieces, use the table as is
    # For black pieces, flip the table vertically
    if is_white:
        index = square
    else:
        index = 63 - square
    
    return table[index]

def is_endgame(board):
    """Determine if the position is in endgame phase"""
    # Simple endgame detection: few pieces left or no queens
    piece_count = len(board.piece_map())
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.QUEEN, chess.BLACK))
    
    return piece_count <= 10 or queens == 0

def evaluate_position(board):
    """
    Evaluate the current position from White's perspective.
    Positive values favor White, negative values favor Black.
    """
    if board.is_checkmate():
        # If it's checkmate, return extreme values
        if board.turn == chess.WHITE:
            return -999999  # Black wins
        else:
            return 999999   # White wins
    
    if board.is_stalemate() or board.is_insufficient_material():
        return 0  # Draw
    
    evaluation = 0
    endgame = is_endgame(board)
    
    # Evaluate all pieces on the board
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue
        
        # Basic piece value
        piece_value = PIECE_VALUES[piece.piece_type]
        
        # Positional bonus/penalty
        positional_value = get_piece_square_value(
            piece.piece_type, square, piece.color == chess.WHITE, endgame
        )
        
        total_piece_value = piece_value + positional_value
        
        if piece.color == chess.WHITE:
            evaluation += total_piece_value
        else:
            evaluation -= total_piece_value
    
    # Additional evaluation factors
    evaluation += evaluate_mobility(board)
    evaluation += evaluate_king_safety(board)
    
    return evaluation

def evaluate_mobility(board):
    """Evaluate mobility (number of legal moves)"""
    # Store current turn
    current_turn = board.turn
    
    # Count white's moves
    board.turn = chess.WHITE
    white_moves = len(list(board.legal_moves))
    
    # Count black's moves
    board.turn = chess.BLACK
    black_moves = len(list(board.legal_moves))
    
    # Restore original turn
    board.turn = current_turn
    
    # Mobility bonus (having more moves is better)
    return (white_moves - black_moves) * 2

def evaluate_king_safety(board):
    """Basic king safety evaluation"""
    safety_score = 0
    
    # Check if kings are castled (simple heuristic)
    white_king_square = board.king(chess.WHITE)
    black_king_square = board.king(chess.BLACK)
    
    # Bonus for castled kings (kings on g1, c1, g8, c8)
    if white_king_square in [chess.G1, chess.C1]:
        safety_score += 30
    if black_king_square in [chess.G8, chess.C8]:
        safety_score -= 30
    
    # Penalty for exposed kings in the center
    if white_king_square in [chess.D1, chess.E1, chess.F1] and not board.has_castling_rights(chess.WHITE):
        safety_score -= 20
    if black_king_square in [chess.D8, chess.E8, chess.F8] and not board.has_castling_rights(chess.BLACK):
        safety_score += 20
    
    return safety_score
