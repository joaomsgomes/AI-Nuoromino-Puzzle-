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

SQUARE_DELTAS = [
    [(0, 0), (0, 1), (1, 0), (1, 1)],    # Lower Right Corner
    [(0, -1), (0, 0), (1, -1), (1, 0)],  # Lower Left Corner
    [(-1, 0), (-1, 1), (0, 0), (0, 1)],  # Upper Right Corner
    [(-1, -1), (-1, 0), (0, -1), (0, 0)] # Upper Left Corner
]

DELTAS = [(-1, 0), (0, -1), (0, 1), (1, 0)]  # Direções principais: cima, esquerda, direita, baixo

class NuruominoState:

    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = NuruominoState.state_id
        NuruominoState.state_id += 1
        

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
        self.num_regions = len(regions)


        self.region_size = 0            # Size of the last region placed
        self.possible_pieces = {}       # Possible pieces by region                     
        self.adj_graph = {}             # Region adjacencies graph


    def set_possible_pieces(self):
        
        for region in self.regions:
            self.possible_pieces[region] = Board.get_possible_pieces(self.regions[region])

    def set_adjacencies_graph(self):

        for region in self.regions:
            self.adj_graph[region] = self.adjacent_regions(region)

    def get_value(grid, row:int, col:int):
        if 0 <= row < len(grid) and 0 <= col < len(grid):
            return grid[row][col]
        else:
            return None
    
    def adjacent_regions(self, region:int) -> list:
        """Devolve uma lista das regiões que fazem fronteira com a região enviada no argumento."""
        
        positions = self.regions[region]
        
        adj_regions = []

        for i, j in positions:
            adj_val = Board.adjacent_values(self, i, j)
            
            
            for r in adj_val:
                if r not in adj_regions and r != region and r not in TETROMINO_SHAPES and r in self.regions.keys():
                    adj_regions.append(r)

        return set(adj_regions)

        
    
    def adjacent_positions(self, row:int, col:int) -> list:
        """Devolve as posições adjacentes à região, em todas as direções, incluindo diagonais."""
        
        adj_pos = []
        for dr, dc in DELTAS:
            r, c = row + dr, col + dc
            if 0 <= r < self.size and 0 <= c < self.size:
                adj_pos.append((r, c))

        return adj_pos
    
        

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
        
        # Dictionary: Region -> all cells
        region_dict = defaultdict(list)
        for i, row in enumerate(board):
            for j, val in enumerate(row):
                region_dict[val].append((i, j))
        
        return Board(board, region_dict)
    
    def print_instance(grid):
        for row in grid:
            print("\t".join(str(x) for x in row))

    def is_square(grid, row, col):

        for deltas in SQUARE_DELTAS:
            square = [Board.get_value(grid, row + dx, col + dy) for dx, dy in deltas]
            count = 0
            i = 1
            for val in square:
                if val in TETROMINO_SHAPES:
                    count+=1
                    i += 1
                    if i == 2 and count == 0:
                        break
            if count == 4:
                return True
        
        return False    
                
    def place_piece(board, region, piece, positions):
        for i, j in positions:
            board.grid[i][j] = piece

        board.possible_pieces.pop(region)
        board.regions.pop(region)
        
        
    def update_graph(initial_grid, region, positions, board):
        graph = board.adj_graph
        adjacent_regions = set()

        for i, j in positions:
            
            for dx, dy in DELTAS:
                ni, nj = i + dx, j + dy
                neighbor = Board.get_value(board.grid, ni, nj)

                if neighbor != None and (ni, nj) not in positions and neighbor != region:

                    if neighbor in TETROMINO_SHAPES:
                        adjacent_regions.add(Board.get_value(initial_grid, ni, nj))
                    elif neighbor in board.regions.keys():
                        adjacent_regions.add(neighbor)

        graph[region] = adjacent_regions

        for reg in graph.keys():
            if reg not in adjacent_regions and region in graph[reg]:
                graph[reg].remove(region)


    def get_possible_pieces(region):
        """Retorna as peças que encaixam numa região"""
               
        xs, ys = zip(*region)
        possible_pieces = []
        
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)
        
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
    
    def clone(self):   

        new_grid = [row[:] for row in self.grid]
        new_regions = {k: v[:] for k, v in self.regions.items()}
        new_possible_pieces = {k: set(v) for k, v in self.possible_pieces.items()}
        new_adj_graph = {k: set(v) for k, v in self.adj_graph.items()}
        b = Board(new_grid, new_regions)
        b.possible_pieces = new_possible_pieces
        b.adj_graph = new_adj_graph
        
        return b

