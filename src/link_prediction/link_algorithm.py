# define abstract class

from abc import ABC, abstractmethod
from typing import Dict

from networkx import Graph


class LinkAlgorithm(ABC):

    def __init__(self, graph: Graph, communities: Dict[str, list], values: dict, filename):

        self.percentage_edges_added = 0
        self.graph = graph
        self.communities = communities
        self.n_edges = len(graph.edges)
        self.values = values
        self.filename = filename
        self.prediction()

    @abstractmethod
    def prediction(self):

        pass

    def link_nodes(self, u, v):

        if self.graph.has_edge(u, v):
            raise Exception("Cannot create connection: the edge is already present")
        else:
            self.graph.add_edge(u, v)

        return self.graph
