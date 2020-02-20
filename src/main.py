# define main

import sys
import networkx as nx
import pandas as pd
from src.common.utility import get_filename, get_folder, write_gexf, write_communities
from src.community.partition import CommunityDetection
from src.controversy.measures import RandomWalkControversy, GMCK, ForceAtlasControversy
from src.link_prediction.algorithms import LinkWithBetweenness, StateOfArtAlgorithm, HybridLinkPrediction

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

    def gather_result(g: nx.Graph, partitions: CommunityDetection, n_edges: list, link_prediction_alg: list, hybrid: bool = True):

        rwc_pre = RandomWalkControversy(graph=g, communities=partitions.communities)
        gmck_pre = GMCK(graph=g, communities=partitions.communities)
        force_atlas_pre = ForceAtlasControversy(graph=g, communities=partitions.communities)

        df_result = pd.DataFrame(
            columns=["Algorithm",
                     "RWC_pre",
                     "RWC_post",
                     "GMCK_pre",
                     "GMCK_post",
                     "ForceAtlas_pre",
                     "ForceAtlas_post",
                     "Original_edges",
                     "New_edges",
                     "Number_edges_added"]
        )

        for k in n_edges:
            for alg in link_prediction_alg:

                graph_copy = g.copy()
                original_edges = len(graph_copy.edges)
                print("Number edges before: {}".format(original_edges))

                if alg == "BETWEENNESS":
                    new_graph = LinkWithBetweenness(graph=graph_copy, communities=partitions.communities, k=k)
                else:
                    if hybrid:
                        new_graph = HybridLinkPrediction(graph=graph_copy, communities=partitions.communities, algorithm=alg, k=k)
                        alg = "BETWEENNESS + " + alg
                    else:
                        new_graph = StateOfArtAlgorithm(graph=graph_copy, communities=partitions.communities, algorithm=alg, k=k)

                new_edges = len(new_graph.graph.edges)
                print("Number edges after: {}".format(new_edges))

                rwc_post = RandomWalkControversy(graph=new_graph.graph, communities=partitions.communities)
                gmck_post = GMCK(graph=new_graph.graph, communities=partitions.communities)
                force_atlas_post = ForceAtlasControversy(graph=new_graph.graph, communities=partitions.communities)

                df_result = df_result.append(
                    {"Algorithm": alg,
                     "RWC_pre": rwc_pre.controversy,
                     "RWC_post": rwc_post.controversy,
                     "GMCK_pre": gmck_pre.controversy,
                     "GMCK_post": gmck_post.controversy,
                     "ForceAtlas_pre": force_atlas_pre.controversy,
                     "ForceAtlas_post": force_atlas_post.controversy,
                     "Original_edges": original_edges,
                     "New_edges": new_edges,
                     "Number_edges_added": k
                     },
                    ignore_index=True
                )

        return df_result

    result = gather_result(g=graph,
                           partitions=communities,
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
                           hybrid=True
                           )

    result.to_csv("../data/result_hybrid_1.csv")

except Exception as e:
    print("An error occurred: {}".format(e))
    raise e
