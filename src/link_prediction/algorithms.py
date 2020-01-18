# define link prediction algorithms

import networkx as nx
from random import shuffle
from src.link_prediction.link_algorithm import LinkAlgorithm
from itertools import islice


class LinkWithBetweenness(LinkAlgorithm):

    def __init__(self, graph: nx.Graph, communities: dict, k: int = 1000):

        self.k = k
        super().__init__(graph, communities)

    def prediction(self):

        highest_betweenness = dict()

        for community in self.communities:

            print("Getting betweenness for community {}".format(community))
            subgraph = nx.subgraph(self.graph, self.communities[community])
            highest_betweenness[community] = self.get_betweenness(subgraph)

        print("Betweenness done")

        highest_betweenness_left = highest_betweenness[0]
        highest_betweenness_right = highest_betweenness[1]
        possible_new_edges = self.get_highest_betweenness(self.graph, highest_betweenness_left, highest_betweenness_right)
        possible_new_edges = {k: v for k, v in sorted(possible_new_edges.items(), reverse=True)}
        edges_to_add = islice(possible_new_edges.values(), self.k) if self.k < len(possible_new_edges) else possible_new_edges
        print("Adding {} edges".format(self.k))

        for edge in edges_to_add:
            self.link_nodes(edge[0], edge[1])

    @staticmethod
    def get_betweenness(graph: nx.Graph):

        betweenness = nx.betweenness_centrality(graph, seed=10)
        sorted_betweenness = {k: v for k, v in sorted(betweenness.items(), key=lambda item: item[1], reverse=True)}
        return sorted_betweenness

    @staticmethod
    def get_highest_betweenness(graph: nx.Graph, highest_b_left: dict, highest_b_right: dict):

        print("Getting 'best' edges")
        non_connected_nodes = nx.non_edges(graph)
        non_connected_nodes = filter(lambda x:
                                     (x[0] in highest_b_right and x[1] in highest_b_left)
                                     or (x[0] in highest_b_left and x[1] in highest_b_right),
                                     non_connected_nodes
                                     )
        nodes_to_add = dict()
        for nodes in non_connected_nodes:

            betweenness_first_node = highest_b_left[nodes[0]] if nodes[0] in highest_b_left else highest_b_right[nodes[0]]
            betweenness_second_node = highest_b_left[nodes[1]] if nodes[1] in highest_b_left else highest_b_right[nodes[1]]
            betweenness_nodes = betweenness_first_node + betweenness_second_node
            nodes_to_add[betweenness_nodes] = nodes

        return nodes_to_add


class RandomLink(LinkAlgorithm):

    def __init__(self, graph: nx.Graph, communities: dict, k: int = 1000):

        self.k = k
        super().__init__(graph, communities)

    def prediction(self):

        left = self.communities[0]
        right = self.communities[1]
        non_connected_nodes = nx.non_edges(self.graph)
        non_connected_nodes = list(
            filter(lambda x:
                   (x[0] in right and x[1] in left)
                   or (x[0] in left and x[1] in right),
                   non_connected_nodes)
        )

        shuffle(non_connected_nodes)
        edges_to_add = islice(non_connected_nodes, self.k) if self.k < len(list(non_connected_nodes)) else non_connected_nodes
        print("Adding {} edges".format(self.k))

        for edge in edges_to_add:
            self.link_nodes(edge[0], edge[1])
