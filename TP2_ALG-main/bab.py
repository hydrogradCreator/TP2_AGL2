import time
import math
import sys

INFINITY = float('inf')
TIME_LIMIT = 30 * 60


class ExecutionTimeoutError(Exception):
    """Exceção personalizada para tempo de execução excedido."""
    pass

class TSPSolver:
    def __init__(self, num_cities):
        self.num_cities = num_cities
        self.best_path = [None] * (num_cities + 1)
        self.visited = [False] * num_cities
        self.best_cost = INFINITY

    def _update_best_path(self, path):
        self.best_path[:self.num_cities + 1] = path[:]
        self.best_path[self.num_cities] = path[0]

    def _find_minimal_edge(self, graph, city):
        return min((weight for neighbor, weight in enumerate(graph[city]) if neighbor != city), default=INFINITY)

    def _find_next_minimal_edge(self, graph, city):
        weights = sorted(weight for neighbor, weight in enumerate(graph[city]) if neighbor != city)
        return weights[1] if len(weights) > 1 else INFINITY

    def solve_tsp(self, graph):
        initial_bound = sum(self._find_minimal_edge(graph, city) + self._find_next_minimal_edge(graph, city) for city in range(self.num_cities))
        initial_bound = math.ceil(initial_bound / 2)

        current_path = [-1] * (self.num_cities + 1)
        current_path[0] = 0
        self.visited[0] = True

        path_stack = [(initial_bound, 0, 1, current_path[:], self.visited[:])]

        start_time = time.time()

        while path_stack:
            bound, path_weight, level, current_path, self.visited = path_stack.pop()

            if level == self.num_cities:
                last_to_first = graph[current_path[-2]][current_path[0]]
                if last_to_first:
                    total_cost = path_weight + last_to_first
                    if total_cost < self.best_cost:
                        self._update_best_path(current_path)
                        self.best_cost = total_cost
                continue

            for next_city in range(self.num_cities):

                if graph[current_path[level - 1]][next_city] and not self.visited[next_city]:
                    temp_bound, temp_weight = bound, path_weight

                    path_weight += graph[current_path[level - 1]][next_city]
                    bound -= (self._find_minimal_edge(graph, current_path[level - 1]) + self._find_minimal_edge(graph, next_city)) / 2 if level == 1 else (self._find_next_minimal_edge(graph, current_path[level - 1]) + self._find_minimal_edge(graph, next_city)) / 2

                    if bound + path_weight < self.best_cost:
                        path_stack.append((bound, path_weight, level + 1, current_path[:level] + [next_city] + current_path[level + 1:], self.visited[:]))
                        self.visited[next_city] = True

                    bound, path_weight = temp_bound, temp_weight
                    self.visited[next_city] = False

        return self.best_cost, self.best_path
