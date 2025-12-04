# Referência Rápida - Batch Experiments

## Comando Principal

```bash
./scripts/batch_experiments.sh <puzzle> <num_tentativas> <--with-pp|--without-pp>
```

## Exemplos Imediatos

| Comando | Descrição |
|---------|-----------|
| `./scripts/batch_experiments.sh s01a 3 --without-pp` | Teste rápido |
| `./scripts/batch_experiments.sh s01a 20 --with-pp` | Experimento completo |
| `./scripts/batch_experiments.sh s02b 10 --without-pp` | Outro puzzle |

## Analisar Resultados

```bash
# Todos os resultados
python scripts/analyze_results.py results/

# Apenas um puzzle
python scripts/analyze_results.py 'results/s01a_*'

# Com padrão específico
python scripts/analyze_results.py 'results/s01*with_pp*.csv'
```

## Estrutura do CSV

```csv
attempt_number, puzzle_name, preprocessing, seed, solved, execution_time_seconds, return_code, final_solution, timestamp
1, s01a, NÃO, 1234567890, SIM, 2.3456, 0, 534678912789..., 2025-02-04T14:30:22
```

## Puzzles Disponíveis

```bash
ls puzzles/mantere_collection/
```

- s01a.txt, s01b.txt, s01c.txt
- s02a.txt, s02b.txt, s02c.txt
- ... até s16.txt

## Casos de Uso Comuns

### Comparar Performance

```bash
./scripts/batch_experiments.sh s01a 20 --with-pp
./scripts/batch_experiments.sh s01a 20 --without-pp
python scripts/analyze_results.py 'results/s01a_*'
```

**Saída esperada:**
```
Pré-processamento: SIM
  Resolvidos: 19/20 (95.0%)
  Tempo médio: 0.1234s

Pré-processamento: NÃO
  Resolvidos: 15/20 (75.0%)
  Tempo médio: 2.3456s
```

### Testar Múltiplos Puzzles

```bash
for p in s01a s01b s02a s02b; do
    ./scripts/batch_experiments.sh "$p" 10 --without-pp
done
```

### Análise com Pandas

```python
import pandas as pd

# Carregar CSV
df = pd.read_csv('results/s01a_with_pp_20251204_162042.csv')

# Taxa de sucesso
print((df['solved'] == 'SIM').sum() / len(df) * 100, "%")

# Tempo médio
print(df['execution_time_seconds'].mean(), "segundos")

# Puzzles mais difíceis
df.groupby('puzzle_name')['solved'].value_counts(normalize=True)
```

## Troubleshooting

| Problema | Solução |
|----------|---------|
| "Puzzle não encontrado" | `ls puzzles/mantere_collection/` e verifique a grafia |
| Execução muito lenta | Reduza `num_tentativas` ou use puzzle mais simples |
| CSV não gerado | `mkdir -p results/` e verifique permissões |
| Erro de import numpy | Já está instalado no venv |

## Arquivos Importantes

| Arquivo | Propósito |
|---------|----------|
| `batch_experiments.sh` | Executar experimentos |
| `batch_runner.py` | Lógica principal (não executar diretamente) |
| `analyze_results.py` | Analisar dados |
| `results/` | CSVs gerados |
| `BATCH_EXPERIMENTS.md` | Documentação completa |

## Diretório de Resultados

```bash
# Listar CSVs gerados
ls -lh results/

# Ver conteúdo de um CSV
cat results/s01a_with_pp_*.csv

# Quantidade de registros
wc -l results/*.csv

# Buscar CSVs de um puzzle específico
ls results/s01a_*
```

## Configurações Avançadas

Para modificar limites de execução, edite `batch_runner.py`:

```python
# Linha 166: Limite de lote
batch_size = min(10, num_attempts)  # Mudar para até 20

# Linha 113: Timeout por execução
timeout=600,  # 10 minutos - pode aumentar para 1200
```

## Atalhos Úteis

```bash
# Ir para o diretório
cd ~/Documentos/UFRPE/evolutionary-sudoku-solver_v2

# Executar teste rápido
./scripts/batch_experiments.sh s01a 3 --with-pp

# Analisar e salvar em arquivo
python scripts/analyze_results.py results/ > analise.txt

# Ver últimas execuções
tail -5 results/s01a_*.csv
```

---

**Dúvidas?** Consulte `BATCH_EXPERIMENTS.md` para documentação completa.
