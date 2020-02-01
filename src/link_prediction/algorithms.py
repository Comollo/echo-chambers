# define link prediction algorithms
import math
from typing import List

import networkx as nx
from collections import Counter
from enum import Enum, unique
from random import shuffle
from src.common.utility import print_element
from src.link_prediction.link_algorithm import LinkAlgorithm
from itertools import islice, chain
from collections.abc import Iterable


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
        non_connected_nodes = nx.non_edges(self.graph)
        non_connected_nodes = list(
            filter(
                lambda x:
                (x[0] in highest_betweenness_right and x[1] in highest_betweenness_left)
                or (x[0] in highest_betweenness_left and x[1] in highest_betweenness_right),
                non_connected_nodes
            )
        )
        possible_new_edges = self.get_highest_betweenness(
            non_connected_nodes,
            highest_betweenness_left,
            highest_betweenness_right
        )
        possible_new_edges = {k: v for k, v in sorted(possible_new_edges.items(), key=lambda item: item[1], reverse=True)}

        if self.k < len(possible_new_edges):
            edges_to_add = islice(possible_new_edges.keys(), self.k)
            number_edges = self.k
        else:
            edges_to_add = possible_new_edges.keys()
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
    def get_highest_betweenness(non_connected_nodes: Iterable, highest_b_left: dict, highest_b_right: dict):

        print("Getting 'best' edges")

        frequency_nodes = Counter(chain.from_iterable(non_connected_nodes))
        edges_to_add = dict()

        for node_pairs in non_connected_nodes:

            betweenness_first_node = \
                highest_b_left[node_pairs[0]] if node_pairs[0] in highest_b_left else highest_b_right[node_pairs[0]]
            frequency_first_node = math.log(frequency_nodes[node_pairs[0]]) if frequency_nodes[node_pairs[0]] else 1
            # frequency_first_node = frequency_nodes[node_pairs[0]]
            betweenness_second_node = \
                highest_b_left[node_pairs[1]] if node_pairs[1] in highest_b_left else highest_b_right[node_pairs[1]]
            frequency_second_node = math.log(frequency_nodes[node_pairs[1]]) if frequency_nodes[node_pairs[1]] else 1
            # frequency_second_node = frequency_nodes[node_pairs[1]]
            betweenness_nodes = (betweenness_first_node / frequency_first_node) +\
                                (betweenness_second_node / frequency_second_node)
            edges_to_add[node_pairs] = betweenness_nodes
            # TODO log(betweenness_nodes)

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


class HybridLinkPrediction(LinkWithBetweenness, StateOfArtAlgorithm):

    def __init__(self, graph: nx.Graph, communities: dict, algorithm: str, k: int = 1000):

        StateOfArtAlgorithm.__init__(self, graph=graph, communities=communities, algorithm=algorithm, k=k)

    def prediction(self):

        highest_betweenness = dict()

        for community in self.communities:

            print("Getting betweenness for community {}".format(community))
            subgraph = nx.subgraph(self.graph, self.communities[community])
            highest_betweenness[community] = self.get_betweenness(subgraph)

        print("Betweenness done")

        highest_betweenness_left = highest_betweenness[0]
        highest_betweenness_right = highest_betweenness[1]
        non_connected_nodes = nx.non_edges(self.graph)
        non_connected_nodes = list(
            filter(
                lambda x:
                (x[0] in highest_betweenness_right and x[1] in highest_betweenness_left)
                or (x[0] in highest_betweenness_left and x[1] in highest_betweenness_right),
                non_connected_nodes
            )
        )
        ranked_betweenness_nodes = self.get_highest_betweenness(
            non_connected_nodes,
            highest_betweenness_left,
            highest_betweenness_right
        )

        algorithm = None
        print("Combining betweenness with {}".format(self.algorithm.lower()))
        if self.algorithm.upper() == TypeOfAlgorithm.ADAMIC_ADAR.value:
            algorithm = nx.adamic_adar_index
        elif self.algorithm == TypeOfAlgorithm.JACCARD_COEFFICIENT.value:
            algorithm = nx.jaccard_coefficient
        elif self.algorithm == TypeOfAlgorithm.RESOURCE_ALLOCATION.value:
            algorithm = nx.resource_allocation_index
        elif self.algorithm == TypeOfAlgorithm.PREFERENTIAL_ATTACHMENT.value:
            algorithm = nx.preferential_attachment

        ranked_similarity_nodes = list(
            sorted(
                algorithm(self.graph, non_connected_nodes),
                key=lambda element: element[2],
                reverse=True)
        )

        scores = self.combine_scores(ranked_betweenness_nodes, ranked_similarity_nodes)
        scores = {k: v for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)}

        if self.k < len(scores):
            edges_to_add = islice(scores.keys(), self.k)
            number_edges = self.k
        else:
            edges_to_add = scores.keys()
            number_edges = len(scores)

        print("Adding {} edges".format(number_edges))

        for edge in edges_to_add:
            self.link_nodes(edge[0], edge[1])

    @staticmethod
    def combine_scores(ranked_betweenness: dict, ranked_similarity: List[tuple]):

        scores = dict()
        for nodes in ranked_similarity:

            node_pairs = nodes[:2]
            score = nodes[2]
            betweenness = ranked_betweenness[node_pairs]
            scores[node_pairs] = score * betweenness

        return scores


