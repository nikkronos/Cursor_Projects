const boardElement = document.getElementById("board");
const statusElement = document.getElementById("status");
const myColorElement = document.getElementById("my-color");
const logElement = document.getElementById("log-entries");

let ws = null;
let myColor = null;
let gameState = null;
let selectedSquare = null; // {x, y}
let possibleMoves = []; // [{x, y}, ...]

function colorToLabel(color) {
    switch (color) {
        case "red":
            return "Красный";
        case "blue":
            return "Синий";
        case "yellow":
            return "Жёлтый";
        case "green":
            return "Зелёный";
        default:
            return "—";
    }
}

function updateMyColorBadge() {
    myColorElement.className = "color-badge";
    if (!myColor) {
        myColorElement.classList.add("color-unknown");
        myColorElement.textContent = "Ожидание…";
        return;
    }
    myColorElement.classList.add(`color-${myColor}`);
    myColorElement.textContent = colorToLabel(myColor);
}

function appendLog(text) {
    const div = document.createElement("div");
    div.className = "log-entry";
    div.textContent = text;
    logElement.appendChild(div);
    logElement.scrollTop = logElement.scrollHeight;
}

function coordToString(x, y) {
    return `${x},${y}`;
}

function pieceTypeToLabel(type) {
    const labels = {
        king: "Ко",
        queen: "Ф",
        knight: "К",
        bishop: "С",
        rook: "Л",
        pawn: "П",
    };
    return labels[type] || type[0].toUpperCase();
}

// Server now sends rotated board, so no coordinate transformation needed

function renderBoard() {
    if (!gameState) return;

    const size = gameState.board.length;
    boardElement.innerHTML = "";

    // Server sends already rotated board, so we just render it as-is
    for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
            const square = document.createElement("div");
            square.className = "square";
            const isLight = (x + y) % 2 === 0;
            square.classList.add(isLight ? "light" : "dark");

            if (selectedSquare && selectedSquare.x === x && selectedSquare.y === y) {
                square.classList.add("selected");
            }

            // Highlight possible moves
            if (possibleMoves.some((move) => move.x === x && move.y === y)) {
                square.classList.add("possible-move");
            }

            // Get piece from board (already rotated by server)
            const piece = gameState.board[y][x];
            if (piece) {
                const pieceDiv = document.createElement("div");
                pieceDiv.className = `piece ${piece.color}`;

                const label = document.createElement("span");
                label.className = "piece-label";
                label.textContent = pieceTypeToLabel(piece.type);

                pieceDiv.appendChild(label);
                square.appendChild(pieceDiv);
            }

            square.addEventListener("click", () => onSquareClick(x, y));
            boardElement.appendChild(square);
        }
    }

    if (gameState.gameOver) {
        if (gameState.winner) {
            statusElement.textContent = `Игра окончена! Победитель: ${colorToLabel(gameState.winner)}.`;
        } else {
            statusElement.textContent = "Игра окончена. Ничья.";
        }
        return;
    }

    const yourTurn =
        myColor && gameState.currentColor && myColor === gameState.currentColor;
    const inCheck = gameState.inCheck || false;
    const currentColorLabel = colorToLabel(gameState.currentColor);

    if (yourTurn) {
        if (inCheck) {
            statusElement.textContent = `ШАХ! Ваш ход (${colorToLabel(myColor)}).`;
        } else {
            statusElement.textContent = `Ваш ход (${colorToLabel(myColor)}).`;
        }
    } else if (gameState.currentColor) {
        if (inCheck) {
            statusElement.textContent = `ШАХ! Ходит: ${currentColorLabel}.`;
        } else {
            statusElement.textContent = `Ходит: ${currentColorLabel}.`;
        }
    } else {
        statusElement.textContent = "Ожидание начала игры…";
    }

    // Check for checkmate
    if (gameState.eliminated && gameState.eliminated.length > 0) {
        const eliminatedLabels = gameState.eliminated.map(colorToLabel).join(", ");
        appendLog(`Игроки выбыли: ${eliminatedLabels}.`);
    }
}

