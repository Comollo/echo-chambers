# define controversy measure

import networkx as nx
import random
from src.controversy.controversy_measure import ControversyMeasure
from src.common.utility import border_msg, lists_to_dict


class RandomWalkControversy(ControversyMeasure):

    def __init__(self, graph: nx.Graph, communities: dict, percent: float = 0.10):

        self.percent = percent
        super().__init__(graph, communities)

    def get_controversy(self):

        percent = self.percent
        graph = self.graph

        left = list(self.communities[0])
        right = list(self.communities[1])

        left_values = [1] * len(left)
        dict_left = lists_to_dict(left, left_values)

        right_values = [1] * len(right)
        dict_right = lists_to_dict(right, right_values)

        left_left = 0
        left_right = 0
        right_right = 0
        right_left = 0

        left_percent = int(percent*len(dict_left.keys()))
        right_percent = int(percent*len(dict_right.keys()))

        for j in range(1, 1000):

            user_nodes_left = self.get_random_nodes_from_labels(left_percent, left, "left")
            user_nodes_right = self.get_random_nodes_from_labels(right_percent, right, "right")

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

                else:
                    continue

            print("Getting probabilities -> round {}".format(j))

        e1 = left_left*1.0 / (left_left+right_left)
        e2 = left_right*1.0 / (left_right+right_right)
        e3 = right_left*1.0 / (left_left+right_left)
        e4 = right_right*1.0 / (left_right+right_right)
        rwc = e1*e4 - e2*e3

        border_msg("Random Walk Controversy: {}".format(rwc))
        return rwc

    @staticmethod
    def get_random_nodes_from_labels(k, side, flag):

        random_nodes = []
        random_nodes1 = {}

        if flag == "left":
            for i in range(k):
                random_num = random.randint(0, len(side)-1)
                random_nodes.append(side[random_num])

        elif flag == "right":
            for i in range(k):
                random_num = random.randint(0, len(side)-1)
                random_nodes.append(side[random_num])

        else:
            for i in range(k/2):
                random_num = random.randint(0, len(side)-1)
                random_nodes.append(side[random_num])
            for i in range(k/2):
                random_num = random.randint(0, len(side)-1)
                random_nodes.append(side[random_num])

        for ele in random_nodes:
            random_nodes1[ele] = 1
        return random_nodes1

    @staticmethod
    def perform_random_walk(graph, starting_node, user_nodes_side1, user_nodes_side2):

        dict_nodes = {}  # contains unique nodes seen till now
        step_count = 0
        flag = 0
        side = ""

        while flag != 1:

            neighbors = list(graph.neighbors(starting_node))
            random_num = random.randint(0, len(neighbors)-1)
            starting_node = neighbors[random_num]
            dict_nodes[starting_node] = 1
            step_count += 1

            if starting_node in user_nodes_side1:
                side = "left"
                flag = 1
            if starting_node in user_nodes_side2:
                side = "right"
                flag = 1

        return side
