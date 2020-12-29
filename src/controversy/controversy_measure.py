# define abstract class

from abc import ABC, abstractmethod
from typing import Dict

from networkx import Graph


class ControversyMeasure(ABC):

    def __init__(self, graph: Graph, compute: bool, communities: Dict[str, list]):
        self.graph = graph
        self.communities = communities
        self.controversy = self.get_controversy() if compute else None

    @abstractmethod
    def get_controversy(self):
        pass
