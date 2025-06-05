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
    [(0, 0), (0, 1), (1, 0), (1, 1)],  # canto superior esquerdo
    [(0, -1), (0, 0), (1, -1), (1, 0)],  # canto superior direito
    [(-1, 0), (-1, 1), (0, 0), (0, 1)],  # canto inferior esquerdo
    [(-1, -1), (-1, 0), (0, -1), (0, 0)]  # canto inferior direito
]

DELTAS = [(-1, 0), (0, -1), (0, 1), (1, 0)]  # Direções principais: cima, esquerda, direita, baixo

class NuruominoState:

    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = NuruominoState.state_id
        NuruominoState.state_id += 1

        #self.bad_path = False
        #self.only_letter = 0
        #self.action_region_size = 0
        #self.region_actions = 0
        #self.not_connected_permanently = False
        #self.region_action = None
        #self.priority_regions = set()


    def __lt__(self, other):
        """ Este método é utilizado em caso de empate na gestão da lista
        de abertos nas procuras informadas. """
        return self.id < other.id
    
    def print_state_info(state):
        print(f"State ID: {state.id}")
        print("Board:")
        Board.print_instance(state.board.grid)
        print("\nRegions restantes:", state.board.regions)
        print("\nPossible pieces por região:")
        for reg, pieces in state.possible_pieces.items():
            print(f"  Região {reg}: {pieces}")
        print("\nAdjacency graph:")
        for reg, adjs in state.adj_graph.items():
            print(f"  Região {reg}: {adjs}")
        print("\nPlaced pieces:", state.placed_pieces)


    def clone_state(self):
        new_possible_pieces = {k: set(v) for k, v in self.possible_pieces.items()}
        new_adj_graph = {k: set(v) for k, v in self.adj_graph.items()}
        new_placed_pieces = set(self.placed_pieces)
        board = self.board.clone_board()
        new_state = NuruominoState(board)
        new_state.possible_pieces = new_possible_pieces
        new_state.adj_graph = new_adj_graph
        new_state.placed_pieces = new_placed_pieces
        return new_state


class Board:
    """Representação interna de um tabuleiro do Puzzle Nuruomino."""

    def __init__(self, grid, regions):
        self.grid = grid  # Representa o tabuleiro como uma lista de listas
        self.size = len(grid)
        self.regions = regions  # Guarda as regiões
        self.num_regions = len(regions)

        self.possible_pieces = {}
        self.adj_graph = {}
        self.placed_pieces = set()
        

    def set_possible_pieces(self):
    
        for region in self.regions:
            self.possible_pieces[region] = Board.get_possible_pieces(self.regions[region])

    def set_adjacent_regions(self):

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
        
        #print(adj_regions)
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
        
        #if (row, col) == (5,1):
        #    print("Adjacent Values for (5,1):", adj_val)
            

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
                self.placed_pieces.add((piece_letter, tuple(self.regions[r])))
                self.regions.pop(r)

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

        board.placed_pieces.add((region, piece, tuple(positions)))
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
    

    def clone(self):   

        new_grid = [row[:] for row in self.grid]
        new_regions = {k: v[:] for k, v in self.regions.items()}
        new_possible_pieces = {k: set(v) for k, v in self.possible_pieces.items()}
        new_adj_graph = {k: set(v) for k, v in self.adj_graph.items()}
        new_placed_pieces = set((region, piece, tuple(positions)) for region, piece, positions in self.placed_pieces)
        b = Board(new_grid, new_regions)
        b.possible_pieces = new_possible_pieces
        b.adj_graph = new_adj_graph
        b.placed_pieces = new_placed_pieces
        return b
        

    # TODO: outros metodos da classe Board

