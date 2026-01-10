var board = null;
var game = new Chess();
var evalChart = null;
var statsHistory = [];

function initChart() {
  const ctx = document.getElementById("evalChart").getContext("2d");
  evalChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label: "Ocena",
        data: [],
        borderColor: "#d4a373",
        borderWidth: 2,
        fill: true,
        pointRadius: 0,
        pointHitRadius: 20,
        pointHoverRadius: 6,
        pointBackgroundColor: "#d4a373",
        pointBorderColor: "#fff",
        pointBorderWidth: 2,
        tension: 0.4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(18, 18, 18, 0.95)",
          titleColor: "#d4a373",
          bodyColor: "#fff",
          borderColor: "#333",
          borderWidth: 1,
          displayColors: false,
          callbacks: {
            label: function (context) {
              return "Ocena: " + context.parsed.y.toFixed(2);
            },
          },
        },
      },
      scales: {
        x: {
          display: true,
          grid: { display: false, drawBorder: false },
          ticks: { color: "#888", maxTicksLimit: 10, font: { size: 10 } },
        },
        y: {
          grid: {
            color: function (context) {
              if (context.tick.value === 0) return "rgba(255, 255, 255, 0.3)";
              return "rgba(255, 255, 255, 0.05)";
            },
            drawBorder: false,
          },
          ticks: {
            color: "#888",
            callback: function (value) { return value.toFixed(1); },
            font: { size: 10 },
          },
        },
      },
      animation: { duration: 400, easing: "easeOutQuart" },
    },
    plugins: [{
      id: "evalGradient",
      beforeRender: function (chart) {
        const ctx = chart.ctx;
        const chartArea = chart.chartArea;
        const yScale = chart.scales.y;
        if (!chartArea) return;

        const yZeroPixel = yScale.getPixelForValue(0);
        const totalHeight = chartArea.bottom - chartArea.top;
        const stop = Math.max(0, Math.min(1, (yZeroPixel - chartArea.top) / totalHeight));

        const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
        const epsilon = 0.0001;
        gradient.addColorStop(0, "rgba(255, 255, 255, 0.4)");
        gradient.addColorStop(Math.max(0, stop - epsilon), "rgba(255, 255, 255, 0.4)");
        gradient.addColorStop(Math.min(1, stop + epsilon), "rgba(0, 0, 0, 0.4)");
        gradient.addColorStop(1, "rgba(0, 0, 0, 0.4)");
        chart.data.datasets[0].backgroundColor = gradient;
      },
    }],
  });
}

function updateChart(moveNumber, evaluation) {
  if (!evalChart) return;
  const clampedEval = Math.max(-100, Math.min(100, evaluation));
  evalChart.data.labels.push(moveNumber);
  evalChart.data.datasets[0].data.push(clampedEval);
  if (evalChart.data.labels.length > 50) {
    evalChart.data.labels.shift();
    evalChart.data.datasets[0].data.shift();
  }
  evalChart.update();
}

function resetChart() {
  if (!evalChart) return;
  statsHistory = [];
  evalChart.data.labels = [];
  evalChart.data.datasets[0].data = [];
  evalChart.update();
}

function resetUI() {
  document.getElementById("main-score").textContent = "0.00";
  document.getElementById("main-score").style.color = "#e0e0e0";
  document.getElementById("score-trend").textContent = "Równowaga";
  document.getElementById("score-trend").style.color = "#a0a0a0";
  document.getElementById("eval-gauge-fill").style.height = "50%";
  document.getElementById("stat-time").textContent = "0.00s";
  document.getElementById("stat-nodes").textContent = "0";
  document.getElementById("stat-nps").textContent = "0";
  document.getElementById("stat-tt-hitrate").textContent = "0%";
  document.getElementById("stat-tt-hashfull-pct").textContent = "0%";
  document.getElementById("stat-tt-hashfull-bar").style.width = "0%";
  document.getElementById("stat-tt-hits").textContent = "0";
  document.getElementById("stat-tt-stores").textContent = "0";
  document.getElementById("stat-material").textContent = "0";
  document.getElementById("pv-display").innerHTML = '';
}

