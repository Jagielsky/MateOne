var board = null;
var game = new Chess();

function onDragStart(source, piece, position, orientation) {
  if (game.game_over()) return false;
  if (piece[0] !== "w") return false;
}

function onDrop(source, target) {
  var move = game.move({
    from: source,
    to: target,
    promotion: "q",
  });

  if (move === null) return "snapback";
}

function updateEvaluationBar(evaluation) {
  const evalBar = document.getElementById("eval-bar");
  const evalText = document.getElementById("eval-text");

  if (!evalBar || !evalText) return;

  const clampedEval = Math.max(-10, Math.min(10, evaluation));

  const percentage = 50 + (clampedEval / 10) * 40;

  const whiteBar = evalBar.querySelector(".eval-white");
  whiteBar.style.height = `${percentage}%`;

  const evalDisplay =
    evaluation > 0 ? `+${evaluation.toFixed(2)}` : evaluation.toFixed(2);
  evalText.textContent = evalDisplay;

  if (evaluation > 0.5) {
    evalText.style.color = "#4CAF50";
  } else if (evaluation < -0.5) {
    evalText.style.color = "#f44336";
  } else {
    evalText.style.color = "#000";
  }
}

function showEngineInfo(data) {
  let infoDiv = document.getElementById("engine-info");
  if (!infoDiv) {
    return;
  }

  let infoHTML = '<h3 style="margin-bottom: 5px;">Information</h3>';

  if (data.error) {
    infoHTML += `<p style="color: red;"><strong>Error:</strong> ${data.error}</p>`;
  } else {
    if (data.move) {
      infoHTML += `<p><strong>Engine Move:</strong> ${data.move}</p>`;
    }
    if (data.evaluation !== undefined) {
      updateEvaluationBar(data.evaluation);
    }
    if (data.search_time) {
      infoHTML += `<p><strong>Search Time:</strong> ${data.search_time}s</p>`;
    }
    if (data.game_over) {
      infoHTML += `<p style="color: red;"><strong>Game Over!</strong></p>`;
    }
  }

  infoDiv.innerHTML = infoHTML;
}

function onSnapEnd() {
  board.position(game.fen());

  const depthSlider = document.getElementById("depth-slider");
  const currentDepth = depthSlider ? parseInt(depthSlider.value) : 4;

  showEngineInfo({ move: "thinking..." });

  fetch("/fen", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fen: game.fen(),
      depth: currentDepth,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        showEngineInfo(data);
        return;
      }

      game.load(data.fen);
      board.position(data.fen);

      showEngineInfo(data);
    });
}

var config = {
  pieceTheme: pieceUrl + "{piece}.svg",
  draggable: true,
  position: "start",
  onDragStart: onDragStart,
  onDrop: onDrop,
  onSnapEnd: onSnapEnd,
};

board = Chessboard("board", config);

