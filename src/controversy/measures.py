# define controversy measures
import math
import networkx as nx
import random
import numpy as np
from scipy.sparse import coo_matrix
from src.controversy.controversy_measure import ControversyMeasure
from src.common.utility import border_msg, lists_to_dict
from operator import itemgetter


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

        left_percent = int(percent * len(left))
        right_percent = int(percent * len(right))

        print("{} Random Walk Iteration".format(self.iteration))
        for j in range(self.iteration):

            # user_nodes_left = self.__get_random_nodes(left_percent, left)
            # user_nodes_right = self.__get_random_nodes(right_percent, right)

            user_nodes_left = self.__get_random_nodes_with_highest_degree(left, left_percent)
            user_nodes_right = self.__get_random_nodes_with_highest_degree(right, right_percent)

            user_nodes_left_list = list(user_nodes_left.keys())
            for i in range(len(user_nodes_left_list) - 1):

                node = user_nodes_left_list[i]
                other_nodes = user_nodes_left_list[:i] + user_nodes_left_list[i + 1:]
                values = [1] * len(other_nodes)
                other_nodes_dict = lists_to_dict(other_nodes, values)

                side = self.__perform_random_walk(graph, node, other_nodes_dict, user_nodes_right)

                if side == "left":
                    left_left += 1

                elif side == "right":
                    left_right += 1

            user_nodes_right_list = list(user_nodes_right.keys())
            for i in range(len(user_nodes_right_list) - 1):

                node = user_nodes_right_list[i]
                other_nodes = user_nodes_right_list[:i] + user_nodes_right_list[i + 1:]
                values = [1] * len(other_nodes)
                other_nodes_dict = lists_to_dict(other_nodes, values)

                side = self.__perform_random_walk(graph, node, user_nodes_left, other_nodes_dict)

                if side == "left":
                    right_left += 1

                elif side == "right":
                    right_right += 1

        e1 = left_left / (left_left + right_left)
        e2 = left_right / (left_right + right_right)
        e3 = right_left / (left_left + right_left)
        e4 = right_right / (left_right + right_right)
        rwc = round(e1 * e4 - e2 * e3, 4)

        border_msg("Random Walk Controversy: {}".format(rwc))
        return rwc

    def __get_random_nodes_with_highest_degree(self, side: list, k: int = 10):

        dict_side: dict = dict((k, 1) for k in side)
        random_nodes = {}
        dict_degrees = {}
        for node in self.graph.nodes():
            dict_degrees[node] = self.graph.degree(node)
        sorted_dict = sorted(dict_degrees.items(), key=itemgetter(1), reverse=True)
        count = 0

        for i in sorted_dict:
            if count > k:
                break
            if not dict_side.get(i[0]):
                continue
            random_nodes[i[0]] = i[1]
            count += 1

        return random_nodes

    @staticmethod
    def __get_random_nodes(k, side):

        random_nodes = []
        random_nodes_dict = {}

        for i in range(k):
            random_num = random.randint(0, len(side) - 1)
            random_nodes.append(side[random_num])
            random_nodes_dict[side[random_num]] = 1

        return random_nodes_dict

    @staticmethod
    def __perform_random_walk(graph, node, left_side, right_side):

        flag = 0
        side = ""
        starting_node = node

        while flag != 1:

            neighbors = list(graph.neighbors(starting_node))
            random_num = random.randint(0, len(neighbors) - 1)
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

            if self.__satisfy_second_condition(keys, self.graph, dict_left, dict_right, cut_nodes1):
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
            polarization_score += (dict_internal[keys] * 1.0 / (dict_internal[keys] + dict_across[keys]) - 0.5)

        polarization_score = round(polarization_score / len(cut_nodes.keys()), 4)
        border_msg("GMCK controversy - boundary connectivity: {}".format(polarization_score))
        return polarization_score

    @staticmethod
    def __satisfy_second_condition(node1, graph: nx.Graph, dict_left, dict_right, cut):
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


