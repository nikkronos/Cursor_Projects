import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from aiohttp import WSMsgType, web


ROOT_DIR = Path(__file__).resolve().parent


Color = str
Piece = Dict[str, Any]
Board = List[List[Optional[Piece]]]


COLOR_ORDER: List[Color] = ["red", "blue", "yellow", "green"]


def create_initial_board() -> Board:
    """Create a simple 14x14 board with four armies.

    This is not an exact copy of any existing 4-player chess layout,
    but it's symmetric and sufficient for casual play:
    - Red at bottom, moving up
    - Yellow at top, moving down
    - Blue at left, moving right
    - Green at right, moving left
    """
    size = 14
    empty_row: List[Optional[Piece]] = [None for _ in range(size)]
    board: Board = [empty_row.copy() for _ in range(size)]

    def place_back_rank(y: int, x_start: int, x_step: int, color: Color) -> None:
        files = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        for i, piece_type in enumerate(files):
            x = x_start + i * x_step
            board[y][x] = {"color": color, "type": piece_type}

    def place_pawns(y: int, x_start: int, x_step: int, color: Color) -> None:
        for i in range(8):
            x = x_start + i * x_step
            board[y][x] = {"color": color, "type": "pawn", "moved": False}

    # Yellow (top, moves down)
    place_back_rank(y=0, x_start=3, x_step=1, color="yellow")
    place_pawns(y=1, x_start=3, x_step=1, color="yellow")

    # Red (bottom, moves up)
    place_back_rank(y=size - 1, x_start=3, x_step=1, color="red")
    place_pawns(y=size - 2, x_start=3, x_step=1, color="red")

    # Blue (left, moves right)
    place_back_rank(y=3, x_start=0, x_step=0, color="blue")  # temporary row
    # For left/right armies, we rotate conceptually: use columns instead of rows.
    # Place blue pieces in a vertical line on the left side.
    blue_files = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
    for i, piece_type in enumerate(blue_files):
        y = 3 + i
        board[y][0] = {"color": "blue", "type": piece_type}
    for i in range(8):
        y = 3 + i
        board[y][1] = {"color": "blue", "type": "pawn", "moved": False}

    # Green (right, moves left)
    green_files = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
    for i, piece_type in enumerate(green_files):
        y = 3 + i
        board[y][size - 1] = {"color": "green", "type": piece_type}
    for i in range(8):
        y = 3 + i
        board[y][size - 2] = {"color": "green", "type": "pawn", "moved": False}

    return board


def rotate_board(board: Board, for_color: Color) -> Board:
    """Rotate the board so the given color's pieces appear at the bottom.
    
    - Red: no rotation (already at bottom)
    - Blue: rotate 90° clockwise (left becomes bottom)
    - Yellow: rotate 180° (top becomes bottom)
    - Green: rotate 90° counter-clockwise (right becomes bottom)
    
    Rotation around center: original (x, y) -> rotated (new_x, new_y)
    """
    size = len(board)
    
    if for_color == "red":
        # No rotation needed - red is already at bottom
        return board
    
    # Create rotated board
    rotated: Board = [[None for _ in range(size)] for _ in range(size)]
    
    if for_color == "blue":
        # Rotate 90° clockwise around center
        # Original (x, y) -> Rotated (y, size-1-x)
        # So rotated[new_y][new_x] = board[y][x] where new_y = y, new_x = size-1-x
        # Actually: rotated[y][size-1-x] = board[y][x]
        # Wait, that's not right. Let me think...
        # If I want original (x, y) to appear at rotated (new_x, new_y):
        # For 90° clockwise: new_x = y, new_y = size-1-x
        for y in range(size):
            for x in range(size):
                new_x = y
                new_y = size - 1 - x
                rotated[new_y][new_x] = board[y][x]
    elif for_color == "yellow":
        # Rotate 180°: (x, y) -> (size-1-x, size-1-y)
        for y in range(size):
            for x in range(size):
                new_x = size - 1 - x
                new_y = size - 1 - y
                rotated[new_y][new_x] = board[y][x]
    elif for_color == "green":
        # Rotate 90° counter-clockwise: (x, y) -> (size-1-y, x)
        for y in range(size):
            for x in range(size):
                new_x = size - 1 - y
                new_y = x
                rotated[new_y][new_x] = board[y][x]
    else:
        # Unknown color, return original
        return board
    
    return rotated


