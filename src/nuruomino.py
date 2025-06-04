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

        self.region_action = None  # Região onde a ação foi executada
        self.bad_path = False
        self.only_letter = 0
        self.action_region_size = 0
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
        #isolated = True

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
                    
                    #if neighbor != piece_letter and neighbor in TETROMINO_SHAPES:
                    #    isolated = False

                    #if neighbor in self.regions.keys():
                    #    isolated = False

        # Se ficou isolada (nenhuma célula adjacente pertence a outra região)
        #if isolated and len(self.regions) < self.num_regions:
            #print("REGIÃO ISOLADA DETETADA!")
        #    return True

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

        #Board.print_instance(state.board.grid)
        region = queue.popleft()
        queued_regions.remove(region)

        #print("Region:", region)
                    
        #filtered_actions = state.board.filter_actions(region, state.board.possible_pieces[region])
        possible_pieces = set()
        for adj_r in state.adj_graph[region].values():
            for piece, positions in adj_r:
                possible_pieces.add((piece, positions))
        
        #Nuruomino.print_adjacency_graph(state.adj_graph)

        #print("Filtered Actions for region", region, ":", filtered_actions)
        if len(possible_pieces) == 0:
            #print("No possible pieces for region", region)
            return False
        
        letter, positions = next(iter(possible_pieces))

        #state.board.possible_pieces[region] = filtered_actions !!!!
        #print("STATE.BOARD.POSSIBLE_pIECES", region, ":", state.board.possible_pieces[region])
        fixed_positions = positions
        fixed_letter = letter

        for let, pos in possible_pieces:
            aux = []
            for (i, j) in pos:
                if (i, j) in fixed_positions:
                    aux.append((i, j))
                if fixed_letter != let:
                    fixed_letter = 'P'
            fixed_positions = aux

        # Se não houver posições fixas, continuar para a próxima região
        if len(fixed_positions) == 0:
            #print("No fixed positions for region", region)
            #print("TEsted on board:")
            #Board.print_instance(state.board.grid)
            continue
        
        # Se houver 4 posições fixas, colocar a peça e continuar para a próxima regiã0
        if len(fixed_positions) == 4 and region in state.board.regions.keys():
            Board.place_piece(state.board.grid, fixed_letter, fixed_positions)
            state.board.placed_pieces.add((region, fixed_letter, tuple(fixed_positions)))
            state.board.regions.pop(region)
            state.board.possible_pieces.pop(region)
            Nuruomino.update_adjacency_graph_piece(state, region, fixed_letter, fixed_positions) # TO BE REVIEWED!!!
            

            for r in state.board.region_adj_regions[region]:
                if r not in queued_regions and r in state.board.regions.keys():
                    queue.append(r)
                    queued_regions.add(r)
        
        else:

            # CC, colocar P's
            new_Ps = False
            for i, j in fixed_positions:
                if state.board.grid[i][j] != fixed_letter:
                    state.board.grid[i][j] = fixed_letter    #TODO: REVER Ps / LETTTERS na grid
                    new_Ps = True
                    state.only_letter += len(fixed_positions)

            if new_Ps:
                
                for adj in state.adj_graph[region]:
                    
                    #print(adj)

                    if region in state.adj_graph[adj] and adj in state.board.regions.keys():
                        invalid_entries = set()

                        for entry in state.adj_graph[adj][region]:
                            
                            entry_piece, entry_positions = entry[0], set(entry[1])
                            # Verifica se há alguma posição adjacente à peça colocada
                            if any((i + dx, j + dy) in fixed_positions for (i, j) in entry_positions for dx, dy in DELTAS):

                                if Nuruomino.is_invalid_entry(state.board.grid, entry_piece, entry_positions, fixed_letter):
                                    invalid_entries.add(entry)
                        
                        for e in invalid_entries:
                            for reg in state.adj_graph[adj]:
                                if e in state.adj_graph[adj][reg]:
                                    state.adj_graph[adj][reg].remove(e)

                        if adj not in queued_regions and len(invalid_entries) > 0:
                            queue.append(adj)
                            queued_regions.add(adj)



                    
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
        self.num_regions = len(board.regions)
        self.region_sizes = { region: len(positions) for region, positions in self.board.regions.items() }

        self.bad_actions = set()

        board.set_possible_pieces()
        board.set_adjacent_regions()


        #Board.print_instance(self.board.grid)
        
        
        self.initial.adj_graph = self.build_adjacency_graph(self.initial) #Criar grafo de adjacências

        
        fixed_positions(self.initial, list(self.board.regions.keys()))#Estado inicial de qualquer no
        self.ordered_actions = self.calculate_min_actions(self.initial.adj_graph)

        #Nuruomino.print_adjacency_graph(self.initial.adj_graph)
        
        #print("BOARD INICIAL:")
        #Board.print_instance(self.board.grid)
        #print("Ordered_Actions: ", self.ordered_actions)
        #print("Initial POSSIBLE PIECES:", self.board.possible_pieces)
        #time.sleep(1)
        
        #TODO
        pass 

    # NAO ESTÀ A FILTRAR TOATALMENTE AS PEÇAS POSSÍVEIS
    # QUANDO SE RETIRA DE UMA REGIAO ADJACENTE UMA PEÇA, TEM QUE SE RETIRAR ESSA MESMA PEÇA


    def calculate_min_actions(self, adj_graph):
        """
        Recebe o grafo de adjacências e devolve uma lista de regiões
        ordenadas por ordem crescente do número de ações possíveis (únicas).
        """

        region_actions = []
        for region in adj_graph:
            if region in self.initial.board.regions:
                unique_actions = set()
                for pieces in adj_graph[region].values():
                    for piece, positions in pieces:
                        unique_actions.add((piece, positions))        
                num_actions = len(unique_actions)
                region_actions.append((region, num_actions))
        # Ordena por número de ações possíveis (crescente)
        region_actions.sort(key=lambda x: x[1])


        return [region for region, _ in region_actions]



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
                connecting_pieces = set()
                for piece, positions in state.board.possible_pieces[region]:
                    for (i, j) in positions:
                        for dx, dy in DELTAS:
                            ni, nj = i + dx, j + dy
                            if (ni, nj) in state.board.regions[adj]:
                                connecting_pieces.add((piece, tuple(positions)))
                                break
                if connecting_pieces:
                    adj_graph[region][adj] = connecting_pieces

        return adj_graph
    
    def is_invalid_entry(grid, entry_piece, entry_positions, piece):
             
        if entry_piece == piece: #ADJACENCIAS
            return True
            
        original = [grid[i][j] for i, j in entry_positions]

        for (i, j) in entry_positions:
            grid[i][j] = entry_piece

        #print("Checking if entry forms a square:", entry)
        #Board.print_instance(board.grid)

        forms_square = any(Board.is_square(grid, row, col) for row, col in entry_positions)
        
        for idx, (i, j) in enumerate(entry_positions):
            grid[i][j] = original[idx]

        if forms_square: #QUADRADOS
            return True

        return False
        


    def update_adjacency_graph_piece(state, placed_region, piece, positions):
        """
        Atualiza o grafo de adjacência após colocar uma peça numa região.
        Remove ligações que deixaram de ser possíveis devido à peça colocada.
        """

        #print("Updating adjacency graph for region:", placed_region, "with piece:", piece, "at positions:", positions)

        positions_set = set(positions)
        graph = state.adj_graph
        board = state.board

        for adj in list(graph[placed_region].keys()):
            updated_entries = set()

            for entry in graph[placed_region][adj]:
                entry_piece, entry_positions = entry[0], set(entry[1])

                # Mantém apenas entradas que correspondem a esta peça colocada
                if entry_piece == piece and entry_positions == positions_set:
                    updated_entries.add(entry)

            graph[placed_region][adj] = updated_entries

            # Atualizar simetricamente o adjacente → placed_region
            if placed_region in graph[adj]:
                invalid_entries = set()
                invalid_region_entries = set()

                for entry in graph[adj][placed_region]:
                    
                    entry_piece, entry_positions = entry[0], set(entry[1])
                    # Verifica se há alguma posição adjacente à peça colocada
                    if any((i + dx, j + dy) in positions_set for (i, j) in entry_positions for dx, dy in DELTAS):

                        if Nuruomino.is_invalid_entry(board.grid, entry_piece, entry_positions, piece):
                            invalid_entries.add(entry)

                    else:
                        #print("No adjacent positions found for entry:", entry)
                        invalid_region_entries.add(entry)
                        
                for reg in graph[adj].keys():
                    to_remove = set()
                    for en in graph[adj][reg]:
                        if en in invalid_entries:
                            to_remove.add(en)
                        if en in invalid_region_entries and reg == placed_region:
                            to_remove.add(en)
                    graph[adj][reg] -= to_remove
 
                        
                            


    def print_adjacency_graph(adj_graph):

        print("Grafo de adjacências entre regiões:")
        for region, neighbors in adj_graph.items():
            print(f"Região {region}:")
            for adj, pieces in neighbors.items():
                print(f"  -> Região {adj}: peças possíveis = {pieces}")
            print()


    def get_smallest_region(self, state):
        # Retorna o id da região com menor número de células
        return min(state.board.regions, key=lambda r: len(state.board.regions[r]))


    
    
    def actions(self, state: NuruominoState):

        # OBTER AÇÕES:
        # -> EM REGIÕES MAIS PEQUENAS
        # -> EM REGIÕES COM MENOS AÇÕES POSSÍVEIS
        # -> PEÇAS COM ADJACENCIA COM MAIS REGIÕES

        # JUNTAR CRITERIOS
        # ORDENAR
        all_actions = []
        for region in self.ordered_actions:
            
            if region in state.board.regions:
                #print("regionnnnnnn")
                actions = set()
                for adj_region in state.adj_graph[region]:
                    for piece in state.adj_graph[region][adj_region]:
                        #print("ADDING TO ACTIONS")
                        actions.add(piece)
                #print(actions)
                for piece, positions in actions:
                    #print("FOR REGION: ", region, "USING PIECE: ", (piece,positions))
                    board_copy = state.board.clone()
                    future_state = NuruominoState(board_copy)
                    future_graph = Nuruomino.copy_adjacency_graph(state.adj_graph)
                    future_state.adj_graph = future_graph

                    Board.place_piece(future_state.board.grid, piece, positions)
                    #print("Placed Piece: ", (piece, positions))
                    #Board.print_instance(future_state.board.grid)
                    future_state.board.placed_pieces.add((region, piece, tuple(positions)))
                    future_state.board.regions.pop(region)
                    
                    Nuruomino.update_adjacency_graph_piece(future_state, region, piece, positions)

                    bad_path = False
                    if not fixed_positions(future_state, future_state.adj_graph[region].keys()):
                        #print("FUTURE STATE: ")
                        #Board.print_instance(future_state.board.grid)
                        #print("PROBLEM FIXED PSOITIONS")
                        bad_path = True
                        
                    elif not self.all_regions_reachable(region, future_state):
                        #print("PROBLEM ALL REGIONS REACHABLE")
                        bad_path = True

                    if not bad_path:
                        all_actions.append((region, piece, positions))
            
                if not all_actions:
                    continue

                #print("NODE EXPANDED State ID:", state.id)
                #Board.print_instance(state.board.grid)
                #print("Possible Actions:", all_actions)
                #time.sleep(1)
                return all_actions

        return []
    

    
    def all_regions_reachable(self, region_action, state: NuruominoState):

        """Retorna uma lista de regiões que podem ser alcançadas a partir do estado passado como argumento."""
        graph = state.adj_graph

        visited = set()
        queue = deque([region_action]) # Começar com uma peça colocada no estado inicial
        while queue:

            current_region = queue.popleft()
            visited.add(current_region)

            for adj_region in graph[current_region]:
                    
                if len(graph[current_region][adj_region]) > 0 and adj_region not in visited:
                    queue.append(adj_region)

        #print("visited:", visited)

        if len(visited) != self.num_regions:
            #print("BAD PATH DETECTED!")
            return False
        
        return True

        # A ESTRUTURA DO GRAFO PODE NAO SER SUFICIENTE PARA DIZER SE AS REGIÕES SÃO ALCANÇÁVEIS
        # UMA REGIÃO ALCANÇA OUTRA ATRAVÉS DE UMA PEÇA,
        # MAS ESSA OUTRA REGIÃO PODE ALCANÇAR OUTRAS REGIÕES ATRAVÉS DE PEÇAS QUE NÃO ESTAM ADJACENTES À ANTERIOR

        # SE CALHAR DÁ, É PRECISO É PENSAR MELHOR NA LÓGICA E ENVOLVER AS PEÇAS USADAS PARA A ADJACENCIA NO ALGORITMO

    def num_connected_pieces(self, state: NuruominoState):
        
        """Retorna uma lista de regiões que podem ser alcançadas a partir do estado passado como argumento."""
        graph = state.adj_graph

        visited = set()
        queued_regions = set()
        queue = deque([next(iter(state.board.placed_pieces))[0]]) # Começar com uma peça colocada no estado inicial
        while queue:

            #print(queue)

            current_region = queue.popleft()
            visited.add(current_region)

            pieces = set()
            for adj_region in graph[current_region]:
                for p in graph[current_region][adj_region]:
                    pieces.add(p)

            #print("pieces", pieces)
            
            # UMA UNICA PEÇA -> região preenchida
            if len(pieces) == 1:
                for adj_region in graph[current_region]:
                    if len(graph[current_region][adj_region]) > 0 and adj_region not in visited and adj_region not in queued_regions:
                        #print("Adding Adjacent Region:", adj_region)
                        queue.append(adj_region)
                        queued_regions.add(adj_region)

        #print("Visited Regions:", visited)
        
        return len(visited)


    def print_state(state):
        print(f"State ID: {state.id}")
        print(f"Region Action: {state.region_action}")
        print(f"Bad Path: {state.bad_path}")
        print(f"Only Letter: {state.only_letter}")
        print(f"Action Region Size: {state.action_region_size}")
        print("Board Grid:")
        Board.print_instance(state.board.grid)
        print("Regions:")
        Board.print_regions(state.board.regions)
        print("Possible Pieces:")
        for region, pieces in state.board.possible_pieces.items():
            print(f"  Região {region}: {pieces}")
        print("Region Adjacent Regions:")
        for region, adjs in state.board.region_adj_regions.items():
            print(f"  Região {region}: {adjs}")
        print("Placed Pieces:")
        print(state.board.placed_pieces)
        print("Adjacency Graph:")
        Nuruomino.print_adjacency_graph(state.adj_graph)
        print("-" * 40)


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

        new_state.adj_graph = Nuruomino.copy_adjacency_graph(state.adj_graph)

        new_state.region_action = region
        new_state.action_region_size = len(state.board.regions[region])
        
        Board.place_piece(new_state.board.grid, piece, positions)
        new_state.board.placed_pieces.add((region, piece, tuple(positions)))
        new_state.board.regions.pop(region)
        
        Nuruomino.update_adjacency_graph_piece(new_state, region, piece, positions)

        if not fixed_positions(new_state, new_state.adj_graph[region].keys()):
            new_state.bad_path = True
            
        #elif not self.all_regions_reachable(new_state):
        #    new_state.bad_path = True
        

        #print("\n\n\n")
        #print("New State ID:", new_state.id)
        #Board.print_instance(new_state.board.grid)
        #state.board = board_copy
        return new_state
    
              
    def goal_test(self, state: NuruominoState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""

        #print("Checking goal test for state ID:", state.id)
        
        if len(state.board.placed_pieces) != self.num_regions:
            #print(len(state.board.placed_pieces))
            #print(self.num_regions)
            #print("Placed pieces nao corresponde ao numero de regioes!")
            return False

        if self.num_connected_pieces(state) == self.num_regions:
            self.board = state.board

            return True
        
        return False
    

    def h_bad_path(state: NuruominoState):
        if state.bad_path:
            return 1000
        return 1
    
    def get_dynamic_weights(state, node):
        #r = len(state.board.regions)
        return {
                'regions_left': 0.3, 
                'connections' : 0.3,
                'piece_adjs' : 0.3,
                'action_region_size': 0.1,
                'critical': 1.0,
                }   
    
    def h_priority_regions(region, state: NuruominoState):
        if region in state.priority_regions:
            return -10
        return 0

    def prioritize_small_regions(state: NuruominoState):
        """
        Calcula uma penalização com base no tamanho da região onde a ação foi tomada.
        Quanto menor a região, menor o valor retornado => melhor para a heurística.
        """
        region_size = len(state.board.regions[state.region_action])
        
        # Fórmula inversa ao tamanho da região: menor tamanho → menor custo
        # Evita divisão por zero
        return 1 / (region_size + 1)
    
    def get_piece_adjacencies(state, action):

        region, letter, positions = action

        graph = state.adj_graph

        adjs = 0

        for adj in graph[region]:
            if (letter, positions) in graph[region][adj]:
                adjs +=1

        for (i, j) in positions:
            for dx, dy in DELTAS:
                ni, nj = i + dx, j + dy
                neighbor = Board.get_value(state.board.grid, ni, nj)
                if neighbor != letter and neighbor != region:
                    adjs +=1


        return adjs


    def h(self, node: Node):
        #print("Node_ID and Action:", node.state.id, node.action)
        
        """Função heuristica utilizada para a procura A*."""

        #print("Number of Regions:", len(node.state.board.regions))

        if node.state.id == 0:
            return 1000
        
        # Quantidade de novas posições fixas descobertas (quanto mais melhor)
        #new_Ps = node.state.only_letter
        # Número de regiões por preencher (quanto menos melhor)
        # Quantidade de ações possíveis na região (quanto menos melhor)
        #num_actions = node.state.region_actions / self.region_sizes[node.state.region_action]
        # Tamanho médio das regiões adjacentes (quanto menos melhor)


        piece_adjs = Nuruomino.get_piece_adjacencies(node.state, node.action)
    

        connections = self.num_connected_pieces(node.state)

        # Penalização, caminho sem solução
        critical = Nuruomino.h_bad_path(node.state)
        
        regions_left = len(node.state.board.regions)

        action_region_size = node.state.action_region_size

        weights = Nuruomino.get_dynamic_weights(node.state, node)

        h = (
            weights['regions_left'] * regions_left -
            weights['connections'] * connections -
            #weights['action_region_size'] * action_region_size -
            weights['piece_adjs'] * piece_adjs +
            weights['critical'] * critical
            
        )
        #if h < 100:
            #print("Node ID:", node.state.id, "\nAction:", node.action, "\nconnections: ", connections, "\nregions_left: ", regions_left, "\nHeuristic Value:", h)
            #print()
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
    

    #Board.print_instance(problem.board.grid)    

    #Nuruomino.print_adjacency_graph(problem.initial.adj_graph)

    #goal_node = astar_search(problem)

    #goal_node = astar_search(problem)
    
    goal_node = depth_first_tree_search(problem)

    Board.print_instance(problem.board.grid)

    #Board.place_piece(problem.initial.board.grid, 'L', ((0,0), (0,1), (0,2), (1,0)))


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
    

