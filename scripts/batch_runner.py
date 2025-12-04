#!/usr/bin/env python3
"""
Script auxiliar para gerenciar execuções em lote do solucionador de Sudoku.
Responsável por:
  - Executar múltiplas instâncias do solver
  - Capturar tempo de execução, sementes, e resultados
  - Salvar dados em CSV

Uso interno via batch_experiments.sh
"""

import sys
import os
import csv
import json
import time
import subprocess
import random
import numpy as np
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Adicionar diretório raiz ao path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(ROOT_DIR)

from core import config  # noqa: E402


def load_sudoku(puzzle_name):
    """Carrega um puzzle de sudoku pelo nome."""
    puzzle_path = os.path.join(ROOT_DIR, "puzzles", "mantere_collection", f"{puzzle_name}.txt")
    
    if not os.path.exists(puzzle_path):
        return None
    
    with open(puzzle_path, "r") as f:
        content = f.read()
        puzzle = content.replace(' ', '').replace('-', '0').replace('\n', '')
    
    return np.array(list(puzzle)).reshape((9, 9)).astype(int)


def sudoku_to_string(sudoku_array):
    """Converte matriz sudoku para string."""
    if sudoku_array is None:
        return "None"
    return ''.join(sudoku_array.flatten().astype(str))


def parse_solver_output(output_str):
    """
    Extrai informações da saída do solver.
    Procura por padrões específicos na saída.
    """
    lines = output_str.split('\n')
    info = {
        'solved': False,
        'total_time': 0.0,
        'generation': 0,
        'solution_found': False,
        'final_solution': None
    }
    
    # Procurar por seed
    for line in lines:
        if 'Seed aleatória' in line and 'configurada' in line:
            try:
                seed_str = line.split(':')[1].strip()
                info['seed'] = int(seed_str)
            except (ValueError, IndexError):
                pass
    
    # Procurar por tempo total
    for line in lines:
        if 'Tempo total de execução' in line:
            try:
                time_str = line.split(':')[1].split('s')[0].strip()
                info['total_time'] = float(time_str)
            except (ValueError, IndexError):
                pass
    
    # Procurar por status
    for line in lines:
        if 'Puzzle resolvido com sucesso' in line:
            info['solved'] = True
            info['solution_found'] = True
        
        if 'Não foi possível resolver' in line:
            info['solution_found'] = True
    
    # Procurar pelo sudoku final na saída (se disponível)
    try:
        sudoku_digits = []
        capture = False
        skip_next_equals = False
        
        for i, line in enumerate(lines):
            if 'SUDOKU FINAL' in line:
                capture = True
                skip_next_equals = True  # Pula a próxima linha de =====
                continue
            
            if capture:
                # Se é a linha de ===== logo após SUDOKU FINAL, pula
                if skip_next_equals and '=====' in line:
                    skip_next_equals = False
                    continue
                
                # Parar quando encontrar outra linha de separação (após os dados)
                if '=====' in line or 'Tempo' in line or 'Puzzle resolvido' in line:
                    break
                
                # Pular linhas de traço ou vazias
                if '-----' in line or line.strip() == '':
                    continue
                
                # Extrair números da linha (formato: " 8  4  5  |  6  3  2  |  1  7  9 ")
                cleaned = line.replace('|', ' ').replace('-', ' ').strip()
                
                # Extrair apenas dígitos desta linha
                digits = ''.join(c for c in cleaned if c.isdigit())
                
                if len(digits) == 9:  # Uma linha do sudoku tem exatamente 9 dígitos
                    sudoku_digits.append(digits)
        
        if len(sudoku_digits) == 9:  # Se conseguiu 9 linhas (sudoku completo)
            # Formatar como grid com espaços e quebras de linha
            formatted_solution = '\n'.join(' '.join(row) for row in sudoku_digits)
            info['final_solution'] = formatted_solution
    except Exception as e:
        pass
    
    return info


