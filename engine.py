import chess
import random

#losowy ruch do testu odpowiedzi silnika
def engine_response(fen):
    board = chess.Board(fen)
    legal_moves = list(board.legal_moves)
    random_move = random.choice(legal_moves)
    board.push(random_move)
    return {'fen': board.fen()}

#dodaj ocene pozycji
#każda figura powinna mieć swoją wartość, król najważniejszy
#sumuj je i odemij wartosci biale od czarnych wtedy wiadomo kto ma przewage
#kazda figura ma lepsze i gorsze pola, je też wliczaj do oceny

#poczytaj o bitboard, musisz jakoś przedstawiac szachownice dla silnika zeby bylo wydajnie, na koncu i tak zwróci fen

#... tutaj zaczynają się schody

#algorytm minmax i przycinanie alfa beta czyli przeszukiwanie każdego możliwego ruchu (głebia określa ile do przodu)
#wybranie najlepszego ruchu po ocenie