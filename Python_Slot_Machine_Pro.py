
import json
import os
import random
import sys
import time

ROWS, COLS = 3, 3

# Base symbol configuration
# weight: likelihood on each reel (relative)
# payout: payout multiplier for 3-in-a-row (per line) times bet per line
# Special symbols:
#  - 'W' = Wild (substitutes any symbol on a payline, 2x line multiplier if present)
#  - '*' = Bonus (no line payout; 3 or more anywhere on board triggers bonus spins)
BASE_SYMBOLS = {
    "A": {"weight": 2, "payout": 10},
    "B": {"weight": 4, "payout": 6},
    "C": {"weight": 6, "payout": 4},
    "D": {"weight": 10, "payout": 2},
    "W": {"weight": 1, "payout": 12},  # Wild, rare
    "*": {"weight": 1, "payout": 0},   # Bonus
}

VOLATILITY_PRESETS = {
    # Adjusts weights; higher volatility => rarer high symbols (A, W), bigger swings
    "low":   {"A": 3, "B": 6, "C": 8, "D": 12, "W": 2, "*": 2},
    "med":   {"A": 2, "B": 4, "C": 6, "D": 10, "W": 1, "*": 1},
    "high":  {"A": 1, "B": 3, "C": 5, "D": 9,  "W": 1, "*": 1},
}

# Payline definitions for a 3x3 grid
PAYLINES = {
    "3": [  # horizontals
        [(0,0),(0,1),(0,2)],
        [(1,0),(1,1),(1,2)],
        [(2,0),(2,1),(2,2)],
    ],
    "5": [  # horizontals + diagonals
        [(0,0),(0,1),(0,2)],
        [(1,0),(1,1),(1,2)],
        [(2,0),(2,1),(2,2)],
        [(0,0),(1,1),(2,2)],
        [(2,0),(1,1),(0,2)],
    ],
    "8": [  # horizontals + verticals + diagonals
        [(0,0),(0,1),(0,2)],
        [(1,0),(1,1),(1,2)],
        [(2,0),(2,1),(2,2)],
        [(0,0),(1,0),(2,0)],
        [(0,1),(1,1),(2,1)],
        [(0,2),(1,2),(2,2)],
        [(0,0),(1,1),(2,2)],
        [(2,0),(1,1),(0,2)],
    ],
}

PROFILE_FILE = "slot_profile.json"

ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "green": "\033[32m",
    "red": "\033[31m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
}

def c(text, color):
    return f"{ANSI.get(color,'')}{text}{ANSI['reset']}"

def load_profile():
    if not os.path.exists(PROFILE_FILE):
        return {"balance": 0, "lifetime_spins": 0, "lifetime_bet": 0, "lifetime_won": 0}
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"balance": 0, "lifetime_spins": 0, "lifetime_bet": 0, "lifetime_won": 0}

def save_profile(profile):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

def input_int(prompt, min_v=None, max_v=None):
    while True:
        val = input(prompt).strip()
        if val.lower() in {"q", "quit"}:
            return None
        if val.isdigit():
            iv = int(val)
            if (min_v is None or iv >= min_v) and (max_v is None or iv <= max_v):
                return iv
        print(f"Enter a number", end="")
        if min_v is not None and max_v is not None:
            print(f" between {min_v}-{max_v}.")
        elif min_v is not None:
            print(f" >= {min_v}.")
        elif max_v is not None:
            print(f" <= {max_v}.")
        else:
            print(".")

def choose_volatility():
    print("Choose volatility: [1] low  [2] med  [3] high")
    m = {1:"low",2:"med",3:"high"}
    while True:
        v = input_int("Volatility (1-3): ",1,3)
        if v is None:
            return "med"
        return m[v]

def build_symbol_pool(volatility):
    weights = VOLATILITY_PRESETS[volatility]
    pool = []
    for sym, base in BASE_SYMBOLS.items():
        w = weights.get(sym, base["weight"])
        pool.extend([sym]*int(w))
    return pool

def spin_reels(pool):
    # returns grid[rows][cols] as symbols
    grid = [[None]*COLS for _ in range(ROWS)]
    for col in range(COLS):
        # Allow repeats within column by sampling with replacement from pool
        for row in range(ROWS):
            grid[row][col] = random.choice(pool)
    return grid

def print_grid(grid):
    # pretty 3x3 box
    line = "+" + "---+"*COLS
    print(line)
    for r in range(ROWS):
        row_syms = []
        for c_ in range(COLS):
            sym = grid[r][c_]
            disp = sym
            if sym == "W":
                disp = c(sym, "yellow")
            elif sym == "*":
                disp = c(sym, "magenta")
            row_syms.append(f" {disp} ")
        print("|" + "|".join(row_syms) + "|")
        print(line)

def evaluate_line(grid, line_coords, bet):
    # Determine base symbol considering wilds. All three must match base or be wild.
    syms = [grid[r][c] for (r,c) in line_coords]
    nonwild = [s for s in syms if s not in ("W","*")]
    if not nonwild:
        # all wilds - pay as top symbol 'W'
        base = "W"
    else:
        base = nonwild[0]

    # bonus symbol does not contribute to payline
    for s in syms:
        if s in ("*",) or (s != base and s != "W"):
            return 0, False  # no win

    payout = BASE_SYMBOLS[base]["payout"] * bet
    has_wild = any(s == "W" for s in syms)
    if has_wild:
        payout *= 2  # wild multiplier
    return payout, True

