# Batch Experiments - Guia de Uso

## Descrição

Script para executar múltiplos experimentos de resolução de Sudoku em lote, com captura automática de estatísticas e salvamento em CSV.

O script permite executar o solucionador várias vezes com os mesmos parâmetros, usando sementes aleatórias diferentes a cada execução. Os resultados são compilados em um arquivo CSV para análise posterior.

## Características

- ✅ Executa o puzzle múltiplas vezes com sementes aleatórias
- ✅ **Execução em paralelo**: Até 10 execuções simultâneas por lote
- ✅ Salvamento automático de resultados em CSV
- ✅ Estatísticas de sucesso, tempo médio, mínimo e máximo
- ✅ Suporte para com/sem pré-processamento
- ✅ Saída colorida e organizada

## Instalação

Os scripts já estão no projeto. Apenas garanta que têm permissão de execução:

```bash
chmod +x scripts/batch_experiments.sh
```

## Uso Básico

### Sintaxe

```bash
./scripts/batch_experiments.sh <puzzle_name> <num_attempts> <--with-pp|--without-pp>
```

### Parâmetros

| Parâmetro | Descrição | Exemplo |
|-----------|-----------|---------|
| `puzzle_name` | Nome do puzzle da coleção Mantere | `s01a`, `s01b`, `s02c`, etc. |
| `num_attempts` | Número de vezes que será executado | `20`, `5`, `100` |
| `preprocessing` | Usar pré-processamento? | `--with-pp` ou `--without-pp` |

### Exemplos

#### Exemplo 1: Resolver s01a 20 vezes sem pré-processamento

```bash
cd /home/weslley-santiago/Documentos/UFRPE/evolutionary-sudoku-solver_v2
./scripts/batch_experiments.sh s01a 20 --without-pp
```

**Output esperado:**
```
[INFO] ==========================================
[INFO] Batch Experiments - Solucionador Sudoku
[INFO] ==========================================
[INFO] Puzzle: s01a
[INFO] Tentativas: 20
[INFO] Configuração: sem pré-processamento
[INFO] Semente: aleatória (random)
...
[BATCH 1/2] Executando 10 tentativas em paralelo...
  [1/20] ✓ RESOLVIDO (2.34s | seed: 123456789)
  [2/20] ✗ NÃO RESOLVIDO (1.89s | seed: 987654321)
  ...
[SUCCESS] Experimentos concluídos com sucesso!
```

#### Exemplo 2: Resolver s01b 15 vezes com pré-processamento

```bash
./scripts/batch_experiments.sh s01b 15 --with-pp
```

#### Exemplo 3: Teste rápido com 5 tentativas

```bash
./scripts/batch_experiments.sh s02a 5 --without-pp
```

## Funcionamento Interno

### Fluxo de Execução

1. **Validação de argumentos** - Verifica se puzzle existe e parâmetros são válidos
2. **Lotes de execuções** - Se num_attempts > 10, executa em lotes de 10
3. **Execução em paralelo** - Cada lote roda até 10 execuções simultaneamente
4. **Cada execução**:
   - Gera uma semente aleatória única
   - Executa o solucionador com essa semente
   - Captura: tempo, resultado, semente, código de retorno
5. **Compilação de dados** - Agrupa todos os resultados em um CSV
6. **Estatísticas** - Exibe taxa de sucesso, tempos, etc.

### Paralelização: 10 Execuções Simultâneas por Lote

O script usa **ThreadPoolExecutor** para executar até 10 experimentos em paralelo dentro de cada lote.

**As 10 execuções rodam SIMULTANEAMENTE** (não uma depois da outra):

- **Exemplo com 25 tentativas:**
  - Lote 1: 10 execuções rodam **ao mesmo tempo**
  - Lote 2: 10 execuções rodam **ao mesmo tempo**
  - Lote 3: 5 execuções rodam **ao mesmo tempo**

Isto acelera significativamente o tempo total de execução!

