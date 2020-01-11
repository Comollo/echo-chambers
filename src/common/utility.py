# define some common useful functions

import os
import networkx as nx
from typing import Dict


def border_msg(msg):
    """
    Print your message in a nice border

    Parameter
    ---------
    msg : string, integer, float
    """
    row = len(msg)
    h = ''.join(['+'] + ['-' * row] + ['+'])
    if type(msg) == str:
        pass
    else:
        msg = str(msg)
    result = h + '\n'"|" + msg + "|"'\n' + h
    print(result)


def print_element(iterable):
    """
    Print the element of your iterable object

    Parameter
    ---------
    iterable : list, dict, set
    """
    for element in iterable:
        print(element)


def get_filename(path):
    """
    Return filename of a specific path

    Parameter
    ---------
    path : string

    Return
    ------
    filename : string
    """
    filename = os.path.basename(path)
    return filename


def get_folder(path):
    """
    Return folder of a specific path

    Parameter
    ---------
    path : string

    Return
    ------
    folder : string
    """
    folder = os.path.dirname(path)
    return folder


def file_to_elist(file, delimiter: str):
    """
    Return list of edges given a file containing pairs of nodes

    Parameter
    ---------
    file : file representing an edge list representation of a graph
    delimiter : string
        kind of delimiter between two nodes in the file
    Return
    ------
    elist: list of edges
    """
    elist = list()
    with open(file) as f:
        for line in f:
            line = tuple(line.strip().split(delimiter))
            elist.append(line)
        number_edges = len(elist)
        border_msg("Number of edges: {}".format(number_edges))

    return elist


def lists_to_dict(keys: list, values: list):
    """
    Return a dict given to list

    Parameter
    ---------
    keys : list containing key
    values : list containing values
    Return
    ------
    keys_and_values : dict from two lists
    """
    if len(keys) != len(values):
        raise Exception("Two lists are not of the same length")
    keys_and_values = dict(zip(keys, values))
    return keys_and_values


def write_communities(communities: Dict[int, set], filename: str, path: str = "../data/"):
    """
    Write nodes to txt

    Parameter
    ---------
    communities : dictionary containing communities and nodes
    filename : name for txt
    path : location of your file
    """
    print("writing communities")
    original_name = filename.strip().split(".")
    for community in communities:

        txt_name = original_name[0] + "_" + str(community) + "." + original_name[1]
        file = open(path + txt_name, 'w')

        for node in communities[community]:
            file.write(node)
            file.write('\n')
        print("{} has been written".format(txt_name))
        file.close()

    print("all communities have been written")


def write_gexf (graph: nx.Graph, filename: str, path: str = "../data/"):
    """
    Write graph into gexf format

    Parameter
    ---------
    graph : nx.Graph
    filename : name for txt
    path : location of your file
    """

    gexf = ".gexf"

    if not path.strip().endswith("/"):
        path = path + "/"

    original_name = filename.strip().split(".")
    destination = path + original_name[0] + gexf
    nx.write_gexf(graph, destination)