function onDragStart(source, piece) {
  if (game.game_over()) return false;
  if (piece[0] !== "w") return false;
}

function onDrop(source, target) {
  var move = game.move({ from: source, to: target, promotion: "q" });
  if (move === null) return "snapback";
  updatePGN();
  updateMaterialBalance();
}

function updatePGN() {
  const pgnEl = document.getElementById("pgn-display");
  const history = game.history();
  let html = "";
  for (let i = 0; i < history.length; i += 2) {
    const moveNum = Math.floor(i / 2) + 1;
    const whiteMove = history[i];
    const blackMove = history[i + 1] || "";
    html += `<div class="pgn-move-row">
      <span class="pgn-move-num">${moveNum}.</span>
      <span class="pgn-move-white">${whiteMove}</span>
      <span class="pgn-move-black">${blackMove}</span>
    </div>`;
  }
  pgnEl.innerHTML = html;
  pgnEl.scrollTop = pgnEl.scrollHeight;
}

function updateMaterialBalance() {
  const boardState = game.board();
  let whiteMaterial = 0;
  let blackMaterial = 0;
  const pieceValues = { p: 1, n: 3, b: 3, r: 5, q: 9, k: 0 };
  for (let row of boardState) {
    for (let piece of row) {
      if (piece) {
        if (piece.color === "w") whiteMaterial += pieceValues[piece.type];
        else blackMaterial += pieceValues[piece.type];
      }
    }
  }
  const balance = whiteMaterial - blackMaterial;
  const balanceEl = document.getElementById("stat-material");
  if (balance > 0) {
    balanceEl.textContent = `+${balance}`;
    balanceEl.style.color = "#4caf50";
  } else if (balance < 0) {
    balanceEl.textContent = `${balance}`;
    balanceEl.style.color = "#f44336";
  } else {
    balanceEl.textContent = "0";
    balanceEl.style.color = "#e0e0e0";
  }
}

function updateUI(data, skipHistorySave) {
  const scoreEl = document.getElementById("main-score");
  const trendEl = document.getElementById("score-trend");
  const gaugeFill = document.getElementById("eval-gauge-fill");

  if (data.evaluation !== undefined) {
    const evalVal = data.evaluation;
    const sign = evalVal > 0 ? "+" : "";
    scoreEl.textContent = `${sign}${evalVal.toFixed(2)}`;

    if (evalVal > 0.5) {
      trendEl.textContent = "Przewaga Białych";
      trendEl.style.color = "#4caf50";
      scoreEl.style.color = "#4caf50";
    } else if (evalVal < -0.5) {
      trendEl.textContent = "Przewaga Czarnych";
      trendEl.style.color = "#f44336";
      scoreEl.style.color = "#f44336";
    } else {
      trendEl.textContent = "Równowaga";
      trendEl.style.color = "#a0a0a0";
      scoreEl.style.color = "#e0e0e0";
    }

    const clampedEval = Math.max(-5, Math.min(5, evalVal));
    const percentage = 50 + (clampedEval / 5) * 50;
    gaugeFill.style.height = `${percentage}%`;

    if (!skipHistorySave) {
      updateChart(game.history().length, evalVal);
    }
  }

  if (data.search_time) document.getElementById("stat-time").textContent = `${data.search_time}s`;
  if (data.nodes) document.getElementById("stat-nodes").textContent = formatNumber(data.nodes);
  if (data.nps) document.getElementById("stat-nps").textContent = formatNumber(data.nps);
  if (data.tt_hit_rate !== undefined) document.getElementById("stat-tt-hitrate").textContent = `${data.tt_hit_rate}%`;
  if (data.tt_hashfull !== undefined) {
    const hashfullPct = (data.tt_hashfull / 10).toFixed(1);
    document.getElementById("stat-tt-hashfull-pct").textContent = `${hashfullPct}%`;
    document.getElementById("stat-tt-hashfull-bar").style.width = `${hashfullPct}%`;
  }
  if (data.tt_hits !== undefined) document.getElementById("stat-tt-hits").textContent = formatNumber(data.tt_hits);
  if (data.tt_stores !== undefined) document.getElementById("stat-tt-stores").textContent = formatNumber(data.tt_stores);

  const pvEl = document.getElementById("pv-display");
  if (data.pv) {
    const moves = data.pv.split(" ");
    let html = "";
    moves.forEach((move, index) => {
      const className = index === 0 ? "pv-chip current" : "pv-chip";
      html += `<span class="${className}">${move}</span>`;
    });
    pvEl.innerHTML = html;
  } else {
    pvEl.innerHTML = '<span class="placeholder" style="color: var(--text-muted); font-style: italic;">Brak danych...</span>';
  }

  if (!skipHistorySave) {
    statsHistory.push({
      evaluation: data.evaluation,
      search_time: data.search_time,
      nodes: data.nodes,
      nps: data.nps,
      tt_hit_rate: data.tt_hit_rate,
      tt_hashfull: data.tt_hashfull,
      tt_hits: data.tt_hits,
      tt_stores: data.tt_stores,
      pv: data.pv
    });
  }

  document.getElementById("analytics-overlay").classList.remove("active");
}