**Comparação:**
- Modo sequencial (antes): 25 tentativas × 2 segundos cada = 50 segundos mínimo
- Modo paralelo (agora): ~5 segundos por lote = ~10 segundos total (aproximadamente)

## Formato do Arquivo CSV

Os resultados são salvos em `results/` com o padrão:

`<puzzle_name>_<preprocessing>_<timestamp>.csv`

**Exemplo de arquivo**: `s01a_without_pp_20250204_143022.csv`

### Colunas do CSV

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| `attempt_number` | Número da tentativa | 1, 2, 3, ... |
| `puzzle_name` | Nome do puzzle | s01a |
| `preprocessing` | SIM ou NÃO | NÃO |
| `seed` | Semente aleatória usada | 1234567890 |
| `solved` | Se foi resolvido (SIM/NÃO) | SIM |
| `execution_time_seconds` | Tempo em segundos | 2.3456 |
| `return_code` | Código de retorno do processo | 0 |
| `final_solution` | Sudoku final preenchido (string 81 dígitos) | 534678912... |
| `timestamp` | Data/hora da execução | 2025-02-04T14:30:22 |

### Exemplo de CSV

```
attempt_number,puzzle_name,preprocessing,seed,solved,execution_time_seconds,return_code,final_solution,timestamp
1,s01a,NÃO,1234567890,SIM,2.3456,0,534678912789...,2025-02-04T14:30:22.123456
2,s01a,NÃO,1234567891,NÃO,1.8901,1,N/A,2025-02-04T14:30:26.456789
3,s01a,NÃO,1234567892,SIM,2.5123,0,534678912789...,2025-02-04T14:30:30.789012
```

## Análise de Resultados

### Interpretar as Estatísticas

Após a execução, o script exibe automaticamente:

```
======================================================================
ESTATÍSTICAS - s01a
======================================================================
Puzzle: s01a
Pré-processamento: NÃO
Total de tentativas: 20
Resolvidos: 18/20 (90.0%)
Tempo médio: 2.3456s
Tempo mínimo: 1.8901s
Tempo máximo: 3.2109s
======================================================================
```

**Interpretação:**
- **Taxa de sucesso**: 90% das tentativas resolveram o puzzle
- **Tempo médio**: Em média, leva ~2.34 segundos
- **Tempo mínimo/máximo**: Variação entre 1.89s e 3.21s

### Script de Análise Automática

O projeto inclui um script Python para análise automática dos resultados:

**Localização:** `scripts/analyze_results.py`

#### Uso

```bash
# Analisar um arquivo específico
python scripts/analyze_results.py results/s01a_without_pp_20250204_143022.csv

# Analisar múltiplos arquivos (padrão glob)
python scripts/analyze_results.py 'results/s01a_*'

# Analisar todos os resultados
python scripts/analyze_results.py results/
```

#### Exemplo de Output

```
======================================================================
ANALISANDO RESULTADOS DOS EXPERIMENTOS
======================================================================

✓ Carregado: s01a_without_pp_20250204_143022.csv (20 registros)

======================================================================
ESTATÍSTICAS GERAIS
======================================================================

Total de registros: 20
Arquivos únicos: 1
Puzzles únicos: 1
Configurações testadas: 1

Resolvidos: 18/20 (90.0%)
Tempo médio: 2.3456s

======================================================================
ESTATÍSTICAS POR PUZZLE
======================================================================

s01a:
  Total: 20 tentativas
  Taxa de sucesso: 90.0%
  Tempo médio: 2.3456s
```

O script também gera um arquivo de resumo: `results_summary_YYYYMMDD_HHMMSS.txt`

### Análise Avançada com Pandas

Para análise mais detalhada, você pode usar pandas diretamente:

