# define abstract class

from abc import ABC, abstractmethod
from networkx import Graph
from networkx.algorithms import community


class ControversyMeasure(ABC):

    def __init__(self, graph: Graph, communities: dict):

        self.graph = graph
        self.communities = communities
        self.__is_partition()
        self.controversy = self.get_controversy()

    def __is_partition(self):

        for c in self.communities:
            if community.is_partition(self.graph, self.communities[c]):
                raise Exception("Community {} is not part of the graph".format(c))
            else:
                pass
        print("Valid communities")

    @abstractmethod
    def get_controversy(self):

        pass