class Nuruomino(Problem):

    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.board = board
        self.initial = NuruominoState(board)
        self.initial.state_id = 0 # ID do estado inicial
        self.num_regions = len(board.regions)
        
        self.main_grid = [row[:] for row in self.board.grid]

        self.region_sizes = { region: len(positions) for region, positions in self.board.regions.items() }
        
        self.initial.board.set_possible_pieces()
        self.initial.board.set_adjacent_regions()

        #print(self.initial.board.adj_graph)

        self.fixed_positions(self.initial.board, list(sorted(self.board.regions, key=lambda r: len(self.board.regions[r])))) #Estado inicial de qualquer no
        #print("BOARD INICIAL:")
        
        #Board.print_instance(self.board.grid)

        #print(self.board.adj_graph)
        #print("Initial POSSIBLE PIECES:", self.board.possible_pieces)
        #time.sleep(1)
        
        #TODO
        pass

    def fixed_positions(self, board, adj_regions):
        #COLOCAR P's na grid
        queue = deque(adj_regions)
        queued_regions = set(adj_regions)

        #print("State:", state.id)
        #print("region ", state.region_action)
        #print("QUEUE:" , queue)
        while queue:
            #rint("Queue:", queue)
            region = queue.popleft()
            queued_regions.remove(region)
                        
            filtered_actions = self.filter_actions(board, region, board.possible_pieces[region])
            
            #print("Filtered Actions for region", region, ":", filtered_actions)
            if len(filtered_actions) == 0:
                #print("No possible pieces for region", region)
                return False
            
            board.possible_pieces[region] = filtered_actions
            #print("STATE.BOARD.POSSIBLE_pIECES", region, ":", state.board.possible_pieces[region])
            region_pieces = board.possible_pieces[region]
            fixed_letter, fixed_positions = next(iter(region_pieces))

            for letter, positions in region_pieces:
                aux = []
                for (i, j) in positions:
                    if (i, j) in fixed_positions:
                        aux.append((i, j))
                    if fixed_letter != letter:
                        fixed_letter = 'P'
                fixed_positions = aux

            # Se não houver posições fixas, continuar para a próxima região
            if len(fixed_positions) == 0:
                continue
            
            # Se houver 4 posições fixas, colocar a peça e continuar para a próxima regiã0
            if len(fixed_positions) == 4:
                #print("PLACED PIECE: ", fixed_letter, fixed_positions)
                Board.place_piece(board, region, fixed_letter, tuple(fixed_positions))

                Board.update_graph(self.main_grid, region, positions, board)

                #print(board.adj_graph)

                for r in board.adj_graph[region]:
                    if r not in queued_regions and r in board.regions.keys():
                        queue.append(r)
                        queued_regions.add(r)

            
            else:
                # CC, colocar P's
                new_Ps = False
                for i, j in fixed_positions:
                    if board.grid[i][j] != fixed_letter:
                        new_Ps = True
                        board.grid[i][j] = fixed_letter    #TODO: REVER Ps / LETTTERS na grid
                        #state.only_letter += len(fixed_positions)

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
                #print(neighbor)
                if (ni, nj) not in board.regions[region] and neighbor is not None:
                    # Se for uma peça igual adjacente fora da região, é inválido
                    if neighbor == piece_letter:
                        #print(f"Peça {piece_letter} ligada a outra peça igual na posição ({ni}, {nj})")
                        return True
                    # Se houver qualquer célula adjacente, que pertença a uma peça, numa região diferente, não está isolada
                    # Se a região da célula adjacente ainda não tiver peça colocada, não se pode dizer que está isolada
                    
                    if neighbor != piece_letter and neighbor in TETROMINO_SHAPES:
                        isolated = False

                    if neighbor in board.regions.keys():
                        isolated = False

        # Se ficou isolada (nenhuma célula adjacente pertence a outra região)
        if isolated and len(board.regions) < board.num_regions:
            return True

        return False

    def filter_actions(self, board, region, possible_pieces):
        
        """Devolve as peças que podem ser colocadas na região atendendo às regras do L.I.T.S ."""

        filtered_pieces = set()
        grid = board.grid
        #print("In filter actions: ")
        #Board.print_instance(grid)
        

        for piece in possible_pieces:

            letter, positions = piece

            has_invalid_adj = Nuruomino.invalid_adjacencies(board, region, letter, positions)
            
            if has_invalid_adj:
                continue
            
            original = [grid[i][j] for i, j in positions]

            for (i, j) in positions:
                grid[i][j] = letter
            
            forms_square = any(Board.is_square(grid, row, col) for row, col in positions)

            for idx, (i, j) in enumerate(positions):
                grid[i][j] = original[idx]

            if forms_square:
                continue
            
            filtered_pieces.add((letter, tuple(positions)))

        return filtered_pieces

    def calculate_least_possibilities(possible_pieces, adj_graph):
        return sorted(
            possible_pieces.keys(),
            key=lambda reg: (len(possible_pieces[reg]), -len(adj_graph[reg]))
        )
    
    

    
    def actions(self, state: NuruominoState):

        actions = []
       
        #print(state.board.possible_pieces)

        ordered_list = Nuruomino.calculate_least_possibilities(state.board.possible_pieces, state.board.adj_graph) #Lista ordenada --> Menos Opções --> Mais Opções

        
        for region in ordered_list:

            if region in state.board.regions.keys():

                pieces = state.board.possible_pieces[region]


                for piece, positions in pieces:
                    
                    new_board = Board.clone(state.board)
                    Board.place_piece(new_board, region, piece, positions)
                    Board.update_graph(self.main_grid, region, positions, new_board)
                    
                    #print(new_board.adj_graph)
                    affected_regions = [r for r in new_board.adj_graph[region] if r in new_board.regions.keys()]

                    bad_path = False
                    #Board.print_instance(new_board.grid)
                    if not self.fixed_positions(new_board, affected_regions):
                        #print("New State ID:", new_state.id)
                        #print("Bad Path Detected!")
                        bad_path = True
                        
                    if not bad_path and not self.all_regions_reachable(region, new_board):
                        #print("NOT REACHABLE")
                        bad_path = True
                    
                    if not bad_path:
                        actions.append(new_board)

                #sorted_actions = sorted(actions, key=lambda tup: len(tup[0].adj_graph[tup[1]]), reverse=True)

                # E se só queres os boards:
                #sorted_actions = [tup[0] for tup in sorted_actions]
                
                return actions
        
        return []
    
    def all_regions_reachable(self, placed_region, board):
        
        visited = set()
        queued_regions = set()
        graph = board.adj_graph

        queue = deque([placed_region])
        
        while queue:

            current_region = queue.popleft()
            visited.add(current_region)

            for adj_region in graph[current_region]:
                if adj_region not in visited and adj_region not in queued_regions:
                    queue.append(adj_region)
                    queued_regions.add(adj_region)

        if len(visited) != self.num_regions:
            return False
        
        return True



    def result(self, state: NuruominoState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        #print("RESULT")
        #print(action)
        new_state = NuruominoState(action)
        
        return new_state
              
    def goal_test(self, state: NuruominoState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        #print("GOAL NODE: ")
        if len(state.board.regions) > 0:
            #print("GOAL NODE: ")
            #print(state.board.regions.keys())
            return False

        if self.all_regions_reachable(1, state.board):
            self.board = state.board
            return True
        
        return False
    
   
    def get_dynamic_weights(state, node):
        #r = len(state.board.regions)
        return {'num_actions': 0.5,
                'regions_left': 0.3, 
                #'new_Ps': 0.2,
                #'num_nurikabes': 0.2,
                #'nuri_size_diff': 0.05,
                'connections' : 0.2,
                'critical': 1.0,}
    
    def h_priority_regions(region, state: NuruominoState):
        if region in state.priority_regions:
            return -10
        return 0


    def h(self, node: Node):
        #print("Node_ID and Action:", node.state.id, node.action)
        
        """Função heuristica utilizada para a procura A*."""

        #print("Number of Regions:", len(node.state.board.regions))

        if node.state.id == 0:
            return 1000
        
        # Quantidade de novas posições fixas descobertas (quanto mais melhor)
        new_Ps = node.state.only_letter
        # Número de regiões por preencher (quanto menos melhor)
        regions_left = len(node.state.board.regions)
        # Quantidade de ações possíveis na região (quanto menos melhor)
        num_actions = node.state.region_actions / self.region_sizes[node.state.region_action]
        # Tamanho médio das regiões adjacentes (quanto menos melhor)

        priority_region = Nuruomino.h_priority_regions(node.state.region_action, node.state)
        
        #adj_regions = Nuruomino.h_adj_regions_priority(node.state)
        num_nurikabes, nuri_size_diff = Nuruomino.num_nurikabes(node.state)

        connections = Nuruomino.h_state_connections(node.state) / len(node.state.board.placed_pieces) 

        # Penalização, caminho sem solução
        critical = Nuruomino.h_bad_path(node.state)

        isolated_move = 1000 
        if not node.state.not_connected_permanently:
            isolated_move = 0
        
        weights = Nuruomino.get_dynamic_weights(node.state, node)

        h = (
            1.0 * priority_region +
            weights['num_actions'] * num_actions +
            #weights['num_nurikabes'] * num_nurikabes +
            weights['regions_left'] * regions_left -
            #weights['nuri_size_diff'] * nuri_size_diff -
            #weights['new_Ps'] * new_Ps -
            weights['connections'] * connections +
            weights['critical'] * critical
            #weights['still_possible_region'] * still_possible_region
        )
        
        if h < 1000:    
            print(f"Possible Moves:{node.state.board.possible_pieces.keys()}") 
            print("Node_id:", node.state.id)
            print("Action:", node.action)
            print(f" Priority REGION: {priority_region} \n H-->  num_Actions: {num_actions} \n| Regions left: {regions_left} \n| New Ps: {new_Ps} \n| Num_nurikabes: {num_nurikabes} \n Connections {connections} \n Critical: {critical}")
            print("Depth:", node.depth)
            print("F(n):", h)
            Board.print_instance(node.state.board.grid)
            print()
        

        return h - node.depth
        

if __name__ == "__main__":
    board = Board.parse_instance()
    problem = Nuruomino(board)
    
    #Board.print_instance(problem.board.grid)
    #Board.print_regions(problem.board)
    #goal_node = astar_search(problem)
    goal_node = depth_first_tree_search(problem)
    #goal_node = greedy_search(problem)
    #print("SOLUTION: ")
    Board.print_instance(problem.board.grid)
    

