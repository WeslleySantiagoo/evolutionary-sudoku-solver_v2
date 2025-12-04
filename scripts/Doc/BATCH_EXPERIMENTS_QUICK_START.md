# Batch Experiments - Quick Start

## Resumo Rápido

Script para executar múltiplos experimentos de resolução de Sudoku em lote com coleta automática de dados.

## Arquivos Criados

| Arquivo | Descrição |
|---------|-----------|
| `scripts/batch_experiments.sh` | Script shell principal (interface de usuário) |
| `scripts/batch_runner.py` | Script Python auxiliar (executa os experimentos) |
| `scripts/analyze_results.py` | Script Python para análise dos resultados |
| `BATCH_EXPERIMENTS.md` | Documentação completa |

## Como Usar

### 1️⃣ Executar Experimentos

```bash
cd /home/weslley-santiago/Documentos/UFRPE/evolutionary-sudoku-solver_v2
./scripts/batch_experiments.sh s01a 20 --without-pp
```

**Parâmetros:**
- `s01a` = nome do puzzle
- `20` = número de vezes que será executado
- `--without-pp` = sem pré-processamento (ou `--with-pp` com pré-processamento)

**Resultado:** CSV salvo em `results/s01a_without_pp_YYYYMMDD_HHMMSS.csv`

### 2️⃣ Analisar Resultados

```bash
python scripts/analyze_results.py results/s01a_without_pp_*.csv
```

**Gera:**
- Estatísticas gerais (taxa de sucesso, tempos, etc.)
- Quebra por configuração e puzzle
- Matriz de comparação
- Arquivo de resumo em TXT

## Exemplos de Uso

### Teste rápido
```bash
./scripts/batch_experiments.sh s01a 3 --without-pp
```

### Comparar com e sem pré-processamento
```bash
./scripts/batch_experiments.sh s01a 20 --without-pp
./scripts/batch_experiments.sh s01a 20 --with-pp
```

### Testar múltiplos puzzles
```bash
for puzzle in s01a s01b s02a; do
    ./scripts/batch_experiments.sh "$puzzle" 10 --without-pp
done
```

## Dados Capturados

O CSV inclui:
- ✅ Número da tentativa
- ✅ Nome do puzzle
- ✅ Configuração (com/sem pré-processamento)
- ✅ Semente aleatória usada
- ✅ Se foi resolvido (SIM/NÃO)
- ✅ Tempo de execução (segundos)
- ✅ Código de retorno
- ✅ Sudoku final preenchido
- ✅ Timestamp

## Recursos Principais

- 🔄 Sementes **sempre aleatórias** (determinísticas quando necessário)
- 📊 Execuções em lotes de até 10 (para evitar sobrecarga)
- 💾 Salvamento automático em CSV
- 📈 Estatísticas instantâneas ao final
- 🎨 Saída colorida e legível
- ⚡ Suporte para múltiplos puzzles e configurações

## Próximos Passos

1. **Coletar dados**: Rode experimentos com diferentes puzzles
2. **Analisar**: Use `analyze_results.py` para gerar estatísticas
3. **Comparar**: Compare resultados com/sem pré-processamento
4. **Otimizar**: Ajuste parâmetros em `core/config.py` baseado nos dados

## Documentação Completa

Para mais detalhes, consulte `BATCH_EXPERIMENTS.md`:

```bash
cat BATCH_EXPERIMENTS.md
```

---

**Status:** ✅ Totalmente funcional  
**Teste:** ✅ Verificado  
**Última atualização:** Dezembro 2025