def rotate_coordinates(x: int, y: int, for_color: Color, size: int = 14) -> Tuple[int, int]:
    """Convert coordinates from rotated board (client view) back to original board space.
    
    This is needed when client sends move coordinates - we need to convert
    them back to the original board coordinates.
    
    Inverse of rotate_board:
    - Blue: rotated (x,y) shows original (size-1-y, x), so inverse is (size-1-y, x)
    - Yellow: rotated (x,y) shows original (size-1-x, size-1-y), so inverse is same
    - Green: rotated (x,y) shows original (y, size-1-x), so inverse is (size-1-y, x)
    """
    if for_color == "red":
        return (x, y)
    elif for_color == "blue":
        # rotate_board: original (orig_x, orig_y) -> rotated (orig_y, size-1-orig_x)
        # So rotated (x, y) shows original (size-1-y, x)
        return (size - 1 - y, x)
    elif for_color == "yellow":
        # rotate_board: original (orig_x, orig_y) -> rotated (size-1-orig_x, size-1-orig_y)
        # So rotated (x, y) shows original (size-1-x, size-1-y)
        return (size - 1 - x, size - 1 - y)
    elif for_color == "green":
        # rotate_board: original (orig_x, orig_y) -> rotated (size-1-orig_y, orig_x)
        # So rotated (x, y) shows original (y, size-1-x)
        return (y, size - 1 - x)
    else:
        return (x, y)


def in_bounds(x: int, y: int, size: int = 14) -> bool:
    return 0 <= x < size and 0 <= y < size


def path_is_clear(board: Board, x1: int, y1: int, x2: int, y2: int) -> bool:
    """Check that all squares between (x1,y1) and (x2,y2) are empty."""
    dx = x2 - x1
    dy = y2 - y1
    step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

    cx, cy = x1 + step_x, y1 + step_y
    while (cx, cy) != (x2, y2):
        if board[cy][cx] is not None:
            return False
        cx += step_x
        cy += step_y
    return True


def pawn_direction(color: Color) -> Tuple[int, int]:
    # (dx, dy) for a "forward" move
    if color == "red":
        return 0, -1
    if color == "yellow":
        return 0, 1
    if color == "blue":
        return 1, 0
    if color == "green":
        return -1, 0
    return 0, 0


def can_attack_square(
    board: Board,
    attacker_color: Color,
    target_x: int,
    target_y: int,
) -> bool:
    """Check if any piece of attacker_color can attack the target square."""
    size = len(board)
    for y in range(size):
        for x in range(size):
            piece = board[y][x]
            if piece is None or piece.get("color") != attacker_color:
                continue
            # Don't check self-check when checking if we can attack (would cause recursion)
            legal, _ = is_legal_move(
                board, attacker_color, x, y, target_x, target_y, check_self_check=False
            )
            if legal:
                return True
    return False


def find_king(board: Board, color: Color) -> Optional[Tuple[int, int]]:
    """Find the king of the given color."""
    size = len(board)
    for y in range(size):
        for x in range(size):
            piece = board[y][x]
            if piece and piece.get("type") == "king" and piece.get("color") == color:
                return (x, y)
    return None


def is_in_check(board: Board, color: Color) -> bool:
    """Check if the king of the given color is in check."""
    king_pos = find_king(board, color)
    if king_pos is None:
        return False  # No king = not in check (eliminated)
    kx, ky = king_pos

    # Check if any opponent can attack the king
    for opp_color in COLOR_ORDER:
        if opp_color == color:
            continue
        if can_attack_square(board, opp_color, kx, ky):
            return True
    return False


