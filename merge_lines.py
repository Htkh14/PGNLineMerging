import merge_pgn
import handle_pgns
import sys
import tkinter as tk
from tkinter import messagebox

def merge_all_lines(file):
    pgn = handle_pgns.split_pgn(file)
    lines = pgn[1:]
    merged = merge_pgn.merge(lines)
    for game in lines:
       merged += "\n" + "".join(game)
    return merged

def pick_file():
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Select a PGN file",
        filetypes=[("PGN files", "*.pgn"), ("All files", "*.*")]
    )
    root.destroy()
    return path

def main():
    if len(sys.argv) >= 2:
        filepath = sys.argv[1]
    else:
        filepath = pick_file()
        if not filepath:
            raise SystemExit("No file selected.")

    with open(filepath, "r") as f:
        pgn = f.readlines()
    result = merge_all_lines(pgn)
    with open(filepath, "w") as f:
        f.write(result)
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Done", "PGN merged successfully!")
    root.destroy()

if __name__ == "__main__":
    main()