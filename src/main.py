# define main

import argparse
from os import listdir, makedirs

import networkx as nx
import sys

from common.collect_results import results
from common.utility import read_json_to_dict, write_dict_to_json
from community.partition import CommunityDetection

parser = argparse.ArgumentParser(description='echo chambers pipeline')
parser.add_argument('folder', help='Folder containing graph data')
parser.add_argument('-perc_edges', help='percentage of new edges to add', nargs='+', type=float, default=[0.005])
parser.add_argument('-hybrid', help='Include to get hybrid result', default=False, action='store_true')
parser.add_argument('-kern', help='Detect community using kernighan-lin', default=False, action='store_true')
parser.add_argument('-complete', help='Run analysis using all controversy measures', default=False, action='store_true')
args = parser.parse_args()

path_community = '../community/'
path_betweenness = '../betweenness/'
path_effective_size = '../effective_size/'
print('Creating folder community, betweenness, effective_size')
makedirs(path_community, exist_ok=True)
makedirs(path_betweenness, exist_ok=True)
makedirs(path_effective_size, exist_ok=True)
try:
    path = args.folder
    hybrid = args.hybrid
    kern = args.kern
    complete = args.complete
    algorithm = 'kernighan-lin' if kern else 'fluidc'
    folder_result = "result_hybrid" if hybrid else "result_standard"
    percentage_edges = args.perc_edges

    files = listdir(path)
    output = map(lambda x: x.split(".")[0], listdir("../" + folder_result + "/"))
    communities_written = listdir(path_community)
    betweenness_values = listdir(path_betweenness)
    effective_size_values = listdir(path_effective_size)
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

            communities_to_write = filename + '_' + algorithm + '.json'
            betweenness_to_evaluate = filename + '_betweenness.json'
            effective_size_to_evaluate = filename + '_effective_size.json'
            if betweenness_to_evaluate in betweenness_values:
                given_betweenness_value = read_json_to_dict(betweenness_to_evaluate, path_betweenness)
            else:
                given_betweenness_value = None
            if effective_size_to_evaluate in effective_size_values:
                given_effective_size = read_json_to_dict(effective_size_to_evaluate, path_effective_size)
            else:
                given_effective_size = None
            if communities_to_write in communities_written:
                given_communities = read_json_to_dict(communities_to_write, path_community)
                communities = CommunityDetection(graph=graph, algorithm=algorithm, given_communities=given_communities)
            else:
                communities = CommunityDetection(graph=graph, algorithm=algorithm)
                write_dict_to_json(communities.communities, communities_to_write, path_community)
            result = results(g=graph,
                             communities=communities.communities,
                             n_edges=percentage_edges,
                             filename=filename,
                             link_prediction_alg=[
                                 "BETWEENNESS",
                                 "EFFECTIVE_SIZE",
                                 "JACCARD_COEFFICIENT",
                                 "ADAMIC_ADAR",
                                 "RESOURCE_ALLOCATION",
                                 "PREFERENTIAL_ATTACHMENT"
                             ],
                             hybrid=hybrid,
                             given_betweenness_value=given_betweenness_value,
                             given_effective_size=given_effective_size,
                             complete=complete)
            result.to_csv("../" + folder_result + "/" + filename + ".csv")

except Exception as e:
    print("An error occurred: {}".format(e))
    raise e