def run_solver_attempt(puzzle_name, preprocessing, seed=None, verbose=False):
    """
    Executa uma tentativa do solver e retorna os resultados.
    
    Args:
        puzzle_name: Nome do puzzle (ex: s01a)
        preprocessing: bool - com ou sem pré-processamento
        seed: int ou None. Se None, usa "random"
        verbose: bool - imprimir saída do solver
    
    Returns:
        dict com informações da execução
    """
    # Usar o Python do venv se disponível
    python_cmd = sys.executable
    if os.path.exists(os.path.join(ROOT_DIR, ".venv/bin/python")):
        python_cmd = os.path.join(ROOT_DIR, ".venv/bin/python")
    
    cmd = [
        python_cmd,
        os.path.join(ROOT_DIR, "solver_without_window.py"),
        puzzle_name,
        "--with-pp" if preprocessing else "--without-pp",
    ]
    
    # Adicionar seed
    if seed is None:
        # Gerar seed aleatória para esta execução
        seed = random.randint(0, 2**32 - 1)
        cmd.append("random")
    else:
        cmd.append(str(seed))
    
    attempt_start = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1200,  # timeout de 20 minutos
            cwd=ROOT_DIR
        )
        
        exec_time = time.time() - attempt_start
        
        output = result.stdout + result.stderr
        
        if verbose:
            print(output)
        
        # Tentar extrair informações da saída
        info = parse_solver_output(output)
        info['return_code'] = result.returncode
        info['execution_time'] = exec_time
        info['seed'] = seed
        info['output'] = output
        
        # Tentar extrair o sudoku final da saída
        # (opcional - depende do formato)
        
        return info
        
    except subprocess.TimeoutExpired:
        return {
            'return_code': -1,
            'execution_time': 1200.0,
            'seed': seed,
            'solved': False,
            'solution_found': False,
            'timeout': True,
            'output': 'TIMEOUT: Execução excedeu 20 minutos'
        }
    except Exception as e:
        return {
            'return_code': -1,
            'execution_time': time.time() - attempt_start,
            'seed': seed,
            'solved': False,
            'solution_found': False,
            'error': str(e),
            'output': f'ERRO: {str(e)}'
        }


def run_batch_experiments(puzzle_name, num_attempts, preprocessing, output_csv=None, verbose=False):
    """
    Executa lote de experimentos e salva resultados em CSV.
    
    Args:
        puzzle_name: Nome do puzzle
        num_attempts: Número total de execuções desejadas
        preprocessing: bool - com ou sem pré-processamento
        output_csv: Caminho do arquivo CSV de saída
        verbose: bool - imprimir saída do solver
    
    Returns:
        list de dicts com resultados
    """
    
    if output_csv is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pp_str = "with_pp" if preprocessing else "without_pp"
        output_csv = os.path.join(ROOT_DIR, "results", f"{puzzle_name}_{pp_str}_{timestamp}.csv")
    
    # Criar diretório de resultados se não existir
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    # Definir limite de 12 execuções paralelas
    batch_size = min(12, num_attempts)
    total_batches = (num_attempts + batch_size - 1) // batch_size
    
    all_results = []
    attempt_number = 1
    
    print(f"\n{'='*70}")
    print(f"BATCH EXPERIMENTS - {puzzle_name}")
    print(f"{'='*70}")
    print(f"Total de tentativas: {num_attempts}")
    print(f"Pré-processamento: {'SIM' if preprocessing else 'NÃO'}")
    print(f"Paralelas por lote: {batch_size}")
    print(f"Total de lotes: {total_batches}")
    print(f"Arquivo de saída: {output_csv}")
    print(f"{'='*70}\n")
    
    for batch_num in range(total_batches):
        batch_start = batch_num * batch_size
        batch_end = min(batch_start + batch_size, num_attempts)
        current_batch_size = batch_end - batch_start
        
        print(f"[BATCH {batch_num + 1}/{total_batches}] Executando {current_batch_size} tentativas em paralelo...")
        
        # Usar ThreadPoolExecutor para executar em paralelo
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            # Submeter todas as tarefas
            futures = {}
            for i in range(current_batch_size):
                future = executor.submit(
                    run_solver_attempt,
                    puzzle_name,
                    preprocessing,
                    seed=None,  # sempre random
                    verbose=False
                )
                futures[future] = (attempt_number, i + 1)
                attempt_number += 1
            
            # Processar resultados conforme completam
            for future in as_completed(futures):
                attempt_num, batch_pos = futures[future]
                try:
                    result = future.result()
                    all_results.append(result)
                    
                    status = "✓ RESOLVIDO" if result.get('solved') else "✗ NÃO RESOLVIDO"
                    print(f"  [{attempt_num}/{num_attempts}] {status} ({result['execution_time']:.2f}s | seed: {result['seed']})")
                except Exception as e:
                    print(f"  [{attempt_num}/{num_attempts}] ✗ ERRO: {str(e)}")
                    all_results.append({
                        'return_code': -1,
                        'execution_time': 0,
                        'seed': 'N/A',
                        'solved': False,
                        'solution_found': False,
                        'error': str(e),
                        'output': f'ERRO: {str(e)}'
                    })
        
        print()
    
    # Salvar resultados em CSV
    save_results_to_csv(all_results, puzzle_name, preprocessing, output_csv)
    
    # Imprimir estatísticas
    print_statistics(all_results, puzzle_name, preprocessing)
    
    return all_results, output_csv


