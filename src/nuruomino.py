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
        self.only_letter = 0
        self.action_region_size = 0
        self.region_actions = 0

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
        
        deltas = [(-1, -1), (-1, 0), (-1, 1),
              ( 0, -1),          ( 0, 1),
              ( 1, -1), ( 1, 0), ( 1, 1)]

        adj_pos = []
        for dr, dc in deltas:
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
        
        board = self.clone()

        filtered_pieces = []

        for piece in possible_pieces:

            piece_type, positions = piece
            aux_board = board.clone()

            for i, j in positions:
                aux_board.grid[i][j] = 'P'

            # Checa adjacências com o aux_board.grid diretamente
            has_invalid_adj = any(
                piece_type in aux_board.adjacent_values(row, col)    #RECEBE BOARD????
                for row, col in positions
            )


            if has_invalid_adj:
                #Board.print_instance(aux_board.grid)
                #print("Invalid adjacency for piece:", piece_type, "at positions:", positions)
                continue

            Board.place_piece(aux_board.grid, piece_type, positions)
            
            forms_square = any(Board.is_square(aux_board.grid, row, col) for row, col in positions)
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

    def clone(self):   

        new_grid = [row[:] for row in self.grid]
        new_regions = {k: v[:] for k, v in self.regions.items()}
        new_possible_pieces = {k: v[:] for k, v in self.possible_pieces.items()}
        new_region_adj_regions = {k: v[:] for k, v in self.region_adj_regions.items()}
        new_placed_pieces = [ (piece, positions[:]) for piece, positions in self.placed_pieces ]
        b = Board(new_grid, new_regions)
        b.possible_pieces = new_possible_pieces
        b.region_adj_regions = new_region_adj_regions
        b.placed_pieces = new_placed_pieces
        b.num_regions = self.num_regions
        return b
        

    # TODO: outros metodos da classe Board


def fixed_positions(state: NuruominoState, adj_regions):
        #COLOCAR P's na grid
    queue = deque(adj_regions)
    queued_regions = set(adj_regions)

    #print("State:", state.id)
    
    while queue:
        #print("Queue:", queue)
        region = queue.popleft()
        queued_regions.remove(region)

        #print("Region:", region)
                    
        filtered_actions = state.board.filter_actions(state.board.possible_pieces[region])
        
        if len(filtered_actions) == 0:
            #print("No possible pieces for region", region)
            return False
        
        state.board.possible_pieces[region] = filtered_actions

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
            state.board.placed_pieces.append((fixed_letter, fixed_positions))
            state.board.regions.pop(region)
            state.board.possible_pieces.pop(region)

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
        
    return True

class Nuruomino(Problem):

    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.board = board
        self.initial = NuruominoState(board)
        self.initial.state_id = 0 # ID do estado inicial

        self.board.fill_tetromino_regions()
        board.set_possible_pieces()
        board.set_adjacent_regions()
        
        fixed_positions(self.initial, list(self.board.regions.keys())) #Estado inicial de qualquer no
        
        Board.print_instance(self.board.grid)
        #time.sleep(1)
        
        #TODO
        pass 

    def actions(self, state: NuruominoState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        all_actions = []
        for region in state.board.regions:

                pieces = state.board.possible_pieces[region]

                for piece, pos in pieces:
                    
                    all_actions.append((region, piece, pos))

        time.sleep(2)
        print("State ID:", state.id)
        Board.print_instance(state.board.grid)
        
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
        new_state.board.placed_pieces.append((piece, positions))

        new_state.action_region_size = len(state.board.regions[region])
        new_state.region_actions = len(state.board.possible_pieces[region])
        new_state.board.regions.pop(region)
        new_state.board.possible_pieces.pop(region)

        
        affected_regions = [r for r in new_state.board.region_adj_regions[region] if r in new_state.board.regions.keys()]

        if not fixed_positions(new_state, affected_regions):
            new_state.bad_path = True

        #print("\n\n\n")
        #print("New State ID:", new_state.id)
        #Board.print_instance(new_state.board.grid)

        return new_state
              
    def goal_test(self, state: NuruominoState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""

        if len(state.board.regions) > 0:
            return False
        
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
        
        self.board = state.board

        return True

    def h_state_connections(state: NuruominoState):

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

        if len(connections) == 0:
            return 0.5
        return len(connections)
    
    def h_bad_path(state: NuruominoState):
        if state.bad_path:
            return 1000
        return 1
    
    def h(self, node: Node):
        #print("Node_ID and Action:", node.state.id, node.action)

        """Função heuristica utilizada para a procura A*."""

        if node.state.id == 0:
            return 1000

        # Número de conexões entre peças (quanto mais melhor)
        connections = Nuruomino.h_state_connections(node.state)
        # Quantidade de novas posições fixas descobertas (quanto mais melhor)
        new_Ps = node.state.only_letter
        region_size = node.state.action_region_size
        # Número de regiões por preencher (quanto menos melhor)
        regions_left = len(node.state.board.regions)
        # Quantidade de ações possíveis na região (quanto menos melhor)
        num_actions = node.state.region_actions
        # Tamanho médio das regiões adjacentes (quanto menos melhor)
        #adj_regions = Nuruomino.h_adj_regions_priority(node.state)

        # Penalização, caminho sem solução
        critical = Nuruomino.h_bad_path(node.state)
        
        
        #depth_bonus = 1 / (node.depth*node.depth*node.depth + 1)  # Evitar que a profundidade penalize muito a heurística

        h = (
            1.0 * num_actions +
            2.0 * region_size +
            3.0 * regions_left -
            1.0 * new_Ps +

            1.0 * critical
        )

        h -= 0.0001 * node.depth

        if h < 100:
            print("Node_id:", node.state.id)
            print("Action:", node.action)
            print(f" H region size: {region_size} \n| Actions: {num_actions} \n| Regions left: {regions_left} \n| New Ps: {new_Ps} \n| Connections: {connections} \n| Critical: {critical}")
            print("F(n):", h)
            Board.print_instance(node.state.board.grid)
            print("\n")
        #print("\n")

        return h
        

if __name__ == "__main__":
    board = Board.parse_instance()
    problem = Nuruomino(board)
    
    
    #Board.print_instance(problem.board.grid)
    #Board.print_regions(problem.board)
    goal_node = astar_search(problem)
    #print("SOLUTION: ")
    Board.print_instance(problem.board.grid)


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
    

