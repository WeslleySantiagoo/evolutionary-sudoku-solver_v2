# Técnicas de Pré-Processamento do Sudoku

Este documento descreve as técnicas implementadas no módulo `core/pre_processing.py` para resolver Sudoku antes de aplicar o Algoritmo Genético.

## Hierarquia de Técnicas

As técnicas são aplicadas na seguinte ordem, do mais simples ao mais complexo:

### 1. **Naked Single** (Célula Óbvia)

- **Complexidade:** Muito Baixa
- **O que faz:** Preenche células que têm apenas 1 candidato possível
- **Exemplo:**
  ```
  Se uma célula só pode ser o número 7, coloca-se 7
  Candidatos: {7} → Valor: 7
  ```

### 2. **Hidden Single** (Candidato Único)

- **Complexidade:** Baixa
- **O que faz:** Encontra números que só podem estar em uma célula dentro de uma linha, coluna ou subgrade
- **Exemplo:**
  ```
  Se o número 5 só pode estar em uma célula da linha 3,
  coloca-se 5 nessa célula, mesmo que ela tenha outros candidatos
  ```

### 3. **Naked Pairs** (Pares Óbvios)

- **Complexidade:** Média
- **O que faz:** Duas células com exatamente os mesmos 2 candidatos
- **Exemplo:**

  ```
  Célula A: {3, 7}
  Célula B: {3, 7}

  → Os números 3 e 7 devem estar em A e B
  → Remove 3 e 7 de todas as outras células do grupo
  ```

### 4. **Naked Triples** (Trios Óbvios) ⭐ NOVO

- **Complexidade:** Média-Alta
- **O que faz:** Três células que juntas contêm apenas 3 candidatos diferentes
- **Exemplo:**

  ```
  Célula A: {2, 5}
  Célula B: {2, 7}
  Célula C: {5, 7}

  → Os números 2, 5 e 7 devem estar em A, B e C
  → Remove 2, 5 e 7 de todas as outras células do grupo
  ```

- **Funcionamento:**
  1. Procura grupos de 3 células com 2 ou 3 candidatos cada
  2. Une os candidatos das 3 células
  3. Se a união tem exatamente 3 números, é um Naked Triple
  4. Remove esses 3 números de todas as outras células do grupo

### 5. **Naked Quads** (Quartetos Óbvios) ⭐ NOVO

- **Complexidade:** Alta
- **O que faz:** Quatro células que juntas contêm apenas 4 candidatos diferentes
- **Exemplo:**

  ```
  Célula A: {1, 4}
  Célula B: {1, 6}
  Célula C: {4, 6, 8}
  Célula D: {4, 8}

  → Os números 1, 4, 6 e 8 devem estar em A, B, C e D
  → Remove 1, 4, 6 e 8 de todas as outras células do grupo
  ```

- **Funcionamento:**
  1. Procura grupos de 4 células com 2, 3 ou 4 candidatos cada
  2. Une os candidatos das 4 células
  3. Se a união tem exatamente 4 números, é um Naked Quad
  4. Remove esses 4 números de todas as outras células do grupo

### 6. **X-Wings** (Padrões Lineares)

- **Complexidade:** Alta
- **O que faz:** Encontra padrões retangulares que permitem eliminar candidatos
- **Exemplo visual:**

  ```
  Candidato 5:
  Linha 2: ... 5 ... 5 ...
  Linha 7: ... 5 ... 5 ...
             Col3   Col6

  → O 5 deve estar em uma dessas posições em cada linha
  → Remove 5 de todas as outras células das colunas 3 e 6
  ```

## Fluxo de Execução

```
┌─────────────────────────────────────────┐
│   Inicializa candidatos para cada célula│
└─────────────────┬───────────────────────┘
                  │
                  ▼
        ┌─────────────────────┐
        │   Loop Principal     │
        │  (até nenhuma        │
        │   mudança)           │
        └──────────┬───────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌────────┐  ┌─────────────┐  ┌────────┐
│ Naked  │  │   Hidden    │  │ Naked  │
│ Single │  │   Single    │  │ Pairs  │
└───┬────┘  └──────┬──────┘  └────┬───┘
    │              │              │
    └──────────────┼──────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌────────┐  ┌─────────────┐  ┌────────┐
│ Naked  │  │   Naked     │  │X-Wings │
│Triples │  │   Quads     │  │        │
└───┬────┘  └──────┬──────┘  └────┬───┘
    │              │              │
    └──────────────┼──────────────┘
                   │
                   ▼
            ┌──────────────┐
            │ Houve mudança?│
            └──────┬───────┘
                   │
         ┌─────────┴─────────┐
         │                   │
       SIM                  NÃO
         │                   │
         └───► (repete)      └───► FIM
```

## Otimização de Eficiência

A ordem das técnicas foi escolhida para maximizar a eficiência:

1. **Técnicas Simples Primeiro:** Naked Single e Hidden Single são rápidas e frequentemente eficazes
2. **Hierarquia Natural:** Pairs → Triples → Quads segue uma progressão lógica de complexidade
3. **Complexas por Último:** X-Wings é computacionalmente mais caro, então é aplicado depois

Esta estratégia minimiza o número de iterações necessárias e reduz o tempo de pré-processamento.

## Resultados

Com a implementação completa das 6 técnicas, o pré-processamento é capaz de:

- Resolver puzzles fáceis e médios **completamente** (sem necessidade do AG)
- Reduzir significativamente o espaço de busca para puzzles difíceis
- Preencher células com **100% de certeza lógica**

## Implementação Técnica

### Estruturas de Dados

- `sudoku`: Array NumPy 9x9 (0 = célula vazia)
- `candidates_matrix`: Matrix 9x9 de conjuntos (set) com candidatos possíveis

### Grupos Analisados

Cada técnica analisa três tipos de grupos:

- **Linhas:** 9 células horizontais
- **Colunas:** 9 células verticais
- **Subgrades:** Blocos 3x3

### Critério de Parada

O loop continua iterando até que **nenhuma técnica** consiga fazer progresso (preencher células ou remover candidatos).

## Exemplo de Uso

```python
from core import pre_processing as pp
import numpy as np

# Carrega puzzle
original = np.array([...])  # 9x9 com zeros

# Aplica pré-processamento
pp_controller = pp.Controller()
pp_controller.load(original)
processed, numbers_filled = pp_controller.controller()

print(f"Preenchidos: {numbers_filled}")
```

## Referências

- Naked Singles/Pairs/Triples/Quads: Técnicas padrão de resolução de Sudoku
- X-Wings: Padrão avançado descoberto por resolventes de Sudoku
- Documentação completa em: `core/pre_processing.py`
