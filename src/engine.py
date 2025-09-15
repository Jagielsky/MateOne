import chess
import time
from src.evaluation import evaluate_position
from src.minimax import find_best_move

def engine_response(fen, depth=4):
    try:
        board = chess.Board(fen)
        
        if board.is_game_over():
            return {
                'fen': fen,
                'game_over': True,
                'result': board.result()
            }
        
        start_time = time.time()
        best_move = find_best_move(board, depth)
        search_time = time.time() - start_time
        
        if best_move is None:
            legal_moves = list(board.legal_moves)
            if legal_moves:
                best_move = legal_moves[0]
            else:
                return {
                    'fen': fen,
                    'game_over': True,
                    'result': 'No legal moves'
                }
        
        board.push(best_move)
        
        position_eval = evaluate_position(board)
        
        return {
            'fen': board.fen(),
            'move': str(best_move),
            'evaluation': position_eval / 100.0,
            'search_time': round(search_time, 3),
            'search_depth': depth,
            'game_over': board.is_game_over(),
            'result': board.result() if board.is_game_over() else None
        }
    
    except Exception as e:
        return {
            'fen': fen,
            'error': str(e)
        }

def get_position_analysis(fen):
    try:
        board = chess.Board(fen)
        evaluation = evaluate_position(board)
        
        return {
            'fen': fen,
            'evaluation': evaluation / 100.0,
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