# define main function

import sys
import networkx as nx
from src.common.utility import get_filename, from_file_to_elist

try:
    file = sys.argv[1]
    filename = get_filename(file)
    print("Creating graph for {}".format(filename))
    elist = from_file_to_elist(file, "\t")
    #G = nx.read_edgelist(file, delimiter='\t')
except Exception as e:
    print("An error occurred: {}".format(e))
    raise e
