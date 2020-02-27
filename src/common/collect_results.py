# define function to collect results

import networkx as nx
import pandas as pd

from src.controversy.measures import RandomWalkControversy, GMCK, ForceAtlasControversy
from src.link_prediction.algorithms import LinkWithBetweenness, HybridLinkPrediction, StateOfArtAlgorithm, \
    LinkWithStructuralHoles


def results(g: nx.Graph, communities: dict, n_edges: list, link_prediction_alg: list,
            hybrid: bool = True):
    """
    Function to collect results of echo-chambers project

    Parameter
    ---------
    g : nx.Graph
    communities : dict containing communities
    n_edges: list of number of edges to add
    link_prediction_alg: list of link prediction algorithms to use
    """
    rwc_pre = RandomWalkControversy(graph=g, communities=communities)
    gmck_pre = GMCK(graph=g, communities=communities)
    force_atlas_pre = ForceAtlasControversy(graph=g, communities=communities)

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
                 "Number_edges_added",
                 "Percentage_edges_added"]
    )

    for k in n_edges:
        for alg in link_prediction_alg:

            graph_copy = g.copy()
            original_edges = len(graph_copy.edges)
            print("Number edges before: {}".format(original_edges))

            if alg == "BETWEENNESS":
                new_graph = LinkWithBetweenness(graph=graph_copy, communities=communities, k=k)
            elif alg == "EFFECTIVE_SIZE":
                new_graph = LinkWithStructuralHoles(graph=graph_copy, communities=communities, k=k)
            else:
                if hybrid:
                    new_graph = HybridLinkPrediction(graph=graph_copy, communities=communities,
                                                     algorithm=alg, k=k)
                    alg = "BETWEENNESS + " + alg
                else:
                    new_graph = StateOfArtAlgorithm(graph=graph_copy, communities=communities,
                                                    algorithm=alg, k=k)

            new_edges = len(new_graph.graph.edges)
            percentage_edges_added = new_graph.percentage_edges_added
            print("Number edges after: {}".format(new_edges))

            rwc_post = RandomWalkControversy(graph=new_graph.graph, communities=communities)
            gmck_post = GMCK(graph=new_graph.graph, communities=communities)
            force_atlas_post = ForceAtlasControversy(graph=new_graph.graph, communities=communities)

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
                 "Number_edges_added": k,
                 "Percentage_edges_added": percentage_edges_added
                 },
                ignore_index=True
            )

    return df_result
