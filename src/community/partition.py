# define function to partition a graph

import networkx as nx


class CommunityDetection:
    algorithms = {"KERNIGHAN"}

    def __init__(self, graph: nx.Graph, algorithm: str):
        self.graph = graph
        self.algorithm = algorithm

    def check_algorithm(self):
        if self.algorithm not in self.algorithms:
            print("the possible algorithms are:")
