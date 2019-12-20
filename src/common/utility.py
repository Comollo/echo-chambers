# define some common useful functions
import os
import pandas as pd
import networkx as nx


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


# def df_to_graph(path, delimiter: str, header: bool = None, attribute: list = None):
#     """
#     Read file as a pandas df and create the graph
#
#     Parameter
#     ---------
#     file : file representing an edge list representation of a graph
#     delimiter : string
#         kind of delimiter between two nodes in the file
#     header : header of the file
#     attribute : columns representing the attribute of the node
#     Return
#     ------
#     G: graph
#     """
#     df = pd.read_csv(path, sep=delimiter, header=header)
#     graph = nx.from_pandas_edgelist(df)
#     return graph