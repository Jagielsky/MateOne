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

function showEngineInfo(data) {
  // Find the info display in the left panel
  let infoDiv = document.getElementById('engine-info');
  if (!infoDiv) {
    // This should not happen as we create it during initialization
    return;
  }

  let infoHTML = '<h3>Engine Information</h3>';
  
  if (data.error) {
    infoHTML += `<p style="color: red;"><strong>Error:</strong> ${data.error}</p>`;
  } else {
    if (data.move) {
      infoHTML += `<p><strong>Engine Move:</strong> ${data.move}</p>`;
    }
    if (data.evaluation !== undefined) {
      const evalDisplay = data.evaluation > 0 ? `+${data.evaluation}` : data.evaluation;
      const evalColor = data.evaluation > 0 ? 'green' : data.evaluation < 0 ? 'red' : 'black';
      infoHTML += `<p><strong>Position Evaluation:</strong> <span style="color: ${evalColor};">${evalDisplay}</span></p>`;
    }
    if (data.search_time) {
      infoHTML += `<p><strong>Search Time:</strong> ${data.search_time}s</p>`;
    }
    if (data.search_depth) {
      infoHTML += `<p><strong>Search Depth:</strong> ${data.search_depth}</p>`;
    }
    if (data.game_over) {
      infoHTML += `<p style="color: red;"><strong>Game Over!</strong></p>`;
      if (data.result) {
        infoHTML += `<p><strong>Result:</strong> ${data.result}</p>`;
      }
    }
  }
  
  infoDiv.innerHTML = infoHTML;
}

function onSnapEnd() {
  board.position(game.fen());

  // Get current depth from slider
  const depthSlider = document.getElementById('depth-slider');
  const currentDepth = depthSlider ? parseInt(depthSlider.value) : 4;

  // Show "thinking" indicator
  showEngineInfo({ move: "Engine thinking..." });

  // Send board state to backend
  fetch("/fen", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      fen: game.fen(),
      depth: currentDepth
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        showEngineInfo(data);
        return;
      }
      
      // Update game and board with engine response
      game.load(data.fen);
      board.position(data.fen);
      
      // Show engine information
      showEngineInfo(data);
      
      // Check if game is over
      if (game.game_over()) {
        let gameOverMsg = "Game Over! ";
        if (game.in_checkmate()) {
          gameOverMsg += game.turn() === 'w' ? "Black wins by checkmate!" : "White wins by checkmate!";
        } else if (game.in_stalemate()) {
          gameOverMsg += "Draw by stalemate!";
        } else if (game.in_threefold_repetition()) {
          gameOverMsg += "Draw by threefold repetition!";
        } else if (game.insufficient_material()) {
          gameOverMsg += "Draw by insufficient material!";
        }
        
        setTimeout(() => {
          alert(gameOverMsg);
        }, 500);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showEngineInfo({ error: "Network error occurred" });
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

// Add button to reset game
document.addEventListener('DOMContentLoaded', function() {
  const container = document.querySelector('.container');
  
  // Create a flex container to hold the left panel and board side by side
  const gameContainer = document.createElement('div');
  gameContainer.style.display = 'flex';
  gameContainer.style.alignItems = 'flex-start';
  gameContainer.style.gap = '20px';
  gameContainer.style.justifyContent = 'center';
  
  // Create left panel container for controls and info
  const leftPanel = document.createElement('div');
  leftPanel.style.display = 'flex';
  leftPanel.style.flexDirection = 'column';
  leftPanel.style.gap = '15px';
  leftPanel.style.minWidth = '250px';
  leftPanel.style.maxWidth = '250px';
  
  // Create New Game button
  const resetButton = document.createElement('button');
  resetButton.textContent = 'New Game';
  resetButton.style.padding = '10px 20px';
  resetButton.style.fontSize = '16px';
  resetButton.style.backgroundColor = '#4CAF50';
  resetButton.style.color = 'white';
  resetButton.style.border = 'none';
  resetButton.style.borderRadius = '5px';
  resetButton.style.cursor = 'pointer';
  resetButton.style.whiteSpace = 'nowrap';
  
  resetButton.addEventListener('click', function() {
    game.reset();
    board.start();
    
    // Clear engine info
    const infoDiv = document.getElementById('engine-info');
    if (infoDiv) {
      infoDiv.innerHTML = '<h3>Engine Information</h3><p>Make a move to see engine analysis</p>';
    }
  });
  
  // Create depth slider container
  const depthContainer = document.createElement('div');
  depthContainer.style.padding = '10px';
  depthContainer.style.backgroundColor = '#f0f0f0';
  depthContainer.style.border = '1px solid #ccc';
  depthContainer.style.borderRadius = '5px';
  
  const depthLabel = document.createElement('label');
  depthLabel.textContent = 'Engine Depth: ';
  depthLabel.style.fontWeight = 'bold';
  depthLabel.style.display = 'block';
  depthLabel.style.marginBottom = '5px';
  
  const depthSlider = document.createElement('input');
  depthSlider.type = 'range';
  depthSlider.id = 'depth-slider';
  depthSlider.min = '1';
  depthSlider.max = '6';
  depthSlider.value = '4';
  depthSlider.style.width = '100%';
  depthSlider.style.marginBottom = '5px';
  
  const depthValue = document.createElement('span');
  depthValue.id = 'depth-value';
  depthValue.textContent = '4';
  depthValue.style.fontWeight = 'bold';
  depthValue.style.color = '#333';
  
  depthSlider.addEventListener('input', function() {
    depthValue.textContent = this.value;
  });
  
  depthContainer.appendChild(depthLabel);
  depthContainer.appendChild(depthSlider);
  depthContainer.appendChild(document.createTextNode('Current: '));
  depthContainer.appendChild(depthValue);
  
  // Create engine info container
  const engineInfoDiv = document.createElement('div');
  engineInfoDiv.id = 'engine-info';
  engineInfoDiv.style.padding = '10px';
  engineInfoDiv.style.backgroundColor = '#f0f0f0';
  engineInfoDiv.style.border = '1px solid #ccc';
  engineInfoDiv.style.borderRadius = '5px';
  engineInfoDiv.style.minHeight = '150px';
  engineInfoDiv.innerHTML = '<h3>Engine Information</h3><p>Make a move to see engine analysis</p>';
  
  // Add all elements to left panel
  leftPanel.appendChild(resetButton);
  leftPanel.appendChild(depthContainer);
  leftPanel.appendChild(engineInfoDiv);
  
  // Create board container with fixed dimensions
  const boardContainer = document.createElement('div');
  boardContainer.style.width = '600px';
  boardContainer.style.height = '600px';
  boardContainer.style.flexShrink = '0'; // Prevent shrinking
  
  // Get the board element and move it to the board container
  const boardElement = document.getElementById('board');
  boardContainer.appendChild(boardElement);
  
  // Assemble the layout
  gameContainer.appendChild(leftPanel);
  gameContainer.appendChild(boardContainer);
  
  // Replace the container content with the new layout
  container.innerHTML = '';
  container.appendChild(gameContainer);
});
