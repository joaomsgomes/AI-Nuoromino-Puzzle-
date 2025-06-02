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

        self.bad_path = False
        self.only_letter = 0
        self.action_region_size = 0
        self.region_actions = 0
        self.not_connected_permanently = False
        self.region_action = None
        self.priority_regions = set()
        self.adj_graph = None


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
        
        self.placed_pieces = set()
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
        
        positions = self.regions[region]
        
        adj_regions = []

        for i, j in positions:
            adj_val = Board.adjacent_values(self, i, j)
            
            
            for r in adj_val:
                if r not in adj_regions and r != region and r not in TETROMINO_SHAPES and r in self.regions.keys():
                    adj_regions.append(r)
        
        
        return adj_regions

        
    
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
                self.placed_pieces.add((r, piece_letter, tuple(self.regions[r])))
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

    def invalid_adjacencies(self, region, piece_letter, positions):
        """
        Verifica se a peça está conectada a outra peça igual (inválido)
        ou se a região ficou isolada (inválido).
        """
        isolated = True

        for (i, j) in positions:
            for dx, dy in DELTAS:
                ni, nj = i + dx, j + dy
                neighbor = Board.get_value(self.grid, ni, nj)

                if (ni, nj) not in self.regions[region] and neighbor is not None:
                    # Se for uma peça igual adjacente fora da região, é inválido
                    if neighbor == piece_letter:
                        #print(f"Peça {piece_letter} ligada a outra peça igual na posição ({ni}, {nj})")
                        return True

                    # Se houver qualquer célula adjacente, que pertença a uma peça, numa região diferente, não está isolada
                    # Se a região da célula adjacente ainda não tiver peça colocada, não se pode dizer que está isolada
                    
                    if neighbor != piece_letter and neighbor in TETROMINO_SHAPES:
                        isolated = False

                    if neighbor in self.regions.keys():
                        isolated = False

        # Se ficou isolada (nenhuma célula adjacente pertence a outra região)
        if isolated and len(self.regions) < self.num_regions:
            #print("REGIÃO ISOLADA DETETADA!")
            return True

        return False

    def filter_actions(self, region, possible_pieces):
        
        """Devolve as peças que podem ser colocadas na região atendendo às regras do L.I.T.S ."""
        
        board = self.clone()

        filtered_pieces = []

        for piece in possible_pieces:

            piece_type, positions = piece
            aux_board = board.clone()

            has_invalid_adj = aux_board.invalid_adjacencies(region, piece_type, positions)

            if has_invalid_adj:
                continue

            Board.place_piece(aux_board.grid, piece_type, positions)
            
            forms_square = any(Board.is_square(aux_board.grid, row, col) for row, col in positions)

            if forms_square:
                continue

            filtered_pieces.append(piece)

        
        return filtered_pieces
    
    
    def is_square(grid, row, col):

        for deltas in SQUARE_DELTAS:
            square = [Board.get_value(grid, row + dx, col + dy) for dx, dy in deltas]
            count = 0
            for val in square:
                if val in TETROMINO_SHAPES:
                    count+=1
            if count == 4:
                return True
        
        return False

    def clone(self):   

        new_grid = [row[:] for row in self.grid]
        new_regions = {k: v[:] for k, v in self.regions.items()}
        new_possible_pieces = {k: v[:] for k, v in self.possible_pieces.items()}
        new_region_adj_regions = {k: v[:] for k, v in self.region_adj_regions.items()}
        new_placed_pieces = set((region, piece, tuple(positions)) for region, piece, positions in self.placed_pieces)
        b = Board(new_grid, new_regions)
        b.possible_pieces = new_possible_pieces
        b.region_adj_regions = new_region_adj_regions
        b.placed_pieces = new_placed_pieces
        b.num_regions = self.num_regions
        return b
        

    # TODO: outros metodos da classe Board



