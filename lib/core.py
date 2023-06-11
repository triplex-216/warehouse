# Resolves class type hinting itself, see https://stackoverflow.com/a/33533514
from __future__ import annotations
import csv
from math import floor
import os
import heapq

""" Configuration Constants """
# Initializes the map with specific size
DEFAULT_ROWS = 21
DEFAULT_COLS = 40


""" Data processing """

class PriorityQueue:
    """
    An implementation of Priority Queue with heapq
    Generated with ChatGPT
    """

    def __init__(self):
        self._queue = []
        self._index = 0

    def is_empty(self):
        return len(self._queue) == 0

    def enqueue(self, item, priority1, priority2=None):
        heapq.heappush(self._queue, (priority1, priority2, self._index, item))
        self._index += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Priority queue is empty")
        priority1, _, _, item = heapq.heappop(self._queue)
        return priority1, item
    
class AccessPoint:
    def __init__(self, coord: tuple[int, int], parent: Node) -> None:
        self.coord = coord
        self.parent = parent  # Pointer to parent node
        self.dv = dict()  # Initialize distance vector

    def add_path(
        self, destination: AccessPoint, distance: int, path: list[tuple[int, int]]
    ) -> None:
        """
        Add a path to the distance vector. The path goes from this AP
        to another AP with a tuple containing the path's distance and
        grid-by-grid path to take
        """
        self.dv[destination] = (distance, path)
        destination.dv[self] = (distance, path[::-1])

    def get_nearest_ap(self) -> tuple[int, list[tuple[int, int]]]:
        """
        Return the nearest AP stored in the current AP's distance vector
        """
        return min(self.dv.items(), key=lambda item: item[1][0])


class Node:
    """
    A Node describes an item in the warehouse. Aside from an ID, it has
    a coordinate and up to 4 APs (AccessPoint, defined in the AccessPoint class).

    Each Node instance is intended to be initialized with a map. The
    map binding should not be changed once created, as the underlying
    AccessPoints depend on the map.

    After creation of Nodes, the distance vectors in their APs are empty
    and do not store any distance information. generate_cost_graph()
    must be called to calculate and create that information, see its
    documentation for usage.
    """

    def __init__(self, id: list, coord: tuple[int, int], map) -> None:
        self.id, self.coord = id, coord

        # The product's neighbors; initialized with empty elements and will be updated later
        self._ap = {"n": None, "e": None, "s": None, "w": None}
        # Bind reference to the map from which this product instance was created
        self._map = map

        # Detect valid neighbors (access points)
        aps = get_aps(self._map, self.coord)
        # Assign each neighbor to a direction (n/s/e/w)
        for direction, ap in aps:
            match direction:
                case (1, 0):
                    self._ap["n"] = AccessPoint(coord=ap, parent=self)
                case (0, 1):
                    self._ap["e"] = AccessPoint(coord=ap, parent=self)
                case (-1, 0):
                    self._ap["s"] = AccessPoint(coord=ap, parent=self)
                case (0, -1):
                    self._ap["w"] = AccessPoint(coord=ap, parent=self)

    @property
    def x(self) -> int:
        return self.coord[0]

    @property
    def y(self) -> int:
        return self.coord[1]

    @property
    def n(self) -> AccessPoint:
        return self._ap["n"]

    @property
    def e(self) -> AccessPoint:
        return self._ap["e"]

    @property
    def s(self) -> AccessPoint:
        return self._ap["s"]

    @property
    def w(self) -> AccessPoint:
        return self._ap["w"]

    @property
    def aps(self):
        return [v for v in self._ap.values() if v]

    @property
    def aps_all(self) -> list[AccessPoint]:
        """
        Return a list of neighbors containing empty directions,
        For example, the first element would be None if the north AP doesn't exist
        """
        return list(self._ap.values())


