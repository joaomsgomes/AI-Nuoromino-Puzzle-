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
        [(0,1), (1,1), (2,0), (2,1)],
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
        self.bad_path = False
        self.region_priority = 0

    def __lt__(self, other):
        """ Este método é utilizado em caso de empate na gestão da lista
        de abertos nas procuras informadas. """
        return self.id < other.id

class Board:
    """Representação interna de um tabuleiro do Puzzle Nuruomino."""

    def __init__(self, grid, regions):
        self.grid = grid  # Representa o tabuleiro como uma lista de listas
        self.size = len(grid)
        self.regions = regions  # Guarda as regiões
        self.possible_pieces = {}
        self.region_adj_regions = {}
        
        self.placed_pieces = []
        self.num_regions = len(regions)


    def set_possible_pieces(self):
    
        for region in self.regions:
            self.possible_pieces[region] = Board.get_possible_pieces(self.regions[region])

    def set_adjacent_regions(self):

        for region in self.regions:
            self.region_adj_regions[region] = self.adjacent_regions(region)


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
        
        for line in stdin:
            if not line.strip():
                continue
            board.append([int(x) for x in line.strip().split()])

        # Agora que temos a board, extraímos as regiões
        
        region_dict = defaultdict(list)
        for i, row in enumerate(board):
            for j, val in enumerate(row):
                region_dict[val].append((i, j))
        
        # Lista de regiões (cada uma é uma lista de coordenadas)
        #regions = list(region_dict.values())

        return Board(board, region_dict)
    
        #TODO
        pass

    def print_instance(grid):
        for row in grid:
            print("\t".join(str(x) for x in row))

    def print_regions(regions):
        for region in regions:
            print(f"Região {region}:")
            for pos in regions[region]:
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

        """Preenche as regioões do tabuleiro com tamanho 4 e remove as suas posições da região e adiciona a peça ao placed_pieces."""
        for r in list(self.regions.keys()):
            if len(self.regions[r]) == 4:
                piece_letter = Board.get_tetromino(self.regions[r])
                Board.place_piece(self.grid, piece_letter, self.regions[r])
                self.placed_pieces.append((piece_letter, self.regions[r]))
                self.regions.pop(r)
                
    
    def place_piece(grid, piece, positions):
        for i, j in positions:
            grid[i][j] = piece

    def get_possible_pieces(region):
        """Retorna as peças que encaixam numa região"""
               
        xs, ys = zip(*region)
        possible_pieces = []
        
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)
        
        # Rever Complexidade Temporal e usar Switches para as peças

        for piece in TETROMINO_SHAPES:
            
            for orientation in TETROMINO_SHAPES[piece]:

                for x in range(min_x, max_x + 1):
                    for y in range(min_y, max_y + 1):
                        
                        count = 0
                        aux_list = []
                        for pos in orientation:
                            
                            if (x+pos[0], y+pos[1]) in region:
                                count += 1
                                aux_list.append((x+pos[0], y+pos[1]))

                            else:
                                break

                        if count == 4:
                            possible_pieces.append((piece, aux_list)) 
        
        
        return possible_pieces


    def filter_actions(self, possible_pieces):
        
        """Devolve as peças que podem ser colocadas na região atendendo às regras do L.I.T.S ."""
        
        filtered_pieces = []

        for piece in possible_pieces:

            piece_type, positions = piece

            aux_grid = copy.deepcopy(self.grid)

            # Checa adjacências com o aux_grid diretamente
            has_invalid_adj = any(
                piece_type in self.adjacent_values(row, col)
                for row, col in positions
            )

            if has_invalid_adj:
                continue

            Board.place_piece(aux_grid, piece_type, positions)

            forms_square = any(Board.is_square(aux_grid, row, col) for row, col in positions)
            if forms_square:
                continue

            filtered_pieces.append(piece)

        
        return filtered_pieces
    
    def is_square(grid, row, col):

        for deltas in square_deltas:
            square = [Board.get_value(grid, row + dx, col + dy) for dx, dy in deltas]
            count = 0
            for val in square:
                if val in TETROMINO_SHAPES:
                    count+=1
            if count == 4:
                return True
        
        return False
    


    def fixed_positions(self):

        queue = deque()
        queued_regions = set()

        while True:
            
            self.fill_tetromino_regions()

            queue.extend(list(self.regions))

            changed = False

            while queue:

                print("Affected regions: ", queue)

                region = queue.popleft()
                queued_regions.discard(region)
                #if len(self.regions[region]) < 4:
                #    continue

                visited_positions = []
                #pieces = Board.get_possible_pieces(self.regions[region])
                #pieces = self.filter_actions(possible_pieces)
                #print(f"region {region}: {self.regions[region]}")
                #print(f"Pieces: {pieces}")

                pieces = self.filter_actions(self.possible_pieces[region])

                print("Pieces: ", pieces)
                
                if not pieces:
                    return False  
                
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
                        if self.grid[a][b] != 'P':
                            self.grid[a][b] = 'P'
                            changed = True
                            for adj_r in self.region_adj_regions[region]:
                                if adj_r not in queued_regions and adj_r in self.regions.keys():
                                    queue.append(adj_r)
                                    queued_regions.add(adj_r)

                #print(f"Visited positions: {visited_positions}")
                self.regions[region] = visited_positions
                self.possible_pieces[region] = pieces
                

            if not changed:
                return True
            
            
    def fixed_positions2(self, affected_regions):
        #COLOCAR P's na grid
        #grid_copy = copy.deepcopy(self.grid)
        visited_positions = []
        print(affected_regions)

        for region in affected_regions:
            
            region_pieces = self.possible_pieces[region]
            fixed_positions = region_pieces[0][1]

            for _, positions in region_pieces:
                aux = []
                for (i, j) in positions:
                    if (i, j) not in visited_positions:
                        visited_positions.append((i,j))
                    if (i, j) in fixed_positions:
                        aux.append((i, j))
                fixed_positions = aux
            
            if len(fixed_positions) > 0:
                for a, b in fixed_positions:
                    if self.grid[a][b] != 'P':
                        self.grid[a][b] = 'P'


            print("region", self.possible_pieces[region])
            self.filter_actions(self.possible_pieces[region])
            print("filtered", self.possible_pieces[region])
        

    # TODO: outros metodos da classe Board

