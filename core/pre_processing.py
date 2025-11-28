import numpy as np


class PreProcessing(object):

    def __init__(self, sudoku):
        """
        Inicializa o objeto de pré-processamento.

        Args:
            sudoku: Array NumPy 9x9 representando o tabuleiro de Sudoku.
                   Células vazias são representadas por 0.
        """
        self.sudoku = sudoku
        self.candidates_matrix = np.full((9, 9), None)
        self.map_initial_candidates()

    def map_initial_candidates(self):
        """
        Mapeia os candidatos iniciais para cada célula vazia do Sudoku.

        Para cada célula vazia (valor 0), calcula os números possíveis
        que podem ser colocados sem violar as regras do Sudoku.
        """
        for row in range(9):
            for col in range(9):
                if self.sudoku[row, col] == 0:
                    self.candidates_matrix[row, col] = self.get_candidates(row, col)
                else:
                    self.candidates_matrix[row, col] = set()

    def get_candidates(self, row, col):
        """
        Calcula os candidatos possíveis para uma célula específica.

        Args:
            row: Índice da linha (0-8)
            col: Índice da coluna (0-8)

        Returns:
            set: Conjunto de números (1-9) que podem ser colocados na célula
                 sem violar as regras do Sudoku (linha, coluna e subgrade 3x3).
        """
        all_numbers = set(range(1, 10))
        used_numbers = set(self.sudoku[row, :]) | set(self.sudoku[:, col])
        grid_row = (row // 3) * 3
        grid_col = (col // 3) * 3
        used_numbers |= set(self.sudoku[
            grid_row:grid_row + 3, grid_col:grid_col + 3
        ].flatten())
        candidates = all_numbers - used_numbers
        return candidates

    def analyze_cell(self, row, col):
        """
        Analisa uma célula e aplica técnicas simples de resolução.

        Aplica as seguintes técnicas na ordem:
        1. Naked Single (Full House): Se a célula tem apenas 1 candidato,
           preenche com esse valor.

        Args:
            row: Índice da linha (0-8)
            col: Índice da coluna (0-8)

        Returns:
            bool: True se o Sudoku foi atualizado, False caso contrário.
        """
        sudoku_updated = False
        candidates = self.candidates_matrix[row, col]

        # Naked Single (Full House): célula com apenas 1 candidato
        if len(candidates) == 1:
            self.sudoku[row, col] = candidates.pop()
            self.update_candidates(row, col)
            sudoku_updated = True

        return sudoku_updated

    def search_hidden_singles(self):
        """
        Procura por Hidden Singles no Sudoku.

        Hidden Single: Um candidato que aparece em apenas uma célula
        dentro de uma linha, coluna ou subgrade 3x3.

        Exemplo: Se o número 7 só pode estar em uma célula de uma linha,
        mesmo que essa célula tenha outros candidatos, coloca-se o 7.

        Returns:
            bool: True se algum número foi colocado, False caso contrário.
        """
        sudoku_updated = False

        # Verifica todas as linhas, colunas e subgrades
        for group_type in ["row", "col", "subgrid"]:
            for index in range(9):
                # Determina as células do grupo (linha, coluna ou subgrade)
                if group_type == "row":
                    group_indice = [(index, i) for i in range(9)]
                elif group_type == "col":
                    group_indice = [(i, index) for i in range(9)]
                elif group_type == "subgrid":
                    row_start, col_start = (index // 3) * 3, (index % 3) * 3
                    group_indice = [
                        (row_start + r, col_start + c)
                        for r in range(3) for c in range(3)
                    ]

                # Para cada número de 1 a 9, verifica se é um hidden single
                for candidate in range(1, 10):
                    count = 0
                    last_position = None

                    # Conta em quantas células vazias o candidato aparece
                    for r, c in group_indice:
                        if self.sudoku[r, c] == 0 and candidate in self.candidates_matrix[r, c]:
                            count += 1
                            last_position = (r, c)

                    # Se aparece em apenas uma célula, é um hidden single
                    if count == 1 and last_position:
                        self.sudoku[last_position[0], last_position[1]] = candidate
                        self.update_candidates(last_position[0], last_position[1])
                        sudoku_updated = True

        return sudoku_updated

    def search_naked_pairs(self):
        """
        Procura por Naked Pairs no Sudoku.

        Naked Pair: Duas células em um mesmo grupo (linha, coluna ou subgrade)
        que possuem exatamente os mesmos 2 candidatos.

        Exemplo: Se as células A e B têm candidatos {3, 7}, então 3 e 7
        devem estar nessas duas células. Portanto, podemos remover 3 e 7
        de todas as outras células do mesmo grupo.

        Returns:
            bool: True se algum candidato foi removido, False caso contrário.
        """
        sudoku_updated = False

        # Verifica linhas, colunas e subgrades
        for group_type in ["row", "col", "subgrid"]:
            for index in range(9):
                # Determina as células do grupo
                if group_type == "row":
                    group_indice = [(index, i) for i in range(9)]
                elif group_type == "col":
                    group_indice = [(i, index) for i in range(9)]
                elif group_type == "subgrid":
                    row_start, col_start = (index // 3) * 3, (index % 3) * 3
                    group_indice = [
                        (row_start + r, col_start + c)
                        for r in range(3) for c in range(3)
                    ]

                # Mapeia células com exatamente 2 candidatos
                pairs = {}
                for r, c in group_indice:
                    if self.sudoku[r, c] == 0 and len(self.candidates_matrix[r, c]) == 2:
                        candidates_tuple = tuple(sorted(self.candidates_matrix[r, c]))
                        if candidates_tuple not in pairs:
                            pairs[candidates_tuple] = []
                        pairs[candidates_tuple].append((r, c))

                # Procura por pares que aparecem em exatamente 2 células
                for candidates_tuple, cells in pairs.items():
                    if len(cells) == 2:
                        # Remove os candidatos do par de todas as outras células
                        for r, c in group_indice:
                            if (r, c) not in cells and self.candidates_matrix[r, c]:
                                before_size = len(self.candidates_matrix[r, c])
                                self.candidates_matrix[r, c] -= set(candidates_tuple)
                                if len(self.candidates_matrix[r, c]) < before_size:
                                    sudoku_updated = True

        return sudoku_updated

    def search_naked_triples(self):
        """
        Procura por Naked Triples no Sudoku.

        Naked Triple: Três células em um mesmo grupo que, juntas, contêm
        apenas 3 candidatos diferentes (cada célula pode ter 2 ou 3 desses
        candidatos).

        Exemplo: Células A, B e C com candidatos:
        A: {2, 5}
        B: {2, 7}
        C: {5, 7}
        Os números 2, 5 e 7 devem estar nessas três células, então podemos
        removê-los de todas as outras células do grupo.

        Returns:
            bool: True se algum candidato foi removido, False caso contrário.
        """
        sudoku_updated = False

        # Verifica linhas, colunas e subgrades
        for group_type in ["row", "col", "subgrid"]:
            for index in range(9):
                # Determina as células do grupo
                if group_type == "row":
                    group_indice = [(index, i) for i in range(9)]
                elif group_type == "col":
                    group_indice = [(i, index) for i in range(9)]
                elif group_type == "subgrid":
                    row_start, col_start = (index // 3) * 3, (index % 3) * 3
                    group_indice = [
                        (row_start + r, col_start + c)
                        for r in range(3) for c in range(3)
                    ]

                # Coleta células vazias com 2 ou 3 candidatos
                cells_with_candidates = []
                for r, c in group_indice:
                    if self.sudoku[r, c] == 0:
                        num_candidates = len(self.candidates_matrix[r, c])
                        if 2 <= num_candidates <= 3:
                            cells_with_candidates.append((r, c))

                # Precisa de pelo menos 3 células para formar um triple
                if len(cells_with_candidates) < 3:
                    continue

                # Testa todas as combinações de 3 células
                from itertools import combinations
                for triple_cells in combinations(cells_with_candidates, 3):
                    # Une todos os candidatos das 3 células
                    union_candidates = set()
                    for r, c in triple_cells:
                        union_candidates |= self.candidates_matrix[r, c]

                    # Se a união tem exatamente 3 candidatos, é um naked triple
                    if len(union_candidates) == 3:
                        # Remove esses candidatos de todas as outras células
                        for r, c in group_indice:
                            if (r, c) not in triple_cells and self.candidates_matrix[r, c]:
                                before_size = len(self.candidates_matrix[r, c])
                                self.candidates_matrix[r, c] -= union_candidates
                                if len(self.candidates_matrix[r, c]) < before_size:
                                    sudoku_updated = True

        return sudoku_updated

    def search_naked_quads(self):
        """
        Procura por Naked Quads no Sudoku.

        Naked Quad: Quatro células em um mesmo grupo que, juntas, contêm
        apenas 4 candidatos diferentes (cada célula pode ter 2, 3 ou 4 desses
        candidatos).

        Exemplo: Células A, B, C e D com candidatos:
        A: {1, 4}
        B: {1, 6}
        C: {4, 6, 8}
        D: {4, 8}
        Os números 1, 4, 6 e 8 devem estar nessas quatro células, então
        podemos removê-los de todas as outras células do grupo.

        Returns:
            bool: True se algum candidato foi removido, False caso contrário.
        """
        sudoku_updated = False

        # Verifica linhas, colunas e subgrades
        for group_type in ["row", "col", "subgrid"]:
            for index in range(9):
                # Determina as células do grupo
                if group_type == "row":
                    group_indice = [(index, i) for i in range(9)]
                elif group_type == "col":
                    group_indice = [(i, index) for i in range(9)]
                elif group_type == "subgrid":
                    row_start, col_start = (index // 3) * 3, (index % 3) * 3
                    group_indice = [
                        (row_start + r, col_start + c)
                        for r in range(3) for c in range(3)
                    ]

                # Coleta células vazias com 2, 3 ou 4 candidatos
                cells_with_candidates = []
                for r, c in group_indice:
                    if self.sudoku[r, c] == 0:
                        num_candidates = len(self.candidates_matrix[r, c])
                        if 2 <= num_candidates <= 4:
                            cells_with_candidates.append((r, c))

                # Precisa de pelo menos 4 células para formar um quad
                if len(cells_with_candidates) < 4:
                    continue

                # Testa todas as combinações de 4 células
                from itertools import combinations
                for quad_cells in combinations(cells_with_candidates, 4):
                    # Une todos os candidatos das 4 células
                    union_candidates = set()
                    for r, c in quad_cells:
                        union_candidates |= self.candidates_matrix[r, c]

                    # Se a união tem exatamente 4 candidatos, é um naked quad
                    if len(union_candidates) == 4:
                        # Remove esses candidatos de todas as outras células
                        for r, c in group_indice:
                            if (r, c) not in quad_cells and self.candidates_matrix[r, c]:
                                before_size = len(self.candidates_matrix[r, c])
                                self.candidates_matrix[r, c] -= union_candidates
                                if len(self.candidates_matrix[r, c]) < before_size:
                                    sudoku_updated = True

        return sudoku_updated

    def search_x_wing(self):
        """
        Procura por padrões X-Wing no Sudoku.

        X-Wing: Um padrão onde um candidato aparece em exatamente 2 posições
        em 2 linhas diferentes, e essas posições estão nas mesmas 2 colunas.
        Ou vice-versa (2 colunas com o candidato nas mesmas 2 linhas).

        Exemplo visual (candidato 5):
        Linha 2: ... 5 ... 5 ...
        Linha 7: ... 5 ... 5 ...
                   Col3   Col6

        Como o 5 deve estar em uma dessas posições em cada linha,
        podemos remover o 5 de todas as outras células das colunas 3 e 6.

        Returns:
            bool: True se algum candidato foi removido, False caso contrário.
        """
        updated_in_x_wing = False

        # Procura X-Wings baseados em linhas
        for number in range(1, 10):
            row_pairs = {}

            # Para cada linha, encontra colunas onde o número é candidato
            for r in range(9):
                cols_with_num = [c for c in range(9)
                                 if (self.sudoku[r, c] == 0 and number in
                                     self.candidates_matrix[r, c])]

                # Se o número aparece em exatamente 2 colunas
                if len(cols_with_num) == 2:
                    cols_tuple = tuple(cols_with_num)
                    if cols_tuple not in row_pairs:
                        row_pairs[cols_tuple] = []
                    row_pairs[cols_tuple].append(r)

            # Se duas linhas têm o número nas mesmas 2 colunas: X-Wing!
            for cols, rows in row_pairs.items():
                if len(rows) == 2:
                    col1, col2 = cols
                    row1, row2 = rows

                    # Remove o número de outras células dessas colunas
                    for r_idx in range(9):
                        if r_idx not in rows:
                            # Coluna 1
                            cell_empty_col1 = self.sudoku[r_idx, col1] == 0
                            has_num_col1 = (
                                number in self.candidates_matrix[r_idx, col1]
                            )
                            if cell_empty_col1 and has_num_col1:
                                self.candidates_matrix[r_idx, col1].remove(
                                    number
                                )
                                updated_in_x_wing = True

                            # Coluna 2
                            cell_empty_col2 = self.sudoku[r_idx, col2] == 0
                            has_num_col2 = (
                                number in self.candidates_matrix[r_idx, col2]
                            )
                            if cell_empty_col2 and has_num_col2:
                                self.candidates_matrix[r_idx, col2].remove(
                                    number
                                )
                                updated_in_x_wing = True

        # Procura X-Wings baseados em colunas (inverso do anterior)
        for number in range(1, 10):
            col_pairs = {}

            # Para cada coluna, encontra linhas onde o número é candidato
            for c in range(9):
                rows_with_num = [r for r in range(9)
                                 if (self.sudoku[r, c] == 0 and number in
                                     self.candidates_matrix[r, c])]

                # Se o número aparece em exatamente 2 linhas
                if len(rows_with_num) == 2:
                    rows_tuple = tuple(rows_with_num)
                    if rows_tuple not in col_pairs:
                        col_pairs[rows_tuple] = []
                    col_pairs[rows_tuple].append(c)

            # Se duas colunas têm o número nas mesmas 2 linhas: X-Wing!
            for rows, cols in col_pairs.items():
                if len(cols) == 2:
                    row1, row2 = rows
                    col1, col2 = cols

                    # Remove o número de outras células dessas linhas
                    for c_idx in range(9):
                        if c_idx not in cols:
                            # Linha 1
                            cell_empty_row1 = self.sudoku[row1, c_idx] == 0
                            has_num_row1 = (
                                number in self.candidates_matrix[row1, c_idx]
                            )
                            if cell_empty_row1 and has_num_row1:
                                self.candidates_matrix[row1, c_idx].remove(
                                    number
                                )
                                updated_in_x_wing = True

                            # Linha 2
                            cell_empty_row2 = self.sudoku[row2, c_idx] == 0
                            has_num_row2 = (
                                number in self.candidates_matrix[row2, c_idx]
                            )
                            if cell_empty_row2 and has_num_row2:
                                self.candidates_matrix[row2, c_idx].remove(
                                    number
                                )
                                updated_in_x_wing = True

        return updated_in_x_wing

    def update_candidates(self, row, col):
        """
        Atualiza a matriz de candidatos após colocar um número em uma célula.

        Remove o número colocado dos candidatos de todas as células que
        compartilham a mesma linha, coluna ou subgrade 3x3.

        Args:
            row: Índice da linha onde o número foi colocado (0-8)
            col: Índice da coluna onde o número foi colocado (0-8)
        """
        placed_number = self.sudoku[row, col]

        # Remove da linha
        for c in range(9):
            if placed_number in self.candidates_matrix[row, c]:
                self.candidates_matrix[row, c].remove(placed_number)

        # Remove da coluna
        for r in range(9):
            if placed_number in self.candidates_matrix[r, col]:
                self.candidates_matrix[r, col].remove(placed_number)

        # Remove da subgrade 3x3
        grid_row = (row // 3) * 3
        grid_col = (col // 3) * 3
        for r in range(grid_row, grid_row + 3):
            for c in range(grid_col, grid_col + 3):
                if placed_number in self.candidates_matrix[r, c]:
                    self.candidates_matrix[r, c].remove(placed_number)

    def preprocess(self):
        """
        Executa o pré-processamento completo do Sudoku.

        Aplica técnicas de resolução na seguinte ordem hierárquica:
        1. Naked Single (mais simples)
        2. Hidden Single
        3. Naked Pairs
        4. Naked Triples
        5. Naked Quads
        6. X-Wings (padrões lineares complexos)

        O processo itera até que nenhuma técnica consiga fazer progresso,
        otimizando a eficiência ao aplicar técnicas simples primeiro.

        Returns:
            tuple: (sudoku_final, números_preenchidos)
                - sudoku_final: Array NumPy 9x9 com o Sudoku pré-processado
                - números_preenchidos: Quantidade de células preenchidas
        """
        initial_zeros = np.count_nonzero(self.sudoku == 0)
        updated = True

        # Itera até que nenhuma técnica faça progresso
        while updated:
            updated = False

            # 1. Naked Single: células com apenas 1 candidato
            for row in range(9):
                for col in range(9):
                    if self.sudoku[row, col] == 0:
                        if self.analyze_cell(row, col):
                            updated = True

            # 2. Hidden Single: candidato que aparece em apenas uma célula
            if self.search_hidden_singles():
                updated = True

            # 3. Naked Pairs: 2 células com os mesmos 2 candidatos
            if self.search_naked_pairs():
                updated = True

            # 4. Naked Triples: 3 células com 3 candidatos no total
            if self.search_naked_triples():
                updated = True

            # 5. Naked Quads: 4 células com 4 candidatos no total
            if self.search_naked_quads():
                updated = True

            # 6. X-Wings: padrões lineares complexos
            if self.search_x_wing():
                updated = True

        final_zeros = np.count_nonzero(self.sudoku == 0)
        numbers_filled_by_pp = initial_zeros - final_zeros
        return self.sudoku, numbers_filled_by_pp


class Controller(object):
    """
    Controlador para gerenciar o pré-processamento do Sudoku.

    Esta classe serve como interface para carregar um Sudoku e
    executar o pré-processamento através da classe PreProcessing.
    """

    def __init__(self):
        """Inicializa o controlador."""
        return

    def load(self, p):
        """
        Carrega um Sudoku para pré-processamento.

        Args:
            p: Array NumPy 9x9 representando o Sudoku inicial.
        """
        self.sudoku = p
        return

    def controller(self):
        """
        Executa o pré-processamento do Sudoku carregado.

        Returns:
            tuple: (tabuleiro_final, números_preenchidos)
                - tabuleiro_final: Sudoku após pré-processamento
                - números_preenchidos: Quantidade de células preenchidas
        """
        preprocessor = PreProcessing(self.sudoku)
        final_board, numbers_filled = preprocessor.preprocess()
        return final_board, numbers_filled
