#!/usr/bin/env python3
"""
Solver de Sudoku sem interface gráfica.
Executa o algoritmo genético e imprime o progresso no terminal.

Uso:
    python solver_without_window.py s01a
"""

import sys
import os
import time
import numpy as np
import random

# Obter o diretório do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Adicionar o diretório raiz ao path
sys.path.append(SCRIPT_DIR)

from core import solver as ga  # noqa: E402
from core import pre_processing as pp  # noqa: E402
from core import config  # noqa: E402


def load_sudoku(puzzle_name):
    """Carrega um puzzle de sudoku pelo nome."""
    puzzle_path = os.path.join(SCRIPT_DIR, "puzzles", "mantere_collection", f"{puzzle_name}.txt")

    if not os.path.exists(puzzle_path):
        print(f"Erro: Puzzle '{puzzle_name}' não encontrado em {puzzle_path}")
        return None

    with open(puzzle_path, "r") as input_file:
        file_content = input_file.read()
        puzzle = file_content.replace(' ', '').replace('-', '0').replace('\n', '')

    return np.array(list(puzzle)).reshape((9, 9)).astype(int)


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


def progress_callback(generation_num, best_candidate, total_individuals, best_fitness, start_time):
    """Callback para imprimir o progresso durante a execução."""
    elapsed = time.time() - start_time

    # Imprimir uma nova linha para cada geração
    if (generation_num - 1) % 1 == 0 or generation_num == 0:
        print(f"Geração: {generation_num + 1:4d} | "
            f"Total Gerações: {generation_num + 1:4d} | "
            f"Indivíduos: {total_individuals:8d} | "
            f"Melhor Aptidão: {best_fitness:.6f} | "
            f"Tempo: {elapsed:.2f}s")

    return True


def solve_with_preprocessing(original_sudoku):
    """Resolve o sudoku com pré-processamento."""
    print("\n" + "=" * 70)
    print("INICIANDO PRÉ-PROCESSAMENTO")
    print("=" * 70)

    start_pre_processing_time = time.time()
    pp_controller = pp.Controller()
    pp_controller.load(np.copy(original_sudoku))
    sudoku_pre_processed, _ = pp_controller.controller()
    end_pre_processing_time = time.time()
    pre_processing_time = end_pre_processing_time - start_pre_processing_time

    print(f"Pré-processamento concluído em {pre_processing_time:.4f}s")
    print_sudoku(sudoku_pre_processed, "SUDOKU APÓS PRÉ-PROCESSAMENTO")

    # Verificar se o pré-processamento resolveu completamente
    if not np.any(sudoku_pre_processed == 0):
        print("\n✓ SOLUÇÃO ENCONTRADA APENAS COM O PRÉ-PROCESSAMENTO!")
        return sudoku_pre_processed, True, pre_processing_time

    print("\n" + "=" * 70)
    print("INICIANDO ALGORITMO GENÉTICO")
    print("=" * 70)
    print(f"População: {config.POPULATION_SIZE} | "
          f"Gerações Máximas: {config.MAX_GENERATIONS} | "
          f"Taxa Mutação Inicial: {config.INITIAL_MUTATION_RATE}")
    print("=" * 70)

    ga_sudoku = ga.Sudoku()
    ga_sudoku.load(sudoku_pre_processed)

    start_time = time.time()
    solve_output = ga_sudoku.solve(
        progress_callback=lambda gen, best_cand, total_ind, best_fit:
            progress_callback(gen, best_cand, total_ind, best_fit, start_time)
    )
    final_time_elapsed = time.time() - start_time

    print()  # Nova linha após o progresso

    generation = solve_output['generation']
    solution_candidate = solve_output['solution_candidate']

    total_time = pre_processing_time + final_time_elapsed

    return process_result(generation, solution_candidate, total_time)


def solve_without_preprocessing(original_sudoku):
    """Resolve o sudoku sem pré-processamento."""
    print("\n" + "=" * 70)
    print("INICIANDO ALGORITMO GENÉTICO (SEM PRÉ-PROCESSAMENTO)")
    print("=" * 70)
    print(f"População: {config.POPULATION_SIZE} | "
          f"Gerações Máximas: {config.MAX_GENERATIONS} | "
          f"Taxa Mutação Inicial: {config.INITIAL_MUTATION_RATE}")
    print("=" * 70)

    ga_sudoku = ga.Sudoku()
    ga_sudoku.load(original_sudoku)

    start_time = time.time()
    solve_output = ga_sudoku.solve(
        progress_callback=lambda gen, best_cand, total_ind, best_fit:
            progress_callback(gen, best_cand, total_ind, best_fit, start_time)
    )
    final_time_elapsed = time.time() - start_time

    print()  # Nova linha após o progresso

    generation = solve_output['generation']
    solution_candidate = solve_output['solution_candidate']

    return process_result(generation, solution_candidate, final_time_elapsed)


