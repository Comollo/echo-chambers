# define main

import sys
from os import listdir

import networkx as nx

from src.common.collect_results import results
from src.common.utility import write_communities
from src.community.partition import CommunityDetection

try:
    if len(sys.argv) < 3:
        print("The code required two arguments")
        print("Argument 1: folder data -> e.g: ../data/")
        print("Argument 2: hybrid -> True or False")
        sys.exit(1)
    else:
        path = sys.argv[1]
        hybrid = eval(sys.argv[2])
        folder_result = "result_hybrid" if hybrid else "result_standard"

    files = listdir(path)
    output = map(lambda x: x.split(".")[0], listdir("../" + folder_result + "/"))
    for file in files:

        filename = file.split(".")[0]
        if filename in output:
            print("Results for {} have already been collected".format(filename))
        else:
            print("Creating graph for {}".format(filename))
            tweet_data = path + file
            graph = nx.read_weighted_edgelist(tweet_data, delimiter=",")
            print("Graph created")

            communities = CommunityDetection(graph=graph, algorithm="fluidc")
            write_communities(communities.communities, filename + "_" + communities.algorithm)
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
                             hybrid=hybrid
                             )
            result.to_csv("../" + folder_result + "/" + filename + ".csv")

except Exception as e:
    print("An error occurred: {}".format(e))
    raise e
