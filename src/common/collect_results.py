# define function to collect results

import networkx as nx
import pandas as pd

from controversy.measures import RandomWalkControversy, GMCK, ForceAtlasControversy
from link_prediction.algorithms import LinkWithBetweenness, HybridLinkPrediction, StateOfArtAlgorithm, \
    LinkWithStructuralHoles


def results(g: nx.Graph,
            communities: dict,
            n_edges: list,
            filename: str,
            given_betweenness_value: dict,
            given_effective_size: dict,
            complete: bool,
            link_prediction_alg: list,
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
    if complete:
        print("Getting all controversy measure")
        gmck_pre = GMCK(graph=g, communities=communities)
        rwc_pre = RandomWalkControversy(graph=g, communities=communities)
        force_atlas_pre = ForceAtlasControversy(graph=g, communities=communities)
    else:
        print("Getting only BCC controversy measure")
        gmck_pre = GMCK(graph=g, communities=communities)
        rwc_pre = RandomWalkControversy(graph=g, communities=communities, compute=complete)
        force_atlas_pre = ForceAtlasControversy(graph=g, communities=communities, compute=complete)

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
                new_graph = LinkWithBetweenness(graph=graph_copy,
                                                communities=communities,
                                                k=k,
                                                filename=filename,
                                                given_betweenness_value=given_betweenness_value)
            elif alg == "EFFECTIVE_SIZE":
                new_graph = LinkWithStructuralHoles(graph=graph_copy,
                                                    communities=communities,
                                                    k=k,
                                                    filename=filename,
                                                    given_effective_size=given_effective_size)
            else:
                if hybrid:
                    new_graph = HybridLinkPrediction(graph=graph_copy,
                                                     communities=communities,
                                                     algorithm=alg,
                                                     k=k,
                                                     filename=filename)
                    alg = "BETWEENNESS + " + alg
                else:
                    new_graph = StateOfArtAlgorithm(graph=graph_copy,
                                                    communities=communities,
                                                    algorithm=alg,
                                                    k=k)

            new_edges = len(new_graph.graph.edges)
            percentage_edges_added = new_graph.percentage_edges_added
            print("Number edges after: {}".format(new_edges))

            if complete:
                gmck_post = GMCK(graph=new_graph.graph, communities=communities)
                rwc_post = RandomWalkControversy(graph=new_graph.graph, communities=communities)
                force_atlas_post = ForceAtlasControversy(graph=new_graph.graph, communities=communities)
            else:
                gmck_post = GMCK(graph=new_graph.graph, communities=communities)
                rwc_post = RandomWalkControversy(graph=new_graph.graph, communities=communities, compute=complete)
                force_atlas_post = ForceAtlasControversy(graph=new_graph.graph, communities=communities, compute=complete)

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
                 "Number_edges_added": new_edges - original_edges,
                 "Percentage_edges_added": percentage_edges_added
                 },
                ignore_index=True
            )

    return df_result
