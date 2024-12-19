import chess
import random

def engine_response(fen):
    board = chess.Board(fen)
    legal_moves = list(board.legal_moves)
    random_move = random.choice(legal_moves)
    board.push(random_move)
    return {'fen': board.fen()}