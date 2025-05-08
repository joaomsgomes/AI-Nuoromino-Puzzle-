# nuruomino.py: Template para implementação do projeto de Inteligência Artificial 2024/2025.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 23:
# 109512 João Gomes
# 110135 Manuel Semedo

from search import *
from sys import stdin
from collections import defaultdict

class NuruominoState:
    state_id = 0

    def __init__(self, board, regions):
        self.board = board
        self.regions = regions
        self.id = Nuruomino.state_id
        Nuruomino.state_id += 1

    def __lt__(self, other):
        """ Este método é utilizado em caso de empate na gestão da lista
        de abertos nas procuras informadas. """
        return self.id < other.id

class Board:
    """Representação interna de um tabuleiro do Puzzle Nuruomino."""

    def get_value(self, row:int, col:int):
        return self[row][col]
    
    def adjacent_regions(self, regions, region:int) -> list:
        """Devolve uma lista das regiões que fazem fronteira com a região enviada no argumento."""
        #TODO
        positions = regions[region]
        print(f"pos: {positions}")
        adj_regions = []

        for i, j in positions:
            adj_val = Board.adjacent_values(self, i, j)
            print(f"adj val on pos {i, j}: {adj_val}")
            
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

        size = len(board)

        adj_pos = []
        for dr, dc in deltas:
            r, c = row + dr, col + dc
            if 0 <= r < size and 0 <= c < size:
                adj_pos.append((r, c))

        return adj_pos
    
        pass

    def adjacent_values(self, row:int, col:int) -> list:
        """Devolve os valores das celulas adjacentes à região, em todas as direções, incluindo diagonais."""
        adj_val = []
        adj_pos = Board.adjacent_positions(self, row, col)
        for i,j in adj_pos:
            adj_val.append(Board.get_value(self, i, j))
        
        return adj_val
    
        #TODO
        pass
    
    
    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 pipe.py < test-01.txt

            > from sys import stdin
            > line = stdin.readline().split()
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

        return board, region_dict
    
        #TODO
        pass

    def print_instance(self):
        for row in self:
            print(" ".join(str(x) for x in row))

    # TODO: outros metodos da classe Board

class Nuruomino(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.board = board
        self.initial = NuruominoState(board)
        self.initial.state_id = 0 # ID do estado inicial

        #TODO
        pass 

    def actions(self, state: NuruominoState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
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
    board, regions = Board.parse_instance()
    Board.print_instance(board)
    # Exemplo de impressão das regiões
    for i, region in enumerate(regions):
        print(f"Região {i+1}: {region}")

    a = 1
    b = 2
    print("\nAdj_pos:")
    print(Board.adjacent_positions(board, a, b))
    print("\nAdj_values:")
    print(Board.adjacent_values(board, a, b))
    print("\nAdj_regions:")
    print(Board.adjacent_regions(board, regions, 5))