function formatNumber(num) {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
  if (num >= 1000) return (num / 1000).toFixed(1) + "k";
  return num.toString();
}

function onSnapEnd() {
  board.position(game.fen());
  updatePGN();
  updateMaterialBalance();

  const depthSlider = document.getElementById("depth-slider");
  const currentDepth = depthSlider ? parseInt(depthSlider.value) : 4;

  document.getElementById("analytics-overlay").classList.add("active");

  fetch("/fen", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fen: game.fen(), depth: currentDepth }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        console.error(data.error);
        document.getElementById("analytics-overlay").classList.remove("active");
        return;
      }

      if (data.move) {
        const from = data.move.substring(0, 2);
        const to = data.move.substring(2, 4);
        const promotion = data.move.length > 4 ? data.move.substring(4, 5) : undefined;
        game.move({ from: from, to: to, promotion: promotion || "q" });
      } else {
        game.load(data.fen);
      }

      board.position(game.fen());
      updatePGN();
      updateMaterialBalance();
      updateUI(data);
    })
    .catch((err) => {
      console.error("Error:", err);
      document.getElementById("analytics-overlay").classList.remove("active");
    });
}

var config = {
  pieceTheme: pieceUrl + "{piece}.svg",
  draggable: true,
  position: "start",
  onDragStart: onDragStart,
  onDrop: onDrop,
  onSnapEnd: onSnapEnd,
  moveSpeed: 300,
  snapbackSpeed: 300,
  snapSpeed: 100,
};

board = Chessboard("board", config);

function resizeBoard() {
  if (board && typeof board.resize === "function") {
    board.resize();
  }
}

window.addEventListener("resize", resizeBoard);

document.addEventListener("DOMContentLoaded", function () {
  initChart();
  resizeBoard();

  document.getElementById("reset-btn").addEventListener("click", function () {
    game.reset();
    board.position("start");
    resizeBoard();
    resetChart();
    updatePGN();
    updateMaterialBalance();
    resetUI();
    document.getElementById("score-trend").textContent = "Start";
  });



  const depthSlider = document.getElementById("depth-slider");
  const depthValue = document.getElementById("depth-value");
  if (depthSlider && depthValue) {
    depthValue.textContent = depthSlider.value;
    const updateSliderProgress = (slider) => {
      const min = parseInt(slider.min);
      const max = parseInt(slider.max);
      const val = parseInt(slider.value);
      const progress = ((val - min) / (max - min)) * 100;
      slider.style.backgroundSize = progress + "% 100%";
    };
    updateSliderProgress(depthSlider);
    depthSlider.addEventListener("input", function () {
      depthValue.textContent = this.value;
      updateSliderProgress(this);
    });
  }
});