def is_legal_move(
    board: Board,
    color: Color,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    check_self_check: bool = True,
) -> Tuple[bool, str]:
    """Chess move validation with check/checkmate support.

    - Enforces piece movement patterns and basic blocking.
    - If check_self_check is True, prevents moves that leave own king in check.
    - Pawns can move 1 or 2 squares forward from their starting line and capture diagonally.
    """
    size = len(board)
    if not (in_bounds(x1, y1, size) and in_bounds(x2, y2, size)):
        return False, "out_of_bounds"

    if x1 == x2 and y1 == y2:
        return False, "same_square"

    piece = board[y1][x1]
    if piece is None:
        return False, "no_piece"
    if piece.get("color") != color:
        return False, "not_your_piece"

    target = board[y2][x2]
    if target is not None and target.get("color") == color:
        return False, "own_piece"

    dx = x2 - x1
    dy = y2 - y1
    adx = abs(dx)
    ady = abs(dy)
    ptype = piece.get("type")

    # Knight
    if ptype == "knight":
        if (adx, ady) in [(1, 2), (2, 1)]:
            if check_self_check:
                # Test move
                test_board = [row.copy() for row in board]
                test_board[y1][x1] = None
                test_board[y2][x2] = piece
                if is_in_check(test_board, color):
                    return False, "would_be_in_check"
            return True, ""
        return False, "illegal_knight_move"

    # King
    if ptype == "king":
        if max(adx, ady) == 1:
            if check_self_check:
                # Test move
                test_board = [row.copy() for row in board]
                test_board[y1][x1] = None
                test_board[y2][x2] = piece
                if is_in_check(test_board, color):
                    return False, "would_be_in_check"
            return True, ""
        return False, "illegal_king_move"

    # Rook-like
    if ptype == "rook":
        if dx == 0 or dy == 0:
            if path_is_clear(board, x1, y1, x2, y2):
                if check_self_check:
                    test_board = [row.copy() for row in board]
                    test_board[y1][x1] = None
                    test_board[y2][x2] = piece
                    if is_in_check(test_board, color):
                        return False, "would_be_in_check"
                return True, ""
            return False, "blocked_path"
        return False, "illegal_rook_move"

    # Bishop-like
    if ptype == "bishop":
        if adx == ady and adx != 0:
            if path_is_clear(board, x1, y1, x2, y2):
                if check_self_check:
                    test_board = [row.copy() for row in board]
                    test_board[y1][x1] = None
                    test_board[y2][x2] = piece
                    if is_in_check(test_board, color):
                        return False, "would_be_in_check"
                return True, ""
            return False, "blocked_path"
        return False, "illegal_bishop_move"

    # Queen
    if ptype == "queen":
        if (dx == 0 or dy == 0) or (adx == ady and adx != 0):
            if path_is_clear(board, x1, y1, x2, y2):
                if check_self_check:
                    test_board = [row.copy() for row in board]
                    test_board[y1][x1] = None
                    test_board[y2][x2] = piece
                    if is_in_check(test_board, color):
                        return False, "would_be_in_check"
                return True, ""
            return False, "blocked_path"
        return False, "illegal_queen_move"

    # Pawn
    if ptype == "pawn":
        fdx, fdy = pawn_direction(color)
        if fdx == 0 and fdy == 0:
            return False, "unknown_color"

        # Forward move
        if (dx, dy) == (fdx, fdy):
            if target is None:
                if check_self_check:
                    test_board = [row.copy() for row in board]
                    test_board[y1][x1] = None
                    test_board[y2][x2] = piece
                    if is_in_check(test_board, color):
                        return False, "would_be_in_check"
                return True, ""
            return False, "pawn_forward_blocked"

        # Two-square forward from starting line
        if (dx, dy) == (2 * fdx, 2 * fdy) and target is None:
            # one square ahead must also be empty
            mid_x = x1 + fdx
            mid_y = y1 + fdy
            if not in_bounds(mid_x, mid_y, size) or board[mid_y][mid_x] is not None:
                return False, "pawn_forward_blocked"

            # starting lines
            if color == "red" and y1 == size - 2:
                if check_self_check:
                    test_board = [row.copy() for row in board]
                    test_board[y1][x1] = None
                    test_board[y2][x2] = piece
                    if is_in_check(test_board, color):
                        return False, "would_be_in_check"
                return True, ""
            if color == "yellow" and y1 == 1:
                if check_self_check:
                    test_board = [row.copy() for row in board]
                    test_board[y1][x1] = None
                    test_board[y2][x2] = piece
                    if is_in_check(test_board, color):
                        return False, "would_be_in_check"
                return True, ""
            if color == "blue" and x1 == 1:
                if check_self_check:
                    test_board = [row.copy() for row in board]
                    test_board[y1][x1] = None
                    test_board[y2][x2] = piece
                    if is_in_check(test_board, color):
                        return False, "would_be_in_check"
                return True, ""
            if color == "green" and x1 == size - 2:
                if check_self_check:
                    test_board = [row.copy() for row in board]
                    test_board[y1][x1] = None
                    test_board[y2][x2] = piece
                    if is_in_check(test_board, color):
                        return False, "would_be_in_check"
                return True, ""
            return False, "pawn_not_on_start_rank"

        # Capture diagonally (depending on orientation)
        if fdx == 0:  # vertical pawns (red, yellow)
            if adx == 1 and dy == fdy and target is not None and target.get("color") != color:
                if check_self_check:
                    test_board = [row.copy() for row in board]
                    test_board[y1][x1] = None
                    test_board[y2][x2] = piece
                    if is_in_check(test_board, color):
                        return False, "would_be_in_check"
                return True, ""
        else:  # horizontal pawns (blue, green)
            if ady == 1 and dx == fdx and target is not None and target.get("color") != color:
                if check_self_check:
                    test_board = [row.copy() for row in board]
                    test_board[y1][x1] = None
                    test_board[y2][x2] = piece
                    if is_in_check(test_board, color):
                        return False, "would_be_in_check"
                return True, ""

        return False, "illegal_pawn_move"

    return False, "unknown_piece_type"


