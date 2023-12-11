import time
import networkx as nx

# Definindo o limite de tempo para a execução
TIME_LIMIT = 30 * 60

class ExecutionTimeoutError(Exception):
    """ para tempo de execução excedido."""
    pass

def approximate_tsp_path(graph_instance, weight_attribute):
    """Aproxima um caminho do problema do caixeiro viajante em um grafo.

    Args:
        graph_instance (networkx.Graph): Uma instância de grafo do NetworkX.
        weight_attribute (str): O atributo de peso usado no grafo.

    Returns:
        list: Uma lista de vértices representando o ciclo Hamiltoniano aproximado.
    """
    start_time = time.time()

    root_vertex = list(graph_instance.nodes)[0]

    mst = nx.minimum_spanning_tree(graph_instance, algorithm='prim', weight=weight_attribute)

    hamiltonian_cycle = preorder_walk(mst, root_vertex, start_time)

    return hamiltonian_cycle

def preorder_walk(tree, start_vertex, exec_start_time):
    """Realiza uma caminhada em pré-ordem na árvore.

    Args:
        tree (networkx.Graph): Uma árvore geradora mínima.
        start_vertex (node): O vértice inicial da caminhada.
        exec_start_time (float): O tempo de início da execução.

    Returns:
        list: Uma lista de vértices visitados durante a caminhada.
    """
    def depth_first_search(vertex, visited, start_time):
        visited.append(vertex)
        for neighbor in tree.neighbors(vertex):
            if neighbor not in visited:
                depth_first_search(neighbor, visited, start_time)

        return visited

    visited_vertices = depth_first_search(start_vertex, [], exec_start_time)

    return visited_vertices
