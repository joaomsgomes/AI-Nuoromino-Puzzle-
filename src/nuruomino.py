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
from collections import deque
import time

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
    ],
    'P':[]
}

square_deltas = [
    [(0, 0), (0, 1), (1, 0), (1, 1)],  # canto superior esquerdo
    [(0, -1), (0, 0), (1, -1), (1, 0)],  # canto superior direito
    [(-1, 0), (-1, 1), (0, 0), (0, 1)],  # canto inferior esquerdo
    [(-1, -1), (-1, 0), (0, -1), (0, 0)]  # canto inferior direito
]

class NuruominoState:

    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = NuruominoState.state_id
        NuruominoState.state_id += 1
        self.possible_actions = []

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
        self.placed_pieces = []
        self.num_regions = len(regions)

    def get_value(grid, row:int, col:int):
        if 0 <= row < len(grid) and 0 <= col < len(grid):
            return grid[row][col]
        else:
            return None
    
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
            print("\t".join(str(x) for x in row))

    def print_regions(self):
        for region in self.regions:
            print(f"Região {region}:")
            for pos in self.regions[region]:
                print(pos)
            print()

    def get_vector_region(region):
        xs, ys = zip(*region)
        
        min_x = min(xs)
        min_y = min(ys)

        piece = []
        for pos in region:
            delta_row = pos[0] - min_x
            delta_col = pos[1] - min_y
            piece.append((delta_row, delta_col))
        
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
        
        for r in list(self.regions.keys()):
            if len(self.regions[r]) == 4:
                piece_letter = Board.get_tetromino(self.regions[r])
                Board.place_piece(self.grid, piece_letter, self.regions[r])
                self.placed_pieces.append((piece_letter, self.regions[r]))
                self.remove_region_positions(r)
        
        #self.filter_square_positions()
        #self.print_regions()

    def filter_square_positions(self):

        filtered_positions = []

        for i, j in self.possible_positions:
            if not Board.is_square(self.grid, i, j, 0):
                filtered_positions.append((i, j))
            else:
                region = Board.get_value(self.grid, i, j)

                if (i,j) in self.regions[region]:
                    self.regions[region].remove((i, j))

        self.possible_positions = filtered_positions
    
    def place_piece(grid, piece, positions):
        for i, j in positions:
            grid[i][j] = piece

    def remove_region_positions(self, region):
        new_possible_positions = []

        for pos in self.possible_positions:
            if pos not in self.regions[region]:
                new_possible_positions.append(pos)
        
        if (region in self.regions):
            self.regions.pop(region)

        self.possible_positions = new_possible_positions

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
        
        
        return possible_pieces


    def filter_actions(self, possible_pieces):
        """Remove as peças que não podem ser colocadas na região."""
        filtered_pieces = []

        for piece in possible_pieces:

            piece_type, positions = piece

            aux_grid = [row[:] for row in self.grid]

            # Checa adjacências com o aux_grid diretamente
            has_invalid_adj = any(
                piece_type in self.adjacent_values(row, col)
                for row, col in positions
            )

            if has_invalid_adj:
                continue

            Board.place_piece(aux_grid, piece_type, positions)

            forms_square = any(Board.is_square(aux_grid, row, col, 1) for row, col in positions)
            if forms_square:
                continue

            filtered_pieces.append(piece)

        
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
                
                return True
        
        return False
    
    
    def fixed_positions(self):

        while (1):
            
            self.fill_tetromino_regions()
            aux_grid = copy.deepcopy(self.grid)

            for region in self.regions:
                visited_positions = []
                possible_pieces = Board.get_possible_pieces(self.regions[region])
                pieces = self.filter_actions(possible_pieces)
                
                #print(f"region {region}: {self.regions[region]}")
                #print(f"Pieces: {pieces}")

                
                fixed_positions = pieces[0][1]

                #print(f"Starting Fixed positions: {fixed_positions}")

                for let, positions in pieces:
                    aux = []
                    for (i, j) in positions:
                        
                        if (i, j) not in visited_positions:
                            visited_positions.append((i,j))
                        
                        if (i, j) in fixed_positions:
                            aux.append((i, j))
                    
                    fixed_positions = aux

                #print(f"Fixed positions: {fixed_positions}")
                if len(fixed_positions) > 0:
                    for a, b in fixed_positions:
                        aux_grid[a][b] = 'P'

                #print(f"Visited positions: {visited_positions}")
                self.regions[region] = visited_positions
                
            if (aux_grid == self.grid):
                self.grid = aux_grid
                return 
            else:
                self.grid = aux_grid

            

                        

    # TODO: outros metodos da classe Board

