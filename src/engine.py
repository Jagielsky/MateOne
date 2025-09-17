import chess
import time
from src.evaluation import evaluate
from src.negamax import search


def get_move(fen, depth=4):
    try:
        board = chess.Board(fen)

        if board.is_game_over():
            return {"fen": fen, "game_over": True}

        t_start = time.time()
        best_move = search(board, depth)
        t_search = time.time() - t_start

        if best_move is None:
            moves = list(board.legal_moves)
            if moves:
                best_move = moves[0]
            else:
                return {"fen": fen, "game_over": True}

        board.push(best_move)
        eval_score = evaluate(board)

        return {
            "fen": board.fen(),
            "move": str(best_move),
            "evaluation": eval_score / 100.0,
            "search_time": round(t_search, 2),
        }

    except Exception as e:
        return {"fen": fen, "error": str(e)}
