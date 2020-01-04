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

        for j in range(self.iteration):

            print("Random Walking -> iteration {}".format(j))

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