class ForceAtlasControversy(ControversyMeasure):

    def __init__(self, graph: nx.Graph, communities: dict, atlas_properties: dict = None):

        if atlas_properties is None:
            atlas_properties = {"iterations": 1000, "linlog": False, "pos": None, "nohubs": False, "k": None, "dim": 2}
        self.position_node = self.__force_atlas2_layout(graph, atlas_properties)
        super().__init__(graph, communities)

    def get_controversy(self):

        left = list(self.communities[0])
        right = list(self.communities[1])
        dict_left = lists_to_dict(left, [1] * len(left))
        dict_right = lists_to_dict(right, [1] * len(right))

        atlas_layout = self.position_node

        dict_positions = {}
        for i in atlas_layout:
            node = i
            line1 = atlas_layout[i]
            [x, y] = [line1[0], line1[1]]
            dict_positions[node] = [x, y]

        left_list = list(dict_left.keys())
        total_lib_lib = 0.0
        count_lib_lib = 0.0

        for i in range(len(left_list)):
            user1 = left_list[i]
            for j in range(i + 1, len(left_list)):
                user2 = left_list[j]
                dist = self.__get_distance(dict_positions[user1], dict_positions[user2])
                total_lib_lib += dist
                count_lib_lib += 1.0
        avg_lib_lib = total_lib_lib / count_lib_lib

        right_list = list(dict_right.keys())
        total_cons_cons = 0.0
        count_cons_cons = 0.0

        for i in range(len(right_list)):
            user1 = right_list[i]
            for j in range(i + 1, len(right_list)):
                user2 = right_list[j]
                dist = self.__get_distance(dict_positions[user1], dict_positions[user2])
                total_cons_cons += dist
                count_cons_cons += 1.0
        avg_cons_cons = total_cons_cons / count_cons_cons

        total_both = 0.0
        count_both = 0.0

        for i in range(len(left_list)):
            user1 = left_list[i]
            for j in range(len(right_list)):
                user2 = right_list[j]
                dist = self.__get_distance(dict_positions[user1], dict_positions[user2])
                total_both += dist
                count_both += 1.0
        avg_both = total_both / count_both

        score = round(1 - ((avg_lib_lib + avg_cons_cons) / (2 * avg_both)), 4)
        print("Embedding score: {}".format(score))
        return score

    @staticmethod
    def __force_atlas2_layout(graph: nx.Graph, atlas_properties: dict):

        print("Start creating Force Atlas Layout")
        iterations = atlas_properties.get("iterations", 1000)
        linlog = atlas_properties.get("linlog", False)
        pos = atlas_properties.get("pos", None)
        nohubs = atlas_properties.get("nohubs", False)
        k = atlas_properties.get("k", None)
        dim = atlas_properties.get("dim", 2)

        A = nx.to_scipy_sparse_matrix(graph, dtype='f')
        nnodes, _ = A.shape

        try:
            A = A.tolil()
        except Exception as e:
            A = (coo_matrix(A)).tolil()
        if pos is None:
            pos = np.asarray(np.random.random((nnodes, dim)), dtype=A.dtype)
        else:
            pos = pos.astype(A.dtype)
        if k is None:
            k = np.sqrt(1.0 / nnodes)
        t = 0.1

        dt = t / float(iterations + 1)
        displacement = np.zeros((dim, nnodes))
        for iteration in range(iterations):
            displacement *= 0
            for i in range(A.shape[0]):
                delta = (pos[i] - pos).T
                distance = np.sqrt((delta ** 2).sum(axis=0))
                distance = np.where(distance < 0.01, 0.01, distance)
                Ai = np.asarray(A.getrowview(i).toarray())
                dist = k * k / distance ** 2
                if nohubs:
                    dist = dist / float(Ai.sum(axis=1) + 1)
                if linlog:
                    dist = np.log(dist + 1)
                displacement[:, i] += \
                    (delta * (dist - Ai * distance / k)).sum(axis=1)
            length = np.sqrt((displacement ** 2).sum(axis=0))
            length = np.where(length < 0.01, 0.01, length)
            pos += (displacement * t / length).T
            t -= dt

        print("Force Atlas done")
        return dict(zip(graph, pos))

    @staticmethod
    def __get_distance(point_a, point_b):
        x1 = point_a[0]
        y1 = point_a[1]
        x2 = point_b[0]
        y2 = point_b[1]
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


# not used
class EdgeBetweennessControversy(ControversyMeasure):

    def __init__(self, graph: nx.Graph, communities: dict):

        self.edge_betweenness = nx.edge_betweenness(graph)
        super().__init__(graph, communities)

    def get_controversy(self):

        left = list(self.communities[0])
        right = list(self.communities[1])

        eb_list = []

        for i in left:
            node1 = i
            for j in right:
                node2 = j
                if self.graph.has_edge(node1, node2):
                    if self.edge_betweenness.get((node1, node2)):
                        edge_betweenness = self.edge_betweenness[(node1, node2)]
                        eb_list.append(edge_betweenness)
                    else:
                        edge_betweenness = self.edge_betweenness[(node2, node1)]
                        eb_list.append(edge_betweenness)

        eb_list1 = np.asarray(eb_list)
        eb_list2 = []
        eb_list_all = []

        for edge in self.edge_betweenness:
            eb_list_all.append(self.edge_betweenness.get(edge))

        eb_list_all1 = np.asarray(eb_list_all)
        print("Ratio of edge betweenness", np.median(eb_list1) / np.median(eb_list_all1))

        for eb in eb_list:
            eb_list2.append(eb / np.max(eb_list1))

        eb_list3 = np.asarray(eb_list2)
        mean = np.mean(eb_list3).round(decimals=4)
        median = np.median(eb_list3).round(decimals=4)
        print("Mean edge betweenness on the cut {}, Median edge betweenness on the cut {}".format(mean, median))
        return mean
