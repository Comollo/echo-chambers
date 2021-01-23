# define link prediction algorithms
from collections import Counter
from collections.abc import Iterable
from enum import Enum, unique
from typing import List

import networkx as nx
from itertools import islice, chain

from common.utility import print_element
from common.utility import write_dict_to_json
from link_prediction.link_algorithm import LinkAlgorithm


@unique
class TypeOfAlgorithm(Enum):
    JACCARD_COEFFICIENT = "JACCARD_COEFFICIENT"
    ADAMIC_ADAR = "ADAMIC_ADAR"
    RESOURCE_ALLOCATION = "RESOURCE_ALLOCATION"
    PREFERENTIAL_ATTACHMENT = "PREFERENTIAL_ATTACHMENT"


class LinkWithBetweenness(LinkAlgorithm):

    def __init__(self,
                 graph: nx.Graph,
                 communities: dict,
                 filename: str,
                 given_betweenness_value: dict = None,
                 k: float = 0.005):

        self.k = k
        filename = filename + '_betweenness'
        super().__init__(graph, communities, values=given_betweenness_value, filename=filename)

    def prediction(self):

        highest_betweenness = dict()

        if not self.values:
            for community in self.communities:
                print("Getting betweenness for community {}".format(community))
                subgraph = nx.subgraph(self.graph, self.communities[community])
                highest_betweenness[community] = self.__get_betweenness(subgraph)

            print("Betweenness done")
            write_dict_to_json(highest_betweenness, self.filename, "../betweenness/")
            print("Betweenness values written")
        else:
            print("Betweenness provided")
            highest_betweenness = self.values

        highest_betweenness_left = highest_betweenness["0"]
        highest_betweenness_right = highest_betweenness["1"]
        non_connected_nodes = list(nx.non_edges(self.graph))
        n_possible_new_connections = len(non_connected_nodes)
        non_connected_nodes = list(
            filter(
                lambda x:
                (x[0] in highest_betweenness_right and x[1] in highest_betweenness_left)
                or (x[0] in highest_betweenness_left and x[1] in highest_betweenness_right),
                non_connected_nodes
            )
        )
        possible_new_edges = self.__get_highest_betweenness(
            non_connected_nodes,
            highest_betweenness_left,
            highest_betweenness_right
        )
        possible_new_edges = {k: v for k, v in
                              sorted(possible_new_edges.items(), key=lambda item: item[1], reverse=True)}

        max_links = len(possible_new_edges)
        number_edges = round(self.k * self.n_edges)
        all_possible_new_edges = possible_new_edges.keys()
        if number_edges < max_links:
            edges_to_add = islice(all_possible_new_edges, number_edges)
        else:
            edges_to_add = all_possible_new_edges

        self.percentage_edges_added = self.k
        print("% of edges added: {}".format(self.percentage_edges_added))
        print("Adding {} edges".format(number_edges))

        for edge in edges_to_add:
            self.link_nodes(edge[0], edge[1])

    @staticmethod
    def __get_betweenness(graph: nx.Graph):

        betweenness = dict(
            filter(
                lambda x: x[1] > 0,
                nx.betweenness_centrality(graph, normalized=True, seed=10).items()
            )
        )
        # betweenness = nx.betweenness_centrality(graph, normalized=True, seed=10)
        sorted_betweenness = {k: v for k, v in sorted(betweenness.items(), key=lambda item: item[1], reverse=True)}
        return sorted_betweenness

    @staticmethod
    def __get_highest_betweenness(non_connected_nodes: Iterable, highest_b_left: dict, highest_b_right: dict):

        print("Getting 'best' edges")

        frequency_nodes = Counter(chain.from_iterable(non_connected_nodes))
        edges_to_add = dict()

        for node_pairs in non_connected_nodes:
            betweenness_first_node = \
                highest_b_left[node_pairs[0]] if node_pairs[0] in highest_b_left else highest_b_right[node_pairs[0]]
            # frequency_first_node = \
            #     math.log(frequency_nodes[node_pairs[0]]) if frequency_nodes[node_pairs[0]] > 1 else 1
            # frequency_first_node = frequency_nodes[node_pairs[0]]
            betweenness_second_node = \
                highest_b_left[node_pairs[1]] if node_pairs[1] in highest_b_left else highest_b_right[node_pairs[1]]
            # frequency_second_node = \
            #     math.log(frequency_nodes[node_pairs[1]]) if frequency_nodes[node_pairs[1]] > 1 else 1
            # frequency_second_node = frequency_nodes[node_pairs[1]]
            # betweenness_nodes = (betweenness_first_node / frequency_first_node) +\
            #                     (betweenness_second_node / frequency_second_node)
            betweenness_nodes = betweenness_first_node + betweenness_second_node
            edges_to_add[node_pairs] = betweenness_nodes

        return edges_to_add


