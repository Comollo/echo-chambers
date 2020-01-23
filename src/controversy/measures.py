# define controversy measures

import networkx as nx
import random
from src.controversy.controversy_measure import ControversyMeasure
from src.common.utility import border_msg, lists_to_dict


class RandomWalkControversy(ControversyMeasure):

    def __init__(self, graph: nx.Graph, communities: dict, iteration: int = 1000, percent: float = 0.10):

        self.iteration = iteration
        self.percent = percent
        super().__init__(graph, communities)

    def get_controversy(self):

        percent = self.percent
        graph = self.graph

        left = list(self.communities[0])
        right = list(self.communities[1])

        left_left = 0
        left_right = 0
        right_right = 0
        right_left = 0

        left_percent = int(percent*len(left))
        right_percent = int(percent*len(right))

        print("{} Random Walk Iteration".format(self.iteration))
        for j in range(self.iteration):

            user_nodes_left = self.get_random_nodes(left_percent, left)
            user_nodes_right = self.get_random_nodes(right_percent, right)

            user_nodes_left_list = list(user_nodes_left.keys())
            for i in range(len(user_nodes_left_list)-1):

                node = user_nodes_left_list[i]
                other_nodes = user_nodes_left_list[:i] + user_nodes_left_list[i+1:]
                values = [1] * len(other_nodes)
                other_nodes_dict = lists_to_dict(other_nodes, values)

                side = self.perform_random_walk(graph, node, other_nodes_dict, user_nodes_right)

                if side == "left":
                    left_left += 1

                elif side == "right":
                    left_right += 1

            user_nodes_right_list = list(user_nodes_right.keys())
            for i in range(len(user_nodes_right_list)-1):

                node = user_nodes_right_list[i]
                other_nodes = user_nodes_right_list[:i] + user_nodes_right_list[i+1:]
                values = [1] * len(other_nodes)
                other_nodes_dict = lists_to_dict(other_nodes, values)

                side = self.perform_random_walk(graph, node, user_nodes_left, other_nodes_dict)

                if side == "left":
                    right_left += 1

                elif side == "right":
                    right_right += 1

        e1 = left_left / (left_left + right_left)
        e2 = left_right / (left_right + right_right)
        e3 = right_left / (left_left + right_left)
        e4 = right_right / (left_right + right_right)
        rwc = round(e1*e4 - e2*e3, 2)

        border_msg("Random Walk Controversy: {}".format(rwc))
        return rwc

    @staticmethod
    def get_random_nodes(k, side):

        random_nodes = []
        random_nodes_dict = {}

        for i in range(k):

            random_num = random.randint(0, len(side)-1)
            random_nodes.append(side[random_num])
            random_nodes_dict[side[random_num]] = 1

        return random_nodes_dict

    @staticmethod
    def perform_random_walk(graph, node, left_side, right_side):

        flag = 0
        side = ""
        starting_node = node

        while flag != 1:

            neighbors = list(graph.neighbors(starting_node))
            random_num = random.randint(0, len(neighbors)-1)
            starting_node = neighbors[random_num]

            if starting_node in left_side:
                side = "left"
                flag = 1

            elif starting_node in right_side:
                side = "right"
                flag = 1

        return side


class GMCK(ControversyMeasure):

    def __init__(self, graph: nx.Graph, communities: dict):
        super().__init__(graph, communities)

    def get_controversy(self):

        left = list(self.communities[0])
        right = list(self.communities[1])
        dict_left = lists_to_dict(left, [1] * len(left))
        dict_right = lists_to_dict(right, [1] * len(right))

        cut_nodes1 = {}
        cut_nodes = {}

        for i in range(len(left)):
            name1 = left[i]
            for j in range(len(right)):
                name2 = right[j]
                if self.graph.has_edge(name1, name2):
                    cut_nodes1[name1] = 1
                    cut_nodes1[name2] = 1

        dict_across = {}  # num. edges across the cut
        dict_internal = {}  # num. edges internal to the cut

        for keys in cut_nodes1.keys():

            if self.satisfy_second_condition(keys, self.graph, dict_left, dict_right, cut_nodes1):
                cut_nodes[keys] = 1

        for edge in self.graph.edges():

            node1 = edge[0]
            node2 = edge[1]

            if node1 not in cut_nodes and (node2 not in cut_nodes):  # only consider edges involved in the cut
                continue
            if node1 in cut_nodes and node2 in cut_nodes:
                # if both nodes are on the cut and both are on the same side, ignore
                if node1 in dict_left and node2 in dict_left:
                    continue
                if node1 in dict_right and node2 in dict_right:
                    continue
            if node1 in cut_nodes:
                if node1 in dict_left:
                    if node2 in dict_left and node2 not in cut_nodes1:
                        if node1 in dict_internal:
                            dict_internal[node1] += 1
                        else:
                            dict_internal[node1] = 1
                    elif node2 in dict_right and node2 in cut_nodes:
                        if node1 in dict_across:
                            dict_across[node1] += 1
                        else:
                            dict_across[node1] = 1
                elif node1 in dict_right:
                    if node2 in dict_left and node2 in cut_nodes:
                        if node1 in dict_across:
                            dict_across[node1] += 1
                        else:
                            dict_across[node1] = 1
                    elif node2 in dict_right and node2 not in cut_nodes1:
                        if node1 in dict_internal:
                            dict_internal[node1] += 1
                        else:
                            dict_internal[node1] = 1
            if node2 in cut_nodes:
                if node2 in dict_left:
                    if node1 in dict_left and node1 not in cut_nodes1:
                        if node2 in dict_internal:
                            dict_internal[node2] += 1
                        else:
                            dict_internal[node2] = 1
                    elif node1 in dict_right and node1 in cut_nodes:
                        if node2 in dict_across:
                            dict_across[node2] += 1
                        else:
                            dict_across[node2] = 1
                elif node2 in dict_right:
                    if node1 in dict_left and node1 in cut_nodes:
                        if node2 in dict_across:
                            dict_across[node2] += 1
                        else:
                            dict_across[node2] = 1
                    elif node1 in dict_right and node1 not in cut_nodes1:
                        if node2 in dict_internal:
                            dict_internal[node2] += 1
                        else:
                            dict_internal[node2] = 1

        polarization_score = 0.0

        for keys in cut_nodes.keys():
            if keys not in dict_internal or (keys not in dict_across):  # for singleton nodes from the cut
                continue
            if dict_across[keys] == 0 and dict_internal[keys] == 0:  # there's some problem
                print("wtf")
            polarization_score += (dict_internal[keys]*1.0/(dict_internal[keys] + dict_across[keys]) - 0.5)

        polarization_score = round(polarization_score/len(cut_nodes.keys()), 2)
        border_msg("GMCK Controversy: {}".format(polarization_score))
        return polarization_score

    @staticmethod
    def satisfy_second_condition(node1, graph: nx.Graph, dict_left, dict_right, cut):
        # A node v in G_i has at least one edge connecting to a member of G_i which is not connected to G_j.
        neighbors = graph.neighbors(node1)
        for n in neighbors:
            if node1 in dict_left and n in dict_right:  # only consider neighbors belonging to G_i
                continue
            if node1 in dict_right and n in dict_left:  # only consider neighbors belonging to G_i
                continue
            if n not in cut:
                return True
        return False
