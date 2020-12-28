# define main

import argparse
import sys
from os import listdir

import networkx as nx

from common.collect_results import results
from common.utility import write_communities
from community.partition import CommunityDetection

parser = argparse.ArgumentParser(description='echo chambers pipeline')
parser.add_argument('folder', help='Folder containing graph data')
parser.add_argument('-hybrid', help='Include to get hybrid result', default=False, action='store_true')
args = parser.parse_args()
try:
    path = args.folder
    hybrid = args.hybrid
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
            if not file.endswith('.gexf'):
                print('Only gexf type is supported')
                print('Convert you data to gexf format using networkx')
                sys.exit(1)
            else:
                graph = nx.read_gexf(tweet_data)
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
                                 "EFFECTIVE_SIZE",
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
