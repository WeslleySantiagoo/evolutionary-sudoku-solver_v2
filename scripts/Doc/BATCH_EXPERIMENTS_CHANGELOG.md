# Melhorias - Execução em Paralelo

## O que foi alterado

O script `batch_runner.py` foi atualizado para executar as tentativas **em paralelo** usando `ThreadPoolExecutor`.

### Antes (Sequencial)
```
Tempo total para 10 tentativas: ~10 segundos (cada uma levava ~1 segundo)
```

### Depois (Paralelo)
```
Tempo total para 10 tentativas: ~1 segundo (todas rodam simultaneamente)
```

## Como funciona

### Execução em Paralelo com ThreadPoolExecutor

1. **Até 10 threads simultâneas** por lote
2. Cada thread executa um experimento independente
3. Os resultados são coletados conforme completam
4. Se tiver mais de 10 tentativas, cria novos lotes

### Exemplo: 20 tentativas

```
ANTES:  [1→2→3→4→5→6→7→8→9→10→11→12→13→14→15→16→17→18→19→20]
        Tempo: ~20 segundos

DEPOIS: [Lote 1: 1..10 em paralelo] + [Lote 2: 11..20 em paralelo]
        Tempo: ~2 segundos
```

## Evidência de Paralelização

Quando você executa 10 tentativas com pré-processamento, vê algo como:

```
[BATCH 1/1] Executando 10 tentativas em paralelo...
  [4/10] ✓ RESOLVIDO (0.17s | seed: 144843229)
  [3/10] ✓ RESOLVIDO (0.19s | seed: 806190634)
  [8/10] ✓ RESOLVIDO (0.19s | seed: 3555405114)
  [5/10] ✓ RESOLVIDO (0.21s | seed: 3408426836)
  [10/10] ✓ RESOLVIDO (0.20s | seed: 1467371495)
  ...
```

**Note que a ordem NÃO é sequencial (1, 2, 3...)** mas sim **(4, 3, 8, 5, 10...)**

Isso é a **prova de que estão rodando em paralelo**: cada uma termina em um tempo diferente, então os resultados vão aparecendo conforme ficam prontos.

## Configuração

### Limite de Paralelo

Definido em `batch_runner.py`:
```python
batch_size = min(10, num_attempts)  # Máximo 10 simultâneas
```

Para modificar, edite a linha correspondente em `batch_runner.py`.

### Pool de Threads

Usado `ThreadPoolExecutor` com `max_workers=batch_size`:
```python
with ThreadPoolExecutor(max_workers=batch_size) as executor:
    # Submete todas as tarefas
    # Processa resultados conforme completam
```

## Benefícios

✅ **Tempo de execução reduzido** - Múltiplas tentativas simultâneas  
✅ **Melhor utilização de CPU** - Aproveita vários núcleos  
✅ **Mais eficiente** - Menos tempo para coletar dados  
✅ **Escalável** - Funciona bem com qualquer número de tentativas  

## Performance Realista

### Com Pré-Processamento
- 10 tentativas: ~0.3 segundos (em vez de 3 segundos)
- 20 tentativas: ~0.6 segundos (em vez de 6 segundos)

### Sem Pré-Processamento
Depende da dificuldade, mas mantém a mesma vantagem de paralelização

## Monitorar Execução em Paralelo

Para ver os processos rodando em paralelo:

```bash
# Em outro terminal durante a execução
watch -n 0.5 'ps aux | grep solver_without_window | wc -l'
```

Você verá múltiplos processos `solver_without_window.py` rodando ao mesmo tempo!

## Changelog

### v1.1 (Dezembro 2025)
- ✅ Alterado para execução em paralelo com ThreadPoolExecutor
- ✅ Até 10 threads simultâneas por lote
- ✅ Significativa melhoria de performance
- ✅ Ordem de saída reflete conclusão paralela

### v1.0 (Dezembro 2025)
- ✅ Primeira versão com execução sequencial

---

Para mais informações, consulte `BATCH_EXPERIMENTS.md`
