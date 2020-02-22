# define main

import sys
from os import listdir

import networkx as nx

from src.common.collect_results import results
from src.community.partition import CommunityDetection

try:
    if len(sys.argv) < 2:
        print("Folder with data has not been set")
        sys.exit(1)
    else:
        path = sys.argv[1]

    files = listdir(path)

    for file in files:
        print("Creating graph for {}".format(file))
        tweet_data = path + file
        graph = nx.read_weighted_edgelist(tweet_data, delimiter=",")
        print("Graph created")

        # filename = get_filename(tweet)
        # folder = get_folder(tweet)
        # print("Creating file gexf")
        # write_gexf(graph, filename, folder)
        # print("Gexf file created")

        communities = CommunityDetection(graph=graph, algorithm="fluidc")

        result = results(g=graph,
                         communities=communities.communities,
                         n_edges=[
                             1000
                         ],
                         link_prediction_alg=[
                             "BETWEENNESS",
                             "JACCARD_COEFFICIENT",
                             "ADAMIC_ADAR",
                             "RESOURCE_ALLOCATION",
                             "PREFERENTIAL_ATTACHMENT"
                         ],
                         hybrid=False
                         )

        filename = file.split(".")[0]
        result.to_csv("../result/" + filename + ".csv")

except Exception as e:
    print("An error occurred: {}".format(e))
    raise e
