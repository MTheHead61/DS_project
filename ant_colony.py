import numpy as np
import routes_calculator


def ant_col_alg(route_list, graph):
    # Define the graph as an adjacency matrix, where the rows and columns correspond to the nodes (stops)
    # and the entries correspond to the weights (distances) between the nodes
    # graph = np.array([[0, 10, 20, 15],
    #                  [10, 0, 25, 30],
    #                  [20, 25, 0, 35],
    #                  [15, 30, 35, 0]])

    calculator = routes_calculator.RoutesCalculator(graph)
    graph, nodes = calculator.generate_weight_matrix(route_list)

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
                next_node = select_next_node(route_list, current_node, ant_path, pheromone, graph, alpha,
                                             beta, epsilon)
                ant_path.append(next_node)
            # Add the starting node to complete the ant's path
            ant_path.append(0)
            # Calculate the distance traveled by the ant
            ant_distance = calculate_distance(ant_path, graph)
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
    best_path_dict = results[results["distance"].index(min(results["distance"]))]
    return [nodes[p] for p in best_path_dict["path"]], best_path_dict


# Define a function to select the next node to visit based on the pheromone levels and the heuristic information
def select_next_node(route_list, current_node, visited_nodes, pheromone, graph, alpha, beta, epsilon):
    unvisited_nodes = []
    nodes_dict = route_list.get_stop_list_as_dict()
    for k in nodes_dict.keys():
        if k in visited_nodes:
            continue
        if nodes_dict[k].is_withdrawal():
            unvisited_nodes.append(k)
        else:
            for i in visited_nodes:
                if nodes_dict[k].get_delivery_id() == nodes_dict[i].get_delivery_id():
                    unvisited_nodes.append(k)
    unvisited_nodes = np.array(unvisited_nodes)
    pheromone_values = pheromone[current_node, unvisited_nodes]
    heuristic_values = 1 / (graph[current_node, unvisited_nodes] + epsilon)
    probability_values = (pheromone_values ** alpha) * (heuristic_values ** beta)
    probability_values /= np.sum(probability_values)
    next_node = np.random.choice(unvisited_nodes, p=probability_values)
    return next_node


# Define a function to calculate the distance traveled by a given ant
def calculate_distance(ant_path, graph):
    distance = 0
    for i in range(len(ant_path) - 1):
        distance += graph[ant_path[i], ant_path[i + 1]]
    return distance
