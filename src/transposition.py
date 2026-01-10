import chess
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


class TTFlag(IntEnum):
    EXACT = 0
    LOWER = 1
    UPPER = 2


@dataclass(slots=True)
class TTEntry:
    key: int
    depth: int
    score: int
    flag: TTFlag
    best_move: Optional[str]
    age: int = 0


class TranspositionTable:
    def __init__(self, size_mb: int = 64):
        self.size = (size_mb * 1024 * 1024) // 64
        self.table: list[Optional[TTEntry]] = [None] * self.size
        self.generation = 0
        self.hits = 0
        self.probes = 0
        self.stores = 0
        self.collisions = 0

    def _index(self, key: int) -> int:
        return key % self.size

    def probe(self, key: int) -> Optional[TTEntry]:
        self.probes += 1
        entry = self.table[self._index(key)]
        if entry is not None and entry.key == key:
            return entry
        return None

    def store(
        self,
        key: int,
        depth: int,
        score: int,
        flag: TTFlag,
        best_move: Optional[chess.Move],
    ) -> None:

        index = self._index(key)
        existing = self.table[index]

        move_str = str(best_move) if best_move else None

        should_replace = (
            existing is None
            or existing.age < self.generation
            or existing.depth <= depth
        )

        if should_replace:
            if existing is not None and existing.key != key:
                self.collisions += 1

            self.table[index] = TTEntry(
                key=key,
                depth=depth,
                score=score,
                flag=flag,
                best_move=move_str,
                age=self.generation,
            )
            self.stores += 1

    def lookup_score(
        self, key: int, depth: int, alpha: int, beta: int
    ) -> tuple[bool, int, Optional[str]]:

        entry = self.probe(key)

        if entry is None:
            return False, 0, None

        if entry.depth < depth:
            return False, 0, entry.best_move

        score = entry.score

        if entry.flag == TTFlag.EXACT:
            self.hits += 1
            return True, score, entry.best_move

        if entry.flag == TTFlag.LOWER and score >= beta:
            self.hits += 1
            return True, score, entry.best_move

        if entry.flag == TTFlag.UPPER and score <= alpha:
            self.hits += 1
            return True, score, entry.best_move

        return False, 0, entry.best_move

    def new_search(self) -> None:
        self.generation += 1
        self.hits = 0
        self.probes = 0
        self.stores = 0
        self.collisions = 0

    def clear(self) -> None:
        self.table = [None] * self.size
        self.generation = 0
        self.hits = 0
        self.probes = 0
        self.stores = 0
        self.collisions = 0

    def hashfull(self) -> int:
        sample_size = min(1000, self.size)
        filled = sum(1 for i in range(sample_size) if self.table[i] is not None)
        return int((filled / sample_size) * 1000)

    def stats(self) -> dict:
        return {
            "hits": self.hits,
            "probes": self.probes,
            "stores": self.stores,
            "collisions": self.collisions,
            "hashfull": self.hashfull(),
            "generation": self.generation,
        }


TT = TranspositionTable(size_mb=64)
