import osmnx
from osmnx.distance import *
import numpy as np
import truck


class RoutesCalculator:
    def __init__(self, t: truck.Truck, string_graph_place="Messina, Italy"):
        self.graph = osmnx.graph_from_place(string_graph_place, network_type="drive", simplify=False)
        self.graph = add_edge_lengths(self.graph)
        self.k = 5
        self.truck = t

    def set_graph(self, graph):
        self.graph = graph

    def get_graph(self):
        return self.graph

    def set_k(self, k):
        self.k = k

    def get_k(self):
        return self.k

    def coord_to_nodes(self, stop_list):
        lats = []
        longs = []
        for s in stop_list:
            lats.append(s.get_latitude())
            longs.append(s.get_longitude())
        return nearest_nodes(self.get_graph(), lats, longs)

    #    def two_points_k_shortest_path(self, stop1, stop2):
    #        nodes = self.coord_to_nodes([stop1, stop2])
    #        return k_shortest_paths(self.get_graph(), nodes[0], nodes[1], self.get_k())

    #    def two_points_shortest_path(self, stop1, stop2):
    #        nodes = self.coord_to_nodes([stop1, stop2])
    #        return shortest_path(self.get_graph(), nodes[0], nodes[1])

    def generate_weight_matrix(self, route_list):
        nodes = self.coord_to_nodes(route_list.get_stop_list())
        length_matrix = np.zeros((len(nodes), len(nodes)))
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i != j:
                    el = (shortest_path(self.get_graph(), nodes[i], nodes[j]))
                    for u, v in zip(el, el[1:]):
                        length_matrix[i][j] += self.get_graph().edges[u, v, 0]['length']
        return length_matrix, nodes

    def shortest_deviation(self, route_list, new_job, path):
        route_list.append_from_job(new_job)
        l_m, nodes = self.generate_weight_matrix(route_list)

        new_path_weight = path["distance"]
        new_path = path["path"]

        # First of all we find the shortest deviation for the withdrawal, the delivery will be a bit more complex

        shortest_deviation = min(l_m[:-2, -2])  # Lowest weight of last column (distances to deviation)
        shortest_deviation_index = list(l_m[:-2, -2]).index(shortest_deviation)  # Index of the node with lowest
        # deviation weight
        deviation_comeback_index = path["path"][path["path"].index(shortest_deviation_index) + 1]  # Index of
        # the node next to the node with the lowest deviation weight in path
        deviation_comeback = l_m[-2, deviation_comeback_index]  # Weight of the comeback from the deviation to the
        # next node from the original path
        new_path_weight += (deviation_comeback + shortest_deviation)
        new_path_weight -= l_m[shortest_deviation_index, deviation_comeback_index]
        new_path.insert(path["path"].index(shortest_deviation_index) + 1, len(l_m) - 2)

        # The delivery stop will need us to ignore the paths coming from stops that will happen before the withdrawal

        truncated_path = new_path[path["path"].index(shortest_deviation_index)+1:-1]
        mask = [True if el in truncated_path else False for el in np.arange(len(path["path"]) - 1)]
        shortest_deviation = min(l_m[:-1, -1][mask])
        shortest_deviation_index = list(l_m[:-1, -1]).index(shortest_deviation)
        deviation_comeback_index = path["path"][path["path"].index(shortest_deviation_index) + 1]
        deviation_comeback = l_m[-1, deviation_comeback_index]
        new_path_weight += (deviation_comeback + shortest_deviation)
        new_path_weight -= l_m[shortest_deviation_index, deviation_comeback_index]
        new_path.insert(path["path"].index(shortest_deviation_index) + 1, len(l_m) - 1)

        return {"path": new_path, "distance": new_path_weight}

    def ant_col_alg(self):
        route_list = self.truck.get_route_list()

        graph, nodes = self.generate_weight_matrix(route_list)

        # Define the number of ants, iterations, and pheromone parameters
        num_ants = 10
        num_iterations = 50
        alpha = 1  # exponent on pheromone, higher alpha gives pheromone more weight (default=1)
        beta = 2  # exponent on distance, higher beta give distance more weight (default=2)
        rho = 0.5  # Rate at which pheromone decays. The pheromone value is multiplied by 1-rho, so 0 will not change
        # the pheromone level
        epsilon = 1e-10  # We add epsilon to the distances between nodes when we calculate their inverse, so we avoid
        # divisions by zero

        # Initialize the pheromone levels on the edges of the graph
        pheromone = np.ones_like(graph) * 0.1

        # Define the main algorithm loop
        results = {"path": [], "distance": []}
        for i in range(num_iterations):
            # Initialize the paths and distances of the ants
            ant_paths = []
            ant_distances = []
            for j in range(num_ants):
                # Initialize the ant's path with the starting node (node 0)
                ant_path = [0]
                # Traverse the graph by selecting the next node to visit based
                # on the pheromone levels and the heuristic information
                while len(ant_path) < len(graph):
                    current_node = ant_path[-1]
                    next_node = self.select_next_node(route_list, current_node, ant_path, pheromone, graph, alpha,
                                                      beta, epsilon)
                    ant_path.append(next_node)
                # Add the starting node to complete the ant's path
                ant_path.append(0)
                # Calculate the distance traveled by the ant
                ant_distance = self.calculate_distance(ant_path, graph)
                # Add the ant's path and distance to the lists
                ant_paths.append(ant_path)
                ant_distances.append(ant_distance)
            # Update the pheromone levels on the edges of the graph
            pheromone *= (1 - rho)
            for j in range(num_ants):
                for k in range(len(ant_paths[j]) - 1):
                    current_node = ant_paths[j][k]
                    next_node = ant_paths[j][k + 1]
                    pheromone[current_node, next_node] += 1 / ant_distances[j]
            # Find the ant that obtained the best solution and print its path and distance
            best_ant_index = np.argmin(ant_distances)
            best_ant_path = ant_paths[best_ant_index]
            best_ant_distance = ant_distances[best_ant_index]
            results["path"].append(best_ant_path)
            results["distance"].append(best_ant_distance)
            print(f"Iteration {i}: Best distance = {best_ant_distance}, Best path = {best_ant_path}")
        best_path = results["path"][results["distance"].index(min(results["distance"]))]
        self.truck.set_node_route([nodes[p] for p in best_path])
        self.truck.set_path({"path": best_path, "distance": min(results["distance"])})
        # self.truck.set_actual_position(self.truck.get_node_route()[0])

    # Define a function to select the next node to visit based on the pheromone levels and the heuristic information
    def select_next_node(self, route_list, current_node, visited_nodes, pheromone, graph, alpha, beta, epsilon):
        unvisited_nodes = []
        priorities = []
        nodes_dict = route_list.get_stop_list_as_dict()
        for k in nodes_dict.keys():
            if k in visited_nodes:
                continue
            if nodes_dict[k].is_withdrawal():
                unvisited_nodes.append(k)
                priorities.append(nodes_dict[k].get_priority())
            else:
                for i in visited_nodes:
                    if nodes_dict[k].get_delivery_id() == nodes_dict[i].get_delivery_id():
                        unvisited_nodes.append(k)
                        priorities.append(nodes_dict[k].get_priority())
        unvisited_nodes = np.array(unvisited_nodes)
        pheromone_values = pheromone[current_node, unvisited_nodes]
        heuristic_values = 1 / (graph[current_node, unvisited_nodes] + epsilon)
        heuristic_values *= priorities
        probability_values = (pheromone_values ** alpha) * (heuristic_values ** beta)
        probability_values /= np.sum(probability_values)
        next_node = np.random.choice(unvisited_nodes, p=probability_values)
        return next_node

    # Define a function to calculate the distance traveled by a given ant
    def calculate_distance(self, ant_path, graph):
        distance = 0
        for i in range(len(ant_path) - 1):
            distance += graph[ant_path[i], ant_path[i + 1]]
        return distance