class Nuruomino(Problem):

    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.board = board
        self.initial = NuruominoState(board)
        self.initial.state_id = 0 # Intial's State ID
        self.num_regions = len(board.regions)
        
        # Original source grid
        self.main_grid = [row[:] for row in self.board.grid]
        
        # Initialize structs
        self.initial.board.set_possible_pieces()
        self.initial.board.set_adjacencies_graph()

        # Placing Pieces in regions with length of 4 and trying to find other regions that might have only one possible piece as well
        self.fixed_positions(self.initial.board, list(sorted(self.board.regions, key=lambda r: len(self.board.regions[r]))))



    def fixed_positions(self, board, adj_regions):

        """Realiza Propagação automática de regiões que apenas têm uma jogada possível e verifica se por meio de alguma jogada
          alguma região deixou de ter jogadas possíveis. Coloca ainda P's nas posições que garantidamente irão ser colocadas e
          restringe o tabuleiro com base nisso. Caso a região apenas possa ter um tipo de peça em vez de P coloca a letra dessa
          peça nas posições fixas"""

        queue = deque(adj_regions)
        queued_regions = set(adj_regions)

        # Study affected regions
        while queue:

            region = queue.popleft()
            queued_regions.remove(region)
            
            # Get filtered actions on current region
            filtered_actions = self.filter_actions(board, region, board.possible_pieces[region])
            
            # No possible pieces -> dead end
            if len(filtered_actions) == 0:
                return False
            
            board.possible_pieces[region] = filtered_actions
            region_pieces = board.possible_pieces[region]
            fixed_letter, fixed_positions = next(iter(region_pieces))

            # Find the positions where the pieces overlap -> fixed positions
            for letter, positions in region_pieces:
                aux = []
                for (i, j) in positions:
                    if (i, j) in fixed_positions:
                        aux.append((i, j))
                    if fixed_letter != letter:
                        fixed_letter = 'P'
                fixed_positions = aux
            
            # No fixed positions -> nothing to do
            if len(fixed_positions) == 0:
                continue
            
            # 4 fixed positions means a piece can be placed
            if len(fixed_positions) == 4:
                Board.place_piece(board, region, fixed_letter, tuple(fixed_positions))
                Board.update_graph(self.main_grid, region, positions, board)

                # Add to queue regions that can be affected by the new piece
                for r in board.adj_graph[region]:
                    if r not in queued_regions and r in board.regions.keys():
                        queue.append(r)
                        queued_regions.add(r)

            
            else:
                new_Ps = False
                for i, j in fixed_positions:
                    if board.grid[i][j] != fixed_letter:
                        new_Ps = True
                        board.grid[i][j] = fixed_letter

                # Add to queue regions that can be affected by the new fixed positions
                if new_Ps:
                    for r in board.adj_graph[region]:
                        if r not in queued_regions and r in board.regions.keys():
                            queue.append(r)
                            queued_regions.add(r)

        return True

    def invalid_adjacencies(board, region, piece_letter, positions):
        """
        Verifica se a peça está conectada a outra peça igual (inválido)
        ou se a região ficou isolada (inválido).
        """
        isolated = True

        for (i, j) in positions:
            for dx, dy in DELTAS:
                ni, nj = i + dx, j + dy
                neighbor = Board.get_value(board.grid, ni, nj)
                
                if (ni, nj) not in board.regions[region] and neighbor is not None:
                    # Looking for an adjacent equal piece
                    if neighbor == piece_letter:
                        return True

                    # if there is any adjacent cell that belongs to a piece in a different region, then its not isolated
                    # if the adjacent cell's region doesnt have a placed piece, we cant assume its isolated                 
                    if neighbor != piece_letter and neighbor in TETROMINO_SHAPES:
                        isolated = False

                    if neighbor in board.regions.keys():
                        isolated = False

        # If its isolated (any adjacent cell belongs to another region )
        if isolated and len(board.regions) < board.num_regions:
            return True

        return False

    def filter_actions(self, board, region, possible_pieces):
        """Devolve as peças que podem ser colocadas na região atendendo às regras do L.I.T.S ."""

        filtered_pieces = set()
        grid = board.grid
        
        for piece in possible_pieces:

            letter, positions = piece

            has_invalid_adj = Nuruomino.invalid_adjacencies(board, region, letter, positions)
            
            if has_invalid_adj:
                continue
            
            # Saves positions values
            original = [grid[i][j] for i, j in positions]

            # Simulates 
            for (i, j) in positions:
                grid[i][j] = letter
            
            forms_square = any(Board.is_square(grid, row, col) for row, col in positions)

            for idx, (i, j) in enumerate(positions):
                grid[i][j] = original[idx]

            if forms_square:
                continue
            
            filtered_pieces.add((letter, tuple(positions)))

        return filtered_pieces

    def order_by_num_actions_and_adjacencies(possible_pieces, adj_graph):

        """Ordenar uma lista consoante o número de possíveis jogadas para cada região e
            tendo em conta a adja"""
        
        return sorted(
            possible_pieces.keys(),
            key=lambda reg: (len(possible_pieces[reg]), -len(adj_graph[reg]))
        )
    
    
    def actions(self, state: NuruominoState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""

        actions = []

        # Ordered regions list by number of possible actions
        ordered_list = Nuruomino.order_by_num_actions_and_adjacencies(state.board.possible_pieces, state.board.adj_graph)

        for region in ordered_list:

            pieces = state.board.possible_pieces[region]

            # Each possible action
            for piece, positions in pieces:
                
                # Create new board and simulate action
                new_board = Board.clone(state.board)
                new_board.region_size = len(new_board.regions[region])

                Board.place_piece(new_board, region, piece, positions)
                Board.update_graph(self.main_grid, region, positions, new_board)
                
                affected_regions = [r for r in new_board.adj_graph[region] if r in new_board.regions.keys()]

                bad_path = False
                
                # Verifies dead-ends using forward-checking
                if not self.fixed_positions(new_board, affected_regions):
                    bad_path = True
                    
                if not bad_path and not self.all_regions_reachable(region, new_board):
                    bad_path = True
                
                if not bad_path:
                    actions.append(new_board)

            # Returns only valid actions on promisable regions
            return actions
        
        return []
    
    def all_regions_reachable(self, placed_region, board):
        """
        Verifica se todas as regiões restantes do tabuleiro estão
        (ou poderão estar) conectadas entre si.
        Importante para garantir que não ficam regiões isoladas após uma jogada.
        True se todas as regiões estão conectadas (acessíveis entre si),
        False caso contrário.
        """
        visited = set()           # Visited Regions
        queued_regions = set()    
        graph = board.adj_graph   # Adjacencies graph

        queue = deque([placed_region])  # Starts BFS on the last filled region

        while queue:
            current_region = queue.popleft()
            visited.add(current_region)

            # For each current region's  adjacent regions
            for adj_region in graph[current_region]:

                # If it was not visited yet, add to queue
                if adj_region not in visited and adj_region not in queued_regions:
                    queue.append(adj_region)
                    queued_regions.add(adj_region)

        # If not all regions were visited
        if len(visited) != self.num_regions:
            return False

        return True


    def result(self, state: NuruominoState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        
        # Create state based on board (action)
        new_state = NuruominoState(action)
        
        return new_state
              
    def goal_test(self, state: NuruominoState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        
        # If there are still regions without pieces
        if len(state.board.regions) > 0:
            
            return False

        # All regions reachable, all regions filled -> final board
        if self.all_regions_reachable(1, state.board):
            self.board = state.board
            return True
        
        return False



    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""

        # Number of regions left to fill (less is better, means more progress)
        regions_left = len(node.state.board.regions)

        
        region_size = node.state.board.region_size

        h = (
            0.5 * region_size +
            0.5 * regions_left
        )

        # subtract g(n) -> prioritize depth
        return h - node.depth
        

if __name__ == "__main__":
    board = Board.parse_instance()
    problem = Nuruomino(board)
    goal_node = depth_first_tree_search(problem)
    Board.print_instance(problem.board.grid)
    