class StateOfArtAlgorithm(LinkAlgorithm):
    algorithms = [TypeOfAlgorithm.JACCARD_COEFFICIENT.value,
                  TypeOfAlgorithm.ADAMIC_ADAR.value,
                  TypeOfAlgorithm.RESOURCE_ALLOCATION.value,
                  TypeOfAlgorithm.PREFERENTIAL_ATTACHMENT.value]

    def __init__(self,
                 graph: nx.Graph,
                 communities: dict,
                 algorithm: str,
                 filename: str,
                 given_values: dict = None,
                 k: float = 0.005):

        filename = filename + f"_{algorithm.lower()}"
        algorithm = algorithm.upper()
        if algorithm not in self.algorithms:
            print("The available partition algorithms are:")
            print_element(self.algorithms)
            raise ValueError("algorithm not valid")
        self.algorithm = algorithm
        self.k = k
        super().__init__(graph, communities, given_values, filename)

    def prediction(self):

        if not self.values:
            left = self.communities["0"]
            right = self.communities["1"]
            non_connected_nodes = list(nx.non_edges(self.graph))
            n_possible_new_connections = len(non_connected_nodes)
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
            if self.algorithm == TypeOfAlgorithm.ADAMIC_ADAR.value:
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

            write_dict_to_json({"value": edges_to_add}, self.filename, f"../{self.algorithm.lower()}/")
            print(f"{self.algorithm} values written")
        else:
            print(f"{self.algorithm.lower()} provided")
            edges_to_add = list(self.values.values())[0]

        max_links = len(edges_to_add)
        number_edges = round(self.k * self.n_edges)
        all_possible_new_edges = edges_to_add
        if number_edges < max_links:
            edges_to_add = islice(all_possible_new_edges, number_edges)
        else:
            edges_to_add = all_possible_new_edges

        self.percentage_edges_added = self.k
        print("% of edges added: {}".format(self.percentage_edges_added))
        print("Adding {} edges".format(number_edges))

        for edge in edges_to_add:
            self.link_nodes(edge[0], edge[1])


class LinkWithStructuralHoles(LinkAlgorithm):

    def __init__(self,
                 graph: nx.Graph(),
                 communities: dict,
                 filename: str,
                 given_effective_size: dict = None,
                 k: float = 0.005):

        filename = filename + '_effective_size'
        self.k = k
        super().__init__(graph, communities, given_effective_size, filename)

    def prediction(self):

        effective_size = dict()

        if not self.values:
            for community in self.communities:
                print("Getting effective size for community {}".format(community))
                subgraph = nx.subgraph(self.graph, self.communities[community])
                effective_size[community] = self.__get_effective_size(subgraph)

            print("Effective size done")
            write_dict_to_json(effective_size, self.filename, "../effective_size/")
            print("Effective size values written")
        else:
            print("Effective size provided")
            effective_size = self.values

        effective_size_left = effective_size["0"]
        effective_size_right = effective_size["1"]
        non_connected_nodes = list(nx.non_edges(self.graph))
        n_possible_new_connections = len(non_connected_nodes)
        non_connected_nodes = list(
            filter(
                lambda x:
                (x[0] in effective_size_right and x[1] in effective_size_left)
                or (x[0] in effective_size_left and x[1] in effective_size_right),
                non_connected_nodes
            )
        )
        possible_new_edges = self.__get_highest_values(
            non_connected_nodes,
            effective_size_left,
            effective_size_right
        )
        possible_new_edges = {k: v for k, v in
                              sorted(possible_new_edges.items(), key=lambda item: item[1], reverse=True)}

        max_links = len(possible_new_edges)
        number_edges = round(self.k * self.n_edges)
        all_possible_new_edges = possible_new_edges.keys()
        if number_edges < max_links:
            edges_to_add = islice(all_possible_new_edges, number_edges)
        else:
            edges_to_add = all_possible_new_edges

        self.percentage_edges_added = self.k
        print("% of edges added: {}".format(self.percentage_edges_added))
        print("Adding {} edges".format(number_edges))

        for edge in edges_to_add:
            self.link_nodes(edge[0], edge[1])

    @staticmethod
    def __get_effective_size(graph: nx.Graph()):
        effective_size = dict(
            filter(
                lambda x: x[1] > 0,
                nx.effective_size(graph).items()
            )
        )
        effective_size = {k: v for k, v in sorted(effective_size.items(), key=lambda item: item[1], reverse=True)}
        return effective_size

    @staticmethod
    def __get_efficiency(graph: nx.Graph(), effective_size: dict):
        efficiency = {n: v / graph.degree(n) for n, v in effective_size.items()}
        efficiency = {k: v for k, v in sorted(efficiency.items(), key=lambda item: item[1], reverse=True)}
        return efficiency

    @staticmethod
    def __get_highest_values(non_connected_nodes: Iterable, values_left: dict,
                             values_right: dict):

        print("Getting 'best' edges")

        edges_to_add = dict()

        for node_pairs in non_connected_nodes:
            values_first_node = \
                values_left[node_pairs[0]] if node_pairs[0] in values_left else values_right[
                    node_pairs[0]]
            values_second_node = \
                values_left[node_pairs[1]] if node_pairs[1] in values_left else values_right[
                    node_pairs[1]]
            values_pair_nodes = values_first_node + values_second_node
            edges_to_add[node_pairs] = values_pair_nodes

        return edges_to_add