def save_results_to_csv(results, puzzle_name, preprocessing, output_file):
    """Salva resultados em arquivo CSV."""
    
    if not results:
        print(f"Nenhum resultado para salvar.")
        return
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Fieldnames do CSV
    fieldnames = [
        'attempt_number',
        'puzzle_name',
        'preprocessing',
        'seed',
        'solved',
        'execution_time_seconds',
        'return_code',
        'final_solution',
        'timestamp'
    ]
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for idx, result in enumerate(results, 1):
            writer.writerow({
                'attempt_number': idx,
                'puzzle_name': puzzle_name,
                'preprocessing': 'SIM' if preprocessing else 'NÃO',
                'seed': result.get('seed', 'N/A'),
                'solved': 'SIM' if result.get('solved') else 'NÃO',
                'execution_time_seconds': f"{result.get('execution_time', 0):.4f}",
                'return_code': result.get('return_code', 'N/A'),
                'final_solution': result.get('final_solution', 'N/A'),
                'timestamp': datetime.now().isoformat()
            })
    
    print(f"✓ Resultados salvos em: {output_file}")


def print_statistics(results, puzzle_name, preprocessing):
    """Imprime estatísticas dos experimentos."""
    
    if not results:
        return
    
    solved_count = sum(1 for r in results if r.get('solved'))
    total_count = len(results)
    success_rate = (solved_count / total_count * 100) if total_count > 0 else 0
    
    execution_times = [r.get('execution_time', 0) for r in results if r.get('execution_time')]
    avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
    min_time = min(execution_times) if execution_times else 0
    max_time = max(execution_times) if execution_times else 0
    
    print(f"\n{'='*70}")
    print(f"ESTATÍSTICAS - {puzzle_name}")
    print(f"{'='*70}")
    print(f"Puzzle: {puzzle_name}")
    print(f"Pré-processamento: {'SIM' if preprocessing else 'NÃO'}")
    print(f"Total de tentativas: {total_count}")
    print(f"Resolvidos: {solved_count}/{total_count} ({success_rate:.1f}%)")
    print(f"Tempo médio: {avg_time:.4f}s")
    print(f"Tempo mínimo: {min_time:.4f}s")
    print(f"Tempo máximo: {max_time:.4f}s")
    print(f"{'='*70}\n")


def main():
    """Função principal."""
    if len(sys.argv) < 4:
        print("Uso: python batch_runner.py <puzzle_name> <num_attempts> <--with-pp|--without-pp> [output_csv]")
        print("\nExemplo:")
        print("  python batch_runner.py s01a 20 --without-pp")
        print("  python batch_runner.py s01b 15 --with-pp /caminho/resultado.csv")
        sys.exit(1)
    
    puzzle_name = sys.argv[1]
    
    try:
        num_attempts = int(sys.argv[2])
    except ValueError:
        print(f"Erro: número de tentativas inválido: {sys.argv[2]}")
        sys.exit(1)
    
    preprocessing_flag = sys.argv[3]
    if preprocessing_flag == "--with-pp":
        preprocessing = True
    elif preprocessing_flag == "--without-pp":
        preprocessing = False
    else:
        print(f"Erro: flag de pré-processamento inválida: {preprocessing_flag}")
        print("Use: --with-pp ou --without-pp")
        sys.exit(1)
    
    output_csv = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Executar experimentos
    results, csv_path = run_batch_experiments(
        puzzle_name,
        num_attempts,
        preprocessing,
        output_csv=output_csv,
        verbose=False
    )


if __name__ == "__main__":
    main()