class Nuruomino(Problem):

    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.board = board
        self.initial = NuruominoState(board)
        self.initial.state_id = 0 # ID do estado inicial

        board.fixed_positions() #Estado inicial de qualquer nó
        #TODO
        pass 
    
    '''
    def get_region_actions(region, actions):

        region_actions = []
        for reg, let, pos in actions:
            if reg == region:
                region_actions.append((reg, let, pos)) 
    
        return region_actions
    '''


    def actions(self, state: NuruominoState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""

        all_pieces = []
        for region in state.board.regions:
            
            if len(state.board.regions[region]) != 0:
                
                pieces = Board.get_possible_pieces(state.board.regions[region])
                filtered_pieces = Board.filter_actions(state.board, pieces)

                for piece, pos in filtered_pieces:
                    
                    all_pieces.append((region, piece, pos))
        
        state.possible_actions = all_pieces
        return all_pieces
        
        #TODO
        pass 

    def result(self, state: NuruominoState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        region, piece, positions = action

        
        board_copy = copy.deepcopy(state.board)
        new_state = NuruominoState(board_copy)

        #new_state.prev_region_num_actions = len(Nuruomino.get_region_actions(
        #                                    region, state.possible_actions))
        
        Board.place_piece(new_state.board.grid, piece, positions)
        new_state.board.placed_pieces.append((piece, positions))
        new_state.board.remove_region_positions(region)
        new_state.board.filter_square_positions()

        time.sleep(2)
        print(new_state.state_id)
        Board.print_instance(new_state.board.grid)
        Board.print_regions(new_state.board)

        #new_state.board.fixed_positions()

        #Board.print_instance(new_state.board.grid)

        return new_state

    def get_state_connections(state: NuruominoState):

        main_directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        connections = []

        for piece_letter, positions in state.board.placed_pieces:
            for (i,j) in positions:
                for dx, dy in main_directions:
                    adj_piece = Board.get_value(state.board.grid, i+dx, j+dy)
                    pos1 = (i, j)
                    pos2 = (i + dx, j + dy)
                    if (adj_piece in TETROMINO_SHAPES and adj_piece != piece_letter
                        and (pos1, pos2) not in connections
                        and (pos2, pos1) not in connections):
                        
                        connections.append((pos1, pos2, (i + dx, j + dy)))

        return connections
    
    def unique_nurikabe(self, state: NuruominoState):
        
        visited = set()
        queue = deque([state.board.placed_pieces[0][1][0]])
        
        main_directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        while queue:

            i, j = queue.popleft()
            visited.add((i, j))

            for dx, dy in main_directions:
                ni, nj = i + dx, j + dy
                adj_piece = Board.get_value(state.board.grid, ni, nj)
                
                if adj_piece in TETROMINO_SHAPES:
                    if (ni, nj) not in visited:
                        queue.append((ni, nj))

        
        if len(visited) < state.board.num_regions * 4:
            return False
        
        return True
            

    
    def goal_test(self, state: NuruominoState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        if len(state.board.regions) > 0:
            return False
        
        if not self.unique_nurikabe(state):
            return False
        
        
        self.board = state.board
        return True

    def broken_regions(state: NuruominoState):

        count = 0
        #Board.print_regions(state.board)
        for region in state.board.regions:
            if len(state.board.regions[region]) < 4:
                count+=1

        return count

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        h1 = node.state.board.num_regions - len(Nuruomino.get_state_connections(node.state))
        h2 = 50 * Nuruomino.broken_regions(node.state)
        print(h2)
        return h1 + h2
        

if __name__ == "__main__":
    board = Board.parse_instance()
    problem = Nuruomino(board)
    
    
    #Board.print_instance(problem.board.grid)
    #Board.print_regions(problem.board)
    #print(problem.board.possible_positions)
    goal_node = astar_search(problem)
    Board.print_instance(problem.board.grid)
    

