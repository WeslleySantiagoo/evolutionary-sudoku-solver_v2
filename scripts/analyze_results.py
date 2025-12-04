#!/usr/bin/env python3
"""
Script auxiliar para análise dos resultados dos experimentos em lote.

Uso:
    python analyze_results.py results/s01a_without_pp_*.csv
    python analyze_results.py results/

Permite:
  - Comparar múltiplos arquivos CSV
  - Gerar estatísticas detalhadas
  - Criar gráficos (opcional com matplotlib)
"""

import sys
import os
import glob
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_csv_files(pattern):
    """Carrega um ou múltiplos arquivos CSV."""
    
    if os.path.isdir(pattern):
        # Se é um diretório, carrega todos os CSVs
        files = glob.glob(os.path.join(pattern, "*.csv"))
    else:
        # Se é um padrão glob, expande
        files = glob.glob(pattern)
    
    if not files:
        print(f"Nenhum arquivo CSV encontrado: {pattern}")
        return None
    
    dfs = []
    for file in files:
        try:
            df = pd.read_csv(file)
            df['source_file'] = os.path.basename(file)
            dfs.append(df)
            print(f"✓ Carregado: {os.path.basename(file)} ({len(df)} registros)")
        except Exception as e:
            print(f"✗ Erro ao carregar {file}: {e}")
    
    if not dfs:
        return None
    
    return pd.concat(dfs, ignore_index=True)


def print_basic_statistics(df):
    """Imprime estatísticas básicas."""
    
    print("\n" + "="*70)
    print("ESTATÍSTICAS GERAIS")
    print("="*70)
    
    print(f"\nTotal de registros: {len(df)}")
    print(f"Arquivos únicos: {df['source_file'].nunique()}")
    print(f"Puzzles únicos: {df['puzzle_name'].nunique()}")
    print(f"Configurações testadas: {df['preprocessing'].nunique()}")
    
    # Taxa de sucesso geral
    solved_total = (df['solved'] == 'SIM').sum()
    total = len(df)
    success_rate = (solved_total / total * 100) if total > 0 else 0
    
    print(f"\n{'Estatística':<30} {'Valor':<20}")
    print("-" * 50)
    print(f"{'Resolvidos':<30} {solved_total}/{total} ({success_rate:.1f}%)")
    print(f"{'Não resolvidos':<30} {total - solved_total}/{total} ({100-success_rate:.1f}%)")
    
    # Tempos
    times = pd.to_numeric(df['execution_time_seconds'], errors='coerce')
    times = times[times.notna()]
    
    if len(times) > 0:
        print(f"{'Tempo médio':<30} {times.mean():.4f}s")
        print(f"{'Tempo mínimo':<30} {times.min():.4f}s")
        print(f"{'Tempo máximo':<30} {times.max():.4f}s")
        print(f"{'Desvio padrão':<30} {times.std():.4f}s")


def print_by_preprocessing(df):
    """Estatísticas por tipo de pré-processamento."""
    
    print("\n" + "="*70)
    print("ESTATÍSTICAS POR CONFIGURAÇÃO DE PRÉ-PROCESSAMENTO")
    print("="*70)
    
    for prep in df['preprocessing'].unique():
        subset = df[df['preprocessing'] == prep]
        solved = (subset['solved'] == 'SIM').sum()
        total = len(subset)
        rate = (solved / total * 100) if total > 0 else 0
        
        times = pd.to_numeric(subset['execution_time_seconds'], errors='coerce')
        times = times[times.notna()]
        
        print(f"\nPré-processamento: {prep}")
        print(f"  Total: {total} tentativas")
        print(f"  Resolvidos: {solved}/{total} ({rate:.1f}%)")
        
        if len(times) > 0:
            print(f"  Tempo médio: {times.mean():.4f}s")
            print(f"  Tempo min/max: {times.min():.4f}s / {times.max():.4f}s")


