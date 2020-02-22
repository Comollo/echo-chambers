# define functions to partition a graph

from enum import Enum, unique
from typing import Dict

import networkx as nx
from networkx.algorithms import community

from src.common.utility import print_element


@unique
class Algorithm(Enum):
    KERNIGHAN_LIN = "KERNIGHAN-LIN"
    FLUIDC = "FLUIDC"


class CommunityDetection:
    algorithms = [Algorithm.KERNIGHAN_LIN.value,
                  Algorithm.FLUIDC.value]

    def __init__(self, graph: nx.Graph, algorithm: str, k: int = 2):

        self.graph = graph
        if algorithm.upper() not in self.algorithms:
            print("The available partition algorithms are:")
            print_element(self.algorithms)
            raise ValueError("algorithm not valid")
        self.algorithm = algorithm
        self.communities = self.get_community(k)

    def get_community(self, k):

        print("Finding communities using: {}".format(self.algorithm.upper()))

        communities: Dict[int, set] = dict()

        if self.algorithm.upper() == Algorithm.KERNIGHAN_LIN.value:
            partitions = community.kernighan_lin_bisection(self.graph)
            for p in range(len(partitions)):
                communities[p] = partitions[p]

        elif self.algorithm.upper() == Algorithm.FLUIDC.value:
            partitions = community.asyn_fluidc(self.graph, k, seed=10)
            for p in range(k):
                communities[p] = next(partitions)

        print("{} communities found".format(len(communities)))
        return communities