```python
import pandas as pd

# Carregar dados
df = pd.read_csv('results/s01a_without_pp_20250204_143022.csv')

# Estatísticas básicas
print(df['execution_time_seconds'].describe())

# Agrupar por pré-processamento
print(df.groupby('preprocessing')['solved'].value_counts())

# Tempo médio por status
print(df.groupby('solved')['execution_time_seconds'].mean())

# Taxas de sucesso
print(f"Taxa de sucesso: {(df['solved'] == 'SIM').sum() / len(df) * 100:.1f}%")
```

## Puzzles Disponíveis

A coleção Mantere contém os seguintes puzzles:

```
s01a.txt, s01b.txt, s01c.txt
s02a.txt, s02b.txt, s02c.txt
s03a.txt, s03b.txt, s03c.txt
...
s16.txt
```

Para ver a lista completa:

```bash
ls puzzles/mantere_collection/
```

## Dicas e Boas Práticas

### 1. **Começar com poucas tentativas**

Para testar o setup, comece com 3-5 tentativas:

```bash
./scripts/batch_experiments.sh s01a 3 --without-pp
```

### 2. **Comparar com e sem pré-processamento**

Execute o mesmo puzzle com ambas as configurações:

```bash
./scripts/batch_experiments.sh s01a 20 --without-pp
./scripts/batch_experiments.sh s01a 20 --with-pp
```

Depois compare os resultados em `results/`.

### 3. **Testar vários puzzles**

Crie um script bash para testar múltiplos puzzles:

```bash
#!/bin/bash
for puzzle in s01a s01b s01c s02a s02b; do
    ./scripts/batch_experiments.sh "$puzzle" 10 --without-pp
done
```

### 4. **Monitorar durante a execução**

Em outro terminal, monitore o uso de recursos:

```bash
watch -n 1 'ps aux | grep solver_without_window'
```

Você verá múltiplos processos rodando em paralelo!

### 5. **Nomeador personalizado de resultados**

Você pode visualizar os arquivos CSV gerados:

```bash
ls -lh results/
tail -20 results/s01a_without_pp_*.csv
```

## Troubleshooting

### "Puzzle não encontrado"

```
[ERROR] Puzzle não encontrado: s01x
```

**Solução**: Verifique a grafia do puzzle. Use `ls puzzles/mantere_collection/` para ver nomes válidos.

### "Flag de pré-processamento inválida"

```
[ERROR] Flag de pré-processamento inválida: --com-pp
```

**Solução**: Use `--with-pp` ou `--without-pp` (exatamente).

### "Script Python não encontrado"

Certifique-se que `scripts/batch_runner.py` existe:

```bash
ls -l scripts/batch_runner.py
```

### Execução muito lenta

Se as execuções estão muito lentas:

1. Verifique o uso de CPU/RAM: `top` ou `htop`
2. Reduza o número de tentativas inicialmente
3. Verifique a configuração em `core/config.py`

### Arquivo CSV não gerado

Verifique se o diretório `results/` foi criado:

```bash
mkdir -p results/
```

## Estrutura de Arquivos

```
evolutionary-sudoku-solver_v2/
├── scripts/
│   ├── batch_experiments.sh   ← Script principal
│   └── batch_runner.py        ← Script Python auxiliar
├── results/                    ← Saída (CSVs)
├── puzzles/
│   └── mantere_collection/    ← Puzzles disponíveis
├── core/
│   └── solver.py              ← Solucionador
└── solver_without_window.py   ← Interface CLI
```

## Próximos Passos

Após coletar dados com o script:

1. **Análise Estatística**: Use Python/pandas para análise detalhada
2. **Visualização**: Crie gráficos com matplotlib/plotly
3. **Otimização**: Ajuste parâmetros em `core/config.py` baseado nos resultados
4. **Comparação**: Compare diferentes configurações de pré-processamento

## Contato / Suporte

Para problemas ou dúvidas:

1. Verifique se todos os requisitos estão instalados: `pip install -r requirements.txt`
2. Teste com um puzzle simples primeiro
3. Verifique os logs em `results/`

---

**Última atualização**: Dezembro 2025
