# Python Slot Machine (Terminal)

A 3×3 terminal slot machine written in pure Python — no external dependencies.

## ✨ Features
- **Volatility presets**: `low`, `med`, `high` (changes reel weights)
- **Wilds (`W`)** substitute and **2×** the line payout when present
- **Bonus (`*`)**: 3 anywhere triggers **3 free spins @ 2×**, with retrigger (+1 spin)
- **Selectable paylines**: 3 / 5 / 8 (rows, +diagonals, +verticals)
- **Gamble** double-or-nothing feature on wins
- **Autospin** and **persistent profile** (`slot_profile.json`) with lifetime stats
- Clean ASCII board with subtle ANSI colors (works in most terminals)

## 🚀 Run
```bash
python Python_Slot_Machine_Pro.py
```
**Controls**
- `s` = single spin
- `a` = autospin (choose spin count)
- `d` = deposit
- `t` = show payout table
- `q` = quit

You’ll also choose **volatility** and **paylines** (3/5/8), then **bet per line** (1–100).

## 🧠 Notes
- Session is saved to `slot_profile.json` automatically on exit.
- Bonus free spins evaluate **all 8 paylines** at a 2× multiplier for excitement.
- Wilds multiply only the line(s) they appear on.

## 🧪 Sample Output
```
+---+---+---+
| C | W | C |
+---+---+---+
| B | * | B |
+---+---+---+
| A | C | A |
+---+---+---+
Line 1 win: $8
Spin won: $8
Gamble win? (y/n):
```
## Project Timeline
- **Jan 2025**: Initial prototype built locally (basic 3×3 reels, payouts)
- **Mar 2025**: Added volatility presets, wilds/bonus, paylines, autospin, persistence
- **Aug 18, 2025**: Cleaned up and published to GitHub (first public release)

## How it Works (Quick)
- **Reels/Grid**: 3×3 grid; reels are sampled from a weighted symbol pool (volatility changes weights)
- **Paylines**: Choose 3/5/8 (rows; +diagonals; +verticals). A line pays if all three match, wilds `W` substitute
- **Wilds**: `W` substitutes and **2×** the payout for that line
- **Bonus**: `*` does not pay on lines; **3 anywhere** triggers **3 free spins @ 2×** (retrigger +1)
- **Gamble**: Optional double-or-nothing on each win
- **Persistence**: Balance + lifetime stats saved to `slot_profile.json`

## Roadmap / Ideas
- Configurable payouts/weights via `config.json`
- Session analytics (hit rate, RTP estimate after N spins)
- `--no-color` flag for dumb terminals; unit tests for payline logic


## 📁 Files
```
.
├── Python_Slot_Machine_Pro.py   # main script
├── README.md                    # this file
├── .gitignore                   # Python ignores
└── LICENSE                      # MIT
```

## 📝 License
MIT © 2025 Yashvi Shah
