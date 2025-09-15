import chess
from src.evaluation import evaluate_position

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_position(board)
    
    if maximizing_player:
        max_eval = float('-inf')
        
        moves = list(board.legal_moves)
        moves = order_moves(board, moves)
        
        for move in moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            
            if beta <= alpha:
                break
        
        return max_eval
    
    else:
        min_eval = float('inf')
        
        moves = list(board.legal_moves)
        moves = order_moves(board, moves)
        
        for move in moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            
            if beta <= alpha:
                break
        
        return min_eval

def find_best_move(board, depth=4):
    best_move = None
    best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
    alpha = float('-inf')
    beta = float('inf')
    
    moves = list(board.legal_moves)
    moves = order_moves(board, moves)
    
    for move in moves:
        board.push(move)
        
        if board.turn == chess.BLACK:
            move_value = minimax(board, depth - 1, alpha, beta, False)
        else:
            move_value = minimax(board, depth - 1, alpha, beta, True)
        
        board.pop()
        
        if board.turn == chess.WHITE:
            if move_value > best_value:
                best_value = move_value
                best_move = move
            alpha = max(alpha, move_value)
        else:
            if move_value < best_value:
                best_value = move_value
                best_move = move
            beta = min(beta, move_value)
    
    return best_move

def order_moves(board, moves):
    def move_priority(move):
        priority = 0
        
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                priority += captured_piece.piece_type * 10
        
        board.push(move)
        if board.is_check():
            priority += 50
        board.pop()
        
        if move.promotion:
            priority += 80
        
        if board.is_castling(move):
            priority += 30
        
        return priority
    
    return sorted(moves, key=move_priority, reverse=True)

def quiescence_search(board, alpha, beta, depth=0, max_depth=5):
    if depth >= max_depth:
        return evaluate_position(board)
    
    stand_pat = evaluate_position(board)
    
    if board.turn == chess.WHITE:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)
    
    moves = []
    for move in board.legal_moves:
        if board.is_capture(move) or board.gives_check(move):
            moves.append(move)
    
    if not moves:
        return stand_pat
    
    moves = order_moves(board, moves)
    
    for move in moves:
        board.push(move)
        score = quiescence_search(board, alpha, beta, depth + 1, max_depth)
        board.pop()
        
        if board.turn == chess.WHITE:
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        else:
            beta = min(beta, score)
            if beta <= alpha:
                break
    
    return alpha if board.turn == chess.WHITE else beta