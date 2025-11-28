#!/usr/bin/env python3
"""
Script de teste para verificar o pré-processamento com as novas técnicas.
"""

import numpy as np
from core import pre_processing as pp


def print_sudoku(sudoku_array, title=""):
    """Imprime o sudoku de forma formatada."""
    if title:
        print(f"\n{title}")
        print("=" * 37)

    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("-" * 37)

        row_str = ""
        for j in range(9):
            if j % 3 == 0 and j != 0:
                row_str += " | "

            value = sudoku_array[i][j]
            row_str += f" {value if value != 0 else '.'} "

        print(row_str)
    print("=" * 37)


def test_preprocessing():
    """Testa o pré-processamento com um puzzle."""
    # Carrega um puzzle de exemplo
    puzzle_path = "puzzles/mantere_collection/s01a.txt"

    with open(puzzle_path, "r") as f:
        file_content = f.read()
        puzzle = file_content.replace(' ', '').replace('-', '0').replace('\n', '')

    original = np.array(list(puzzle)).reshape((9, 9)).astype(int)

    print("=" * 70)
    print("TESTE DE PRÉ-PROCESSAMENTO")
    print("=" * 70)
    print("\nTécnicas aplicadas na ordem:")
    print("1. Naked Single")
    print("2. Hidden Single")
    print("3. Naked Pairs")
    print("4. Naked Triples (NOVO)")
    print("5. Naked Quads (NOVO)")
    print("6. X-Wings")

    print_sudoku(original, "PUZZLE ORIGINAL")

    # Aplica pré-processamento
    pp_controller = pp.Controller()
    pp_controller.load(np.copy(original))
    processed, numbers_filled = pp_controller.controller()

    print_sudoku(processed, "APÓS PRÉ-PROCESSAMENTO")
    print(f"\nNúmeros preenchidos: {numbers_filled}")
    print(f"Células vazias restantes: {np.count_nonzero(processed == 0)}")

    # Verifica se está correto
    if np.count_nonzero(processed == 0) == 0:
        print("\n✓ Sudoku completamente resolvido pelo pré-processamento!")
    else:
        print("\n→ Sudoku parcialmente resolvido. Pronto para o AG.")


if __name__ == "__main__":
    test_preprocessing()