class LinkWithEffectiveSize(LinkAlgorithm):

    def __init__(self, graph:  nx.Graph(), communities: dict, k: int = 1000):

        self.k = k
        super().__init__(graph, communities)

    def prediction(self):

        effective_size = dict()

        for community in self.communities:

            print("Getting effective size for community {}".format(community))
            subgraph = nx.subgraph(self.graph, self.communities[community])
            effective_size[community] = self.get_effective_size(subgraph)

        print("Effective size done")

        effective_size_left = effective_size[0]
        effective_size_right = effective_size[1]
        non_connected_nodes = nx.non_edges(self.graph)
        non_connected_nodes = list(
            filter(
                lambda x:
                (x[0] in effective_size_right and x[1] in effective_size_left)
                or (x[0] in effective_size_left and x[1] in effective_size_right),
                non_connected_nodes
            )
        )
        possible_new_edges = self.get_highest_effective_size(
            non_connected_nodes,
            effective_size_left,
            effective_size_right
        )
        possible_new_edges = {k: v for k, v in sorted(possible_new_edges.items(), key=lambda item: item[1], reverse=True)}

        if self.k < len(possible_new_edges):
            edges_to_add = islice(possible_new_edges.keys(), self.k)
            number_edges = self.k
        else:
            edges_to_add = possible_new_edges.keys()
            number_edges = len(possible_new_edges)

        print("Adding {} edges".format(number_edges))

        for edge in edges_to_add:
            self.link_nodes(edge[0], edge[1])

    @staticmethod
    def get_effective_size(graph: nx.Graph()):
        effective_size = dict(
            filter(
                lambda x: x[1] > 0,
                nx.effective_size(graph).items()
            )
        )
        effective_size = {k: v for k, v in sorted(effective_size.items(), key=lambda item: item[1], reverse=True)}
        return effective_size

    @staticmethod
    def get_highest_effective_size(non_connected_nodes: Iterable, effective_size_left: dict, effective_size_right: dict):

        print("Getting 'best' edges")

        edges_to_add = dict()

        for node_pairs in non_connected_nodes:

            effective_size_first_node = \
                effective_size_left[node_pairs[0]] if node_pairs[0] in effective_size_left else effective_size_right[node_pairs[0]]
            effective_size_second_node = \
                effective_size_left[node_pairs[1]] if node_pairs[1] in effective_size_left else effective_size_right[node_pairs[1]]
            betweenness_nodes = effective_size_first_node + effective_size_second_node
            edges_to_add[node_pairs] = betweenness_nodes

        return edges_to_add
        # TODO use efficiency instead of effective size


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
