var board = null;
var game = new Chess();

function onDragStart(source, piece, position, orientation) {
  if (game.game_over()) return false;

  if (
    (game.turn() === "w" && piece.search(/^b/) !== -1) ||
    (game.turn() === "b" && piece.search(/^w/) !== -1)
  ) {
    return false;
  }
}

function onDrop(source, target) {
  var move = game.move({
    from: source,
    to: target,
    promotion: "q",
  });

  if (move === null) return "snapback";
}

function onSnapEnd() {
  board.position(game.fen());

  // Wysyłanie stanu planszy do backendu
  fetch("/fen", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fen: game.fen() }),
  })
    .then((response) => response.json())
    .then((data) => {
      game.load(data.fen);
      board.position(data.fen);
    });
}

//Konfiguracja szachownicy chessboardjs
var config = {
  pieceTheme: pieceUrl + "{piece}.svg",
  draggable: true,
  position: "start",
  onDragStart: onDragStart,
  onDrop: onDrop,
  onSnapEnd: onSnapEnd,
};

//Wygenerowanie szachownicy z konfiguracją
board = Chessboard("board", config);