def has_legal_moves(board: Board, color: Color) -> bool:
    """Check if the given color has any legal moves."""
    size = len(board)
    for y1 in range(size):
        for x1 in range(size):
            piece = board[y1][x1]
            if piece is None or piece.get("color") != color:
                continue
            for y2 in range(size):
                for x2 in range(size):
                    legal, _ = is_legal_move(board, color, x1, y1, x2, y2, check_self_check=True)
                    if legal:
                        return True
    return False


def is_checkmated(board: Board, color: Color) -> bool:
    """Check if the given color is checkmated."""
    if not is_in_check(board, color):
        return False
    return not has_legal_moves(board, color)


class GameState:
    def __init__(self) -> None:
        self.board: Board = create_initial_board()
        self.current_turn_index: int = 0  # index in COLOR_ORDER
        self.players: Dict[Color, Optional[web.WebSocketResponse]] = {
            color: None for color in COLOR_ORDER
        }
        self.game_over: bool = False
        self.winner: Optional[Color] = None
        self.eliminated: List[Color] = []

    @property
    def current_color(self) -> Color:
        return COLOR_ORDER[self.current_turn_index]

    def to_dict(self, for_color: Optional[Color] = None) -> Dict[str, Any]:
        """Return game state, optionally rotated for a specific player."""
        board = self.board
        # Rotate board so player's color is at the bottom
        if for_color:
            board = rotate_board(self.board, for_color)
        
        return {
            "board": board,
            "currentColor": self.current_color,
            "colors": COLOR_ORDER,
            "gameOver": self.game_over,
            "winner": self.winner,
            "eliminated": self.eliminated,
            "inCheck": is_in_check(self.board, self.current_color) if not self.game_over else False,
        }

    def advance_turn(self) -> None:
        # Skip eliminated players
        attempts = 0
        while attempts < len(COLOR_ORDER):
            self.current_turn_index = (self.current_turn_index + 1) % len(COLOR_ORDER)
            if COLOR_ORDER[self.current_turn_index] not in self.eliminated:
                break
            attempts += 1


