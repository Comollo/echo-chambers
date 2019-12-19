# define main function

import sys
import networkx as nx

filename = sys.argv[1]

print("Creating graph for {}".format(filename)) #TODO create logging
G = nx.read_edgelist(filename, delimiter=',')
a = 90
