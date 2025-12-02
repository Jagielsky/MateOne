import chess
from src.evaluation import evaluate


def negamax(board, depth, alpha, beta, color, stats):
    stats["nodes"] += 1
    if depth == 0 or board.is_game_over():
        return color * evaluate(board), []

    best_score = float("-inf")
    best_line = []

    for move in sorted(
        board.legal_moves, key=lambda m: board.is_capture(m), reverse=True
    ):
        board.push(move)
        score, line = negamax(board, depth - 1, -beta, -alpha, -color, stats)
        score = -score
        board.pop()

        if score > best_score:
            best_score = score
            best_line = [move] + line

        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return best_score, best_line


def search(board, depth=4):
    best_move = None
    alpha, beta = float("-inf"), float("inf")
    color = 1 if board.turn == chess.WHITE else -1
    stats = {"nodes": 0}
    best_pv = []

    best_score = float("-inf")

    for move in sorted(
        board.legal_moves, key=lambda m: board.is_capture(m), reverse=True
    ):
        board.push(move)
        score, line = negamax(board, depth - 1, -beta, -alpha, -color, stats)
        score = -score
        board.pop()

        if score > alpha:
            alpha = score
            best_move = move
            best_score = score
            best_pv = [move] + line

    return best_move, stats, best_score, best_pv