game_state = GameState()
connected_sockets: List[web.WebSocketResponse] = []


def is_websocket_alive(ws: Optional[web.WebSocketResponse]) -> bool:
    """Check if websocket connection is still alive."""
    if ws is None:
        return False
    try:
        # Check if connection is closed
        if ws.closed:
            return False
        # Check if it's in connected_sockets list
        if ws not in connected_sockets:
            return False
        return True
    except Exception:
        return False


async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    try:
        await ws.prepare(request)
        print(f"[CONNECT] New WebSocket connection established")
    except Exception as e:
        print(f"[ERROR] Failed to prepare WebSocket: {e}")
        return ws

    connected_sockets.append(ws)
    print(f"[CONNECT] Total connected sockets: {len(connected_sockets)}")

    # Clean up any dead connections first
    cleaned_count = 0
    for color in COLOR_ORDER:
        existing_ws = game_state.players[color]
        if not is_websocket_alive(existing_ws):
            if existing_ws is not None:
                if existing_ws in connected_sockets:
                    connected_sockets.remove(existing_ws)
                    cleaned_count += 1
            game_state.players[color] = None
            print(f"[CLEANUP] Freed slot for color: {color}")
    
    if cleaned_count > 0:
        print(f"[CLEANUP] Cleaned up {cleaned_count} dead connections")

    # Assign a color if available
    assigned_color: Optional[Color] = None
    for color in COLOR_ORDER:
        if game_state.players[color] is None:
            game_state.players[color] = ws
            assigned_color = color
            print(f"[CONNECT] Player assigned color: {color} (slots: {[c for c in COLOR_ORDER if game_state.players[c] is not None]})")
            break

    if assigned_color is None:
        print(f"[CONNECT] No free slots, player connected as spectator (all slots: {[c for c in COLOR_ORDER if game_state.players[c] is not None]})")

    try:
        await ws.send_json({"type": "assign", "color": assigned_color})
        print(f"[CONNECT] Sent assign message to player (color: {assigned_color})")
    except Exception as e:
        print(f"[ERROR] Failed to send assign message: {e}")

    # Send current state (rotated for this player)
    try:
        await ws.send_json({"type": "state", "state": game_state.to_dict(for_color=assigned_color)})
        print(f"[CONNECT] Sent initial state to player (color: {assigned_color})")
    except Exception as e:
        print(f"[ERROR] Failed to send initial state: {e}")

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                except json.JSONDecodeError:
                    try:
                        await ws.send_json({"type": "error", "reason": "invalid_json"})
                    except Exception:
                        pass  # Connection might be closed
                    continue

                try:
                    if data.get("type") == "move":
                        await handle_move(ws, data)
                    elif data.get("type") == "get_moves":
                        await handle_get_moves(ws, data)
                except Exception as e:
                    print(f"[ERROR] Error handling message: {e}")
                    try:
                        await ws.send_json({"type": "error", "reason": str(e)})
                    except Exception:
                        pass  # Connection might be closed
            elif msg.type == WSMsgType.ERROR:
                print(f"[ERROR] WebSocket error for connection")
            elif msg.type == WSMsgType.CLOSE:
                print(f"[DISCONNECT] WebSocket close message received")
                break
    except (ConnectionResetError, ConnectionError, RuntimeError) as e:
        print(f"[DISCONNECT] Connection error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error in websocket handler: {e}")
    finally:
        # Cleanup on disconnect - always execute
        disconnected_color = None
        for color, sock in list(game_state.players.items()):
            if sock is ws:
                game_state.players[color] = None
                disconnected_color = color
                print(f"[DISCONNECT] Player {color} disconnected (cleanup)")
                break

        if ws in connected_sockets:
            connected_sockets.remove(ws)

        # Notify other players about the disconnection (only if we have a color)
        if disconnected_color:
            try:
                asyncio.create_task(broadcast({
                    "type": "player_disconnected",
                    "color": disconnected_color
                }))
            except Exception as e:
                print(f"[ERROR] Failed to broadcast disconnection: {e}")

    return ws


