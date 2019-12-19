# define random walk controversy metric

import networkx as nx


class ControversyMeasure:

    def __init__(self, graph: nx.Graph):
        self.graph = graph
