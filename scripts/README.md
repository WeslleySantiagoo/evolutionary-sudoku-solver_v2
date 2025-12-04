# Scripts de Batch Experiments

Este diretório contém scripts para executar experimentos em lote do solucionador de Sudoku.

## 📋 Arquivos

### 1. `batch_experiments.sh` (Principal)

Script shell para executar experimentos em lote.

**Uso:**

```bash
./batch_experiments.sh <puzzle_name> <num_attempts> <--with-pp|--without-pp>
```

**Exemplos:**

```bash
./batch_experiments.sh s01a 20 --without-pp
./batch_experiments.sh s01b 15 --with-pp
```

**Características:**

- Valida argumentos
- Chama o script Python auxiliar
- Exibe mensagens coloridas
- Verifica se puzzle existe

### 2. `batch_runner.py` (Auxiliar)

Script Python que gerencia a execução das tentativas.

**Responsabilidades:**

- Executa o solucionador múltiplas vezes
- Captura saída e dados de cada execução
- Salva resultados em CSV
- Imprime estatísticas finais

**Uso direto (raro):**

```bash
python batch_runner.py <puzzle_name> <num_attempts> <--with-pp|--without-pp>
```

### 3. `analyze_results.py` (Análise)

Script Python para análise dos resultados coletados.

**Uso:**

```bash
python analyze_results.py results/s01a_without_pp_*.csv
python analyze_results.py results/
```

**Gera:**

- Estatísticas gerais
- Dados por configuração
- Dados por puzzle
- Matriz de comparação
- Arquivo de resumo em TXT

## 🚀 Fluxo Completo

```
1. Execute experimentos:
   ./batch_experiments.sh s01a 20 --without-pp
   └─> Gera: results/s01a_without_pp_YYYYMMDD_HHMMSS.csv

2. Analise resultados:
   python analyze_results.py results/
   └─> Gera estatísticas e results_summary_*.txt
```

## 📊 Dados Capturados

Cada execução captura:

- Número da tentativa
- Nome do puzzle
- Configuração (com/sem pré-processamento)
- Semente aleatória
- Se foi resolvido
- Tempo de execução
- Código de retorno
- Sudoku final
- Timestamp

## ⚙️ Configuração

### Limite de Execuções por Lote

Definido em `batch_runner.py`:

```python
batch_size = min(10, num_attempts)
```

Para modificar, edite `batch_runner.py` linha 166.

### Timeout por Execução

Definido em `batch_runner.py`:

```python
timeout=600,  # 10 minutos
```

Para modificar, edite `batch_runner.py` linha 113.

## 🐛 Troubleshooting

### "Puzzle não encontrado"

Verifique a grafia:

```bash
ls ../puzzles/mantere_collection/ | head
```

### Execução muito lenta

- Reduza `num_attempts`
- Verifique CPU/RAM com `top` ou `htop`
- Ajuste `core/config.py`

### Arquivo CSV não gerado

Verifique permissões:

```bash
ls -ld results/
```

## 📝 Exemplos de Uso Avançado

### Testar múltiplos puzzles

```bash
#!/bin/bash
for puzzle in s01a s01b s01c s02a s02b; do
    ./batch_experiments.sh "$puzzle" 10 --without-pp
done
```

### Comparar com e sem pré-processamento

```bash
./batch_experiments.sh s01a 20 --with-pp
./batch_experiments.sh s01a 20 --without-pp
python analyze_results.py results/s01a_*
```

### Análise em Python

```python
import pandas as pd
df = pd.read_csv('results/s01a_with_pp_*.csv')
print(df.groupby('solved')['execution_time_seconds'].mean())
```

## 🔗 Dependências

- Python 3.7+
- numpy (instalado automaticamente)
- pandas (para análise)

## 📚 Documentação Completa

Consulte `BATCH_EXPERIMENTS.md` para documentação detalhada.

---

**Versão:** 1.0  
**Data:** Dezembro 2025
