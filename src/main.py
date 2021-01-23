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
parser.add_argument('-per', help='percentage of new edges to add', default=0.005, type=float)
parser.add_argument('-hybrid', help='Include to get hybrid result', default=False, action='store_true')
parser.add_argument('-kern', help='Detect community using kernighan-lin', default=False, action='store_true')
parser.add_argument('-complete', help='Run analysis using all controversy measures', default=False, action='store_true')
args = parser.parse_args()

path_community = '../community/'
path_betweenness = '../betweenness/'
path_effective_size = '../effective_size/'
path_jaccard = '../jaccard_coefficient/'
path_adamic_adar = '../adamic_adar/'
path_resource_allocation = '../resource_allocation/'
path_preferential_attachment = '../preferential_attachment/'
print('Creating folder community, betweenness, effective_size')
makedirs(path_community, exist_ok=True)
makedirs(path_betweenness, exist_ok=True)
makedirs(path_effective_size, exist_ok=True)
makedirs(path_jaccard, exist_ok=True)
makedirs(path_adamic_adar, exist_ok=True)
makedirs(path_resource_allocation, exist_ok=True)
makedirs(path_preferential_attachment, exist_ok=True)

try:
    path = args.folder
    hybrid = args.hybrid
    kern = args.kern
    complete = args.complete
    algorithm = 'kernighan-lin' if kern else 'fluidc'
    folder_result = "result_hybrid" if hybrid else "result_standard"
    percentage_edges = args.per

    files = listdir(path)
    output = map(lambda x: x.split(".")[0], listdir("../" + folder_result + "/"))
    communities_written = listdir(path_community)
    betweenness_values = listdir(path_betweenness)
    effective_size_values = listdir(path_effective_size)
    jaccard_values = listdir(path_jaccard)
    adamic_adar_values = listdir(path_adamic_adar)
    resource_allocation_values = listdir(path_resource_allocation)
    preferential_attachment_values = listdir(path_preferential_attachment)

    for file in files:

        graph_name = file.split(".")[0]
        filename = graph_name + f"_{percentage_edges}"
        if filename in output:
            print("Results for {} have already been collected".format(graph_name))
        else:
            print("Creating graph for {}".format(graph_name))
            tweet_data = path + file
            if not file.endswith('.gexf'):
                print('Only gexf type is supported')
                print('Convert you data to gexf format using networkx')
                sys.exit(1)
            else:
                graph = nx.read_gexf(tweet_data)
                print("Graph created")

            communities_to_write = graph_name + '_' + algorithm + '.json'
            betweenness_to_evaluate = graph_name + '_betweenness.json'
            effective_size_to_evaluate = graph_name + '_effective_size.json'
            jaccard_to_evaluate = graph_name + '_jaccard_coefficient.json'
            adamic_adar_to_evaluate = graph_name + '_adamic_adar.json'
            resource_allocation_to_evaluate = graph_name + '_resource_allocation.json'
            preferential_attachment_to_evaluate = graph_name + '_preferential_attachment.json'

            if betweenness_to_evaluate in betweenness_values:
                given_betweenness_value = read_json_to_dict(betweenness_to_evaluate,
                                                            path_betweenness)
            else:
                given_betweenness_value = None
            if effective_size_to_evaluate in effective_size_values:
                given_effective_size_value = read_json_to_dict(effective_size_to_evaluate,
                                                               path_effective_size)
            else:
                given_effective_size_value = None
            if jaccard_to_evaluate in jaccard_values:
                given_jaccard_value = read_json_to_dict(jaccard_to_evaluate,
                                                        path_jaccard)
            else:
                given_jaccard_value = None
            if adamic_adar_to_evaluate in adamic_adar_values:
                given_adamic_adar_value= read_json_to_dict(adamic_adar_to_evaluate,
                                                           path_adamic_adar)
            else:
                given_adamic_adar_value = None
            if resource_allocation_to_evaluate in resource_allocation_values:
                given_resource_allocation_value = read_json_to_dict(resource_allocation_to_evaluate,
                                                                    path_resource_allocation)
            else:
                given_resource_allocation_value = None
            if preferential_attachment_to_evaluate in preferential_attachment_values:
                given_preferential_attachment_value = read_json_to_dict(preferential_attachment_to_evaluate,
                                                                        path_preferential_attachment)
            else:
                given_preferential_attachment_value = None

            if communities_to_write in communities_written:
                given_communities = read_json_to_dict(communities_to_write, path_community)
                communities = CommunityDetection(graph=graph, algorithm=algorithm, given_communities=given_communities)
                print('Getting communities from file')
            else:
                communities = CommunityDetection(graph=graph, algorithm=algorithm)
                write_dict_to_json(communities.communities, communities_to_write, path_community)

            result = results(g=graph,
                             communities=communities.communities,
                             per_edges=percentage_edges,
                             filename=graph_name,
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
                             given_effective_size=given_effective_size_value,
                             given_jaccard_value=given_jaccard_value,
                             given_adamic_adar_value=given_adamic_adar_value,
                             given_resource_allocation_value=given_resource_allocation_value,
                             given_preferential_attachment_value=given_preferential_attachment_value,
                             complete=complete)

            result.to_csv("../" + folder_result + "/" + filename + ".csv")

except Exception as e:
    print("An error occurred: {}".format(e))
    raise e