def print_by_puzzle(df):
    """Estatísticas por puzzle."""
    
    print("\n" + "="*70)
    print("ESTATÍSTICAS POR PUZZLE")
    print("="*70)
    
    for puzzle in sorted(df['puzzle_name'].unique()):
        subset = df[df['puzzle_name'] == puzzle]
        solved = (subset['solved'] == 'SIM').sum()
        total = len(subset)
        rate = (solved / total * 100) if total > 0 else 0
        
        times = pd.to_numeric(subset['execution_time_seconds'], errors='coerce')
        times = times[times.notna()]
        
        print(f"\n{puzzle}:")
        print(f"  Total: {total} tentativas")
        print(f"  Taxa de sucesso: {rate:.1f}%")
        
        if len(times) > 0:
            print(f"  Tempo médio: {times.mean():.4f}s")


def print_comparison_matrix(df):
    """Cria uma matriz de comparação puzzle x preprocessamento."""
    
    print("\n" + "="*70)
    print("MATRIZ DE COMPARAÇÃO")
    print("="*70)
    print("\nTaxa de sucesso (%) por puzzle e configuração:\n")
    
    # Criar tabela cruzada
    comparison = pd.crosstab(
        df['puzzle_name'],
        df['preprocessing'],
        values=(df['solved'] == 'SIM'),
        aggfunc='mean'
    )
    
    if comparison is not None and len(comparison) > 0:
        # Converter para percentual
        comparison = comparison * 100
        
        # Imprimir
        print(comparison.to_string())
        print()
    else:
        print("Dados insuficientes para criar matriz de comparação")


def export_summary(df, output_file='results_summary.txt'):
    """Exporta resumo para arquivo de texto."""
    
    with open(output_file, 'w') as f:
        f.write(f"Resumo de Resultados\n")
        f.write(f"Gerado em: {datetime.now().isoformat()}\n")
        f.write(f"{'='*70}\n\n")
        
        # Estatísticas gerais
        solved_total = (df['solved'] == 'SIM').sum()
        total = len(df)
        success_rate = (solved_total / total * 100) if total > 0 else 0
        
        f.write(f"Total de tentativas: {total}\n")
        f.write(f"Resolvidas: {solved_total} ({success_rate:.1f}%)\n\n")
        
        # Por pré-processamento
        for prep in df['preprocessing'].unique():
            subset = df[df['preprocessing'] == prep]
            solved = (subset['solved'] == 'SIM').sum()
            total_prep = len(subset)
            rate = (solved / total_prep * 100) if total_prep > 0 else 0
            f.write(f"{prep}: {solved}/{total_prep} ({rate:.1f}%)\n")
    
    print(f"\n✓ Resumo exportado para: {output_file}")


def main():
    """Função principal."""
    
    if len(sys.argv) < 2:
        print("Uso: python analyze_results.py <arquivo_csv ou diretório ou padrão>")
        print("\nExemplos:")
        print("  python analyze_results.py results/s01a_without_pp_*.csv")
        print("  python analyze_results.py results/")
        print("  python analyze_results.py results/s01a_without_pp_20250204_143022.csv")
        sys.exit(1)
    
    pattern = sys.argv[1]
    
    # Carregar dados
    print("\n" + "="*70)
    print("ANALISANDO RESULTADOS DOS EXPERIMENTOS")
    print("="*70)
    print()
    
    df = load_csv_files(pattern)
    
    if df is None:
        sys.exit(1)
    
    # Imprimir estatísticas
    print_basic_statistics(df)
    print_by_preprocessing(df)
    print_by_puzzle(df)
    print_comparison_matrix(df)
    
    # Exportar resumo
    print(f"\n\n\n{pattern}\n\n\n")
    output_file = f"{pattern.replace('.csv', '')}.txt"
    output_file = f"results/results_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    export_summary(df, output_file)
    
    print("\n" + "="*70)
    print("Análise concluída!")
    print("="*70)


if __name__ == "__main__":
    main()
