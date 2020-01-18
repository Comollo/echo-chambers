# define abstract class

from abc import ABC, abstractmethod
from typing import Dict
from networkx import Graph


class LinkAlgorithm(ABC):

    def __init__(self, graph: Graph, communities: Dict[int, set]):

        self.graph = graph
        self.communities = communities
        self.prediction()

    @abstractmethod
    def prediction(self):

        pass
