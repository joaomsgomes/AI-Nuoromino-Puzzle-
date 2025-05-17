# nuruomino.py: Template para implementação do projeto de Inteligência Artificial 2024/2025.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 23:
# 109512 João Gomes
# 110135 Manuel Semedo

from search import *
from sys import stdin
from collections import defaultdict
import copy

TETROMINO_SHAPES = {
    'I': [
        [(0,0), (0,1), (0,2), (0,3)],
        [(0,0), (1,0), (2,0), (3,0)]
    ],
    'L': [
        [(0,0), (1,0), (2,0), (2,1)],
        [(0,1), (1,1), (2,1), (2,0)],
        [(0,0), (0,1), (1,1), (2,1)],
        [(0,0), (0,1), (1,0), (2,0)],
        [(0,2), (1,0), (1,1), (1,2)],
        [(0,0), (1,0), (1,1), (1,2)],
        [(0,0), (0,1), (0,2), (1,0)],
        [(0,0), (0,1), (0,2), (1,2)]
    ],
    'T': [
        [(0,0), (0,1), (0,2), (1,1)],
        [(0,1), (1,0), (1,1), (2,1)],
        [(0,1), (1,0), (1,1), (1,2)],
        [(0,0), (1,0), (1,1), (2,0)]
    ],
    'S': [
        [(0,1), (0,2), (1,0), (1,1)],
        [(0,0), (1,0), (1,1), (2,1)],
        [(0,0), (0,1), (1,1), (1,2)],
        [(0,1), (1,0), (1,1), (2,0)]
    ]
}

square_deltas = [
    [(0, 0), (0, 1), (1, 0), (1, 1)],  # canto superior esquerdo
    [(0, -1), (0, 0), (1, -1), (1, 0)],  # canto superior direito
    [(-1, 0), (-1, 1), (0, 0), (0, 1)],  # canto inferior esquerdo
    [(-1, -1), (-1, 0), (0, -1), (0, 0)]  # canto inferior direito
]

class NuruominoState:

    def __init__(self, board):
        self.board = board
        self.id = Nuruomino.state_id
        Nuruomino.state_id += 1

    def __lt__(self, other):
        """ Este método é utilizado em caso de empate na gestão da lista
        de abertos nas procuras informadas. """
        return self.id < other.id

