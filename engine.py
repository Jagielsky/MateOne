import chess
import time
from evaluation import evaluate_position
from minimax import find_best_move

def engine_response(fen, depth=4):
    """
    Main engine response function.
    
    Args:
        fen: Current position in FEN notation
        depth: Search depth (default 4)
    
    Returns:
        Dictionary with new FEN after engine move and additional info
    """
    try:
        board = chess.Board(fen)
        
        # Check if game is over
        if board.is_game_over():
            return {
                'fen': fen,
                'game_over': True,
                'result': board.result()
            }
        
        # Find the best move
        start_time = time.time()
        best_move = find_best_move(board, depth)
        search_time = time.time() - start_time
        
        if best_move is None:
            # Fallback to random move if no move found
            legal_moves = list(board.legal_moves)
            if legal_moves:
                best_move = legal_moves[0]
            else:
                return {
                    'fen': fen,
                    'game_over': True,
                    'result': 'No legal moves'
                }
        
        # Make the move
        board.push(best_move)
        
        # Evaluate the new position
        position_eval = evaluate_position(board)
        
        return {
            'fen': board.fen(),
            'move': str(best_move),
            'evaluation': position_eval,
            'search_time': round(search_time, 3),
            'search_depth': depth,
            'game_over': board.is_game_over(),
            'result': board.result() if board.is_game_over() else None
        }
    
    except Exception as e:
        # Error handling - return original position
        return {
            'fen': fen,
            'error': str(e)
        }

def get_position_analysis(fen):
    """
    Analyze a position without making a move.
    
    Args:
        fen: Position to analyze
    
    Returns:
        Dictionary with position analysis
    """
    try:
        board = chess.Board(fen)
        evaluation = evaluate_position(board)
        
        return {
            'fen': fen,
            'evaluation': evaluation,
            'turn': 'white' if board.turn == chess.WHITE else 'black',
            'legal_moves': len(list(board.legal_moves)),
            'is_check': board.is_check(),
            'is_checkmate': board.is_checkmate(),
            'is_stalemate': board.is_stalemate(),
            'can_castle_kingside': board.has_kingside_castling_rights(board.turn),
            'can_castle_queenside': board.has_queenside_castling_rights(board.turn)
        }
    
    except Exception as e:
        return {
            'fen': fen,
            'error': str(e)
        }