class Nuruomino(Problem):

    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.board = board
        self.initial = NuruominoState(board)
        self.initial.state_id = 0 # ID do estado inicial

        self.board.fill_tetromino_regions()
        Board.print_regions(self.board.regions)
        board.set_possible_pieces()
        board.set_adjacent_regions()

        Board.print_regions(self.board.possible_pieces)

        self.board.fixed_positions2(list(self.board.regions.keys())) #Estado inicial de qualquer no
        print("BOARD:")
        Board.print_instance(board.grid)

        Board.print_regions(self.board.possible_pieces)
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

        all_actions = []
        for region in state.board.regions:
            
            #if len(state.board.regions[region]) != 0:
                
                #pieces = Board.get_possible_pieces(state.board.regions[region])
                #filtered_pieces = Board.filter_actions(state.board, pieces)
                
                pieces = state.board.possible_pieces[region]

                for piece, pos in pieces:
                    
                    all_actions.append((region, piece, pos))
        
        #print("ON STATE:", state.state_id)
        #Board.print_instance(state.board.grid)
        #print("Actions: ", all_actions)
        #Board.print_regions(state.board.regions)
        #time.sleep(1)
        #print("Regions: ")
        return all_actions
    

    def result(self, state: NuruominoState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        region, piece, positions = action

        if len(state.board.regions[region]) < 4:
            return None
        
        board_copy = copy.deepcopy(state.board)
        new_state = NuruominoState(board_copy)

        
        Board.place_piece(new_state.board.grid, piece, positions)
        new_state.board.placed_pieces.append((piece, positions))

        new_state.region_priority = Nuruomino.find_region_priority(state.board.regions, region)
        new_state.board.regions.pop(region)
        new_state.board.possible_pieces.pop(region)

        print("NEW STATE:", new_state.state_id)
        Board.print_instance(new_state.board.grid)

        for adj_r in new_state.board.region_adj_regions[region]:
            if adj_r in list(new_state.board.regions.keys()):

                print("adjacent region pieces: ", adj_r)
                print(new_state.board.possible_pieces[adj_r])
                new_state.board.filter_actions(new_state.board.possible_pieces[adj_r])
                print(new_state.board.possible_pieces[adj_r])
        


        #if not new_state.board.fixed_positions2():
        #    new_state.bad_path = True


        #time.sleep(0.5)
        #print("NEW STATE:", new_state.state_id)
        #print("ACtion:", action)
        #Board.print_instance(new_state.board.grid)
        Board.print_regions(new_state.board.regions)

        
        
        #new_state.board.fixed_positions()
        #print("after fixed positions: \n")
        #Board.print_instance(new_state.board.grid)
        #Board.print_regions(new_state.board)

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
                
                if adj_piece in TETROMINO_SHAPES and adj_piece != 'P':
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

    '''
    def broken_regions(state: NuruominoState):

        #Board.print_regions(state.board)
        future_state = copy.deepcopy(state)
        future_state.board.fixed_positions()

        for region in future_state.board.regions:
            if len(future_state.board.regions[region]) < 4:
                return 1000
            
        state = future_state
        return 0
    '''

    def find_region_priority(regions, action_region):
    
        sorted_regions = sorted(regions.keys(),
                            key=lambda r: len(regions[r]))

        #Board.print_instance(node.state.board.grid)
        #print(sorted_regions)
        h = 0
        for reg in sorted_regions:
            #print("reg", reg)
            if action_region == reg:
                return h
            
            h+=1
        
        return h


    def broken_regions(node: Node):

       for region in node.state.board.regions:
            if len(node.state.board.regions[region]) < 4:
                return 1000
            
       return 0
    
    def is_bad_path(node: Node):
        if node.state.bad_path:
            return 1000
        return 0
    
    def get_region_priority(node: Node):
        return node.state.region_priority
    
    def h(self, node: Node):
        #print("Node_ID and Action:", node.state.id, node.action)

        """Função heuristica utilizada para a procura A*."""
      
        h1 = 0 - len(Nuruomino.get_state_connections(node.state))
        h2 = 0

        if node.state.id != 0:
            h2 = Nuruomino.get_region_priority(node)
            #node.state.board.regions.pop(node.action[0])

        h3 = len(node.state.board.regions) # Priorizar estados com menos regiões por preencher
        #h4 = Nuruomino.broken_regions(node) # Por ver se vale a pena
        h4 = Nuruomino.is_bad_path(node)

        #print("Node State Board:")
        #print(f"h1: {h1}, h2: {h2}")
        #Board.print_regions(node.state.board)
        return h1 + h2 + h3 + h4
        

if __name__ == "__main__":
    board = Board.parse_instance()
    problem = Nuruomino(board)
    
    
    #Board.print_instance(problem.board.grid)
    #Board.print_regions(problem.board)
    goal_node = astar_search(problem)
    Board.print_instance(problem.board.grid)
    

