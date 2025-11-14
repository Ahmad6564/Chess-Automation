# Chess Vision Agent - Setup & Usage Guide

## 🚀 Quick Start

### 1. Installation

#### Prerequisites
- Python 3.8 or higher
- CUDA-capable GPU (recommended for LLaVA model)
- Stockfish chess engine

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Install Stockfish
Download from: https://stockfishchess.org/download/

**Windows:**
- Download the Windows executable
- Extract to a folder (e.g., `C:\Stockfish\`)
- Update `config.yaml` with the path, or leave as `null` for auto-detection

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install stockfish

# Mac
brew install stockfish
```

### 2. Initial Setup

#### Configure Board Region
Run the setup wizard to define your chessboard location:

```bash
python main.py --setup
```

This will:
1. Ask you to click on the **center** of the chessboard
2. Ask for the board size (default: 800 pixels)
3. Automatically update `config.yaml`

#### Manual Configuration
Alternatively, edit `config.yaml` directly:

```yaml
board_region:
  left: 100      # X coordinate of top-left corner
  top: 100       # Y coordinate of top-left corner
  width: 800     # Board width in pixels
  height: 800    # Board height in pixels

orientation: white  # 'white' or 'black' (which color is at bottom)
```

### 3. Run the Agent

```bash
python main.py
```

The agent will:
1. Capture the current board position
2. Recognize pieces using LLaVA
3. Calculate the best move with Stockfish
4. Execute the move with human-like behavior
5. Wait for opponent's move
6. Repeat

## ⚙️ Configuration

### Vision Model Settings

```yaml
vision_model:
  # Smaller, faster model (recommended for most users)
  model_name: llava-hf/llava-v1.6-mistral-7b-hf
  
  # Larger, more accurate model (requires more VRAM)
  # model_name: llava-hf/llava-v1.6-34b-hf
  
  target_size: [512, 512]
```

### Stockfish Settings

```yaml
stockfish:
  skill_level: 20    # 0-20 (20 = strongest)
  depth: 15          # Search depth
  time_limit: 1.0    # Time per move (seconds)
```

### Humanizer Settings

Make the agent play more like a human:

```yaml
humanizer:
  enabled: true
  min_delay: 1.0        # Minimum thinking time
  max_delay: 3.5        # Maximum thinking time
  skill_level: 7        # 1-10 (affects speed and precision)
  jitter_pixels: 3      # Mouse movement randomness
  hover_probability: 0.3  # Chance to hover before clicking
```

## 📊 Usage Examples

### Basic Usage

```python
from main import ChessAgent

# Create and run agent
with ChessAgent('config.yaml') as agent:
    agent.run()
```

### Play a Single Move

```python
agent = ChessAgent()

# Analyze board
fen = agent.capture_and_analyze_board()

# Calculate best move
move = agent.calculate_best_move(fen)

# Execute move
agent.execute_move_on_board(move)
```

### Custom Configuration

```python
# Load custom config
agent = ChessAgent('my_custom_config.yaml')

# Adjust settings on the fly
agent.engine.skill_level = 10
agent.humanizer.set_skill_level(5)

agent.run()
```

## 🎯 Workflow Modes

### Manual Mode (Default)
The agent waits for you to press Enter after each opponent move:

```yaml
game_loop:
  opponent_move_detection: manual
```

### Continuous Mode
For fully autonomous play (detection logic not yet implemented):

```yaml
game_loop:
  opponent_move_detection: auto
```

## 🔧 Troubleshooting

### Issue: "Stockfish not found"
**Solution:** 
- Download Stockfish from the official website
- Place in a known location
- Update `config.yaml`:
  ```yaml
  stockfish:
    path: "C:\\Stockfish\\stockfish.exe"  # Windows
    # path: "/usr/local/bin/stockfish"    # Linux/Mac
  ```

### Issue: "CUDA out of memory"
**Solution:**
- Use the smaller model:
  ```yaml
  vision_model:
    model_name: llava-hf/llava-v1.6-mistral-7b-hf
  ```
- Or run on CPU (slower):
  ```python
  # The code automatically detects and uses CPU if CUDA unavailable
  ```

### Issue: "Board not detected correctly"
**Solution:**
- Re-run setup: `python main.py --setup`
- Ensure good lighting and clear board visibility
- Adjust `board_region` manually in `config.yaml`

### Issue: "Pieces not recognized accurately"
**Solution:**
- Increase image quality/size
- Use better lighting
- Try the larger model (if you have enough VRAM):
  ```yaml
  vision_model:
    model_name: llava-hf/llava-v1.6-34b-hf
  ```

## 📝 Logging

Logs are saved to `logs/` directory with timestamps.

View logs:
```bash
# Windows
type logs\chess_agent_*.log

# Linux/Mac
cat logs/chess_agent_*.log
```

Adjust logging level in `config.yaml`:
```yaml
logging:
  level: DEBUG  # DEBUG, INFO, WARNING, ERROR
```

## 🎮 Platform Support

### Desktop Chess Applications
- Works with any desktop chess app
- Ensure the board is clearly visible
- Run setup to define board region

### Chess.com / Lichess
- Browser-based play supported
- May require additional browser automation (future feature)
- Currently uses screen capture + mouse automation

## 🔒 Safety Features

- **FailSafe**: Move mouse to top-left corner to abort
- **Move Validation**: All moves validated before execution
- **Error Recovery**: Automatic retry on failures
- **Logging**: Complete audit trail of all actions

## 📚 Module Documentation

### Vision Module
- `capture.py` - Screen capture
- `board_detection.py` - Board detection and cropping
- `piece_recognition.py` - LLaVA-based piece recognition
- `fen_converter.py` - FEN notation conversion

### Engine Module
- `stockfish_wrapper.py` - Stockfish interface
- `move_validator.py` - Move validation and board state sync

### Control Module
- `mapping_utils.py` - Coordinate mapping
- `move_executor.py` - Mouse automation
- `humanizer.py` - Human-like behavior

### Utils Module
- `logger.py` - Logging utilities
- `helpers.py` - Helper functions

## 🤝 Contributing

Feel free to contribute improvements:
- Better board detection algorithms
- Auto-detection of opponent moves
- Support for more platforms
- Performance optimizations

## 📄 License

This project is for educational purposes. Ensure you comply with the terms of service of any platform where you use this agent.