async def broadcast(message: Dict[str, Any]) -> None:
    """Broadcast message to all connected clients.
    
    If message type is "state", rotate board for each player's color.
    """
    dead: List[web.WebSocketResponse] = []
    for ws in list(connected_sockets):  # Use list copy to avoid modification during iteration
        try:
            if ws.closed:
                dead.append(ws)
            else:
                # If it's a state update, rotate board for each player
                if message.get("type") == "state" and "state" in message:
                    # Find player color for this websocket
                    player_color: Optional[Color] = None
                    for color, sock in game_state.players.items():
                        if sock is ws:
                            player_color = color
                            break
                    
                    # Create rotated state for this player
                    rotated_state = message["state"].copy()
                    if player_color:
                        # Rotate the board for this player's view
                        rotated_state["board"] = rotate_board(game_state.board, player_color)
                    # If no color (spectator), send original board
                    
                    await ws.send_json({"type": "state", "state": rotated_state})
                else:
                    await ws.send_json(message)
        except (ConnectionResetError, ConnectionError, RuntimeError, Exception) as e:
            dead.append(ws)
            print(f"[BROADCAST] Error sending to client: {e}")
    
    # Clean up dead connections
    for ws in dead:
        if ws in connected_sockets:
            connected_sockets.remove(ws)
        # Free up color slot
        for color, sock in list(game_state.players.items()):
            if sock is ws:
                game_state.players[color] = None
                print(f"[CLEANUP] Freed color slot: {color}")
                break


async def handle_get_moves(ws: web.WebSocketResponse, data: Dict[str, Any]) -> None:
    """Return possible moves for a selected piece."""
    color: Optional[Color] = None
    for c, sock in game_state.players.items():
        if sock is ws:
            color = c
            break

    if color is None:
        await ws.send_json({"type": "error", "reason": "spectator_cannot_move"})
        return

    try:
        x = int(data["x"])
        y = int(data["y"])
    except (KeyError, ValueError, TypeError):
        await ws.send_json({"type": "error", "reason": "invalid_coordinates"})
        return

    # Convert from rotated coordinates to original board coordinates
    size = len(game_state.board)
    orig_x, orig_y = rotate_coordinates(x, y, color, size)
    
    piece = game_state.board[orig_y][orig_x]
    if not piece or piece.get("color") != color:
        await ws.send_json({"type": "moves", "moves": []})
        return

    possible_moves = []
    for y2 in range(size):
        for x2 in range(size):
            legal, _ = is_legal_move(
                game_state.board, color, orig_x, orig_y, x2, y2, check_self_check=True
            )
            if legal:
                # Convert original coordinates to rotated coordinates for client
                # This is the forward rotation (same as rotate_board logic)
                if color == "red":
                    rot_x2, rot_y2 = x2, y2
                elif color == "blue":
                    # Forward: original (x2, y2) -> rotated (y2, size-1-x2)
                    rot_x2, rot_y2 = y2, size - 1 - x2
                elif color == "yellow":
                    # Forward: original (x2, y2) -> rotated (size-1-x2, size-1-y2)
                    rot_x2, rot_y2 = size - 1 - x2, size - 1 - y2
                elif color == "green":
                    # Forward: original (x2, y2) -> rotated (size-1-y2, x2)
                    rot_x2, rot_y2 = size - 1 - y2, x2
                else:
                    rot_x2, rot_y2 = x2, y2
                
                possible_moves.append({"x": rot_x2, "y": rot_y2})

    await ws.send_json({"type": "moves", "moves": possible_moves})


