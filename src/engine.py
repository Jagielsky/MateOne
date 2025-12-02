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
        best_move, stats, best_score, best_pv = search(board, depth)
        t_search = time.time() - t_start

        if best_move is None:
            moves = list(board.legal_moves)
            if moves:
                best_move = moves[0]

                board.push(best_move)
                best_score = evaluate(board)
                if board.turn == chess.BLACK:
                    pass
                else:
                    best_score = -best_score
                board.pop()
                best_pv = []
            else:
                return {"fen": fen, "game_over": True}

        if board.turn == chess.WHITE:
            display_score = best_score
        else:
            display_score = -best_score

        pv_san = []
        temp_board = board.copy()
        for move in best_pv:
            pv_san.append(temp_board.san(move))
            temp_board.push(move)
        pv_str = " ".join(pv_san)

        board.push(best_move)

        nps = int(stats["nodes"] / t_search) if t_search > 0 else 0

        return {
            "fen": board.fen(),
            "move": str(best_move),
            "evaluation": display_score / 100.0,
            "search_time": round(t_search, 2),
            "nodes": stats["nodes"],
            "nps": nps,
            "depth": depth,
            "pv": pv_str,
        }

    except Exception as e:
        return {"fen": fen, "error": str(e)}