class SingleNode(Node):
    """
    Single Access Nodes that are on both "ends" of the nodes list, i.e.
    the starting or ending nodes. SingleNode have a item ID of 0 and a north
    AP that has the same coordinate as the SingleNode themselves, so that they
    can be treated like standard Nodes in algorithms.
    """

    def __init__(self, coord, map, access_self=True):
        super().__init__([-1], coord, map)  # Initialize APs like a normal Node

        if access_self:
            # If the node's grid itself can be accessed,
            # i.e. Start/End nodes where no AP is necessary
            self._ap["n"] = AccessPoint(coord=self.coord, parent=self)
            # Remove all APs except the north one, and set it to have the
            # same coordinate as the node
            for direction in ["e", "s", "w"]:
                self._ap[direction] = None
        else:
            # Keep the first available AP and drop others
            # Has a priority: N-E-S-W
            drop = True
            for direction in ["n", "e", "s", "w"]:
                if not drop:
                    self._ap[direction] = None
                if self._ap[direction]:
                    drop = False  # Drop APs on other directions

class Config:
    def __init__(
        self,
        use_random_item=False,
        save_instructions=False,
        default_algorithm="b",  # branch and bound by default
        start_position=(0, 0),
        end_position=(0, 0),
        default_timeout_value=60,
        map_data=None,
        prod_db=None,
    ) -> None:
        self.use_random_item = use_random_item
        self.save_instructions = save_instructions
        self.default_algorithm = default_algorithm
        self.start_position = start_position
        self.end_position = end_position
        self.default_timeout_value = default_timeout_value
        self.map_data = map_data
        self.prod_db = prod_db


# Read data from the file
def read_inventory_data(file_path: str, conf: Config) -> tuple[list[list[int]], dict[tuple]]:
    """
    Input:
        file_path: Path to the inventory dataset file

    Output:
        map_data: A 2D list describing the warehouse map.
        prod_db: An dictionary; key is the product's id, and the value
                 is a Prod instance describing that product
    """
    id = []
    col = []
    row = []

    # Read data
    with open(file_path) as csvfile:
        reader = csv.reader(csvfile, delimiter="\t")
        for curr in reader:  # For every data (row)
            id.append(curr[0])
            col.append(curr[1])
            row.append(curr[2])

    id, col, row = id[1:], col[1:], row[1:]  # Remove the table header
    id = [int(i) for i in id]
    col = [floor(float(a)) for a in col]  # Drop the decimals in xLocation
    row = [int(b) for b in row]

    # Product database
    prod_db = dict()

    # Initialize an empty map, it should be a 2-d list[40][21]
    # Note: 0 - empty, 1 - shelf
    # Column - X, Row - Y, map[X][Y]
    cols, rows = DEFAULT_COLS, DEFAULT_ROWS
    map_data = [[0] * rows for _ in range(cols)]

    for i, c, r in zip(id, col, row):
        # Set all shelves to 1
        map_data[c][r] = 1
        prod_db[i] = (c, r)

    conf.map_data = map_data
    conf.prod_db = prod_db


def get_item(product_db: dict, id_list: list) -> list[tuple]:
    prod_list = []
    for id in id_list:
        try:
            prod_list.append(product_db[id])
        except KeyError:
            print(f"Item {id} not found, skipping...")

    return prod_list


# Read order list from the file
def read_order_file(file_path):
    order_list = {}
    if os.path.exists(file_path):
        id = 1
        with open(file_path) as csvfile:
            reader = csv.reader(csvfile, delimiter="\t")
            for curr in reader:
                order_list[id] = [int(num) for num in curr[0].split(",")]
                id += 1
    return order_list

def is_valid(map, coord):
    valid = True
    if coord[0] not in range(len(map)) or coord[1] not in range(len(map[0])):
        print("Coordinate exceeds the range of map, please try again.")
        valid = False
    elif map[coord[0]][coord[1]] == 1:
        valid = False
    return valid

def get_aps(map, node: tuple) -> list[tuple[tuple, tuple]]:
    aps = []  # list record dir and ap coord
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    row, col = len(map), len(map[0])
    for direction in directions:
        d_x, d_y = direction
        neighbor = (node[0] + d_x, node[1] + d_y)
        if (
            neighbor[0] in range(row)
            and neighbor[1] in range(col)
            and map[neighbor[0]][neighbor[1]] == 0
        ):
            aps.append((direction, neighbor))
    return aps
