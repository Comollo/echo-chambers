# define main function
import sys
import networkx as nx

import src.controversy.measure as measure

filename = sys.argv[1]

print("Creating graph for {}".format(filename)) #TODO create logging
G = nx.read_weighted_edgelist(filename, delimiter=',')
