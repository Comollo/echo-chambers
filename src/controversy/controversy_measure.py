# define abstract class

from abc import ABC, abstractmethod
from networkx import Graph


class ControversyMeasure(ABC):

    def __init__(self, graph: Graph, communities: dict):

        self.graph = graph
        self.communities = communities
        self.controversy = self.get_controversy()

    @abstractmethod
    def get_controversy(self):

        pass