def count_bonus(grid):
    # count '*' anywhere
    return sum(1 for r in range(ROWS) for c in range(COLS) if grid[r][c] == "*")

def perform_spin(pool, paylines_key, bet_per_line):
    grid = spin_reels(pool)
    lines = PAYLINES[paylines_key]
    total_win = 0
    winning_lines = []
    for idx, coords in enumerate(lines, start=1):
        win, ok = evaluate_line(grid, coords, bet_per_line)
        if ok and win > 0:
            total_win += win
            winning_lines.append((idx, win))
    bonus_count = count_bonus(grid)
    return grid, total_win, winning_lines, bonus_count

def gamble_feature(win_amount):
    # Optional double or nothing
    if win_amount <= 0:
        return 0
    ans = input("Gamble win? (y/n): ").strip().lower()
    if ans != "y":
        return win_amount
    choice = input("Pick (h)eads or (t)ails: ").strip().lower()
    coin = random.choice(["h","t"])
    if choice == coin:
        print(c("You doubled it!", "green"))
        return win_amount * 2
    else:
        print(c("Lost the gamble.", "red"))
        return 0

def bonus_round(pool, spins=3, multiplier=2):
    print(c(f"BONUS! {spins} free spins @ {multiplier}x", "magenta"))
    total = 0
    for i in range(1, spins+1):
        time.sleep(0.2)
        grid = spin_reels(pool)
        print_grid(grid)
        # Use all 8 lines during bonus for excitement
        win = 0
        for coords in PAYLINES["8"]:
            w, ok = evaluate_line(grid, coords, bet=1)
            if ok:
                win += w
        bonus_stars = count_bonus(grid)
        if bonus_stars >= 3:
            print(c("BONUS retrigger +1 spin!", "magenta"))
            spins += 1
        gained = win * multiplier
        total += gained
        print(f"Bonus Spin {i}: won {c(gained,'green')}")
    return total

def show_payout_table():
    print("\nPAYOUTS (3-in-a-row):")
    for s, cfg in BASE_SYMBOLS.items():
        if s == "*":
            print(f"  {s}: bonus symbol (3 anywhere triggers bonus)")
        elif s == "W":
            print(f"  {s}: {cfg['payout']}x (wild; 2x line multiplier when present)")
        else:
            print(f"  {s}: {cfg['payout']}x")
    print("")

def main():
    profile = load_profile()
    print(c("=== Python Slot Machine ===", "cyan"))
    if profile["balance"] <= 0:
        dep = input_int("Deposit amount to start: $", 1, 10_000_000)
        if dep is None:
            print("Bye.")
            return
        profile["balance"] += dep

    show_payout_table()
    vol = choose_volatility()
    pool = build_symbol_pool(vol)

    while True:
        print(f"Balance: ${profile['balance']}  | Spins: {profile['lifetime_spins']}  | Net: ${profile['lifetime_won']-profile['lifetime_bet']}")
        cmd = input("(s)pin, (a)utospin, (d)eposit, (t)able, (q)uit: ").strip().lower()
        if cmd == "q":
            break
        if cmd == "d":
            dep = input_int("Deposit: $", 1, 10_000_000)
            if dep is not None:
                profile["balance"] += dep
            continue
        if cmd == "t":
            show_payout_table()
            continue

        if cmd in {"s","a"}:
            # choose paylines and bet
            pl = input("Paylines 3/5/8 (default 5): ").strip()
            if pl not in PAYLINES:
                pl = "5"
            num_lines = len(PAYLINES[pl])
            bet = input_int(f"Bet per line ($1-$100): $", 1, 100)
            if bet is None:
                continue
            spins = 1
            if cmd == "a":
                spins = input_int("How many spins? (1-100): ", 1, 100) or 1
            total_bet_per_spin = bet * num_lines
            if total_bet_per_spin > profile["balance"]:
                print(c("Insufficient balance.", "red"))
                continue

            for s in range(spins):
                if profile["balance"] < total_bet_per_spin:
                    print(c("Balance too low to continue autospin.", "red"))
                    break
                profile["balance"] -= total_bet_per_spin
                profile["lifetime_bet"] += total_bet_per_spin
                grid, win, wins_list, bonus_count = perform_spin(pool, pl, bet)
                print_grid(grid)
                if wins_list:
                    for idx, amt in wins_list:
                        print(f"Line {idx} win: ${amt}")
                if bonus_count >= 3:
                    win += bonus_round(pool, spins=3, multiplier=2)
                # optional gamble
                if win > 0:
                    print(f"Spin won: {c('$'+str(win),'green')}")
                    win = gamble_feature(win)
                else:
                    print(f"Spin won: {c('$0','red')}")
                profile["balance"] += win
                profile["lifetime_won"] += win
                profile["lifetime_spins"] += 1
                time.sleep(0.1)
            continue

        print("Unknown command.")

    save_profile(profile)
    print(f"Session saved to {PROFILE_FILE}. Final balance: ${profile['balance']}")

def input_int(prompt, min_v=None, max_v=None):
    while True:
        val = input(prompt).strip()
        if val.lower() in {"q", "quit"}:
            return None
        if val.isdigit():
            iv = int(val)
            if (min_v is None or iv >= min_v) and (max_v is None or iv <= max_v):
                return iv
        print(f"Enter a number", end="")
        if min_v is not None and max_v is not None:
            print(f" between {min_v}-{max_v}.")
        elif min_v is not None:
            print(f" >= {min_v}.")
        elif max_v is not None:
            print(f" <= {max_v}.")
        else:
            print(".")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye.")