class Board:
    """Representação interna de um tabuleiro do Puzzle Nuruomino."""

    def __init__(self, grid, regions, positions):
        self.grid = grid  # Representa o tabuleiro como uma lista de listas
        self.size = len(grid)
        self.regions = regions  # Guarda as regiões
        self.possible_positions = positions

    def get_value(grid, row:int, col:int):
        if 0 <= row < len(grid) and 0 <= col < len(grid):
            return grid[row][col]
        else:
            return 0
    
    def adjacent_regions(self, region:int) -> list:
        """Devolve uma lista das regiões que fazem fronteira com a região enviada no argumento."""
        #TODO
        positions = self.regions[region]
        
        adj_regions = []

        for i, j in positions:
            adj_val = Board.adjacent_values(self, i, j)
            
            
            for r in adj_val:
                if r not in adj_regions and r != region:
                    adj_regions.append(r)
        
        
        print(f"adj regions: {adj_regions}")
        return adj_regions

        pass
    
    def adjacent_positions(self, row:int, col:int) -> list:
        """Devolve as posições adjacentes à região, em todas as direções, incluindo diagonais."""
        #TODO
        deltas = [(-1, -1), (-1, 0), (-1, 1),
              ( 0, -1),          ( 0, 1),
              ( 1, -1), ( 1, 0), ( 1, 1)]

        adj_pos = []
        for dr, dc in deltas:
            r, c = row + dr, col + dc
            if 0 <= r < self.size and 0 <= c < self.size:
                adj_pos.append((r, c))

        return adj_pos
    
        pass

    def adjacent_values(self, row:int, col:int) -> list:
        """Devolve os valores das celulas adjacentes à região, em todas as direções, incluindo diagonais."""
        adj_val = []
        adj_pos = Board.adjacent_positions(self, row, col)
        for i,j in adj_pos:
            adj_val.append(Board.get_value(self.grid, i, j))
        
        return adj_val
    
    
    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.
        """
        board = []
        positions = []

        for line in stdin:
            if not line.strip():
                continue
            board.append([int(x) for x in line.strip().split()])

        # Agora que temos a board, extraímos as regiões
        region_dict = defaultdict(list)
        for i, row in enumerate(board):
            for j, val in enumerate(row):
                positions.append((i,j))
                region_dict[val].append((i, j))
        
        # Lista de regiões (cada uma é uma lista de coordenadas)
        #regions = list(region_dict.values())

        return Board(board, region_dict, positions)
    
        #TODO
        pass

    def print_instance(grid):
        for row in grid:
            print(" ".join(str(x) for x in row))

    def print_regions(self):
        for region_id, positions in self.regions.items():
            print(f"Região {region_id}:")
            for pos in positions:
                print(pos)
            print()  # Linha em branco entre regiões

    def get_vector_region(region):
        xs, ys = zip(*region)
        
        min_x = min(xs)
        min_y = min(ys)

        piece = []
        for pos in region:
            delta_row = pos[0] - min_x
            delta_col = pos[1] - min_y
            piece.append((delta_row, delta_col))
        print(piece)
        return piece
    
    def get_tetromino(region):
        piece = Board.get_vector_region(region)
        if Board.is_L(piece):
            return "L"
        if Board.is_I(piece):
            return "I"
        if Board.is_T(piece):
            return "T"
        if Board.is_S(piece):
            return "S"

    def is_L(piece):
        if piece in TETROMINO_SHAPES['L']:
            return True
        return False
    
    def is_I(piece):
        if piece in TETROMINO_SHAPES['I']:
            return True
        return False
    
    def is_T(piece):
        if piece in TETROMINO_SHAPES['T']:
            return True
        return False
    
    def is_S(piece):
        if piece in TETROMINO_SHAPES['S']:
            return True
        return False
    
        
    def fill_tetromino_regions(self):
        
        for r in range(1, len(self.regions)+1):
            if len(self.regions[r]) == 4:
                piece_letter = Board.get_tetromino(self.regions[r])
                while len(self.regions[r]) != 0:
                    i, j = self.regions[r][0]
                    self.possible_positions.remove((i,j))
                    self.regions[r].remove((i,j))
                    self.grid[i][j] = piece_letter
        
        print("Possible positions: ", self.possible_positions)
        self.filter_square_positions()
        self.print_regions()

    def filter_square_positions(self):

        filtered_positions = []

        for i, j in self.possible_positions:
            if not Board.is_square(self.grid, i, j, 0):
                filtered_positions.append((i, j))
            else:
                region = Board.get_value(self.grid, i, j)
            
                self.regions[region].remove((i, j))

        #print(f"Possible positions after filtering: {filtered_positions}")
        self.possible_positions = filtered_positions
        print(f"Possible positions after filtering: {self.possible_positions}")
    
    def place_piece(grid, piece, positions):
        
        for i, j in positions:
            grid[i][j] = piece


    def get_possible_pieces(region):
               
        xs, ys = zip(*region)
        possible_pieces = []
        
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)
        
        # Rever Complexidade Temporal e usar Switches para as peças

        for piece in TETROMINO_SHAPES:
            
            for orientation in range(len(TETROMINO_SHAPES[piece])):
                for x in range(min_x, max_x + 1):
                    for y in range(min_y, max_y + 1):
                        
                        count = 0
                        aux_list = []
                        for pos in TETROMINO_SHAPES[piece][orientation]:
                            
                            if (x+pos[0], y+pos[1]) in region:
                                count += 1
                                aux_list.append((x+pos[0], y+pos[1]))

                            else:
                                break

                        if count == 4:
                            possible_pieces.append((piece, aux_list)) 
        
        
        print(f"Possible pieces for region: {possible_pieces}")
        return possible_pieces


    def filter_adjacent_pieces(self, possible_pieces):
        """Remove as peças que não podem ser colocadas na região."""
        filtered_pieces = []

        original_grid = self.grid  # Guarda o grid original

        for piece in possible_pieces:
            piece_type, positions = piece

            aux_grid = copy.deepcopy(original_grid)

            # Substitui temporariamente o self.grid
            self.grid = aux_grid

            print("/////////////////////")

            # Checa adjacências com o self.grid temporário
            has_invalid_adj = any(
                piece_type in self.adjacent_values(row, col) for row, col in positions
            )
            
            
            if has_invalid_adj:
                print(f"Invalid piece: {piece}")
                continue
            
            Board.place_piece(aux_grid, piece_type, positions)
            Board.print_instance(aux_grid)


            # Agora testa se forma quadrado no aux_grid (sem precisar alterar self)
            forms_square = any(Board.is_square(aux_grid, row, col, 1) for row, col in positions)
            if forms_square:
                continue

            # Peça válida
            print(f"Valid piece: {piece}")
            filtered_pieces.append(piece)
            self.grid = original_grid  # Restaura o grid original
        # Restaura o grid original
            
        print(f"Possible pieces after filtering: {filtered_pieces}")
        return filtered_pieces
    

    # n = 0: the position is free
    # n = 1: the position is filled
    def is_square(grid, row, col, n):

        for deltas in square_deltas:
            square = [Board.get_value(grid, row + dx, col + dy) for dx, dy in deltas]
            count = 0
            for val in square:
                if val in TETROMINO_SHAPES:
                    count+=1
            if count == 3 + n:
                print(f"Square found at ({row}, {col}) with deltas: {deltas}")
                return True
        
        return False

    

        


    # TODO: outros metodos da classe Board

class Nuruomino(Problem):

    state_id = 0

    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.board = board
        self.initial = NuruominoState(board)
        self.initial.state_id = 0 # ID do estado inicial

        Board.fill_tetromino_regions(board)
        #TODO
        pass 
    

    def actions(self, state: NuruominoState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""

        all_pieces = []
        for region in self.board.regions.values():
            if len(region) != 0:
                print(len(region))
                pieces = Board.get_possible_pieces(region)
                filtered_pieces = Board.filter_adjacent_pieces(self.board, pieces)

                all_pieces.append(filtered_pieces)
        
        Board.print_instance(self.board.grid)
        return all_pieces
        
        #TODO
        pass 

    def result(self, state: NuruominoState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""

        #TODO
        pass 

    def goal_test(self, state: NuruominoState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        #TODO
        pass 

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

if __name__ == "__main__":
    board = Board.parse_instance()
    #Board.print_instance(board)
    #Board.print_regions(board)
    # Exemplo de impressão das regiões
    # Board.print_regions(board.regions)
    #print(f"Possible_pos: {board.possible_positions}")
    
    problem = Nuruomino(board)
    
    #s0 = NuruominoState(board)

    actions = problem.actions(problem.initial)
    print(actions)
