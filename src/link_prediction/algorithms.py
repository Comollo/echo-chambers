# define link prediction algorithms

import networkx as nx

from src.common.utility import lists_to_dict
from src.link_prediction.link_algorithm import LinkAlgorithm


class LinkWithBetweenness(LinkAlgorithm):

    def __init__(self, graph: nx.Graph, communities: dict, k: int = 10):

        self.k = k
        super().__init__(graph, communities)

    def prediction(self):

        # left = list(self.communities[0])
        # left_values = [1] * len(left)
        # dict_left = lists_to_dict(left, left_values)
        #
        # right = list(self.communities[1])
        # right_values = [1] * len(right)
        # dict_right = lists_to_dict(right, right_values)

        highest_betweenness = dict()

        for community in self.communities:

            print("Getting betweenness for community {}".format(community))
            subgraph = nx.subgraph(self.graph, self.communities[community])
            highest_betweenness[community] = self.get_betweenness(subgraph)

        print("Betweenness done")

        # k_highest_nodes = list(betweenness.keys())[:self.k]

        # highest_left = dict()
        # highest_right = dict()
        #
        # for node in k_highest_nodes:
        #     if node in dict_left:
        #         highest_left[node] = betweenness[node]
        #
        #     elif node in dict_right:
        #         highest_right[node] = betweenness[node]

        # print("Number of left nodes with highest betweenness: {}".format(len(highest_left)))
        # print("Number of right nodes with highest betweenness: {}".format(len(highest_right)))
        highest_b_left = highest_betweenness[0].keys()
        highest_b_right = highest_betweenness[1].keys()

        left_node = next(iter(highest_b_left))
        right_node = next(iter(highest_b_right))
        graph = self.link_nodes(self.graph, left_node, right_node)

        return graph

    @staticmethod
    def get_betweenness(graph: nx.Graph):

        betweenness = nx.betweenness_centrality(graph, seed=10)
        sorted_betweenness = {k: v for k, v in sorted(betweenness.items(), key=lambda item: item[1], reverse=True)}
        return sorted_betweenness

    @staticmethod
    def link_nodes(graph: nx.Graph, u, v):

        if graph.has_edge(u, v):
            raise Exception("Cannot create connection: the edge is already present")
            # Todo implement alternative
        else:
            graph.add_edge(u, v)
            print("Edge between {} and {} added".format(u,v))

        print("Edge added")
        return graph
