import osmnx
from osmnx.distance import *
import matplotlib.pyplot as plt


class Plotter:
    def __init__(self, graph):
        self.graph = graph
        plt.ion()
        self.fig, self.ax = osmnx.plot_graph(self.get_graph(), node_size=1)

    def plot_routes(self, routes):
        routes_list = self.get_route_list(routes)

        osmnx.plot_graph_routes(self.get_graph(), routes_list, route_colors='r', node_size=1, show=False, ax=self.ax)

    def update_plot(self, routes):
        self.plot_routes(routes)

    '''def add_position(self, position):
        pcs = self.position_color_size(position)
        osmnx.plot_graph(self.get_graph(), node_color=pcs['color'], node_size=pcs['size'])'''

    def position_color_size(self, position):
        if isinstance(position, list):
            actual_position = nearest_nodes(self.get_graph(), position[0], position[1])
        else:
            actual_position = position
        nc = []
        ns = []
        for el in self.get_graph().nodes:
            nc.append('g' if el == actual_position else 'w')
            ns.append(100 if el == actual_position else 1)
        return {'color': nc, 'size': ns}

    def set_graph(self, graph):
        self.graph = graph

    def get_graph(self):
        return self.graph

    def get_route_list(self, routes):
        routes_list = []
        for u, v in zip(routes, routes[1:]):
            routes_list.append(shortest_path(self.get_graph(), u, v))
        return routes_list
