# define link prediction algorithms

import networkx as nx
from collections import Counter
from enum import Enum, unique
from random import shuffle
from src.common.utility import print_element
from src.link_prediction.link_algorithm import LinkAlgorithm
from itertools import islice, chain


@unique
class TypeOfAlgorithm(Enum):

    JACCARD_COEFFICIENT = "JACCARD_COEFFICIENT"
    ADAMIC_ADAR = "ADAMIC_ADAR"
    RESOURCE_ALLOCATION = "RESOURCE_ALLOCATION"
    PREFERENTIAL_ATTACHMENT = "PREFERENTIAL_ATTACHMENT"


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
        possible_new_edges = self.get_highest_betweenness(self.graph,
                                                          highest_betweenness_left,
                                                          highest_betweenness_right)
        possible_new_edges = {k: v for k, v in sorted(possible_new_edges.items(), reverse=True)}

        if self.k < len(possible_new_edges):
            edges_to_add = islice(possible_new_edges.values(), self.k)
            number_edges = self.k
        else:
            edges_to_add = possible_new_edges
            number_edges = len(possible_new_edges)

        print("Adding {} edges".format(number_edges))

        for edge in edges_to_add:
            self.link_nodes(edge[0], edge[1])

    @staticmethod
    def get_betweenness(graph: nx.Graph):

        betweenness = dict(
            filter(
                lambda x: x[1] > 0,
                nx.betweenness_centrality(graph, normalized=True, seed=10).items()
            )
        )
        sorted_betweenness = {k: v for k, v in sorted(betweenness.items(), key=lambda item: item[1], reverse=True)}
        return sorted_betweenness

    @staticmethod
    def get_highest_betweenness(graph: nx.Graph, highest_b_left: dict, highest_b_right: dict):

        print("Getting 'best' edges")
        non_connected_nodes = nx.non_edges(graph)
        non_connected_nodes = list(
            filter(
                lambda x:
                (x[0] in highest_b_right and x[1] in highest_b_left)
                or (x[0] in highest_b_left and x[1] in highest_b_right),
                non_connected_nodes
            )
        )

        frequency_nodes = Counter(chain.from_iterable(non_connected_nodes))
        edges_to_add = dict()

        for nodes in non_connected_nodes:

            betweenness_first_node = highest_b_left[nodes[0]] if nodes[0] in highest_b_left else highest_b_right[nodes[0]]
            # frequency_first_node = math.log(frequency_nodes[nodes[0]]) if frequency_nodes[nodes[0]] > 1 else 1
            frequency_first_node = frequency_nodes[nodes[0]]
            betweenness_second_node = highest_b_left[nodes[1]] if nodes[1] in highest_b_left else highest_b_right[nodes[1]]
            # frequency_second_node = math.log(frequency_nodes[nodes[1]]) if frequency_nodes[nodes[1]] > 1 else 1
            frequency_second_node = frequency_nodes[nodes[1]]
            betweenness_nodes = (betweenness_first_node/frequency_first_node) + \
                                (betweenness_second_node/frequency_second_node)
            edges_to_add[betweenness_nodes] = nodes
            # TODO log(betweenness_nodes)
            # TODO set limit on

        return edges_to_add


class StateOfArtAlgorithm(LinkAlgorithm):

    algorithms = [TypeOfAlgorithm.JACCARD_COEFFICIENT.value,
                  TypeOfAlgorithm.ADAMIC_ADAR.value,
                  TypeOfAlgorithm.RESOURCE_ALLOCATION.value,
                  TypeOfAlgorithm.PREFERENTIAL_ATTACHMENT.value]

    def __init__(self, graph: nx.Graph, communities: dict, algorithm: str, k: int = 1000):

        if algorithm.upper() not in self.algorithms:
            print("The available partition algorithms are:")
            print_element(self.algorithms)
            raise ValueError("algorithm not valid")
        self.algorithm = algorithm
        self.k = k
        super().__init__(graph, communities)

    def prediction(self):

        left = self.communities[0]
        right = self.communities[1]
        non_connected_nodes = list(nx.non_edges(self.graph))
        non_connected_nodes = list(
            filter(
                lambda x:
                (x[0] in right and x[1] in left)
                or (x[0] in left and x[1] in right),
                non_connected_nodes
            )
        )

        algorithm = None
        print("Adding edges using {}".format(self.algorithm.lower()))
        if self.algorithm.upper() == TypeOfAlgorithm.ADAMIC_ADAR.value:
            algorithm = nx.adamic_adar_index
        elif self.algorithm == TypeOfAlgorithm.JACCARD_COEFFICIENT.value:
            algorithm = nx.jaccard_coefficient
        elif self.algorithm == TypeOfAlgorithm.RESOURCE_ALLOCATION.value:
            algorithm = nx.resource_allocation_index
        elif self.algorithm == TypeOfAlgorithm.PREFERENTIAL_ATTACHMENT.value:
            algorithm = nx.preferential_attachment

        edges_to_add = list(
            sorted(
                algorithm(self.graph, non_connected_nodes),
                key=lambda element: element[2],
                reverse=True)
        )

        if self.k < len(edges_to_add):
            edges_to_add = islice(edges_to_add, self.k)
            number_edges = self.k
        else:
            edges_to_add = edges_to_add
            number_edges = len(edges_to_add)

        print("Adding {} edges".format(number_edges))

        for edge in edges_to_add:
            self.link_nodes(edge[0], edge[1])


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
        edges_to_add = islice(non_connected_nodes, self.k) if self.k < len(non_connected_nodes) else non_connected_nodes
        print("Adding {} edges".format(self.k))

        for edge in edges_to_add:
            self.link_nodes(edge[0], edge[1])