# Perceber se vale realmente a pena
def fixed_positions(state: NuruominoState, adj_regions):
        #COLOCAR P's na grid
    queue = deque(adj_regions)
    queued_regions = set(adj_regions)

    #print("State:", state.id)
    #print("region ", state.region_action)
    #print("QUEUE:" , queue)
    while queue:
        #print("Queue:", queue)
        region = queue.popleft()
        queued_regions.remove(region)

        #print("Region:", region)
                    
        filtered_actions = state.board.filter_actions(region, state.board.possible_pieces[region])
        
        #print("Filtered Actions for region", region, ":", filtered_actions)
        if len(filtered_actions) == 0:
            #print("No possible pieces for region", region)
            return False
        
        state.board.possible_pieces[region] = filtered_actions
        #print("STATE.BOARD.POSSIBLE_pIECES", region, ":", state.board.possible_pieces[region])
        region_pieces = state.board.possible_pieces[region]
        fixed_positions = region_pieces[0][1]
        fixed_letter = region_pieces[0][0]

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
            #print("No fixed positions for region", region)
            #print("TEsted on board:")
            #Board.print_instance(state.board.grid)
            continue
        
        # Se houver 4 posições fixas, colocar a peça e continuar para a próxima regiã0
        if len(fixed_positions) == 4:
            Board.place_piece(state.board.grid, fixed_letter, fixed_positions)
            state.board.placed_pieces.add((region, fixed_letter, tuple(fixed_positions)))
            state.board.regions.pop(region)
            state.board.possible_pieces.pop(region)
            Nuruomino.update_adjacency_graph_piece(state.adj_graph, region, fixed_letter, fixed_positions) # TO BE REVIEWED!!!
            

            for r in state.board.region_adj_regions[region]:
                if r not in queued_regions and r in state.board.regions.keys():
                    queue.append(r)
                    queued_regions.add(r)
        
        else:
            # CC, colocar P's
            for i, j in fixed_positions:
                if state.board.grid[i][j] != fixed_letter:
                    state.board.grid[i][j] = fixed_letter    #TODO: REVER Ps / LETTTERS na grid
                    state.only_letter += len(fixed_positions)

    

        #self.regions[region] = list(visited_positions)

    #Board.print_regions(self.possible_pieces)
    #if state.id == 241:
    #    Board.print_regions(state.board.regions)
    #    time.sleep(5)

    return True

