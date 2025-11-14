# ♟️ Chess Vision Agent — Human-Like Autonomous Chess Player

An end-to-end AI agent that **plays chess like a human**, combining **computer vision**, a **multimodal vision-language model (LLaVA)**, and the **Stockfish chess engine**.

The agent can observe a chessboard (desktop or web platform like Chess.com), understand the current position visually, decide the best move using Stockfish, and physically execute the move via mouse or browser automation.

---

## 🧠 Core Idea

> **See → Understand → Think → Act → Repeat**

This project fuses **vision intelligence** with **chess reasoning**.  
Instead of relying on raw game APIs, it interacts with the chess interface like a real human would — by visually perceiving and physically playing moves.

---

## 📜 Table of Contents

1. [Features](#-features)
2. [System Architecture](#-system-architecture)
3. [Workflow](#-workflow)
4. [Project Structure](#-project-structure)
5. [Installation](#-installation)
6. [Configuration](#-configuration)
7. [Usage](#-usage)
8. [Core Modules Explained](#-core-modules-explained)
9. [Error Handling](#-error-handling)
10. [Future Enhancements](#-future-enhancements)
11. [Credits & License](#-credits--license)

---

## ✨ Features

- 🎥 **Vision-based perception** — understands the board purely from images.  
- 🧩 **LLaVA model integration** — detects chess pieces and their locations.  
- ♟️ **Stockfish reasoning** — computes best moves using world-class chess logic.  
- 🖱️ **GUI automation** — performs moves with realistic human-like behavior.  
- 🕵️ **Platform agnostic** — works on web (Chess.com) or desktop apps.  
- ⚙️ **Modular architecture** — each subsystem is independently upgradable.  

---

## 🧭 System Architecture

```mermaid
flowchart TD

A[Screen Capture / Webcam] --> B[Board Detection & Preprocessing]
B --> C[LLaVA Model - Piece Recognition]
C --> D[FEN Converter]
D --> E[Stockfish Engine]
E --> F[Move Mapping & Automation]
F --> G[Humanizer Module]
G --> H[GUI Interaction (Desktop/Web)]
H --> I[Opponent Move Detected]
I --> A

style A fill:#333,stroke:#fff,stroke-width:1px,color:#fff
style E fill:#f39c12,stroke:#fff,stroke-width:1px,color:#fff
style C fill:#2ecc71,stroke:#fff,stroke-width:1px,color:#fff
style F fill:#3498db,stroke:#fff,stroke-width:1px,color:#fff
style H fill:#9b59b6,stroke:#fff,stroke-width:1px,color:#fff





🧠 High-Level Goal

You’re building an autonomous chess-playing agent that:

Sees the board (via LLaVA vision model),

Thinks using Stockfish,

Acts on a GUI (desktop or Chess.com),

Repeats in real time.

So let’s structure the system into 5 core Python modules.

🧩 1. Project Architecture Overview
Folder Structure Example
chess_agent/
│
├── main.py                      # entry point: orchestrates everything
├── config.yaml                  # configuration for paths, delays, etc.
│
├── vision/
│   ├── capture.py               # screen capture & preprocessing
│   ├── board_detection.py       # detect & crop chessboard region
│   ├── piece_recognition.py     # LLaVA inference to identify pieces
│   └── fen_converter.py         # convert detected pieces → FEN
│
├── engine/
│   ├── stockfish_wrapper.py     # interface to Stockfish engine
│   └── move_validator.py        # ensure legal moves, sync states
│
├── control/
│   ├── move_executor.py         # automation (mouse/keyboard/web)
│   ├── mapping_utils.py         # pixel ↔ chessboard square mapping
│   └── humanizer.py             # add randomization/delays
│
├── utils/
│   ├── logger.py                # unified logging & error tracking
│   └── helpers.py               # utility functions
│
└── tests/                       # unit tests for each module

⚙️ 2. Module-by-Module Blueprint
🖼️ A. Vision System
1. capture.py

Purpose: Capture the current game board from the screen or browser.

Responsibilities:

Identify chessboard window or screen region (via template matching or manual ROI).

Use mss or pyautogui.screenshot() to capture image frames.

Optional: detect board rotation (e.g., white at bottom).

Input: None
Output: board_image (numpy array or PIL image)

2. board_detection.py

Purpose: Detect exact board boundaries and crop.

Responsibilities:

Locate 8x8 board grid from full screenshot.

Optionally detect coordinate overlay (a1–h8 orientation).

Normalize size (e.g., 512×512 px) for model consistency.

Output: Cropped, normalized board image.

3. piece_recognition.py

Purpose: Use LLaVA to identify piece type & color on each square.

Responsibilities:

Load llava-hf/llava-v1.6-34b-hf.

Query model with prompt like:

“Describe the position of all chess pieces in this board image. Return JSON with square and piece type (e.g. 'e4: white pawn').”

Parse LLaVA’s textual output into a structured dictionary:

{
  "a1": "white rook",
  "b1": "white knight",
  ...
}


Output: piece_dict (square → piece)

4. fen_converter.py

Purpose: Convert recognized board into valid FEN notation.

Responsibilities:

Convert 8x8 piece map → FEN string.

Include side-to-move, castling rights, etc. (defaults if unknown).

Validate with python-chess.

Output: fen_string

♟️ B. Engine System
1. stockfish_wrapper.py

Purpose: Manage Stockfish engine lifecycle and queries.

Responsibilities:

Initialize Stockfish binary via stockfish or python-chess.engine.

Set difficulty (Elo, depth, move time).

Pass FEN → get best move (uci string, e.g., e2e4).

Output: Best move string

API Example:

engine = StockfishWrapper("/path/to/stockfish")
best_move = engine.get_best_move(fen, depth=15)

2. move_validator.py

Purpose: Ensure move legality & sync board state.

Responsibilities:

Keep internal python-chess.Board updated.

Validate Stockfish’s move matches possible moves.

Detect discrepancies (e.g., vision misread) and trigger board recapture.

🖱️ C. Control System (Actuation)
1. mapping_utils.py

Purpose: Translate board squares (e.g., e2) → pixel coordinates.

Responsibilities:

Given board bounding box (x, y, width, height), compute per-square pixels.

Handle both color orientations (white bottom vs. black bottom).

API Example:

(x1, y1), (x2, y2) = get_square_pixels('e2', 'e4', board_bbox)

2. move_executor.py

Purpose: Physically make the move.

Responsibilities:

Read Stockfish’s e2e4 → pixel mapping.

Use:

pyautogui (desktop)

selenium or playwright (web)

Click & drag from source → destination.

Verify visually that move succeeded.

Input: move string, board coordinates
Output: Updated screen (after move)

3. humanizer.py

Purpose: Make the agent appear human.

Responsibilities:

Add randomized delay (0.8–3s) before move.

Add small pixel jitter in cursor movement.

Occasionally “hover” before clicking.

Maintain logs for realism tuning.

🧩 D. Orchestration (main.py)

Purpose: Glue everything together.

Main Loop Pseudocode:

while True:
    image = capture_board()
    board_image = detect_board(image)
    piece_map = recognize_pieces(board_image)
    fen = to_fen(piece_map)
    
    best_move = stockfish.get_best_move(fen)
    make_move(best_move)
    
    wait_for_opponent_move()


Optional Enhancements:

Threaded architecture for async processing.

Error recovery loop (if board mismatch).

UI overlay showing detected move & confidence.

🛠️ E. Configuration & Utilities
config.yaml

Example:

board_region: [100, 200, 800, 800]
move_delay_range: [1.0, 3.5]
stockfish_path: "C:/engines/stockfish.exe"
difficulty: 5
chess_platform: "chess.com"
orientation: "white"

logger.py

Centralized logging for:

Vision model confidence.

Move execution timing.

Error recovery.

🔄 3. Full Data Flow Summary
[Screen] 
   ↓ (capture.py)
[Raw Image]
   ↓ (board_detection.py)
[Cropped Board]
   ↓ (piece_recognition.py - LLaVA)
[Piece Map]
   ↓ (fen_converter.py)
[FEN]
   ↓ (stockfish_wrapper.py)
[Best Move]
   ↓ (mapping_utils + move_executor)
[Move Played]
   ↓
[Loop back to screen]