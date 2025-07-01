import chess
from evaluation import evaluate_position

def minimax(board, depth, alpha, beta, maximizing_player):
    """
    Minimax algorithm with alpha-beta pruning.
    
    Args:
        board: Chess board position
        depth: Search depth remaining
        alpha: Alpha value for pruning
        beta: Beta value for pruning
        maximizing_player: True if maximizing (White), False if minimizing (Black)
    
    Returns:
        Evaluation score of the position
    """
    # Base case: if depth is 0 or game is over
    if depth == 0 or board.is_game_over():
        return evaluate_position(board)
    
    if maximizing_player:
        max_eval = float('-inf')
        
        # Get all legal moves and sort them for better pruning
        moves = list(board.legal_moves)
        moves = order_moves(board, moves)
        
        for move in moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            
            # Alpha-beta pruning
            if beta <= alpha:
                break
        
        return max_eval
    
    else:
        min_eval = float('inf')
        
        # Get all legal moves and sort them for better pruning
        moves = list(board.legal_moves)
        moves = order_moves(board, moves)
        
        for move in moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            
            # Alpha-beta pruning
            if beta <= alpha:
                break
        
        return min_eval

def find_best_move(board, depth=4):
    """
    Find the best move using minimax with alpha-beta pruning.
    
    Args:
        board: Current chess position
        depth: Search depth (default 4)
    
    Returns:
        Best move found
    """
    best_move = None
    best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
    alpha = float('-inf')
    beta = float('inf')
    
    # Get all legal moves and sort them for better performance
    moves = list(board.legal_moves)
    moves = order_moves(board, moves)
    
    for move in moves:
        board.push(move)
        
        if board.turn == chess.BLACK:  # After white's move, it's black's turn
            move_value = minimax(board, depth - 1, alpha, beta, False)
        else:  # After black's move, it's white's turn
            move_value = minimax(board, depth - 1, alpha, beta, True)
        
        board.pop()
        
        # Update best move based on whose turn it is
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
    """
    Order moves to improve alpha-beta pruning efficiency.
    Better moves first = more pruning.
    """
    def move_priority(move):
        priority = 0
        
        # Prioritize captures
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                # Higher value captures first
                priority += captured_piece.piece_type * 10
        
        # Prioritize checks
        board.push(move)
        if board.is_check():
            priority += 50
        board.pop()
        
        # Prioritize promotions
        if move.promotion:
            priority += 80
        
        # Prioritize castling
        if board.is_castling(move):
            priority += 30
        
        return priority
    
    # Sort moves by priority (highest first)
    return sorted(moves, key=move_priority, reverse=True)

def quiescence_search(board, alpha, beta, depth=0, max_depth=5):
    """
    Quiescence search to avoid horizon effect.
    Only searches captures and checks to find quiet positions.
    """
    if depth >= max_depth:
        return evaluate_position(board)
    
    # Stand pat - the current position evaluation
    stand_pat = evaluate_position(board)
    
    if board.turn == chess.WHITE:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)
    
    # Generate only captures and checks
    moves = []
    for move in board.legal_moves:
        if board.is_capture(move) or board.gives_check(move):
            moves.append(move)
    
    # If no tactical moves, return stand pat
    if not moves:
        return stand_pat
    
    # Order tactical moves
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
