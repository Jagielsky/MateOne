//Konfiguracja szachownicy chessboardjs
var config = {
  pieceTheme: '../static/img/{piece}.svg', //tutaj powinno być zastosowane url_for
  position: 'start',
  draggable: true
}

//Wygenerowanie szachownicy z konfiguracją
board = Chessboard('board', config)