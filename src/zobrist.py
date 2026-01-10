import chess
import random


class ZobristHashing:
    def __init__(self, seed: int = 0xDEADBEEF):
        random.seed(seed)

        self.piece_keys = [
            [[self._random_u64() for _ in range(64)] for _ in range(2)]
            for _ in range(7)
        ]

        self.castling_keys = [self._random_u64() for _ in range(16)]

        self.ep_keys = [self._random_u64() for _ in range(9)]

        self.side_key = self._random_u64()

    def _random_u64(self) -> int:
        return random.getrandbits(64)

    def hash_board(self, board: chess.Board) -> int:
        key = 0

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                color_idx = 0 if piece.color == chess.WHITE else 1
                key ^= self.piece_keys[piece.piece_type][color_idx][square]

        castling_index = self._castling_to_index(board)
        key ^= self.castling_keys[castling_index]

        ep_index = self._ep_to_index(board)
        key ^= self.ep_keys[ep_index]

        if board.turn == chess.BLACK:
            key ^= self.side_key

        return key

    def _castling_to_index(self, board: chess.Board) -> int:
        index = 0
        if board.has_kingside_castling_rights(chess.WHITE):
            index |= 1
        if board.has_queenside_castling_rights(chess.WHITE):
            index |= 2
        if board.has_kingside_castling_rights(chess.BLACK):
            index |= 4
        if board.has_queenside_castling_rights(chess.BLACK):
            index |= 8
        return index

    def _ep_to_index(self, board: chess.Board) -> int:
        if board.ep_square is None:
            return 8
        return chess.square_file(board.ep_square)

    def update_piece(self, key: int, piece_type: int, color: bool, square: int) -> int:
        color_idx = 0 if color == chess.WHITE else 1
        return key ^ self.piece_keys[piece_type][color_idx][square]

    def update_castling(self, key: int, old_rights: int, new_rights: int) -> int:
        return key ^ self.castling_keys[old_rights] ^ self.castling_keys[new_rights]

    def update_ep(self, key: int, old_ep: int, new_ep: int) -> int:
        return key ^ self.ep_keys[old_ep] ^ self.ep_keys[new_ep]

    def toggle_side(self, key: int) -> int:
        return key ^ self.side_key


ZOBRIST = ZobristHashing()
