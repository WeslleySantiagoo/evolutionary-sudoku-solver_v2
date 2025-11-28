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
            value = list(candidates)[0]
            self.sudoku[row, col] = value
            print(f"  [Naked Single] Linha {row + 1}, Coluna {col + 1}: "
                  f"colocado {value}")
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
                        print(f"  [Hidden Single] {group_type.capitalize()} {index + 1}, "
                              f"Linha {last_position[0] + 1}, Coluna {last_position[1] + 1}: "
                              f"colocado {candidate}")
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
                        removed_count = 0
                        for r, c in group_indice:
                            if (r, c) not in cells and self.candidates_matrix[r, c]:
                                before_size = len(self.candidates_matrix[r, c])
                                self.candidates_matrix[r, c] -= set(candidates_tuple)
                                if len(self.candidates_matrix[r, c]) < before_size:
                                    sudoku_updated = True
                                    removed_count += 1
                        if removed_count > 0:
                            print(f"  [Naked Pairs] {group_type.capitalize()} {index + 1}: "
                                  f"Par {candidates_tuple} encontrado, "
                                  f"{removed_count} candidatos removidos")

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
                        removed_count = 0
                        for r, c in group_indice:
                            if (r, c) not in triple_cells and self.candidates_matrix[r, c]:
                                before_size = len(self.candidates_matrix[r, c])
                                self.candidates_matrix[r, c] -= union_candidates
                                if len(self.candidates_matrix[r, c]) < before_size:
                                    sudoku_updated = True
                                    removed_count += 1
                        if removed_count > 0:
                            print(f"  [Naked Triples] {group_type.capitalize()} {index + 1}: "
                                  f"Triple {sorted(union_candidates)} encontrado, "
                                  f"{removed_count} candidatos removidos")

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
                        removed_count = 0
                        for r, c in group_indice:
                            if (r, c) not in quad_cells and self.candidates_matrix[r, c]:
                                before_size = len(self.candidates_matrix[r, c])
                                self.candidates_matrix[r, c] -= union_candidates
                                if len(self.candidates_matrix[r, c]) < before_size:
                                    sudoku_updated = True
                                    removed_count += 1
                        if removed_count > 0:
                            print(f"  [Naked Quads] {group_type.capitalize()} {index + 1}: "
                                  f"Quad {sorted(union_candidates)} encontrado, "
                                  f"{removed_count} candidatos removidos")

        return sudoku_updated

    def search_naked_quints(self):
        """
        Procura por Naked Quints no Sudoku.

        Naked Quint: Cinco células em um mesmo grupo que, juntas, contêm
        apenas 5 candidatos diferentes (cada célula pode ter 2, 3, 4 ou 5 desses
        candidatos).

        Exemplo: Células A, B, C, D e E com candidatos:
        A: {1, 3}
        B: {1, 5}
        C: {3, 5, 7}
        D: {3, 7, 9}
        E: {5, 9}
        Os números 1, 3, 5, 7 e 9 devem estar nessas cinco células, então
        podemos removê-los de todas as outras células do grupo.

        Esta é uma técnica mais rara, mas pode ser útil em puzzles muito difíceis.
        Como há apenas 9 células em cada grupo (linha/coluna/subgrade), encontrar
        5 células que compartilham apenas 5 candidatos é menos comum, mas quando
        ocorre, pode eliminar muitos candidatos das 4 células restantes.

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

                # Coleta células vazias com 2, 3, 4 ou 5 candidatos
                cells_with_candidates = []
                for r, c in group_indice:
                    if self.sudoku[r, c] == 0:
                        num_candidates = len(self.candidates_matrix[r, c])
                        if 2 <= num_candidates <= 5:
                            cells_with_candidates.append((r, c))

                # Precisa de pelo menos 5 células para formar um quint
                if len(cells_with_candidates) < 5:
                    continue

                # Testa todas as combinações de 5 células
                from itertools import combinations
                for quint_cells in combinations(cells_with_candidates, 5):
                    # Une todos os candidatos das 5 células
                    union_candidates = set()
                    for r, c in quint_cells:
                        union_candidates |= self.candidates_matrix[r, c]

                    # Se a união tem exatamente 5 candidatos, é um naked quint
                    if len(union_candidates) == 5:
                        # Remove esses candidatos de todas as outras células
                        removed_count = 0
                        for r, c in group_indice:
                            if (r, c) not in quint_cells and self.candidates_matrix[r, c]:
                                before_size = len(self.candidates_matrix[r, c])
                                self.candidates_matrix[r, c] -= union_candidates
                                if len(self.candidates_matrix[r, c]) < before_size:
                                    sudoku_updated = True
                                    removed_count += 1
                        if removed_count > 0:
                            print(f"  [Naked Quints] {group_type.capitalize()} {index + 1}: "
                                  f"Quint {sorted(union_candidates)} encontrado, "
                                  f"{removed_count} candidatos removidos")

        return sudoku_updated

    def search_naked_sextets(self):
        """
        Procura por Naked Sextets (Sextetos) no Sudoku.

        Naked Sextet: Seis células em um mesmo grupo que, juntas, contêm
        apenas 6 candidatos diferentes (cada célula pode ter 2 a 6 desses
        candidatos).

        Como há 9 células em cada grupo, encontrar 6 células que compartilham
        apenas 6 candidatos significa que podemos remover esses 6 números
        das 3 células restantes do grupo.

        Esta é uma técnica muito rara, mas pode ser decisiva em puzzles
        extremamente difíceis onde técnicas menores não fazem progresso.

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

                # Coleta células vazias com 2 a 6 candidatos
                cells_with_candidates = []
                for r, c in group_indice:
                    if self.sudoku[r, c] == 0:
                        num_candidates = len(self.candidates_matrix[r, c])
                        if 2 <= num_candidates <= 6:
                            cells_with_candidates.append((r, c))

                # Precisa de pelo menos 6 células para formar um sextet
                if len(cells_with_candidates) < 6:
                    continue

                # Testa todas as combinações de 6 células
                from itertools import combinations
                for sextet_cells in combinations(cells_with_candidates, 6):
                    # Une todos os candidatos das 6 células
                    union_candidates = set()
                    for r, c in sextet_cells:
                        union_candidates |= self.candidates_matrix[r, c]

                    # Se a união tem exatamente 6 candidatos, é um naked sextet
                    if len(union_candidates) == 6:
                        # Remove esses candidatos de todas as outras células
                        removed_count = 0
                        for r, c in group_indice:
                            if (r, c) not in sextet_cells and self.candidates_matrix[r, c]:
                                before_size = len(self.candidates_matrix[r, c])
                                self.candidates_matrix[r, c] -= union_candidates
                                if len(self.candidates_matrix[r, c]) < before_size:
                                    sudoku_updated = True
                                    removed_count += 1
                        if removed_count > 0:
                            print(f"  [Naked Sextets] {group_type.capitalize()} {index + 1}: "
                                  f"Sextet {sorted(union_candidates)} encontrado, "
                                  f"{removed_count} candidatos removidos")

        return sudoku_updated

    def search_naked_septets(self):
        """
        Procura por Naked Septets (Septetos) no Sudoku.

        Naked Septet: Sete células em um mesmo grupo que, juntas, contêm
        apenas 7 candidatos diferentes (cada célula pode ter 2 a 7 desses
        candidatos).

        Como há 9 células em cada grupo, encontrar 7 células que compartilham
        apenas 7 candidatos significa que podemos remover esses 7 números
        das 2 células restantes do grupo.

        Esta é uma técnica extremamente rara, útil apenas em casos muito
        específicos onde todas as outras técnicas falharam.

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

                # Coleta células vazias com 2 a 7 candidatos
                cells_with_candidates = []
                for r, c in group_indice:
                    if self.sudoku[r, c] == 0:
                        num_candidates = len(self.candidates_matrix[r, c])
                        if 2 <= num_candidates <= 7:
                            cells_with_candidates.append((r, c))

                # Precisa de pelo menos 7 células para formar um septet
                if len(cells_with_candidates) < 7:
                    continue

                # Testa todas as combinações de 7 células
                from itertools import combinations
                for septet_cells in combinations(cells_with_candidates, 7):
                    # Une todos os candidatos das 7 células
                    union_candidates = set()
                    for r, c in septet_cells:
                        union_candidates |= self.candidates_matrix[r, c]

                    # Se a união tem exatamente 7 candidatos, é um naked septet
                    if len(union_candidates) == 7:
                        # Remove esses candidatos de todas as outras células
                        removed_count = 0
                        for r, c in group_indice:
                            if (r, c) not in septet_cells and self.candidates_matrix[r, c]:
                                before_size = len(self.candidates_matrix[r, c])
                                self.candidates_matrix[r, c] -= union_candidates
                                if len(self.candidates_matrix[r, c]) < before_size:
                                    sudoku_updated = True
                                    removed_count += 1
                        if removed_count > 0:
                            print(f"  [Naked Septets] {group_type.capitalize()} {index + 1}: "
                                  f"Septet {sorted(union_candidates)} encontrado, "
                                  f"{removed_count} candidatos removidos")

        return sudoku_updated

    def search_naked_octets(self):
        """
        Procura por Naked Octets (Octetos) no Sudoku.

        Naked Octet: Oito células em um mesmo grupo que, juntas, contêm
        apenas 8 candidatos diferentes (cada célula pode ter 2 a 8 desses
        candidatos).

        Como há 9 células em cada grupo, encontrar 8 células que compartilham
        apenas 8 candidatos significa que podemos remover esses 8 números
        da 1 célula restante do grupo - essencialmente descobrindo o valor
        dessa célula por eliminação.

        Esta é a técnica naked mais extrema possível. É equivalente a um
        Hidden Single (a célula restante terá apenas 1 candidato após a
        remoção), mas encontrada por um caminho diferente.

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

                # Coleta células vazias com 2 a 8 candidatos
                cells_with_candidates = []
                for r, c in group_indice:
                    if self.sudoku[r, c] == 0:
                        num_candidates = len(self.candidates_matrix[r, c])
                        if 2 <= num_candidates <= 8:
                            cells_with_candidates.append((r, c))

                # Precisa de exatamente 8 células para formar um octet
                # (se houver 9 células vazias, não há célula para eliminar)
                if len(cells_with_candidates) != 8:
                    continue

                # Une todos os candidatos das 8 células
                union_candidates = set()
                for r, c in cells_with_candidates:
                    union_candidates |= self.candidates_matrix[r, c]

                # Se a união tem exatamente 8 candidatos, é um naked octet
                if len(union_candidates) == 8:
                    # Remove esses candidatos da única célula restante
                    removed_count = 0
                    for r, c in group_indice:
                        if (r, c) not in cells_with_candidates and self.candidates_matrix[r, c]:
                            before_size = len(self.candidates_matrix[r, c])
                            self.candidates_matrix[r, c] -= union_candidates
                            if len(self.candidates_matrix[r, c]) < before_size:
                                sudoku_updated = True
                                removed_count += 1
                    if removed_count > 0:
                        print(f"  [Naked Octets] {group_type.capitalize()} {index + 1}: "
                              f"Octet {sorted(union_candidates)} encontrado, "
                              f"{removed_count} candidatos removidos")

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
        x_wings_found = 0

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
                    removed_this_wing = 0

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
                                removed_this_wing += 1

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
                                removed_this_wing += 1

                    if removed_this_wing > 0:
                        x_wings_found += 1
                        print(f"  [X-Wing] Número {number} nas linhas "
                              f"{row1 + 1},{row2 + 1} e colunas {col1 + 1},{col2 + 1}: "
                              f"{removed_this_wing} candidatos removidos")

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
                    removed_this_wing = 0

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
                                removed_this_wing += 1

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
                                removed_this_wing += 1

                    if removed_this_wing > 0:
                        x_wings_found += 1
                        print(f"  [X-Wing] Número {number} nas colunas "
                              f"{col1 + 1},{col2 + 1} e linhas {row1 + 1},{row2 + 1}: "
                              f"{removed_this_wing} candidatos removidos")

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
        6. Naked Quints
        7. Naked Sextets (6 células com 6 candidatos)
        8. Naked Septets (7 células com 7 candidatos)
        9. Naked Octets (8 células com 8 candidatos)
        10. X-Wings (padrões lineares complexos)

        O processo itera até que nenhuma técnica consiga fazer progresso,
        otimizando a eficiência ao aplicar técnicas simples primeiro.

        Returns:
            tuple: (sudoku_final, números_preenchidos)
                - sudoku_final: Array NumPy 9x9 com o Sudoku pré-processado
                - números_preenchidos: Quantidade de células preenchidas
        """
        initial_zeros = np.count_nonzero(self.sudoku == 0)
        print(f"\n{'=' * 60}")
        print("INICIANDO PRÉ-PROCESSAMENTO")
        print(f"Células vazias iniciais: {initial_zeros}")
        print(f"{'=' * 60}")

        updated = True
        iteration = 0

        # Itera até que nenhuma técnica faça progresso
        while updated:
            iteration += 1
            updated = False
            print(f"\n--- Iteração {iteration} ---")
            cells_before = np.count_nonzero(self.sudoku == 0)

            # 1. Naked Single: células com apenas 1 candidato
            naked_single_found = False
            for row in range(9):
                for col in range(9):
                    if self.sudoku[row, col] == 0:
                        if self.analyze_cell(row, col):
                            updated = True
                            naked_single_found = True
            if not naked_single_found:
                print("  [Naked Single] Nenhum encontrado")

            # 2. Hidden Single: candidato que aparece em apenas uma célula
            if self.search_hidden_singles():
                updated = True
            else:
                print("  [Hidden Single] Nenhum encontrado")

            # 3. Naked Pairs: 2 células com os mesmos 2 candidatos
            if self.search_naked_pairs():
                updated = True
            else:
                print("  [Naked Pairs] Nenhum encontrado")

            # 4. Naked Triples: 3 células com 3 candidatos no total
            if self.search_naked_triples():
                updated = True
            else:
                print("  [Naked Triples] Nenhum encontrado")

            # 5. Naked Quads: 4 células com 4 candidatos no total
            if self.search_naked_quads():
                updated = True
            else:
                print("  [Naked Quads] Nenhum encontrado")

            # 6. Naked Quints: 5 células com 5 candidatos no total
            if self.search_naked_quints():
                updated = True
            else:
                print("  [Naked Quints] Nenhum encontrado")

            # 7. Naked Sextets: 6 células com 6 candidatos no total
            if self.search_naked_sextets():
                updated = True
            else:
                print("  [Naked Sextets] Nenhum encontrado")

            # 8. Naked Septets: 7 células com 7 candidatos no total
            if self.search_naked_septets():
                updated = True
            else:
                print("  [Naked Septets] Nenhum encontrado")

            # 9. Naked Octets: 8 células com 8 candidatos no total
            if self.search_naked_octets():
                updated = True
            else:
                print("  [Naked Octets] Nenhum encontrado")

            # 10. X-Wings: padrões lineares complexos
            if self.search_x_wing():
                updated = True
            else:
                print("  [X-Wing] Nenhum encontrado")

            cells_after = np.count_nonzero(self.sudoku == 0)
            cells_filled_this_iteration = cells_before - cells_after
            print(f"  → Células preenchidas nesta iteração: {cells_filled_this_iteration}")
            print(f"  → Células vazias restantes: {cells_after}")

        final_zeros = np.count_nonzero(self.sudoku == 0)
        numbers_filled_by_pp = initial_zeros - final_zeros

        print(f"\n{'=' * 60}")
        print("PRÉ-PROCESSAMENTO CONCLUÍDO")
        print(f"Total de iterações: {iteration}")
        print(f"Células preenchidas: {numbers_filled_by_pp}")
        print(f"Células vazias restantes: {final_zeros}")
        print(f"{'=' * 60}\n")

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