def process_result(generation, solution_candidate, total_time):
    """Processa o resultado da execução."""
    print("\n" + "=" * 70)
    print("RESULTADO")
    print("=" * 70)

    if generation == -1:
        print("✗ ENTRADA INVÁLIDA")
        return None, False, total_time
    elif generation == -3:
        print("✗ EXECUÇÃO CANCELADA PELO USUÁRIO")
        if solution_candidate and hasattr(solution_candidate, 'values'):
            return solution_candidate.values, False, total_time
        return None, False, total_time
    elif generation == -2:
        print("✗ SOLUÇÃO NÃO ENCONTRADA - LIMITE DE GERAÇÕES ATINGIDO")
        if solution_candidate and hasattr(solution_candidate, 'values'):
            return solution_candidate.values, False, total_time
        return None, False, total_time
    elif (solution_candidate and hasattr(solution_candidate, 'values')
          and abs(solution_candidate.fitness - 1.0) < 1e-9
          and not np.any(solution_candidate.values == 0)):
        print("✓ SOLUÇÃO ENCONTRADA COM SUCESSO!")
        print(f"Geração: {generation + 1}")
        print(f"Aptidão: {solution_candidate.fitness:.6f}")
        return solution_candidate.values, True, total_time
    else:
        print("✗ SOLUÇÃO NÃO ENCONTRADA")
        if solution_candidate and hasattr(solution_candidate, 'values'):
            return solution_candidate.values, False, total_time
        return None, False, total_time


def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("Uso: python solver_without_window.py <puzzle_name> [--with-pp|--without-pp] [seed]")
        print("Exemplo: python solver_without_window.py s01a --with-pp 42")
        print("\nOpções:")
        print("  --with-pp      : Resolver com pré-processamento (padrão)")
        print("  --without-pp   : Resolver sem pré-processamento")
        print("  seed           : Semente aleatória (opcional, sobrescreve config.py)")
        sys.exit(1)

    puzzle_name = sys.argv[1]
    use_preprocessing = True
    custom_seed = None
    # Verificar opções adicionais
    if len(sys.argv) > 2:
        if sys.argv[2] == "--without-pp":
            use_preprocessing = False
        elif sys.argv[2] == "--with-pp":
            use_preprocessing = True
        else:
            # Tentar interpretar como seed
            try:
                custom_seed = int(sys.argv[2])
            except ValueError:
                print(f"Opção desconhecida: {sys.argv[2]}")
                sys.exit(1)

    # Aplicar seed global ANTES de usar random para "random"
    # Determinar a seed a usar
    if custom_seed is None:
        seed_to_use = config.RANDOM_SEED
    else:
        seed_to_use = custom_seed

    if seed_to_use is not None:
        random.seed(seed_to_use)
        np.random.seed(seed_to_use)
        print(f"Seed aleatória configurada: {seed_to_use}\n")

    # Verificar se há um terceiro parâmetro (seed)
    if len(sys.argv) > 3:
        try:
            if sys.argv[3] == "random":
                # Agora random está seedado, então isso é determinístico
                custom_seed = random.randint(0, 2**32 - 1)
                # Re-aplicar com a nova seed gerada
                random.seed(custom_seed)
                np.random.seed(custom_seed)
                print(f"Seed aleatória gerada e configurada: {custom_seed}\n")
            else:
                custom_seed = int(sys.argv[3])
                # Re-aplicar se necessário
                if custom_seed != seed_to_use:
                    random.seed(custom_seed)
                    np.random.seed(custom_seed)
                    print(f"Seed aleatória reconfigurada: {custom_seed}\n")
        except ValueError:
            print(f"Seed inválida: {sys.argv[3]}. Deve ser um número inteiro.")
            sys.exit(1)

    # Carregar puzzle
    print("=" * 70)
    print(f"SOLUCIONADOR DE SUDOKU - {puzzle_name.upper()}")
    print("=" * 70)

    original_sudoku = load_sudoku(puzzle_name)
    if original_sudoku is None:
        sys.exit(1)

    print_sudoku(original_sudoku, "PUZZLE ORIGINAL")

    # Resolver
    start_total = time.time()

    if use_preprocessing:
        final_sudoku, solved, exec_time = solve_with_preprocessing(original_sudoku)
    else:
        final_sudoku, solved, exec_time = solve_without_preprocessing(original_sudoku)

    total_elapsed = time.time() - start_total

    # Imprimir resultado final
    if final_sudoku is not None:
        print_sudoku(final_sudoku, "SUDOKU FINAL")

    print(f"\nTempo total de execução: {total_elapsed:.4f}s")

    if solved:
        print("\n✓ Puzzle resolvido com sucesso!")
        sys.exit(0)
    else:
        print("\n✗ Não foi possível resolver o puzzle completamente.")
        sys.exit(1)


if __name__ == "__main__":
    main()
