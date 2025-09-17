import chess
from src.evaluation import evaluate


def negamax(board, depth, alpha, beta, color):
    if depth == 0 or board.is_game_over():
        return color * evaluate(board)

    best_score = float("-inf")
    for move in sorted(
        board.legal_moves, key=lambda m: board.is_capture(m), reverse=True
    ):
        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha, -color)
        board.pop()

        best_score = max(best_score, score)
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return best_score


def search(board, depth=4):
    best_move = None
    alpha, beta = float("-inf"), float("inf")
    color = 1 if board.turn == chess.WHITE else -1

    for move in sorted(
        board.legal_moves, key=lambda m: board.is_capture(m), reverse=True
    ):
        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha, -color)
        board.pop()

        if score > alpha:
            alpha = score
            best_move = move
    return best_move
