# define some common useful functions
import os
import numpy as np


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


def from_file_to_elist(file, delimiter: str):
    """
    Return list of edges given a file containing pairs of nodes

    Parameter
    ---------
    file : file
    delimiter : string
        kind of delimiter between two nodes in the file
    Return
    ------
    elist: list of edges
    """
    #TODO optimize this function
    elist = np.array(())
    with open(file) as f:
        for line in f:
            line = tuple(line.strip().split(delimiter))
            elist = np.append(elist, line)
        number_edges = elist.shape
        border_msg("Number of edges: {}".format(number_edges))

    return elist