async def handle_move(ws: web.WebSocketResponse, data: Dict[str, Any]) -> None:
    color: Optional[Color] = None
    for c, sock in game_state.players.items():
        if sock is ws:
            color = c
            break

    if color is None:
        await ws.send_json({"type": "error", "reason": "spectator_cannot_move"})
        return

    if color != game_state.current_color:
        await ws.send_json({"type": "error", "reason": "not_your_turn"})
        return

    try:
        x1 = int(data["from"]["x"])
        y1 = int(data["from"]["y"])
        x2 = int(data["to"]["x"])
        y2 = int(data["to"]["y"])
    except (KeyError, ValueError, TypeError):
        await ws.send_json({"type": "error", "reason": "invalid_move_payload"})
        return

    # Convert from rotated coordinates (client view) to original board coordinates
    size = len(game_state.board)
    orig_x1, orig_y1 = rotate_coordinates(x1, y1, color, size)
    orig_x2, orig_y2 = rotate_coordinates(x2, y2, color, size)

    legal, reason = is_legal_move(game_state.board, color, orig_x1, orig_y1, orig_x2, orig_y2)
    if not legal:
        await ws.send_json({"type": "invalid_move", "reason": reason})
        return

    # Apply move (using original coordinates)
    piece = game_state.board[orig_y1][orig_x1]
    target = game_state.board[orig_y2][orig_x2]

    # Simple promotion: pawn reaching far edge becomes queen
    if piece and piece.get("type") == "pawn":
        if (
            (color == "red" and orig_y2 == 0)
            or (color == "yellow" and orig_y2 == size - 1)
            or (color == "blue" and orig_x2 == size - 1)
            or (color == "green" and orig_x2 == 0)
        ):
            piece = {"color": color, "type": "queen"}
        else:
            piece["moved"] = True

    game_state.board[orig_y1][orig_x1] = None
    game_state.board[orig_y2][orig_x2] = piece

    # Check if a king was captured
    if target and target.get("type") == "king":
        eliminated_color = target.get("color")
        if eliminated_color not in game_state.eliminated:
            game_state.eliminated.append(eliminated_color)

    # Check for checkmate on all remaining players
    remaining_colors = [c for c in COLOR_ORDER if c not in game_state.eliminated]
    checkmated_colors = []
    for c in remaining_colors:
        if is_checkmated(game_state.board, c):
            checkmated_colors.append(c)

    # Eliminate checkmated players
    for c in checkmated_colors:
        if c not in game_state.eliminated:
            game_state.eliminated.append(c)

    # Check if game is over (only one player left)
    remaining_colors = [c for c in COLOR_ORDER if c not in game_state.eliminated]
    if len(remaining_colors) <= 1:
        game_state.game_over = True
        game_state.winner = remaining_colors[0] if remaining_colors else None
    else:
        game_state.advance_turn()

    # Broadcast will handle rotation for each player
    await broadcast({"type": "state", "state": game_state.to_dict()})


async def index_handler(request: web.Request) -> web.Response:
    html_path = ROOT_DIR / "index.html"
    content = html_path.read_text(encoding="utf-8")
    return web.Response(text=content, content_type="text/html")


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", index_handler)
    app.router.add_get("/ws", websocket_handler)
    app.router.add_static("/static/", ROOT_DIR / "static", show_index=False)
    return app


def get_local_ip() -> str:
    """Get local IP address."""
    import socket
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_public_ip() -> str:
    """Get public IP address."""
    import urllib.request
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=3) as response:
            return response.read().decode("utf-8")
    except Exception:
        return "не удалось определить"


def main() -> None:
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    print("=" * 60)
    print("Сервер запущен!")
    print(f"Локальный IP: {local_ip}")
    print(f"Публичный IP: {public_ip}")
    print("=" * 60)
    print(f"\nДля игры на этой машине: http://localhost:8000/")
    print(f"Для игры в локальной сети: http://{local_ip}:8000/")
    if public_ip != "не удалось определить":
        print(f"\n🌐 Для игры через интернет с туннелем:")
        print(f"   Пароль туннеля (Tunnel Password): {public_ip}")
        print(f"   (Это ваш публичный IP адрес)")
        print(f"\n   Отправьте друзьям:")
        print(f"   1. URL туннеля (из окна с localtunnel)")
        print(f"   2. Пароль: {public_ip}")
    print("=" * 60)
    print("\nНажмите CTRL+C для остановки сервера\n")
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

