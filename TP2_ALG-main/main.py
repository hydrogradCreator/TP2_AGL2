import sys
import networkx as nx
import pandas as pd
import bab
import tat
import christofides
import time
import multiprocessing


from memory_profiler import memory_usage


OUTPUT = "saida_twice_around.txt"
OUTPUT1 = "saida_christofides.txt"
OUTPUT2 = "saida_bab.txt"


def datasets(arquivo_path):
    with open(arquivo_path, 'r') as arquivo:
        linhas = arquivo.readlines()
    return linhas

def wrapper_algoritmo_christofides(queue, G):
    result = christofides.christofides_algo(G)
    queue.put(result)


def calculate_total_distance(cycle, adjacency_matrix):
    total_distance = 0
    for i in range(len(cycle) - 1):
        total_distance += adjacency_matrix[cycle[i]][cycle[i+1]]
    return total_distance

def dataset(nome_dataset):
    def convert_to_int(valor):
        return int(float(valor))

    def calcular_distancia(pos_u, pos_v):
        return ((pos_u[0] - pos_v[0]) ** 2 + (pos_u[1] - pos_v[1]) ** 2) ** 0.5

    caminho_dataset = f'data/{nome_dataset}.tsp'
    coordenadas = {}
    grafo = []

    with open(caminho_dataset, 'r') as arquivo:
        coord_section = False

        for linha in arquivo:
            partes = linha.strip().split()

            if partes:
                if partes[0] == 'NODE_COORD_SECTION':
                    coord_section = True
                elif partes[0] == 'EOF':
                    coord_section = False
                elif coord_section:
                    no, x, y = map(convert_to_int, partes)
                    coordenadas[no] = (x, y)

    for u, pos_u in coordenadas.items():
        node_row = [0 if u == v else calcular_distancia(pos_u, pos_v) for v, pos_v in coordenadas.items()]
        grafo.append(node_row)

    return grafo


if len(sys.argv) < 2:
    print("Por favor, forneça o nome do algoritmo como argumento. Exemplo: python main.py christofides")
    sys.exit()

algoritmo_escolhido = sys.argv[1].lower()

def escreve_arquivo(label, caminho, mode):
    with open(caminho, mode) as arquivo:
        arquivo.write(f'{label}\n')


def execute_algoritmo(algoritmo_escolhido, tp_datasets):
    
    open(OUTPUT, 'w').close()
    open(OUTPUT1, 'w').close()

    for line in tp_datasets:
        nome_dataset = line.split('\t')[0]
        grafo_do_dataset = dataset(nome_dataset)
        adjacency_matrix = pd.DataFrame(grafo_do_dataset)

        if algoritmo_escolhido == 'branch_and_bound':
            print(f"Lendo: {nome_dataset}. Algoritmo: branch and bound...")
            bab_inst = bab.TSPSolver(len(grafo_do_dataset))

            start_time = time.time()  # Início da medição de tempo
            mem_before = memory_usage()[0]  # Início da medição de memória

            try:
                bab_inst.solve_tsp(grafo_do_dataset)

                end_time = time.time()  # Fim da medição de tempo
                mem_after = memory_usage()[0]  # Fim da medição de memória

                total_time = end_time - start_time  # Cálculo do tempo total
                total_memory = mem_after - mem_before  # Cálculo do uso total de memória
                total_distance = bab_inst.best_cost  # O custo total do ciclo
                escreve_arquivo(f"{nome_dataset}, Distance: {total_distance}, Time: {total_time} s, Memory: {total_memory} MB", OUTPUT1, 'a')

            except bab.ExecutionTimeoutError as err:
                escreve_arquivo(f"{nome_dataset}, NaN", OUTPUT1, 'a')


        elif algoritmo_escolhido == 'twice_around_the_tree':
            print(f"Lendo: {nome_dataset}. Algoritmo: twice-around-the-tree...")
            INITIAL_MEM = memory_usage()[0]
            G = nx.from_pandas_adjacency(adjacency_matrix)

            try:
                start_time = time.time()  # Início da medição de tempo
                mem_before = memory_usage()[0]  # Início da medição de memória

                hamiltonian_cycle = tat.approximate_tsp_path(G, 'weight')  # Execução do algoritmo

                total_distance = calculate_total_distance(hamiltonian_cycle, adjacency_matrix)  # Calcula a distância total do ciclo

                mem_after = memory_usage()[0]  # Fim da medição de memória
                end_time = time.time()  # Fim da medição de tempo

                total_time = end_time - start_time  # Cálculo do tempo total
                total_memory = mem_after - mem_before  # Cálculo do uso total de memória

                escreve_arquivo(f"{nome_dataset}, Distance: {total_distance}, Time: {total_time} s, Memoria inicial: {INITIAL_MEM}, Memory: {total_memory} MB", OUTPUT,'a')

            except tat.ExecutionTimeoutError as err:
                escreve_arquivo(f"{nome_dataset}, NaN", OUTPUT,'a')

        elif algoritmo_escolhido == 'christofides':
            print(f"Lendo: {nome_dataset}. Algoritmo: Christofides...")
            INITIAL_MEM = memory_usage()[0]

            G = nx.from_pandas_adjacency(adjacency_matrix)

            start_time = time.time()
            mem_before = memory_usage(proc=-1, interval=0.1, timeout=None)

            
            result_queue = multiprocessing.Queue()
            p = multiprocessing.Process(target=wrapper_algoritmo_christofides, args=(result_queue, G))
            p.start()
            p.join(30*60)

            end_time = time.time()
            mem_after = memory_usage(proc=-1, interval=0.1, timeout=None)

            total_time = end_time - start_time
            total_memory = mem_after[0] - mem_before[0]
            if p.is_alive():
                p.terminate()
                p.join()
            if not result_queue.empty():
                tour_result = result_queue.get()
                total_distance = calculate_total_distance(tour_result, grafo_do_dataset)
                escreve_arquivo(nome_dataset + " Distance: " + str(total_distance) + f", Time: {total_time} s, Memoria Inicial: {INITIAL_MEM} Memory: {total_memory} MB", OUTPUT1,'a')
            else:
                print("Max execution time reached.")
                escreve_arquivo(nome_dataset + f", Time: {total_time} s, Memoria inicial: {INITIAL_MEM}, Memory: {total_memory} MB", OUTPUT1,'a')

        else:
            print(f"Algoritmo '{algoritmo_escolhido}' não reconhecido.")



if __name__ == "__main__":
    tp_datasets = datasets('tp2_datasets.txt')
    tp_datasets.pop(0)

    if len(sys.argv) < 2:
        print("Por favor, forneça o nome do algoritmo como argumento. Exemplo: python main.py christofides")
        sys.exit()

    algoritmo_escolhido = sys.argv[1].lower()
    execute_algoritmo(algoritmo_escolhido, tp_datasets)