document.addEventListener("DOMContentLoaded", function () {
  const container = document.querySelector(".container");

  const gameContainer = document.createElement("div");
  gameContainer.style.display = "flex";
  gameContainer.style.alignItems = "flex-start";
  gameContainer.style.gap = "20px";
  gameContainer.style.justifyContent = "center";

  const leftPanel = document.createElement("div");
  leftPanel.style.display = "flex";
  leftPanel.style.flexDirection = "column";
  leftPanel.style.gap = "15px";
  leftPanel.style.minWidth = "250px";
  leftPanel.style.maxWidth = "250px";

  const resetButton = document.createElement("button");
  resetButton.textContent = "New Game";
  resetButton.style.padding = "10px 20px";
  resetButton.style.fontSize = "16px";
  resetButton.style.backgroundColor = "#4CAF50";
  resetButton.style.color = "white";
  resetButton.style.border = "none";
  resetButton.style.borderRadius = "5px";
  resetButton.style.cursor = "pointer";
  resetButton.style.whiteSpace = "nowrap";

  resetButton.addEventListener("click", function () {
    game.reset();
    board.start();

    updateEvaluationBar(0);

    const infoDiv = document.getElementById("engine-info");
    if (infoDiv) {
      infoDiv.innerHTML =
        '<h3 style="margin-bottom: 5px;">Information</h3><p>Make a move to see analysis</p>';
    }
  });

  const depthContainer = document.createElement("div");
  depthContainer.style.padding = "10px";
  depthContainer.style.backgroundColor = "#f0f0f0";
  depthContainer.style.border = "1px solid #ccc";
  depthContainer.style.borderRadius = "5px";

  const depthLabel = document.createElement("label");
  depthLabel.textContent = "Engine Depth: ";
  depthLabel.style.fontWeight = "bold";
  depthLabel.style.display = "block";
  depthLabel.style.marginBottom = "5px";

  const depthSlider = document.createElement("input");
  depthSlider.type = "range";
  depthSlider.id = "depth-slider";
  depthSlider.min = "1";
  depthSlider.max = "6";
  depthSlider.value = "4";
  depthSlider.style.width = "100%";
  depthSlider.style.marginBottom = "5px";

  const depthValue = document.createElement("span");
  depthValue.id = "depth-value";
  depthValue.textContent = "4";
  depthValue.style.fontWeight = "bold";
  depthValue.style.color = "#333";

  depthSlider.addEventListener("input", function () {
    depthValue.textContent = this.value;
  });

  depthContainer.appendChild(depthLabel);
  depthContainer.appendChild(depthSlider);
  depthContainer.appendChild(document.createTextNode("Current: "));
  depthContainer.appendChild(depthValue);

  const engineInfoDiv = document.createElement("div");
  engineInfoDiv.id = "engine-info";
  engineInfoDiv.style.padding = "10px";
  engineInfoDiv.style.backgroundColor = "#f0f0f0";
  engineInfoDiv.style.border = "1px solid #ccc";
  engineInfoDiv.style.borderRadius = "5px";
  engineInfoDiv.style.minHeight = "150px";
  engineInfoDiv.innerHTML =
    '<h3 style="margin-bottom: 5px;">Information</h3><p>Make a move to see analysis</p>';

  const evalBarContainer = document.createElement("div");
  evalBarContainer.style.display = "flex";
  evalBarContainer.style.alignItems = "center";
  evalBarContainer.style.gap = "10px";
  evalBarContainer.style.height = "596px";

  const evalBarWrapper = document.createElement("div");
  evalBarWrapper.style.position = "relative";
  evalBarWrapper.style.width = "30px";
  evalBarWrapper.style.height = "592px";
  evalBarWrapper.style.border = "2px solid #333";
  evalBarWrapper.style.borderRadius = "3px";
  evalBarWrapper.style.overflow = "hidden";

  const evalBlack = document.createElement("div");
  evalBlack.className = "eval-black";
  evalBlack.style.position = "absolute";
  evalBlack.style.top = "0";
  evalBlack.style.left = "0";
  evalBlack.style.width = "100%";
  evalBlack.style.height = "100%";
  evalBlack.style.backgroundColor = "#000";

  const evalWhite = document.createElement("div");
  evalWhite.className = "eval-white";
  evalWhite.style.position = "absolute";
  evalWhite.style.bottom = "0";
  evalWhite.style.left = "0";
  evalWhite.style.width = "100%";
  evalWhite.style.height = "50%";
  evalWhite.style.backgroundColor = "#fff";
  evalWhite.style.transition = "height 0.3s ease";

  const centerLine = document.createElement("div");
  centerLine.style.position = "absolute";
  centerLine.style.top = "50%";
  centerLine.style.left = "0";
  centerLine.style.right = "0";
  centerLine.style.height = "1px";
  centerLine.style.backgroundColor = "#999";
  centerLine.style.transform = "translateY(-50%)";

  evalBarWrapper.id = "eval-bar";
  evalBarWrapper.appendChild(evalBlack);
  evalBarWrapper.appendChild(evalWhite);
  evalBarWrapper.appendChild(centerLine);

  const evalText = document.createElement("div");
  evalText.id = "eval-text";
  evalText.textContent = "0.00";
  evalText.style.fontWeight = "bold";
  evalText.style.fontSize = "16px";
  evalText.style.color = "#000";
  evalText.style.minWidth = "50px";
  evalText.style.textAlign = "left";

  evalBarContainer.appendChild(evalBarWrapper);
  evalBarContainer.appendChild(evalText);

  leftPanel.appendChild(resetButton);
  leftPanel.appendChild(depthContainer);
  leftPanel.appendChild(engineInfoDiv);

  const boardContainer = document.createElement("div");
  boardContainer.style.width = "600px";
  boardContainer.style.height = "600px";
  boardContainer.style.flexShrink = "0";

  const boardElement = document.getElementById("board");
  boardContainer.appendChild(boardElement);

  gameContainer.appendChild(leftPanel);
  gameContainer.appendChild(boardContainer);
  gameContainer.appendChild(evalBarContainer);

  container.innerHTML = "";
  container.appendChild(gameContainer);
});
