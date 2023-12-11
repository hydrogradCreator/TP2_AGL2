import networkx as nx

def criar_agm(grafo):
    mst = nx.minimum_spanning_tree(grafo)
    return mst

def emparelhamento_otimizado(grafo, vertices_impares):
    subgraph = grafo.subgraph(vertices_impares)
    matching = nx.max_weight_matching(subgraph, maxcardinality=True)
    return matching

def gerar_circuito_euleriano(grafo):
    circuito = list(nx.eulerian_circuit(grafo))
    return circuito

def achar_vertices_impares(mst):
    impares = [v for v, d in mst.degree() if d % 2 == 1]
    return impares


def christofides_algo(grafo):

    mst = criar_agm(grafo)
    impares = achar_vertices_impares(mst)

    matching = emparelhamento_otimizado(grafo, impares)

    multigrafo = nx.MultiGraph()
    multigrafo.add_edges_from(mst.edges())
    multigrafo.add_edges_from(matching)

    euler_circuito = gerar_circuito_euleriano(multigrafo)

    trajeto = []
    visitados = set()
    for aresta in euler_circuito:
        if aresta[0] not in visitados:
            trajeto.append(aresta[0])
            visitados.add(aresta[0])

    trajeto.append(euler_circuito[-1][1])

    return trajeto
