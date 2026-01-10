import chess
from src.evaluation import evaluate
from src.zobrist import ZOBRIST
from src.transposition import TT, TTFlag

MATE_SCORE = 100000
MATE_THRESHOLD = MATE_SCORE - 1000


def _order_moves(board: chess.Board, tt_move_str: str = None):
    tt_move = None
    if tt_move_str:
        try:
            tt_move = chess.Move.from_uci(tt_move_str)
            if tt_move in board.legal_moves:
                yield tt_move
        except ValueError:
            tt_move = None

    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0,
    }

    def move_score(move):
        score = 0

        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            if victim and attacker:
                score = 100 * piece_values.get(victim.piece_type, 0) - piece_values.get(
                    attacker.piece_type, 0
                )
            else:
                score = 50

        if move.promotion:
            score += 200 + piece_values.get(move.promotion, 0)

        return score

    remaining_moves = [m for m in board.legal_moves if m != tt_move]
    for move in sorted(remaining_moves, key=move_score, reverse=True):
        yield move


def _adjust_mate_score(score: int, ply: int, storing: bool) -> int:
    if score > MATE_THRESHOLD:
        return score + ply if storing else score - ply
    elif score < -MATE_THRESHOLD:
        return score - ply if storing else score + ply
    return score


def negamax(board, depth, alpha, beta, color, stats, ply=0):
    stats["nodes"] += 1
    original_alpha = alpha

    zobrist_key = ZOBRIST.hash_board(board)

    tt_usable, tt_score, tt_move = TT.lookup_score(zobrist_key, depth, alpha, beta)
    if tt_usable:
        adjusted_score = _adjust_mate_score(tt_score, ply, storing=False)
        return adjusted_score, []

    if board.is_game_over():
        if board.is_checkmate():
            return -MATE_SCORE + ply, []
        return 0, []

    if depth == 0:
        return color * evaluate(board), []

    best_score = float("-inf")
    best_line = []
    best_move = None

    for move in _order_moves(board, tt_move):
        board.push(move)
        score, line = negamax(board, depth - 1, -beta, -alpha, -color, stats, ply + 1)
        score = -score
        board.pop()

        if score > best_score:
            best_score = score
            best_line = [move] + line
            best_move = move

        alpha = max(alpha, score)
        if alpha >= beta:
            stats["beta_cutoffs"] = stats.get("beta_cutoffs", 0) + 1
            break

    if best_score <= original_alpha:
        flag = TTFlag.UPPER
    elif best_score >= beta:
        flag = TTFlag.LOWER
    else:
        flag = TTFlag.EXACT

    store_score = _adjust_mate_score(best_score, ply, storing=True)
    TT.store(zobrist_key, depth, int(store_score), flag, best_move)

    return best_score, best_line


def _search_root(board, depth, stats):
    best_move = None
    alpha, beta = float("-inf"), float("inf")
    color = 1 if board.turn == chess.WHITE else -1
    best_pv = []
    best_score = float("-inf")

    zobrist_key = ZOBRIST.hash_board(board)
    _, _, tt_move = TT.lookup_score(zobrist_key, depth, alpha, beta)

    for move in _order_moves(board, tt_move):
        board.push(move)
        score, line = negamax(board, depth - 1, -beta, -alpha, -color, stats, ply=1)
        score = -score
        board.pop()

        if score > alpha:
            alpha = score
            best_move = move
            best_score = score
            best_pv = [move] + line

    if best_move:
        TT.store(zobrist_key, depth, int(best_score), TTFlag.EXACT, best_move)

    return best_move, best_score, best_pv


def search(board, depth=4):
    TT.new_search()

    best_move = None
    best_score = 0
    best_pv = []
    stats = {"nodes": 0, "beta_cutoffs": 0}
    iteration_info = []

    for current_depth in range(1, depth + 1):
        nodes_before = stats["nodes"]

        move, score, pv = _search_root(board, current_depth, stats)

        nodes_this_depth = stats["nodes"] - nodes_before

        if move is not None:
            best_move = move
            best_score = score
            best_pv = pv

            iteration_info.append(
                {
                    "depth": current_depth,
                    "score": score,
                    "nodes": nodes_this_depth,
                    "pv": [str(m) for m in pv],
                }
            )

    stats["tt_stats"] = TT.stats()
    stats["iterations"] = iteration_info
    stats["final_depth"] = depth

    return best_move, stats, best_score, best_pv
