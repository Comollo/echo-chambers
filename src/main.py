# define main

import sys
import networkx as nx
from src.common.utility import get_filename, get_folder, write_gexf, write_communities
from src.community.partition import CommunityDetection
from src.controversy.measures import RandomWalkControversy
from src.link_prediction.algorithms import LinkWithBetweenness

try:
    path = sys.argv[1]
    filename = get_filename(path)
    folder = get_folder(path)

    print("Creating graph for {}".format(filename))
    graph = nx.read_weighted_edgelist(path, delimiter=",")
    print("Graph created")

    # print("Creating file gexf")
    # write_gexf(graph, filename, folder)
    # print("Gexf file created")

    communities = CommunityDetection(graph=graph, algorithm="fluidc")
    # write_communities(communities.communities, filename)
    controversy = RandomWalkControversy(graph=graph, communities=communities.communities)
    print("Number edges before: {}".format(len(graph.edges)))
    new_graph = LinkWithBetweenness(graph=graph, communities=communities.communities)
    print("Number edges after: {}".format(len(new_graph.graph.edges)))
    controversy_post = RandomWalkControversy(graph=new_graph.graph, communities=communities.communities)

except Exception as e:
    print("An error occurred: {}".format(e))
    raise e
