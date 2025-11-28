import sys
import os
import random
import numpy as np
from tkinter import Tk

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Apply global random seed before importing modules that use randomness.
from core.config import RANDOM_SEED  # noqa: E402
from gui import frame as sg  # noqa: E402

if RANDOM_SEED is not None:
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

try:
    tk = Tk()
    sudoku_gui = sg.SudokuGUI(tk)
    sudoku_gui.mainloop()

except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
    sys.exit(1)
