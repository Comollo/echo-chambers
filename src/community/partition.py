# define function to partition a graph

import networkx as nx
from enum import Enum, unique
from networkx.algorithms import community
from src.common.utility import print_element


@unique
class Algorithm(Enum):
    KERNIGHAN = "KERNIGHAN"


class CommunityDetection:

    algorithms = [Algorithm.KERNIGHAN.value]

    def __init__(self, graph: nx.Graph, algorithm: str):
        self.graph = graph
        if algorithm not in self.algorithms:
            print("The available partition algorithms are:")
            print_element(self.algorithms)
            raise ValueError("algorithm not valid")
        self.algorithm = algorithm
        self.community = None

    def get_community(self):
        if self.algorithm == Algorithm.KERNIGHAN.value:
            self.community = community.kernighan_lin_bisection(self.graph)
