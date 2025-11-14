# 🚀 Chess Vision Agent - Quick Reference

## 📦 Installation (One-Time Setup)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Download Stockfish
# Windows: https://stockfishchess.org/download/
# Linux: sudo apt-get install stockfish
# Mac: brew install stockfish

# 3. Verify installation
python test_setup.py
```

## 🎮 Running the Agent

### First Time Setup
```bash
python main.py --setup
```
- Click on the center of the chessboard
- Enter board size (default: 800)

### Start Playing
```bash
python main.py
```

## ⚙️ Quick Configuration

Edit `config.yaml` for these common settings:

### Adjust Difficulty
```yaml
stockfish:
  skill_level: 20    # 0-20 (0=beginner, 20=master)
  depth: 15          # 10-20 (higher=stronger, slower)
```

### Adjust Speed (Human-like behavior)
```yaml
humanizer:
  min_delay: 1.0     # Minimum thinking time (seconds)
  max_delay: 3.5     # Maximum thinking time (seconds)
  skill_level: 7     # 1-10 (1=slow/imprecise, 10=fast/precise)
```

### Vision Model Configuration
```yaml
vision_model:
  # UI-TARS 1.5 - 7B parameters (efficient and accurate)
  model_name: ByteDance-Seed/UI-TARS-1.5-7B
```

## 🎯 Common Commands

```bash
# Run with custom config
python main.py --config my_config.yaml

# Test system
python test_setup.py

# Setup board region
python main.py --setup
```

## 🔍 Troubleshooting

### Stockfish Not Found
```yaml
# Add to config.yaml:
stockfish:
  path: "C:\\Stockfish\\stockfish.exe"  # Windows
  # path: "/usr/local/bin/stockfish"    # Linux/Mac
```

### Out of Memory (GPU)
```yaml
# UI-TARS is already efficient with 7B parameters
# Try closing other GPU applications or use CPU mode
```

### Board Detection Issues
```bash
# Re-run setup
python main.py --setup

# Ensure:
# - Good lighting
# - Clear board view
# - No overlapping windows
```

## 📊 Module Imports (For Custom Scripts)

```python
# Vision
from vision import capture_board, detect_board, recognize_pieces, to_fen

# Engine
from engine import StockfishEngine, MoveValidator

# Control
from control import SquareMapper, MoveExecutor, Humanizer

# Utils
from utils import setup_logger, get_logger
```

## 🎨 Example Custom Script

```python
from main import ChessAgent

# Create agent with custom settings
agent = ChessAgent('config.yaml')

# Adjust on-the-fly
agent.engine.skill_level = 15
agent.humanizer.set_skill_level(8)

# Run
agent.run()
```

## 🛑 Emergency Stop

**Move mouse to top-left corner** - PyAutoGUI FailSafe will abort

## 📝 Logs

Logs are saved in `logs/` directory:
```bash
# View latest log (Windows)
type logs\chess_agent_*.log

# View latest log (Linux/Mac)
cat logs/chess_agent_*.log
```

## 🎯 Workflow at a Glance

```
1. Agent captures screen → Board image
2. Detects chessboard → Cropped board
3. UI-TARS recognizes pieces → Piece positions
4. Converts to FEN → Chess notation
5. Stockfish calculates → Best move
6. Executes move → Mouse automation
7. Waits for opponent → Press Enter (manual mode)
8. Repeat steps 1-7
```

## 🔧 File Overview

| File | Purpose |
|------|---------|
| `main.py` | Main program entry point |
| `config.yaml` | All settings and configuration |
| `test_setup.py` | Verify installation |
| `requirements.txt` | Python dependencies |
| `SETUP.md` | Detailed setup guide |
| `PROJECT_SUMMARY.md` | Complete implementation details |

## 💡 Pro Tips

1. **Better Accuracy**: Use good lighting, clear board view
2. **Faster Moves**: Decrease `min_delay` and `max_delay`
3. **Stronger Play**: Increase `skill_level` and `depth`
4. **Save Games**: Enable `save_game: true` in config
5. **Debug Issues**: Set `logging.level: DEBUG` in config

## 📱 Support

Check these files for detailed help:
- `SETUP.md` - Complete setup instructions
- `PROJECT_SUMMARY.md` - Full implementation details
- `README.md` - Project overview and architecture

---

**Happy Chess Playing! ♟️🤖**