class Nuruomino(Problem):

    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.board = board
        self.initial = NuruominoState(board)
        self.initial.state_id = 0 # ID do estado inicial
        self.region_sizes = { region: len(positions) for region, positions in self.board.regions.items() }
        
        self.board.fill_tetromino_regions()
        board.set_possible_pieces()
        board.set_adjacent_regions()
        
        fixed_positions(self.initial, list(self.board.regions.keys()))#Estado inicial de qualquer no
        self.initial.adj_graph = self.build_adjacency_graph(self.initial) #Criar grafo de adjacências
        #print("BOARD INICIAL:")
        #Board.print_instance(self.board.grid)
        #print("Initial POSSIBLE PIECES:", self.board.possible_pieces)
        #time.sleep(1)
        
        #TODO
        pass 

    def copy_adjacency_graph(adj_graph):
        """
        Faz uma cópia profunda do grafo de adjacências sem usar deepcopy().
        """
        new_graph = {}
        for region, neighbors in adj_graph.items():
            new_graph[region] = {}
            for adj, pieces in neighbors.items():
                # Cada peça é um tuplo (piece, positions), onde positions é um tuplo de tuplos
                new_graph[region][adj] = set((piece, tuple(pos)) for piece, pos in pieces)
        return new_graph


    def build_adjacency_graph(self, state):

        adj_graph = defaultdict(dict)
        for region in state.board.regions:
            for adj in state.board.region_adj_regions[region]:
                connecting_pieces = []
                for piece, positions in state.board.possible_pieces[region]:
                    for (i, j) in positions:
                        for dx, dy in DELTAS:
                            ni, nj = i + dx, j + dy
                            if (ni, nj) in state.board.regions[adj]:
                                connecting_pieces.append((piece, tuple(positions)))
                                break
                if connecting_pieces:
                    adj_graph[region][adj] = set(connecting_pieces)

        return adj_graph

    def update_adjacency_graph_piece(graph, placed_region, piece, positions):
        """
        Atualiza o grafo de adjacência após colocar uma peça numa região.
        Remove ligações que deixaram de ser possíveis devido à peça colocada.
        """

        positions_set = set(positions)

        for adj in list(graph[placed_region].keys()):
            updated_entries = []

            for entry in graph[placed_region][adj]:
                entry_piece, entry_positions = entry[0], set(entry[1])

                # Mantém apenas entradas que correspondem a esta peça colocada
                if entry_piece == piece and entry_positions == positions_set:
                    updated_entries.append(entry)

            graph[placed_region][adj] = updated_entries

            # Atualizar simetricamente o adjacente → placed_region
            if placed_region in graph[adj]:
                inverse_entries = []

                for entry in graph[adj][placed_region]:
                    entry_piece, entry_positions = entry[0], set(entry[1])

                    # Verifica se há alguma posição adjacente à peça colocada
                    if any((i + dx, j + dy) in positions_set and entry_piece != piece for (i, j) in entry_positions for dx, dy in DELTAS):
                        original = [board.grid[i][j] for i, j in entry_positions]
                        for (i, j) in entry_positions:
                            board.grid[i][j] = entry_piece

                        Board.print_instance(board.grid)
                        forms_square = any(Board.is_square(board.grid, row, col) for row, col in entry_positions)
                        print("Forms_Square: ", forms_square, "for position: ", (i, j))
                        for idx, (i, j) in enumerate(entry_positions):
                            board.grid[i][j] = original[idx]
                        if not forms_square:
                            inverse_entries.append(entry)

                graph[adj][placed_region] = inverse_entries

    def print_adjacency_graph(adj_graph):

        print("Grafo de adjacências entre regiões:")
        for region, neighbors in adj_graph.items():
            print(f"Região {region}:")
            for adj, pieces in neighbors.items():
                print(f"  -> Região {adj}: peças possíveis = {sorted(pieces)}")
            print()

    def actions(self, state: NuruominoState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        all_actions = []
        for region in state.board.regions:
                if region in state.adj_graph:
                    print("Region in Graph: ", region)
                    for adj, pieces in state.adj_graph[region].items():
                        for piece, positions in pieces:
                            action = (region, piece, positions)
                            if action not in all_actions:
                                print("We are going to Add: ", (region, piece, positions))
                                all_actions.append(action)
        
        #print("State ID:", state.id)
        #print("Action on Region:", state.region_action)
        #Board.print_instance(state.board.grid)
        #time.sleep(2)
        
        return all_actions

    def result(self, state: NuruominoState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        region, piece, positions = action

        #Board.print_instance(state.board.grid)

        if len(state.board.regions[region]) < 4:
            return None
        
        board_copy = state.board.clone()
        new_state = NuruominoState(board_copy)
        
        Board.place_piece(new_state.board.grid, piece, positions)
        new_state.board.placed_pieces.add((region, piece, tuple(positions)))
        Nuruomino.update_adjacency_graph_piece(new_state.adj_graph, region, piece, positions)
        new_state.region_actions = len(state.board.possible_pieces[region])
        new_state.region_action = region        # TO REMOVE

        new_state.action_region_size = len(state.board.regions[region])
        
        new_state.board.regions.pop(region)
        new_state.board.possible_pieces.pop(region)

        
        affected_regions = [r for r in new_state.board.region_adj_regions[region] if r in new_state.board.regions.keys()]
        
        if not fixed_positions(new_state, affected_regions):
            #print("New State ID:", new_state.id)
            #print("Bad Path Detected!")
            new_state.bad_path = True

        Nuruomino.set_priority_regions(new_state)
        

        #print("\n\n\n")
        #print("New State ID:", new_state.id)
        #Board.print_instance(new_state.board.grid)
        #state.board = board_copy
        return new_state
    
    def set_priority_regions(state: NuruominoState):
        
        priority_regions = set()

        #print(state.id, "SET PRIORITY REGIONS")

        for _, _, positions in state.board.placed_pieces:
            break_for = False

            for (i, j) in positions:
                if break_for:
                    break

                for dx, dy in DELTAS:
                    if break_for:
                        break

                    ni, nj = i + dx, j + dy
                    neighbor = Board.get_value(state.board.grid, ni, nj)

                    if (ni, nj) not in positions:
                        #print("Neighbor:", neighbor, "Position:", (ni, nj))
                        if neighbor in TETROMINO_SHAPES:
                            state.priority_regions = set()
                            break_for = True
                            break

                        if neighbor in state.board.regions.keys():
                            #print("APPENEDING NEIGHBOR:", neighbor)
                            priority_regions.add(neighbor)
        
        state.priority_regions = priority_regions
              
    def goal_test(self, state: NuruominoState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""

        if len(state.board.regions) > 0:
            return False
        
        visited = set()
        queue = deque([next(iter(state.board.placed_pieces))[2][0]])
        # TO CHANGE: COMEÇAR NA PEÇA QUE FOI COLOCADA NO ESTADO INICIAL

        while queue:

            i, j = queue.popleft()
            visited.add((i, j))

            for dx, dy in DELTAS:
                ni, nj = i + dx, j + dy
                adj_piece = Board.get_value(state.board.grid, ni, nj)
                
                if adj_piece in TETROMINO_SHAPES and adj_piece != 'P':
                    if (ni, nj) not in visited:
                        queue.append((ni, nj))
        
        if len(visited) < state.board.num_regions * 4:
            return False
        
        self.board = state.board

        return True
    
    def h_critical_regions(self, state: NuruominoState):

        visited = set()
        queue = deque([next(iter(state.board.placed_pieces))[1][0]])
        # TO CHANGE: COMEÇAR NA PEÇA QUE FOI COLOCADA NO ESTADO INICIAL

        while queue:
            i, j = queue.popleft()
            visited.add((i, j))

            for dx, dy in DELTAS:
                ni, nj = i + dx, j + dy
                adj_piece = Board.get_value(state.board.grid, ni, nj)
                
                if adj_piece in TETROMINO_SHAPES and adj_piece != 'P':
                    if (ni, nj) not in visited:
                        queue.append((ni, nj))
    

    def num_nurikabes(state: NuruominoState):
        
        num_nurikabes = 0
        filled_positions = {pos for _, _, positions in state.board.placed_pieces for pos in positions}
        nurikabes_sizes = []

        while filled_positions:
            #print("Placed Pieces:", filled_positions)

            visited = set()
            queue = deque([next(iter(filled_positions))])
            filled_positions.discard(queue[0])

            while queue:
                #print("Queue:", queue)

                i, j = queue.popleft()
                visited.add((i, j))

                for dx, dy in DELTAS:
                    ni, nj = i + dx, j + dy
                    adj_piece = Board.get_value(state.board.grid, ni, nj)

                    
                    if adj_piece in TETROMINO_SHAPES and adj_piece != 'P':
                        if (ni, nj) not in visited:
                            queue.append((ni, nj))
                            filled_positions.discard((ni, nj))

                        
            num_nurikabes +=1
            nurikabes_sizes.append(len(visited))


        diff = max(nurikabes_sizes) - min(nurikabes_sizes)


        return num_nurikabes, diff


    def region_no_moves(node):
        
        region = node.action[0]

        region_adj_regions = node.state.board.region_adj_regions

        if region not in region_adj_regions:
            return 0
        
        for adj_region in region_adj_regions[region]:
            if adj_region in node.state.board.possible_pieces.keys() and len(node.state.board.possible_pieces[adj_region]) == 0:
                return 1000

        return 0



    def h_state_connections(state: NuruominoState):

        main_directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        connections = set()
    

        for _, piece_letter, positions in state.board.placed_pieces:
            for (i,j) in positions:
                for dx, dy in main_directions:
                    adj_piece = Board.get_value(state.board.grid, i+dx, j+dy)
                    pos1 = (i, j)
                    pos2 = (i + dx, j + dy)
                    if (adj_piece in TETROMINO_SHAPES and adj_piece != piece_letter
                        and (pos1, pos2) not in connections
                        and (pos2, pos1) not in connections):
                        
                        connections.add((pos1, pos2, (i + dx, j + dy)))

        if len(connections) == 0:
            return -100
        return len(connections)
    
    def h_bad_path(state: NuruominoState):
        if state.bad_path:
            return 1000
        return 1
    
    def number_tetrominos_connected(state: NuruominoState):
   
        connected_letters = set()
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        #print("Placed Pieces:", state.board.placed_pieces)

        for _, piece_letter, positions in state.board.placed_pieces:
            #print("Piece Letter:", piece_letter, "Positions:", positions)
            for (i, j) in positions:
                for dx, dy in directions:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < len(state.board.grid) and 0 <= nj < len(state.board.grid):
                        adj_piece = Board.get_value(state.board.grid, ni, nj)
                        if adj_piece in TETROMINO_SHAPES and adj_piece != piece_letter:
                            connected_letters.add((piece_letter, positions))
                            break
                else:
                    continue
                break
        return len(connected_letters)

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
            #1.0 * priority_region +
            weights['num_actions'] * num_actions +
            #weights['num_nurikabes'] * num_nurikabes +
            weights['regions_left'] * regions_left -
            #weights['nuri_size_diff'] * nuri_size_diff -
            #weights['new_Ps'] * new_Ps -
            weights['connections'] * connections +
            weights['critical'] * critical
            #weights['still_possible_region'] * still_possible_region
        )
        
        """if h < 1000:    
            print(f"Possible Moves:{node.state.board.possible_pieces.keys()}") 
            print("Node_id:", node.state.id)
            print("Action:", node.action)
            print(f" Priority REGION: {priority_region} \n H-->  num_Actions: {num_actions} \n| Regions left: {regions_left} \n| New Ps: {new_Ps} \n| Num_nurikabes: {num_nurikabes} \n Connections {connections} \n Critical: {critical}")
            print("Depth:", node.depth)
            print("F(n):", h)
            Board.print_instance(node.state.board.grid)
            print()
        """

        return h - node.depth
        

if __name__ == "__main__":
    board = Board.parse_instance()
    problem = Nuruomino(board)
    

    Board.print_instance(problem.board.grid)    
    
    print("BEFORE PLACING A PIECE !!")

    Nuruomino.print_adjacency_graph(problem.initial.adj_graph)
    
    print("AFTER PLACING A PIECE !!")


    #Nuruomino.update_adjacency_graph_piece(problem.initial.adj_graph, 1, 'L', ((0,0), (0,1), (0,2), (1,0)))

    #Nuruomino.print_adjacency_graph(problem.initial.adj_graph)
    
    #problem.actions(problem.initial)

    #Nuruomino.print_adjacency_graph(problem.initial.adj_graph)

    #Board.print_regions(problem.board)
    #goal_node = astar_search(problem)
    #goal_node = greedy_search(problem)
    #print("SOLUTION: ")
    #Board.print_instance(problem.board.grid)

    # PROBLEM:   Ações diferentes geram os mesmos estados equivalentes, mas formados por ordens diferentes
    # CAUSE:        Função Fixed Positions resolve as implicações de regiões imediatamente, em vez de só colocar novas peças em estados futuros
    # SOLUTION:     Mudar abordagem? Misturar com versão anterior?
    # Esta versão:      Mais condições no fixed_positions (peças únicas na região mas em posições diferentes)
    # Anterior versão:    Colocar peças apenas em novos estados!
    '''
    Exatamente, é isso mesmo!
    O teu algoritmo está a considerar estados equivalentes como diferentes porque,
    apesar do grid ser igual, outros atributos do estado (como placed_pieces, regions,
    possible_pieces, etc.) podem estar em ordens diferentes ou conter informação redundante,
    levando a diferentes hashes ou comparações
    '''
    

