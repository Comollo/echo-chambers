# define main function

import sys
import networkx as nx
from src.common.utility import get_filename, border_msg
from src.community.partition import CommunityDetection
from src.controversy.measures import RandomWalkControversy

try:
    path = sys.argv[1]
    filename = get_filename(path)

    print("Creating graph for {}".format(filename))
    graph = nx.read_weighted_edgelist(path, delimiter=",")
    print("Graph created")

    communities = CommunityDetection(graph=graph, algorithm="fluidc")

    controversy = RandomWalkControversy(graph=graph, communities=communities.communities)
    # G = nx.read_edgelist(file, delimiter='\t')
except Exception as e:
    print("An error occurred: {}".format(e))
    raise e