class HybridLinkPrediction(LinkWithBetweenness, StateOfArtAlgorithm):

    def __init__(self,
                 graph: nx.Graph,
                 communities: dict,
                 algorithm: str,
                 filename: str,
                 given_betweenness_value: dict = None,
                 given_values: dict = None,
                 k: float = 0.005):

        self.betweeness_value = given_betweenness_value
        filename = filename + '_betweenness'
        StateOfArtAlgorithm.__init__(self,
                                     graph=graph,
                                     communities=communities,
                                     algorithm=algorithm,
                                     k=k,
                                     filename=filename,
                                     given_values=given_values)

    def prediction(self):

        highest_betweenness = dict()

        if not self.betweeness_value:
            for community in self.communities:
                print("Getting betweenness for community {}".format(community))
                subgraph = nx.subgraph(self.graph, self.communities[community])
                highest_betweenness[community] = self._LinkWithBetweenness__get_betweenness(subgraph)

            print("Betweenness done")
            write_dict_to_json(highest_betweenness, self.filename, "../betweenness/")
            print("Betweenness values written")
        else:
            print("Betweenness provided")
            highest_betweenness = self.betweeness_value

        highest_betweenness_left = highest_betweenness["0"]
        highest_betweenness_right = highest_betweenness["1"]
        non_connected_nodes = list(nx.non_edges(self.graph))
        n_possible_new_connections = len(non_connected_nodes)
        non_connected_nodes = list(
            filter(
                lambda x:
                (x[0] in highest_betweenness_right and x[1] in highest_betweenness_left)
                or (x[0] in highest_betweenness_left and x[1] in highest_betweenness_right),
                non_connected_nodes
            )
        )
        ranked_betweenness_nodes = self._LinkWithBetweenness__get_highest_betweenness(
            non_connected_nodes,
            highest_betweenness_left,
            highest_betweenness_right
        )

        if not self.values:
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

            write_dict_to_json({"values": ranked_similarity_nodes}, self.filename, f"../{self.algorithm.lower()}/")
            print(f"{self.algorithm} values written")
        else:
            print(f"{self.algorithm.lower()} provided")
            ranked_similarity_nodes = list(self.values.values())[0]
            ranked_similarity_nodes = list(map(tuple, ranked_similarity_nodes))

        scores = self.__combine_scores(ranked_betweenness_nodes, ranked_similarity_nodes)
        scores = {k: v for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)}

        max_links = len(scores)
        number_edges = round(self.k, self.n_edges)
        all_possible_new_edges = scores.keys()
        if number_edges < max_links:
            edges_to_add = islice(all_possible_new_edges, number_edges)
        else:
            edges_to_add = all_possible_new_edges

        self.percentage_edges_added = self.k
        print("% of edges added: {}".format(self.percentage_edges_added))
        print("Adding {} edges".format(number_edges))

        for edge in edges_to_add:
            self.link_nodes(edge[0], edge[1])

    @staticmethod
    def __combine_scores(ranked_betweenness: dict, ranked_similarity: List[tuple]):

        scores = dict()
        for nodes in ranked_similarity:
            node_pairs = nodes[:2]
            score = nodes[2]
            inverted_pairs = (node_pairs[1], node_pairs[0])
            betweenness = ranked_betweenness.get(node_pairs)
            if not betweenness:
                betweenness = ranked_betweenness.get(inverted_pairs)
            scores[node_pairs] = score * betweenness

        return scores