function onSquareClick(x, y) {
    if (!gameState || !myColor || gameState.gameOver) return;

    const piece = gameState.board[y][x];
    const yourTurn = myColor === gameState.currentColor;

    // Первая клик — выбираем свою фигуру
    if (!selectedSquare) {
        if (!piece || piece.color !== myColor) {
            return;
        }
        if (!yourTurn) {
            appendLog("Сейчас не ваш ход.");
            return;
        }
        selectedSquare = { x, y };
        possibleMoves = [];
        // Request possible moves from server
        ws?.send(
            JSON.stringify({
                type: "get_moves",
                x,
                y,
            })
        );
        return;
    }

    // Если кликнули на ту же фигуру — снимаем выбор
    if (selectedSquare.x === x && selectedSquare.y === y) {
        selectedSquare = null;
        possibleMoves = [];
        renderBoard();
        return;
    }

    // Если кликнули на другую свою фигуру — выбираем её
    if (piece && piece.color === myColor) {
        selectedSquare = { x, y };
        possibleMoves = [];
        ws?.send(
            JSON.stringify({
                type: "get_moves",
                x,
                y,
            })
        );
        return;
    }

    // Вторая клик — попытка хода
    const from = selectedSquare;
    const to = { x, y };
    selectedSquare = null;
    possibleMoves = [];
    renderBoard();

    if (!yourTurn) {
        appendLog("Сейчас не ваш ход.");
        return;
    }

    ws?.send(
        JSON.stringify({
            type: "move",
            from,
            to,
        })
    );
}

function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const url = `${protocol}://${window.location.host}/ws`;
    
    console.log(`[WS] Connecting to: ${url}`);
    appendLog(`Подключение к ${url}...`);

    ws = new WebSocket(url);

    ws.onopen = () => {
        console.log("[WS] Connection opened");
        statusElement.textContent = "Подключено. Ожидаем назначения цвета…";
        appendLog("Подключено к серверу.");
    };

    ws.onmessage = (event) => {
        let msg;
        try {
            msg = JSON.parse(event.data);
        } catch (e) {
            console.error("Failed to parse message:", event.data, e);
            appendLog(`Ошибка получения сообщения: ${e.message}`);
            return;
        }

        if (msg.type === "assign") {
            console.log(`[WS] Received assign message, color: ${msg.color}`);
            myColor = msg.color;
            updateMyColorBadge();
            if (!myColor) {
                appendLog("Вы подключены как зритель (мест для игроков нет).");
                statusElement.textContent =
                    "Вы зритель. Игру могут вести первые четыре подключившихся.";
            } else {
                appendLog(`Вам назначен цвет: ${colorToLabel(myColor)}.`);
                console.log(`[WS] Assigned color: ${myColor}`);
                // Server will send rotated board, so just re-render if we have state
                if (gameState) {
                    renderBoard();
                }
            }
            return;
        }

        if (msg.type === "player_disconnected") {
            appendLog(`Игрок ${colorToLabel(msg.color)} отключился.`);
            return;
        }

        if (msg.type === "state") {
            gameState = msg.state;
            // Clear selection if game is over or turn changed
            if (gameState.gameOver || (selectedSquare && gameState.currentColor !== myColor)) {
                selectedSquare = null;
                possibleMoves = [];
            }
            renderBoard();
            if (gameState.gameOver && gameState.winner === myColor) {
                appendLog("🎉 Вы победили!");
            } else if (gameState.gameOver && gameState.winner) {
                appendLog(`Игра окончена. Победитель: ${colorToLabel(gameState.winner)}.`);
            }
            return;
        }

        if (msg.type === "moves") {
            possibleMoves = msg.moves || [];
            renderBoard();
            return;
        }

        if (msg.type === "invalid_move") {
            appendLog(`Ход отклонён: ${msg.reason}.`);
            selectedSquare = null;
            possibleMoves = [];
            renderBoard();
            return;
        }

        if (msg.type === "error") {
            appendLog(`Ошибка: ${msg.reason}.`);
            return;
        }
    };

    ws.onclose = (event) => {
        if (event.wasClean) {
            statusElement.textContent = "Соединение закрыто. Обновите страницу для переподключения.";
            appendLog("Соединение закрыто.");
        } else {
            statusElement.textContent = "Соединение разорвано. Обновите страницу для переподключения.";
            appendLog(`Соединение разорвано (код: ${event.code}).`);
        }
    };
}

connectWebSocket();

